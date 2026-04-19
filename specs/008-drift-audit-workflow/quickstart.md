# Quickstart: Drift-Audit Workflow

**Branch**: `008-drift-audit-workflow` | **Date**: 2026-04-20
**Audience**: operator (Zoe), cross-reviewing agent (Dalgos / LLM-judge / future reviewer), or anyone preparing to run an audit on a closed session bundle.

This document walks through the three main paths: single-auditor, two-auditor, and re-audit. It assumes you have already read `observations/drift-audits/RUBRIC.md` §4 (manual-audit checklist). This workflow wraps the rubric procedure with the commit + reconciliation discipline.

---

## Prerequisites (common to all paths)

1. The target session bundle exists at `observations/sessions/<session-id>/` and is closed per spec 001 (has `meta.json.closed_at`, transcript, interventions log, pinned_rules_ref).
2. `observations/drift-audits/RUBRIC.md` is committed (no uncommitted working-tree changes).
3. You have write access to the repo (branch permissions per `docs/ways-of-working/pull-requests.md`).

If any of these fail, the workflow halts per C1. Fix upstream first.

---

## Path A — Single-auditor audit (exploratory / pre-calibration sessions)

Use this for early Phase 3 sessions before LLM-judge is calibrated, for non-counted sessions, or when the cross-reviewer is genuinely unavailable.

**Step 1 — Pin the rubric version**

```bash
cd <repo-root>
RUBRIC_SHA=$(git log -1 --format=%H -- observations/drift-audits/RUBRIC.md)
RUBRIC_SHORT=$(git rev-parse --short "$RUBRIC_SHA")
echo "Auditing against RUBRIC.md @ $RUBRIC_SHA (short: $RUBRIC_SHORT)"
```

**Step 2 — Run RUBRIC.md §4 against the bundle**

Follow `observations/drift-audits/RUBRIC.md` §4 Step 1–4 manually. Produce your findings list with `turn_ref`, `quote`, `category`, `severity`, `rationale` per finding.

**Step 3 — Author `drift-audit.json`**

Create `observations/sessions/<session-id>/drift-audit.json` conforming to spec 005's schema:

- `rubric_version`: full 40-char SHA (`$RUBRIC_SHA` from Step 1)
- `session_id`: from `meta.json.session_id`
- `pinned_rules_ref`: from `meta.json.pinned_rules_ref`
- `audited_at`: current RFC3339 UTC timestamp
- `audited_by`: `"manual"` (for now; `"hybrid"` or `"llm_assisted"` only once the LLM path is specced)
- `auditor`: your identity as a free-text string (e.g. `"Zoe"`, `"Dalgos"`, `"LLM-judge-v1"`)
- `findings`: the array from Step 2
- `load_bearing_findings_count`: count of `severity: "finding"` entries
- `verdict`: computed per spec 005 §3 (`no_drift` / `minor_drift` / `load_bearing_drift`)

**Step 4 — Commit as a session-bundle amend**

```bash
git add observations/sessions/<session-id>/drift-audit.json
git commit -m "session bundle amend: <session-id> — drift-audit @ $RUBRIC_SHORT"
```

No taxonomy token — single-auditor within-tolerance is the default case.

**Done.** The session now has a committed single-auditor audit. If this session is intended as counted Phase 3 evidence, flag it for an upgrade pass (Path B, starting from Step 2 of the upgrade subsection below).

---

## Path B — Two-auditor audit (counted sessions)

Use this for sessions intended as counted H1/H2 evidence. In the POC, this usually means one human (operator) and one LLM-judge (per spec 005 §7, active from Phase 3 session 3+).

**Step 1 — Pin the rubric version (shared)**

Same as Path A Step 1. Both auditors MUST use the same `$RUBRIC_SHA`.

**Step 2 — Primary auditor produces draft A**

The primary auditor (typically the operator or a dedicated cross-reviewing agent) runs RUBRIC.md §4 and produces a draft `drift-audit.json` — **do not commit yet**. Keep it as a working file (e.g. `observations/sessions/<session-id>/drift-audit.draft-primary.json`).

**Step 3 — Cross-reviewer produces draft B independently**

The cross-reviewer (human or LLM-judge) runs RUBRIC.md §4 against the same bundle and same `$RUBRIC_SHA`. Independence: the cross-reviewer MUST NOT read draft A before finalizing draft B. For LLM-judge, the prompt template in RUBRIC.md §7 provides isolation naturally. For human cross-reviewers, the operator attests to independence in the commit body (C5).

Store as `observations/sessions/<session-id>/drift-audit.draft-cross.json`.

**Step 4 — Reconciliation**

Compute `|A.load_bearing_findings_count − B.load_bearing_findings_count|`.

- **If ≤ 1 (within spec 005 FR-016 tolerance)**: go to Step 5a.
- **If > 1 (diverged)**: go to Step 5b.

**Step 5a — Within tolerance: merge and commit**

The primary auditor merges the two drafts into a single `drift-audit.json`:
- findings: union of A and B, deduplicated by `(category, turn_ref, severity)`
- `auditor`: `"<primary-id>, <cross-reviewer-id>"` (comma-separated)
- `audited_by`: `"manual"` if both human, `"hybrid"` if one is LLM

Commit:

```bash
git add observations/sessions/<session-id>/drift-audit.json
rm observations/sessions/<session-id>/drift-audit.draft-*.json  # clean drafts
git add -u
git commit -m "session bundle amend: <session-id> — drift-audit @ $RUBRIC_SHORT" \
           -m "Two-auditor: primary=<primary-id>, cross=<cross-reviewer-id>. Within tolerance."
```

**Step 5b — Diverged: operator arbitrates**

The operator reviews both drafts, decides which findings stand, and authors the final `drift-audit.json`:
- findings: operator-selected set
- `auditor`: `"<operator-id> (arbitrating <primary-id>/<cross-reviewer-id>)"`

Commit with the `[arbitrated]` token (critical — this is the arbitration ledger per C7):

```bash
git add observations/sessions/<session-id>/drift-audit.json
rm observations/sessions/<session-id>/drift-audit.draft-*.json
git add -u
git commit -m "session bundle amend: <session-id> — drift-audit [arbitrated] @ $RUBRIC_SHORT" \
           -m "Operator arbitration. Primary=<primary-id> found N findings; cross=<cross-reviewer-id> found M. Arbitrated: <brief rationale>."
```

**Done.** Verify the arbitration ledger includes this session:

```bash
git log --all --grep='\[arbitrated\]' --format='%H %s'
```

---

## Path C — Re-audit (rubric evolved or upgrade single→two)

Use this when:
- the rubric has a new version and a past session's audit should be refreshed, OR
- a session's single-auditor audit should be upgraded to two-auditor (counted-eligibility), OR
- POC-exit sweep flagged the bundle as stale.

**Step 1 — Identify the reason and the new state**

- If rubric evolution: pin the new `$RUBRIC_SHA` (may differ from the prior audit's version).
- If single→two upgrade: you're adding a cross-reviewer; rubric version typically stays the same unless it also evolved.

**Step 2 — Retrieve the prior audit's rubric_version for the commit message**

```bash
OLD_RUBRIC_SHORT=$(jq -r '.rubric_version' observations/sessions/<session-id>/drift-audit.json | cut -c1-7)
```

**Step 3 — Run the appropriate path (A or B) to produce a new `drift-audit.json`**

The new artifact fully replaces the prior one. Do NOT append to the prior audit.

**Step 4 — Commit with the correct taxonomy token**

Pick based on the reason:

- Rubric evolution: `re-run, supersedes <OLD_RUBRIC_SHORT>`
- Single→two upgrade (rubric unchanged): `two-auditor-upgrade`
- Both (upgrade + rubric evolution): `two-auditor-upgrade re-run, supersedes <OLD_RUBRIC_SHORT>`
- Arbitration on top of any of the above: prefix with `[arbitrated]`

Examples:

```bash
# Rubric evolution, two-auditor within tolerance:
git commit -m "session bundle amend: <session-id> — drift-audit re-run, supersedes $OLD_RUBRIC_SHORT @ $RUBRIC_SHORT"

# Single→two upgrade, no rubric change:
git commit -m "session bundle amend: <session-id> — drift-audit two-auditor-upgrade @ $RUBRIC_SHORT"

# Combined:
git commit -m "session bundle amend: <session-id> — drift-audit two-auditor-upgrade re-run, supersedes $OLD_RUBRIC_SHORT @ $RUBRIC_SHORT"

# Arbitrated upgrade + rubric evolution:
git commit -m "session bundle amend: <session-id> — drift-audit [arbitrated] two-auditor-upgrade re-run, supersedes $OLD_RUBRIC_SHORT @ $RUBRIC_SHORT"
```

**Step 5 — Verify the prior audit is preserved in git history**

```bash
git log --all --follow --format='%H %s' -- observations/sessions/<session-id>/drift-audit.json
git show <prior-commit>:observations/sessions/<session-id>/drift-audit.json
```

The prior audit is reconstructible; the current file is the authoritative consumer-relevant version.

---

## Halt conditions (quick reference)

Stop and fix upstream if any of these are true (per C1):

| Condition | Fix where |
|---|---|
| `meta.json` missing `pinned_rules_ref` | session-bundle close step (spec 001) |
| `meta.json.closed_at` unset | session-bundle close step (spec 001) |
| `transcript.md` missing | transcript export (spec 006) |
| `interventions.json` missing | intervention-tagging slice (Codex) |
| `observations/drift-audits/RUBRIC.md` has uncommitted changes | rubric authoring workflow (spec 005) |
| Working tree has other uncommitted changes unrelated to the audit | user shell state |

The workflow does NOT paper over any of these.

---

## Sanity checks after any committed audit

```bash
# 1. The committed file is valid JSON:
jq '.' observations/sessions/<session-id>/drift-audit.json

# 2. rubric_version resolves to an existing commit:
git show "$(jq -r '.rubric_version' observations/sessions/<session-id>/drift-audit.json)" --stat | head -5

# 3. load_bearing_findings_count matches the findings array:
jq '[.findings[] | select(.severity == "finding")] | length' observations/sessions/<session-id>/drift-audit.json

# 4. The amend commit is discoverable:
git log -1 --format='%H %s' -- observations/sessions/<session-id>/drift-audit.json
```

If any check fails, the audit has drifted from the contract; fix and re-commit before marking the audit complete.
