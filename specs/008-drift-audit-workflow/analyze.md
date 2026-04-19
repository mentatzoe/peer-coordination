# Analysis: Drift-Audit Workflow

**Feature**: `008-drift-audit-workflow`
**Input**: `spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `contracts/workflow-contracts.md`, `quickstart.md`, `checklists/requirements.md`.
**Date**: 2026-04-20
**Scope**: non-destructive cross-artifact consistency analysis per `/speckit.analyze`. Read-only; no file modifications in this run.

## Summary

- **CRITICAL**: 0
- **HIGH**: 0
- **MEDIUM**: 2 (one inconsistency between FR-009 and contract C4; one coverage gap on FR-010 idempotency)
- **LOW**: 4 (two coverage gaps, one terminology drift, one minor inconsistency)

No blocking issues. Recommended to address the 2 MEDIUM findings pre-implement; the 4 LOW findings can be absorbed during WORKFLOW.md authoring in T005–T014.

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| I1 | Inconsistency | MEDIUM | `spec.md` FR-009 vs `contracts/workflow-contracts.md` C4 | FR-009 says the amend commit "includes the rubric version and auditor identity"; C4's format `session bundle amend: <session-id> — drift-audit[ <token>] @ <rubric-short-sha>` includes the rubric short SHA but NOT auditor identity. Auditor identity lives on `drift-audit.json.auditor` only. | Tighten FR-009 to drop "auditor identity" from the commit-message requirement — auditor identity is already captured on the artifact field per spec 005's schema. Alternative: require auditor identity in the commit *body* (not subject) and state that explicitly in both FR-009 and C4. |
| C1 | Coverage Gap | MEDIUM | `tasks.md` vs `spec.md` FR-010 | FR-010 idempotency (byte-identical modulo `audited_at`) is a workflow-level invariant but no task explicitly surfaces it. Idempotency is only implicit in whatever WORKFLOW.md content T005 authors. | Add a sentence to T005 (or split into an extra sub-task) directing the WORKFLOW.md to state the idempotency expectation + reference `research.md` R3 for canonical-form inheritance from spec 005. |
| C2 | Coverage Gap | LOW | `tasks.md` T010 vs `spec.md` FR-014 | T010 documents the LLM-judge-as-cross-reviewer assumption but does NOT explicitly spell out FR-014's entry criteria (≥2 calibrated manual two-auditor audits land before LLM-assisted authoring is available). | Expand T010's description to include the entry criteria, or split it into a sub-task that documents the criteria explicitly. |
| C3 | Coverage Gap | LOW | `tasks.md` vs `spec.md` FR-016 | FR-016 (H2 composition — consumers read `drift-audit.json.verdict` directly, MUST NOT re-derive findings) has no task reference. Naturally honored by following spec 005 §8, but runtime WORKFLOW.md readers might miss the consumer-direction guidance. | Add a short "Downstream consumption" pointer in WORKFLOW.md as part of T005 or as a new task, linking to spec 005 §8 and contract C8. |
| F1 | Terminology | LOW | `spec.md` (multiple locations) | Three terms used for the same role: "cross-reviewer", "cross-reviewing agent", "cross-auditor". All obviously the same, but drift exists across Users section, FRs, Edge Cases, and Entities. | Standardize on **"cross-reviewer"** when authoring WORKFLOW.md (T005+). Don't retro-edit the spec — the drift is non-blocking and retro-edits add churn. |
| F2 | Inconsistency | LOW | `spec.md` Key Entities vs `data-model.md` E2 | Spec says Reconciliation Outcome recorded "in the commit message or a bundle-adjacent note"; data-model narrowed to commit-message-only (cleaner). | Align on commit-message-only when writing WORKFLOW.md; drop the "or bundle-adjacent note" phrasing in a fast-follow patch if noticed during authoring. Not blocking for implement. |

## Coverage Summary (FRs → tasks)

| FR | Has Task? | Task IDs | Notes |
|---|---|---|---|
| FR-001 | ✓ | T005, T009, T012 | All three paths produce a conforming `drift-audit.json` |
| FR-002 | ✓ | T005, T006 | Rubric-pinning step + halt conditions |
| FR-003 | ✓ | T005 | Authoring step specifies required fields |
| FR-004 | ✓ | T005 (single), T009 (two) | Both modes covered |
| FR-005 | ✓ | T009, T010 | Operator-attested independence documented |
| FR-006 | ✓ | T009 | Tolerance check in Path B |
| FR-007 | ✓ | T009, T011 | Divergence branch + ledger reference |
| FR-008 | ✓ | T009, T011, T003 | Arbitration path + `[arbitrated]` token + taxonomy doc |
| FR-009 | ✓ | T005, T003 | **See I1** — format drift with C4 |
| FR-010 | ✗ | — | **See C1** — no explicit task |
| FR-011 | ✓ | T012 | Replacement (not append) in Path C |
| FR-012 | ✓ | T013 | Sweep cross-slice dependency documented |
| FR-013 | ✓ (implicit) | — | Constraint honored by omission — no task introduces LLM runtime |
| FR-014 | ◐ (partial) | T010 | **See C2** — entry criteria not explicit |
| FR-015 | ✓ (implicit) | — | Constraint honored by omission — no task redefines intervention-tag |
| FR-016 | ✗ | — | **See C3** — consumer-direction missing |
| FR-017 | ✓ (implicit) | T005 | Authoring step covers cross-refs |
| FR-018 | ✓ | T006 | Halt conditions section |

**Coverage**: 14/18 explicitly tasked, 3/18 honored by constraint-omission (FR-013, FR-015, FR-017), 1/18 partial (FR-014). **No FR is uncovered in effect**; the gaps (FR-010, FR-016) are workflow-level invariants that would be naturally reflected in WORKFLOW.md content but aren't singled out as tasks — the recommendations above fix that.

## Success Criteria Coverage

| SC | Validation Path | Status |
|---|---|---|
| SC-001 ≤15 operator-minutes per ≤200-turn bundle | Phase 3 session trial (operational, not test-suite) | Ready — depends on real sessions |
| SC-002 ≥90% within-tolerance agreement across counted sessions | Phase 3 data | Ready — depends on real sessions |
| SC-003 100% counted bundles carry audit within 24 operator-hours | Phase 3 data | Ready — depends on real sessions |
| SC-004 re-audit preserves historical reconstructibility 100% | Testable via `git show <prior-commit>:...` per T012 Path C | Ready — testable in WORKFLOW.md |
| SC-005 downstream consumer reads verdict without tooling | Testable by documentation per C8 | Ready — testable in WORKFLOW.md |
| SC-006 ≤30s lookup for rubric version | Testable by single-file read per C2 | Ready — testable in WORKFLOW.md |

All SCs are either operational (Phase 3 metric) or testable by the documented procedures. No blocking gap.

## Constitution Alignment

No violations. All 6 principles of v1.5.0 pass:

- **I. Constitution Is Canonical** ✓ (plan.md explicit check)
- **II. Transport Is Plumbing, Not Governance** ✓ (Layer 3 evaluation, no transport scope)
- **III. Scratchpad First, Then Promotion** ✓ (speckit-promoted slice)
- **IV. Human Arbitration and Explicit Consent** ✓ (FR-008 operator as arbiter)
- **V. Parallel Work Requires Explicit Ownership** ✓ (ACTIVE-SLICES row maintained)
- **VI. Coordination Is Human-Legible, Not Over-Protocolized** ✓ (grep-able `[arbitrated]` token, operator-initiated re-audit, no daemons)

## Cross-Slice Consistency

- **Spec 005** (data-model.md, contracts/drift-audit-output.md, RUBRIC.md): spec 008 defers schema + rubric ownership correctly. No redefinition. ✓
- **Spec 001 FR-014** (bundle-amend-commit convention `session bundle amend: <session-id> — <reason>`): spec 008's format `session bundle amend: <session-id> — drift-audit[ <token>] @ <rubric-short-sha>` fills the `<reason>` slot consistently. ✓
- **Spec 006** (transcript export): spec 008 C1 names `transcript.md` as a pre-condition. ✓
- **Intervention-tagging (Codex slice)**: spec 008 consumes `interventions.json` opaquely per FR-015. ✓

No cross-slice drift.

## Unmapped Tasks

None. Every task maps to at least one FR or a process requirement (T015/T018 map to `pull-requests.md` governance, which is expected for Polish tasks).

## Metrics

- **Total FRs**: 18
- **Total SCs**: 6
- **Total Tasks**: 18
- **FR Coverage**: 14 explicit, 3 implicit (constraint-omission), 1 partial (see C2)
- **Ambiguity Count**: 0 (no TODO / TKTK / placeholder; no vague adjective unmatched to measurable criteria)
- **Duplication Count**: 0
- **Critical Issues Count**: 0

## Next Actions

No CRITICAL or HIGH findings. Two MEDIUM findings worth a pre-implement fast-follow:

1. **I1**: tighten `spec.md` FR-009 to match `contracts/workflow-contracts.md` C4 (drop "auditor identity" from the commit-subject requirement; auditor identity lives on the artifact field).
2. **C1**: add a one-line note to `tasks.md` T005 (or a new sub-task) pointing the WORKFLOW.md author at `research.md` R3 for idempotency canonical-form inheritance from spec 005.

The 4 LOW findings (C2, C3, F1, F2) are best absorbed during T005–T014 authoring (standardize terminology, include entry criteria, include H2 composition pointer, drop redundant "or bundle-adjacent note" phrasing) rather than via pre-implement spec patches.

**Recommended sequence**:

1. Apply I1 + C1 patches to `spec.md` and `tasks.md` (narrow, quick).
2. Proceed to `/speckit-implement`, absorbing C2, C3, F1, F2 during WORKFLOW.md authoring.
3. Open PR per `docs/ways-of-working/pull-requests.md` once T015 (this analyze pass, now complete) + T016/T017 consistency checks land during Polish.

This report is the T015 output. T016/T017 still pending and will run during the Polish phase to confirm no drift introduced during implement.
