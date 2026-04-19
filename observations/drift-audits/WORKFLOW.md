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

*Filled by US2 — see `specs/008-drift-audit-workflow/quickstart.md` Path B until this section lands.*

## Path C — Re-audit and single→two upgrade

*Filled by US3 — see `specs/008-drift-audit-workflow/quickstart.md` Path C until this section lands.*

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

*Filled by US3 — pointer to spec 005 §8 + contract C8 about consumers reading `drift-audit.json.verdict` directly.*

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
