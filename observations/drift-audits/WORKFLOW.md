# Drift-Audit Workflow (v1 scaffolding)

**Runtime artifact** — how auditors actually run the drift-audit procedure on a closed session bundle and commit the result. Paired with [`RUBRIC.md`](RUBRIC.md) (which defines *what* drift is) — this file defines *how* the audit is executed, reconciled, committed, and re-audited.

**Authoritative spec**: [`specs/008-drift-audit-workflow/spec.md`](../../specs/008-drift-audit-workflow/spec.md).
**Scope boundary**: this file is the operator-facing procedure. Schema for `drift-audit.json` is owned by [spec 005 data-model](../../specs/005-drift-audit-rubric/data-model.md); rubric content is owned by [`RUBRIC.md`](RUBRIC.md). This file does not redefine either.

---

## When to use which path

| Situation | Path |
|---|---|
| Closed session bundle, exploratory / pre-calibration audit, single auditor | **Path A — Single-auditor** |
| Closed session bundle, counted Phase 3 session, independent review required | **Path B — Two-auditor** |
| Prior audit exists, rubric evolved OR upgrading single → two-auditor | **Path C — Re-audit / upgrade** |

> **Counted sessions require Path B** for H1/H2 evidence eligibility per constitution v1.5.0 Principle IV (independent review). Single-auditor audits on counted sessions must be upgraded via Path C before the session is eligible.

---

## Prerequisites (common to all paths)

Verify before starting any audit:

1. `observations/sessions/<session-id>/` exists and is closed per [spec 001](../../specs/001-session-bundle-skeleton/spec.md):
   - `transcript.md` present (non-empty; zero-turn transcripts still produce a valid file per [spec 006](../../specs/006-discord-transcript-export/spec.md))
   - `meta.json` present with `session_id`, `pinned_rules_ref`, `closed_at`
   - `interventions.json` present (may be empty per the Codex intervention-tagging slice; this workflow treats the shape opaquely)
2. `observations/drift-audits/RUBRIC.md` has no uncommitted working-tree changes (rubric version must resolve to a committed SHA per [FR-002](../../specs/008-drift-audit-workflow/spec.md)).
3. You have write access to the session bundle's branch / main, per [`docs/ways-of-working/pull-requests.md`](../../docs/ways-of-working/pull-requests.md).

If any prerequisite fails, see **Halt conditions** below — fix upstream first; do not paper over.

---

## Path A — Single-auditor audit

Use this for exploratory / pre-calibration sessions, non-counted sessions, or cases where a cross-reviewer is genuinely unavailable. Counted Phase 3 sessions must either use Path B directly or be upgraded via Path C.

### Step 1 — Pin the rubric version

```bash
cd <repo-root>
RUBRIC_SHA=$(git log -1 --format=%H -- observations/drift-audits/RUBRIC.md)
RUBRIC_SHORT=$(git rev-parse --short "$RUBRIC_SHA")
echo "Auditing against RUBRIC.md @ $RUBRIC_SHA (short: $RUBRIC_SHORT)"
```

If `RUBRIC.md` has uncommitted working-tree changes, **halt** — see **Halt conditions**.

### Step 2 — Walk the rubric against the bundle

Open the bundle:

```bash
cd observations/sessions/<session-id>/
```

Follow [`RUBRIC.md`](RUBRIC.md) §4 Steps 1–3 (gather inputs; scan transcript turn by turn against each category; assign severity per candidate). Keep your candidate findings as a working list — one row per finding with `category`, `severity`, `quote`, `turn_ref`, `rationale`.

### Step 3 — Author `drift-audit.json`

Create `observations/sessions/<session-id>/drift-audit.json` conforming to [spec 005 data-model](../../specs/005-drift-audit-rubric/data-model.md):

- `rubric_version`: full 40-char SHA (`$RUBRIC_SHA` from Step 1) — not the short form
- `session_id`: from `meta.json.session_id`
- `pinned_rules_ref`: from `meta.json.pinned_rules_ref`
- `audited_at`: current RFC3339 UTC timestamp
- `audited_by`: `"manual"` (the workflow's v1 single-auditor path is always manual; `"hybrid"` / `"llm_assisted"` values come online with Path B once LLM-judge is calibrated)
- `auditor`: your identity as a free-text string (e.g. `"Zoe"`, `"Dalgos"`)
- `findings`: the array you built in Step 2, ordered by `turn_ref` ascending per spec 005's determinism rule
- `load_bearing_findings_count`: count of entries with `severity: "finding"`
- `verdict`: computed per [`RUBRIC.md`](RUBRIC.md) §3 (`no_drift` / `minor_drift` / `load_bearing_drift`)

**Idempotency note** ([FR-010](../../specs/008-drift-audit-workflow/spec.md), [research.md R3](../../specs/008-drift-audit-workflow/research.md)): re-running Path A on the same bundle with the same rubric version by the same auditor produces byte-identical `drift-audit.json` *modulo the `audited_at` timestamp*. Determinism comes from spec 005's canonical-form serialization (ordered findings, computed `load_bearing_findings_count`, full-SHA `rubric_version`) — no new normalization rule applies here. Only `audited_at` legitimately varies.

### Step 4 — Commit as a session-bundle amend

```bash
git add observations/sessions/<session-id>/drift-audit.json
git commit -m "session bundle amend: <session-id> — drift-audit @ $RUBRIC_SHORT"
```

No taxonomy token — Path A's default is untagged (see [`COMMIT-TAXONOMY.md`](COMMIT-TAXONOMY.md)).

### Step 5 — Run sanity checks

See **Post-commit sanity checks** below. If any check fails, fix and re-commit with `--amend` (same commit, not a new one) before marking the audit complete.

**Done.** Session now carries a committed single-auditor audit. If this session is intended as counted Phase 3 evidence, flag it for upgrade via Path C.

## Path B — Two-auditor audit (counted sessions)

Use this for sessions intended as counted H1/H2 evidence. Two independent passes against the same pinned rubric version get reconciled against spec 005's FR-016 tolerance. In the POC, the two auditors are typically one human operator and one LLM-judge cross-reviewer — see **LLM-judge as cross-reviewer** below for the entry criteria.

### Step 1 — Pin the rubric version (shared by both auditors)

Same as Path A Step 1. Both primary auditor and cross-reviewer MUST use the identical `$RUBRIC_SHA`.

### Step 2 — Primary auditor produces draft A

Primary auditor (typically the operator) runs [`RUBRIC.md`](RUBRIC.md) §4 and produces a draft `drift-audit.json` — **do not commit yet**. Keep it as a working file next to the bundle, e.g.:

```bash
observations/sessions/<session-id>/drift-audit.draft-primary.json
```

### Step 3 — Cross-reviewer produces draft B independently

The cross-reviewer (human or LLM-judge) runs [`RUBRIC.md`](RUBRIC.md) §4 against the **same** bundle and the **same** `$RUBRIC_SHA`.

**Independence discipline** ([FR-005](../../specs/008-drift-audit-workflow/spec.md), [contract C5](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md)):

- Either the cross-reviewer never sees draft A before finalizing draft B (enforced isolation), OR
- the cross-reviewer finalizes draft B before seeing draft A and the **operator attests to that independence** in the commit body.

The workflow does NOT enforce isolation mechanically; operator attestation is the gate. For LLM-judge cross-reviewers, see **LLM-judge as cross-reviewer** below — the prompt template produces natural isolation.

Store as:

```bash
observations/sessions/<session-id>/drift-audit.draft-cross.json
```

### Step 4 — Reconciliation against spec 005 FR-016 tolerance

Compute:

```bash
PC=$(jq -r '.load_bearing_findings_count' observations/sessions/<session-id>/drift-audit.draft-primary.json)
CC=$(jq -r '.load_bearing_findings_count' observations/sessions/<session-id>/drift-audit.draft-cross.json)
DIFF=$(( PC > CC ? PC - CC : CC - PC ))
echo "|primary($PC) - cross($CC)| = $DIFF"
```

- **If `$DIFF` ≤ 1** (within spec 005 FR-016 tolerance for ≤200-turn sessions): go to Step 5a.
- **If `$DIFF` > 1** (diverged): go to Step 5b — operator arbitration.

### Step 5a — Within tolerance: merge and commit

The primary auditor merges the two drafts into a single `drift-audit.json`:

- `findings`: union of primary + cross, deduplicated by `(category, turn_ref, severity)`, ordered by `turn_ref` ascending
- `auditor`: `"<primary-id>, <cross-reviewer-id>"` (comma-separated; spec 005's free-text schema accepts this)
- `audited_by`: `"manual"` if both auditors are human, `"hybrid"` if one is the LLM-judge
- other fields: as in Path A Step 3

Commit:

```bash
git add observations/sessions/<session-id>/drift-audit.json
rm observations/sessions/<session-id>/drift-audit.draft-*.json
git add -u
git commit -m "session bundle amend: <session-id> — drift-audit @ $RUBRIC_SHORT" \
           -m "Two-auditor: primary=<primary-id>, cross=<cross-reviewer-id>. Within tolerance (diff=$DIFF)."
```

No taxonomy token — agreed two-auditor is the default within-tolerance case (see [`COMMIT-TAXONOMY.md`](COMMIT-TAXONOMY.md)).

### Step 5b — Diverged: operator arbitrates

When `$DIFF` > 1, the operator reviews both drafts, decides which findings stand, and authors the final `drift-audit.json`:

- `findings`: operator-selected set (can include subsets from either draft, or a fresh synthesis)
- `auditor`: `"<operator-id> (arbitrating <primary-id>/<cross-reviewer-id>)"`
- `audited_by`: `"manual"` or `"hybrid"` depending on who produced the drafts
- other fields: as in Path A Step 3

Commit with the `[arbitrated]` token — this is the **arbitration-ledger signal** per [contract C7](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md):

```bash
git add observations/sessions/<session-id>/drift-audit.json
rm observations/sessions/<session-id>/drift-audit.draft-*.json
git add -u
git commit -m "session bundle amend: <session-id> — drift-audit [arbitrated] @ $RUBRIC_SHORT" \
           -m "Operator arbitration. Primary=<primary-id> found $PC load-bearing; cross=<cross-reviewer-id> found $CC. Arbitrated to <N>: <brief rationale>."
```

**The `[arbitrated]` token is the calibration signal.** POC-exit synthesis and mid-POC calibration review grep for it — if a high fraction of counted sessions arbitrate, that's the signal that spec 005 §6.3 calibration is owed. Per spec 008 FR-008, an arbitrated session remains counted-eligible — the signal is emitted via commit message, not by holding the session in a pending state.

Verify the ledger includes this session:

```bash
git log --all --grep='\[arbitrated\]' --format='%H %s'
```

### Step 6 — Run sanity checks

Same as Path A Step 5. See **Post-commit sanity checks** below.

**Done.** Session is counted-eligible with independent-review evidence satisfying constitution v1.5.0 Principle IV.

---

### LLM-judge as cross-reviewer

In the POC, two-auditor mode in practice usually means **one human operator + one LLM-judge**, not two humans. POC staffing is thin.

**Entry criteria** ([FR-014](../../specs/008-drift-audit-workflow/spec.md), [spec 005 §7](../../specs/005-drift-audit-rubric/spec.md)): the LLM-judge path becomes available only after:

1. At least 2 counted manual Phase 3 sessions have completed two-auditor audits (two humans), AND
2. Those sessions landed within spec 005 FR-016 tolerance at Step 4 (evidence the rubric has been calibrated enough to be reliable), AND
3. The operator has read [`RUBRIC.md`](RUBRIC.md) §7 (the LLM-judge prompt template) and decided the template is ready for the specific rubric version active in the session.

Before those criteria are met, counted sessions either use two humans (if available) or run as single-auditor via Path A and are upgraded via Path C once a cross-reviewer passes.

**Operating note**:

- The LLM-judge is invoked per [`RUBRIC.md`](RUBRIC.md) §7's prompt template. The template provides natural isolation — the LLM does not see draft A.
- The operator is still the arbiter in Step 5b; LLM-judge output is input to reconciliation, not the final verdict.
- `audited_by: "hybrid"` is the correct value when one auditor is manual and one is LLM-judge; `"llm_assisted"` is reserved for a future slice where the primary pass itself is LLM-produced (not scoped here).

## Path C — Re-audit and single→two upgrade

Use this when:

- The rubric has evolved (calibration commit on `RUBRIC.md`) and a past session's audit should be refreshed against the new version, OR
- A session's single-auditor audit (Path A) should be upgraded to two-auditor so it's counted-eligible for H1/H2 evidence, OR
- The [POC-exit rubric-version sweep](#triggers-when-re-audit) flagged this bundle as stale and the operator chose to re-audit.

Path C is a **replacement** operation, not a delta — the new `drift-audit.json` fully replaces the prior committed file. The prior audit remains reconstructible via git history per [contract C6](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md).

### Step 1 — Identify the reason

Pick from:

1. **Rubric evolution**: `RUBRIC.md` has a new commit since the prior audit landed. Pin the new `$RUBRIC_SHA`.
2. **Single → two upgrade** (rubric unchanged): a cross-reviewer pass is landing against an existing single-auditor audit. Rubric version typically stays the same.
3. **Both**: new rubric version AND cross-reviewer upgrade — combine tokens.

### Step 2 — Retrieve the prior audit's rubric version (for the commit message)

```bash
SID=<session-id>
OLD_RUBRIC_SHORT=$(jq -r '.rubric_version' "observations/sessions/$SID/drift-audit.json" | cut -c1-7)
NEW_RUBRIC_SHA=$(git log -1 --format=%H -- observations/drift-audits/RUBRIC.md)
NEW_RUBRIC_SHORT=$(git rev-parse --short "$NEW_RUBRIC_SHA")
echo "Re-audit: supersedes $OLD_RUBRIC_SHORT, now auditing against $NEW_RUBRIC_SHORT"
```

(If rubric version is unchanged, `OLD_RUBRIC_SHORT` == `NEW_RUBRIC_SHORT` — that's fine, the token format still carries the correct information.)

### Step 3 — Run the appropriate audit path

- For a rubric-evolution re-audit staying in the same mode: run Path A or Path B (whichever the bundle was) end-to-end with the new `$NEW_RUBRIC_SHA`.
- For a single → two upgrade: run Path B (both auditors reading the existing rubric, producing independent drafts).
- For combined: run Path B with the new rubric version.

The new `drift-audit.json` replaces the prior one on disk. Do NOT try to merge with or append to the prior audit — Path C is replacement.

### Step 4 — Commit with the correct taxonomy token

Pick the token based on the reason (see [`COMMIT-TAXONOMY.md`](COMMIT-TAXONOMY.md)):

| Reason | Token |
|---|---|
| Rubric evolution only, mode unchanged | `re-run, supersedes $OLD_RUBRIC_SHORT` |
| Single → two upgrade only, rubric unchanged | `two-auditor-upgrade` |
| Both rubric evolution AND upgrade | `two-auditor-upgrade re-run, supersedes $OLD_RUBRIC_SHORT` |
| Any of the above, arbitrated in Step 5b of Path B | prefix with `[arbitrated]` |

Examples:

```bash
# Rubric evolution, within-tolerance two-auditor:
git commit -m "session bundle amend: $SID — drift-audit re-run, supersedes $OLD_RUBRIC_SHORT @ $NEW_RUBRIC_SHORT"

# Single → two upgrade, no rubric change:
git commit -m "session bundle amend: $SID — drift-audit two-auditor-upgrade @ $NEW_RUBRIC_SHORT"

# Combined upgrade + rubric evolution:
git commit -m "session bundle amend: $SID — drift-audit two-auditor-upgrade re-run, supersedes $OLD_RUBRIC_SHORT @ $NEW_RUBRIC_SHORT"

# Arbitrated combined (rare):
git commit -m "session bundle amend: $SID — drift-audit [arbitrated] two-auditor-upgrade re-run, supersedes $OLD_RUBRIC_SHORT @ $NEW_RUBRIC_SHORT"
```

### Step 5 — Verify the prior audit is preserved in git history

```bash
git log --all --follow --format='%H %s' -- "observations/sessions/$SID/drift-audit.json"
git show <prior-commit>:"observations/sessions/$SID/drift-audit.json"
```

The prior audit is retrievable; the current file on disk is the authoritative consumer-relevant version per [contract C8](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md).

### Step 6 — Run sanity checks

Same as Path A Step 5. See **Post-commit sanity checks** below.

---

### <a id="triggers-when-re-audit"></a>Triggers — when to re-audit

Per [FR-012](../../specs/008-drift-audit-workflow/spec.md), re-audit runs on two paths:

1. **Explicit operator request** — at any time, the operator selects a specific bundle for re-audit. Always valid regardless of rubric-version state.
2. **POC-exit rubric-version sweep** — at POC-exit synthesis time, the POC-exit synthesis slice (not yet specced) produces a sweep artifact enumerating each counted-session bundle, its pinned `rubric_version`, and the synthesis-time `RUBRIC.md` HEAD SHA. Stale bundles are flagged re-audit-eligible; the operator decides per-bundle whether to re-audit before the final KPI roll-up.

This workflow supports both paths but only specifies path (1) operationally. Path (2) is delegated to the POC-exit synthesis slice when that slice is cut — this workflow only guarantees the data it needs (reliable `rubric_version` pins on every committed audit) is available.

**Not supported**: continuous or daemon-driven detection of stale audits between sessions. Out of scope per FR-012 — keeps this slice narrow and aligned with POC staffing constraints.

---

## Halt conditions

Stop and fix upstream — do NOT produce a partial or placeholder `drift-audit.json`, per [FR-018](../../specs/008-drift-audit-workflow/spec.md). Every halt corresponds to a [workflow contract C1](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md) pre-condition that failed.

| Condition | Fix where |
|---|---|
| `observations/sessions/<session-id>/` does not exist | Confirm `session_id`; session may not be closed yet |
| `meta.json` missing or unreadable | Session-bundle close step ([spec 001](../../specs/001-session-bundle-skeleton/spec.md)) |
| `meta.json.pinned_rules_ref` unset | Session-bundle close step ([spec 001 FR-010](../../specs/001-session-bundle-skeleton/spec.md)) |
| `meta.json.closed_at` unset | Session is still open — close it first via the session-control path (spec 004) |
| `meta.json.session_id` empty | Session-bundle close step (spec 001) |
| `transcript.md` missing | Transcript export ([spec 006](../../specs/006-discord-transcript-export/spec.md)) |
| `interventions.json` missing | Intervention-tagging slice (Codex) — if intervention-tagging hasn't landed yet, log this as a Phase 2 blocker rather than running the audit without interventions context |
| `observations/drift-audits/RUBRIC.md` has uncommitted working-tree changes | Commit the rubric change first via the rubric-authoring workflow in [`README.md`](README.md) |
| Working tree has other uncommitted changes unrelated to the audit | Stash or commit those first — audit amend commit should land clean |

**Non-silent failure principle** ([FR-018](../../specs/008-drift-audit-workflow/spec.md)): when halting, surface the specific unmet condition to whoever is running the audit (operator, agent, or future tooling). Don't silently produce a half-formed artifact or emit a placeholder. The bundle-producer upstream is the right place to fix.

---

## Post-commit sanity checks

Run these after every committed audit (Path A, B, or C). If any check fails, the audit has drifted from [contract C2](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md) — fix and re-commit with `git commit --amend` before marking the audit complete.

```bash
SID=<session-id>

# 1. The committed file is valid JSON
jq '.' "observations/sessions/$SID/drift-audit.json" >/dev/null && echo "✓ valid JSON"

# 2. rubric_version resolves to an existing commit
RV=$(jq -r '.rubric_version' "observations/sessions/$SID/drift-audit.json")
git cat-file -e "$RV" 2>/dev/null && echo "✓ rubric_version resolves: $RV"

# 3. load_bearing_findings_count matches the findings array
COUNT=$(jq -r '.load_bearing_findings_count' "observations/sessions/$SID/drift-audit.json")
ACTUAL=$(jq '[.findings[] | select(.severity == "finding")] | length' "observations/sessions/$SID/drift-audit.json")
[ "$COUNT" = "$ACTUAL" ] && echo "✓ load_bearing_findings_count=$COUNT matches"

# 4. session_id and pinned_rules_ref match meta.json
SID_IN_AUDIT=$(jq -r '.session_id' "observations/sessions/$SID/drift-audit.json")
SID_IN_META=$(jq -r '.session_id' "observations/sessions/$SID/meta.json")
[ "$SID_IN_AUDIT" = "$SID_IN_META" ] && echo "✓ session_id matches meta.json"

PRR_IN_AUDIT=$(jq -r '.pinned_rules_ref' "observations/sessions/$SID/drift-audit.json")
PRR_IN_META=$(jq -r '.pinned_rules_ref' "observations/sessions/$SID/meta.json")
[ "$PRR_IN_AUDIT" = "$PRR_IN_META" ] && echo "✓ pinned_rules_ref matches meta.json"

# 5. The amend commit is discoverable via the session-bundle's history
git log -1 --format='%H %s' -- "observations/sessions/$SID/drift-audit.json"
```

All five checks are cheap and fast — run them as a habit after every audit commit.

---

## Downstream consumption

Per [FR-016](../../specs/008-drift-audit-workflow/spec.md) and [contract C8](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md), downstream consumers of audit evidence (Phase 5 KPI rollup, H2 per-session reviewer, POC-exit synthesis) read `drift-audit.json.verdict` directly — they MUST NOT re-derive drift findings from transcript + rubric.

Composition rules for H2 evidence are specified in [`RUBRIC.md`](RUBRIC.md) §8:

- `verdict: "no_drift"` → H2 judgment proceeds on other grounds (transcript completeness, etc.); drift is not the blocker.
- `verdict: "minor_drift"` → H2 is probably still passable; reviewer notes the warnings without them blocking reconstruction.
- `verdict: "load_bearing_drift"` → H2 likely fails on this session; reviewer cites the specific `findings[].rationale` entries that block the fresh-reader reconstruction.

**What consumers rely on** (from [contract C8](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md)):

- The session bundle directory is self-contained — no bundle-specific context outside `observations/sessions/<id>/` is needed.
- The *current* `drift-audit.json` is always the consumer-relevant version; re-audits (Path C) mean historical versions are in git history only, not live evidence.
- Re-runs are idempotent modulo `audited_at` — repeated reads of the same current file return the same `verdict` + `findings`.

---

## Cross-references

- **Spec chain**: [`specs/008-drift-audit-workflow/spec.md`](../../specs/008-drift-audit-workflow/spec.md) → [`plan.md`](../../specs/008-drift-audit-workflow/plan.md) → [`tasks.md`](../../specs/008-drift-audit-workflow/tasks.md)
- **Contracts**: [`specs/008-drift-audit-workflow/contracts/workflow-contracts.md`](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md) (C1–C8)
- **Quickstart** (operator walkthrough, more verbose): [`specs/008-drift-audit-workflow/quickstart.md`](../../specs/008-drift-audit-workflow/quickstart.md)
- **Commit taxonomy**: [`COMMIT-TAXONOMY.md`](COMMIT-TAXONOMY.md) — grep-able vocabulary for audit amend commits
- **Rubric content**: [`RUBRIC.md`](RUBRIC.md) (spec 005)
- **Bundle contract**: [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md) FR-008 (where `drift-audit.json` lives), FR-014 (bundle-amend-commit convention)
- **H2 composition**: spec 005 §8 and workflow contract C8

---

## Scope boundary (explicit)

- **In scope**: audit execution procedure, reconciliation, commit format, re-audit and upgrade paths.
- **Out of scope**: rubric content (spec 005 / `RUBRIC.md`), `drift-audit.json` schema (spec 005 `data-model.md`), intervention-tag shape (Codex slice), LLM automation (deferred follow-on; entry criteria documented in the Path B LLM-judge block), KPI rollup (Phase 5 slice).
