# Analysis: Session-Summary Workflow

**Feature**: `009-session-summary-workflow`
**Input**: `spec.md` (with /speckit.clarify Q/As encoded), `plan.md`, `research.md`, `data-model.md`, `contracts/workflow-contracts.md`, `quickstart.md`, `tasks.md`, `checklists/requirements.md`.
**Date**: 2026-04-21
**Scope**: non-destructive cross-artifact consistency analysis per `/speckit.analyze`. Read-only; no file modifications in this run.

## Summary

- **CRITICAL**: 0
- **HIGH**: 0
- **MEDIUM**: 2 (FR-015 no task, FR-017 downstream-consumption no task)
- **LOW**: 4 (T010 CHANGELOG ambiguity, sanity-check conditional wording, FR-006 "or sub-section" stale, FR-007 poc.md pointer not tasked)

No blocking issues. Recommend 1 narrow spec patch (F3) + 2 new/expanded tasks (C1, C2) pre-implement; the remaining 3 LOW items are absorbable during T006/T009 authoring.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Coverage Gap | MEDIUM | `spec.md` FR-015 vs `tasks.md` | FR-015 mandates the workflow MUST document entry criteria for deferred LLM-assisted authoring (mirrors spec 008 FR-014), but no task authors this into `SUMMARY-WORKFLOW.md`. Spec 008's T010 had a dedicated sub-task for the analogous pattern; spec 009 doesn't. | Add a sub-task to US1 or Polish: "Document LLM-assisted authoring entry criteria in SUMMARY-WORKFLOW.md per FR-015" — one paragraph mirroring spec 008's LLM-judge cross-reviewer block. |
| C2 | Coverage Gap | MEDIUM | `spec.md` FR-017 + `contracts/workflow-contracts.md` C8 vs `tasks.md` | FR-017 + C8 say KPI rollup reads verdict lines directly and MUST NOT re-derive; spec 008 addressed this by authoring a "Downstream consumption" section in its WORKFLOW.md. Spec 009's plan/research/contracts/quickstart all cover it, but no task explicitly authors it into the runtime `SUMMARY-WORKFLOW.md`. | Add a sub-task to US1 or Polish: "Add Downstream consumption section to SUMMARY-WORKFLOW.md pointing at FR-017 + C8 so runtime readers see the consumer-direction contract." |
| F2 | Inconsistency | LOW | `quickstart.md` line 290 sanity-check block vs Paths C/D | Post-commit sanity check 5 greps `^Mode:` from `git log -1 --format=%b`. Revisions (Path C) and peer-audits (Path D) typically do NOT carry a new `Mode:` line — mode is inherited from the initial commit. The text says "Expected for initial commits: one match" but the script is unconditional; applying it after Path C/D commits would false-positive. | Clarify in T009 + quickstart that check 5 applies only to initial commits (no `[peer-audited]` or `revision:` token in subject) and skip for follow-up commits. Trivial runbook wording change. |
| F3 | Inconsistency | LOW | `spec.md` FR-006 vs FR-010 | FR-006 says verdicts appear as "an explicit labeled line **or sub-section**" (allows flexibility); FR-010 pins to the grep-stable list-bullet line format only. The "or sub-section" language in FR-006 is stale w.r.t. the clarify Q2 decision. | Drop "or sub-section" from FR-006 so it aligns with FR-010's list-bullet discipline. Narrow pre-implement wording fix. |
| C3 | Coverage Gap | LOW | `spec.md` FR-007 vs `tasks.md` | FR-007 mandates referencing `design/poc.md`'s per-session clear-definition criteria for the three verdict judgments. No task explicitly adds that pointer to `SUMMARY-WORKFLOW.md` — the quickstart has a "Verdict rubric" block that explains the enum but doesn't cite poc.md's judgment thresholds. | During T006 authoring, include a pointer to `design/poc.md` "Per-session clear definitions" in the Verdict rubric block of SUMMARY-WORKFLOW.md. Absorbable inline, no separate task needed. |
| F1 | Inconsistency | LOW | `tasks.md` T010 | T010 offers the author two choices: "dated section in README.md **or** create `observations/sessions/CHANGELOG.md` if parallel structure with `observations/drift-audits/CHANGELOG.md` is preferred." Uncommitted choice may produce inconsistent structure across Phase 2 runtime directories. | Pick one at task level. Recommend creating `observations/sessions/CHANGELOG.md` to match the `observations/drift-audits/CHANGELOG.md` pattern already established by spec 005 — consistency across runtime directories. |

## Coverage Summary (FRs → tasks)

| FR | Has Task? | Task IDs | Notes |
|---|---|---|---|
| FR-001 | ✓ | T006 | Path A establishes core input→output |
| FR-002 | ✓ | T008 | Halt conditions |
| FR-003 | ✓ | T004, T006 | Template + Path A authoring |
| FR-004 | ✓ | T006, T007 | Both modes as first-class paths |
| FR-005 | ✓ | T007 | Explicit operator verdict authority |
| FR-006 | ✓ | T006 | Verdict line format in Path A — **see F3** |
| FR-007 | ◐ (partial) | T006 | Verdict rubric block — **see C3** |
| FR-008 | ✓ | T011 | Dedicated drift-citation task |
| FR-009 | ✓ | T002, T003, T006 | Scaffolding + Path A example |
| FR-010 | ✓ | T004, T006 | Template + hybrid structure authoring |
| FR-011 | ✓ | T013 | Path C revision |
| FR-012 | ✓ | T013 | Drift-refresh case examples |
| FR-013 | ✓ | T008 | Halt conditions include trigger pre-conditions |
| FR-014 | ✓ (implicit) | — | No task introduces LLM — constraint honored by omission |
| FR-015 | ✗ | — | **See C1** — no explicit task |
| FR-016 | ✓ (implicit) | — | No task introduces intervention-tag assumptions |
| FR-017 | ◐ (partial) | T006 | Verdict-line format tasked; downstream-consumption pointer isn't — **see C2** |
| FR-018 | ✓ | T014, T015 | Path D + combined-token examples |

**Coverage**: 14/18 explicitly tasked, 2/18 honored by constraint-omission (FR-014, FR-016), 2/18 partial (FR-007, FR-017), 1/18 missing (FR-015).

## Success Criteria Coverage

| SC | Validation Path | Status |
|---|---|---|
| SC-001 ≤20 operator-minutes per ≤200-turn bundle | Phase 3 session trial | Ready (depends on real sessions) |
| SC-002 100% counted bundles carry non-placeholder summary within 48 operator-hours | Phase 3 data | Ready (depends on real sessions) |
| SC-003 ≥80% fresh-reader reconstruction success | Phase 3 data (doubles as H2 KPI threshold) | Ready (depends on real sessions) |
| SC-004 100% drift-citation discipline | Testable by inspection per C2 | Ready — testable in SUMMARY-WORKFLOW.md |
| SC-005 100% revision preserves history (no `--amend`) | Testable via `git log` + `--amend` prohibition at spec/plan/contract/quickstart/task levels | Ready — verified in cross-slice checks below |
| SC-006 100% mechanical verdict extraction | Testable by the grep recipe in quickstart sanity check 2 | Ready |

All SCs either operational (Phase 3) or testable by documented procedures.

## Constitution Alignment

No violations. All 6 v1.5.0 principles pass (verified in plan.md Constitution Check pre- and post-design).

## Cross-Slice Consistency Checks (requested)

- **`--amend` prohibition (PR #66 lesson)** ✓ consistent: encoded in spec FR-011 + SC-005 + US3 acceptance, plan Constraints, research R5, contracts C4 + C6, quickstart 4 places, tasks T009 + T013 + T017, data-model E4. Propagated everywhere an operator could encounter the temptation.
- **Commit format** ✓ consistent: `session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>` appears identically in spec FR-009, research R1, contracts C4, data-model E6, quickstart (all 4 paths), tasks T003.
- **`Mode:` / `drafted-by:` / `ratified-by:` identity contract** ✓ consistent: spec FR-004, data-model E1, contracts C5, research R1 + R4, quickstart Step 4, tasks T007 — all use identical `Mode: single-author` and `Mode: agent-drafted, drafted-by: <id>, ratified-by: <id>` strings.
- **Verdict-line format** ✓ consistent: `- **<KPI>**: \`<value>\` — <rationale>` appears identically in spec FR-010, research R2, data-model E2, contracts C2, quickstart Step 2.
- **Spec 001 FR-014 compliance** ✓ verified: no instruction anywhere in the artifact set suggests `git commit --amend` on session-bundle history.
- **Spec 005 data-model consistency** ✓ verified: all `drift-audit.json` field references (`verdict`, `findings`, `turn_ref`, `category`, `severity`) match spec 005's schema; no new fields introduced.
- **Spec 008 commit-taxonomy pattern** ✓ verified: bracket-token + `@ <short-sha>` convention reused identically; taxonomy tokens are summary-specific but follow the same grammar.
- **Spec 006 transcript input** ✓ verified: consumed via `transcript.md` with turn-timestamp citations.
- **Intervention-tag opacity (FR-016)** ✓ verified: no task or entity introduces a specific intervention-tag schema assumption.

## Unmapped Tasks

None. T016–T019 (Polish phase) map to `pull-requests.md` governance rather than individual FRs, which is expected convention for the final phase.

## Metrics

- **Total FRs**: 18
- **Total SCs**: 6
- **Total Tasks**: 19
- **FR Coverage**: 14 explicit, 2 implicit (constraint-omission), 2 partial (T006-absorbable), 1 gap (needs new task) — **effective coverage 17/18 after C1 fix; 18/18 with T006 inline expansion for C2/C3**
- **Ambiguity Count**: 0 (no TODO/TKTK/placeholder; no unquantified vague adjective)
- **Duplication Count**: 0
- **Critical Issues Count**: 0

## Next Actions

No CRITICAL or HIGH findings. Two MEDIUM findings (C1, C2) + one LOW spec patch (F3) are worth a pre-implement patch pass:

1. **Pre-implement patches**:
   - **C1 fix**: add a new task (e.g. T010b or fold into T010) authoring the FR-015 LLM-assisted authoring entry criteria into SUMMARY-WORKFLOW.md.
   - **C2 fix**: add a new task (or expand T006) authoring a Downstream consumption section in SUMMARY-WORKFLOW.md pointing at FR-017 + C8.
   - **F3 fix**: drop "or sub-section" from spec.md FR-006 for alignment with FR-010.
2. **Absorbable during T006/T009 authoring** (no pre-implement patch needed):
   - C3: cite `design/poc.md` per-session clear-definition criteria in the Verdict rubric block.
   - F2: add "initial commits only" qualifier to the sanity-check Mode: line grep.
   - F1: pick one path for T010 — recommended: `observations/sessions/CHANGELOG.md` to match `observations/drift-audits/CHANGELOG.md`.
3. **After patches land**: ready for Codex cross-agent review + implement handoff.

This report is the T016 output. T017 / T018 (cross-slice consistency checks) will run during the Polish phase to re-verify after implement.

---

## Polish addendum — T017 / T018 results (2026-04-22)

### T017 — Amend-commit format vs spec 001 FR-014 + `--amend` scan

- **Spec 001 FR-014 format**: `session bundle amend: <session-id> — <reason>`
- **Spec 009 C4 format**: `session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>`

**Verdict**: ✓ consistent. Spec 009 fills spec 001's `<reason>` slot with a structured sub-grammar (`summary[ <taxonomy-token>] @ <drift-audit-short-sha>`). No redefinition of FR-014's base convention.

- **`git commit --amend` scan in SUMMARY-WORKFLOW.md**: 3 mentions, all negations ("NEVER", "do NOT") with proper cross-references to spec 001 FR-014 + contract C6. No instruction anywhere suggests using `--amend` on session-bundle history. The PR #66 I1 lesson is encoded in the runtime doc as well as the spec chain.

### T018 — `drift-audit.json` field usage vs spec 005 data-model + spec 008 commit-taxonomy

Fields / enums this slice references in `observations/sessions/SUMMARY-WORKFLOW.md`: `verdict` enum (`no_drift` / `minor_drift` / `load_bearing_drift`), `findings[]`, `severity` enum (`finding` / `warn` / `info` implied), `turn_ref`, `category`.

All values match [spec 005 data-model](../005-drift-audit-rubric/data-model.md) exactly:
- `Drift-Audit Output.verdict` enum: `no_drift`, `minor_drift`, `load_bearing_drift` ✓
- `Finding.severity` enum: `info`, `warn`, `finding` ✓
- `Finding.category` enum: not enumerated in summary-workflow (generic cross-reference only) — correct, spec 005 owns the category enum.

**Commit-taxonomy pattern vs spec 008**: bracket-token + `@ <short-sha>` grammar reused identically. Token ordering convention (bracket first, `revision:` or `re-run, supersedes` second) mirrors spec 008's `[arbitrated]` → `two-auditor-upgrade` → `re-run, supersedes` ordering.

**Verdict**: ✓ consistent. No schema extension, no enum drift, no taxonomy-pattern deviation.

### Implement-phase absorbed findings (from the Next Actions of the initial analyze)

All 4 LOW findings flagged for inline absorption during T006/T009 authoring were addressed:

- **C3 (FR-007 poc.md criteria pointer)** — addressed inline in Path A Step 2's "Verdict rubric" subsection, which cites `design/poc.md` "Per-session clear definitions" and summarizes the three AND-gate conditions.
- **F2 (sanity-check Mode: line conditional)** — addressed inline in check 5 of Post-commit sanity checks, which uses a subject-grep guard (`revision:|\[peer-audited`) to skip the Mode-line check on follow-up commits.

No new findings surfaced during implement.

### Codex review findings (PR #68) — applied 2026-04-22

- **Finding 1** (FR-003 ↔ FR-010 inconsistency on "five sections" vs four headings): resolved in spec.md FR-003 + data-model E-series. FR-003 now says "five required content elements" with explicit mapping to four top-level headings. Normative chain consistent.
- **Finding 2** (C1 interventions.json storage shape widened beyond spec 001 FR-011): resolved in contracts/workflow-contracts.md C1 + spec.md FR-016. Array-of-objects storage is honored per spec 001; opacity scope tightened to per-object tag schema only.

No additional findings surfaced.

### Final status

Ready for Codex re-review on PR #68. All 21 tasks complete (T019 maps to a PR re-review comment on the existing open PR, not a new PR).

