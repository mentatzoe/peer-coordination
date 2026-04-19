# Analysis: Drift-Audit Rubric

**Feature**: `005-drift-audit-rubric`
**Input**: `spec.md`, `plan.md`, `tasks.md`, and the implementation under `observations/drift-audits/`.
**Date**: 2026-04-19
**Scope**: retrospective consistency check across artifacts per `/speckit.analyze`. Read-only; no file modifications.

## What the analyze stage checks

1. **Spec ↔ plan**: are all FRs planned?
2. **Plan ↔ tasks**: are all plan steps taskified?
3. **Tasks ↔ implementation**: are all completed tasks reflected in actual files on disk?
4. **Implementation ↔ spec**: does the scaffolding actually satisfy the FRs?
5. **Constitution**: does the slice honor the v1.5.0 principles?
6. **Cross-artifact consistency**: do spec 005, spec 001, spec 003, `design/poc.md`, and `design/architecture.md` compose cleanly?

Drift in any direction is a finding.

## FR coverage map (spec ↔ implementation)

| FR | Covered by | Status |
|---|---|---|
| FR-001 `drift-audit.json` is single JSON object | `data-model.md` JSON shape; worked example in `RUBRIC.md` §5 | ✓ |
| FR-002 top-level fields present | `data-model.md` "Drift-Audit Output" validation table | ✓ |
| FR-003 `Finding` required fields | `data-model.md` "Finding" validation table; RUBRIC.md §5 example | ✓ |
| FR-004 category enum | `RUBRIC.md` §1 (definitions for all 6 categories) | ✓ |
| FR-005 severity enum | `RUBRIC.md` §2 (severity table + disambiguation) | ✓ |
| FR-006 `turn_ref` = ISO-8601 timestamp | `data-model.md`; `RUBRIC.md` §4 Step 2; `quickstart.md` | ✓ |
| FR-007 verdict deterministic | `RUBRIC.md` §3 (verdict logic table); `data-model.md` validation rule; explicitly called out in worked example | ✓ |
| FR-008 manual audit applicable | `RUBRIC.md` §4 (4-step checklist); `quickstart.md` section "Manual audit walkthrough" | ✓ |
| FR-009 LLM-assisted audit applicable | `RUBRIC.md` §7 (prompt template); `quickstart.md` section "LLM-assisted audit" | ✓ |
| FR-010 private_shorthand uninvolved-reviewer test | `RUBRIC.md` §1.3; cross-referenced in severity disambiguation §2 | ✓ |
| FR-011 post-session only | `RUBRIC.md` intro paragraph ("Canonical post-session procedure"); §4 Step 1 ("Walk this end-to-end per session bundle"); grep check for "during session / live / real-time" returns no matches | ✓ |
| FR-012 blocked-path for incomplete bundle | `data-model.md` "blocked path" JSON shape | ✓ |
| FR-013 rubric at `observations/drift-audits/RUBRIC.md` | Implementation lands the file at exactly that path; `README.md` documents the location | ✓ |
| FR-014 discrete commits | `RUBRIC.md` §6.1; `README.md` "Versioning discipline" section | ✓ |
| FR-015 operator-wins on disagreement | `RUBRIC.md` §7 (LLM-judge workflow — "operator then ratifies"); spec clarifications-applied block captures the rationale | ✓ |
| FR-016 cross-auditor tolerance | `RUBRIC.md` §6.3 (calibration triggers); `quickstart.md` "Cross-auditor agreement check" | ✓ |
| FR-017 no out-of-scope (no intervention-tagging, no KPI rollup, etc.) | `plan.md` project structure lists artifacts; no out-of-scope artifact produced. Grep confirms `RUBRIC.md` doesn't author intervention or KPI logic | ✓ |
| FR-018 no live-session instrumentation, no agent-facing drift feedback | Grep check for "during session / live / real-time / agent-facing" returns no matches in RUBRIC.md | ✓ |

**No drift detected. 18/18 FRs covered.**

## Success Criteria coverage (spec ↔ implementation readiness)

| SC | Validation readiness | Status |
|---|---|---|
| SC-001 every Phase 3 session has valid drift-audit.json | Scaffolding supports this; actual validation happens during Phase 3 | ✓ (ready) |
| SC-002 two auditors agree within FR-016 tolerance ≥80% of cases | Requires Phase 3 data; scaffolding supports the agreement check | ✓ (ready) |
| SC-003 H2 judgment from drift-audit alone ≥80% of sessions | Requires Phase 3 data; `RUBRIC.md` §8 supports this workflow | ✓ (ready) |
| SC-004 rubric calibration via discrete commits | Workflow is documented; git enforces the mechanism | ✓ |
| SC-005 manual audit ≤15 min per session | Target, not hard limit; Phase 3 data will validate | ✓ (ready) |

## Spec → plan

- All 18 FRs referenced in `plan.md`'s FR-to-artifact mapping either explicitly or via the plan's Phase 0/1 artifact list.
- `plan.md` Constitution Check gate passed; no violations.
- **No drift.**

## Plan → tasks

- `plan.md`'s 6-phase structure (Setup / Foundational / 3 user stories / Polish) mirrors `tasks.md`.
- Each `plan.md` phase step maps to at least one task in `tasks.md`.
- **No drift.**

## Tasks → implementation

Cross-check against repo state on branch `005-drift-audit-rubric`:

| Task | Expected artifact | Present on disk |
|---|---|---|
| T001 | `observations/drift-audits/` directory | ✓ |
| T002 | `observations/drift-audits/README.md` | ✓ |
| T003 | `observations/drift-audits/CHANGELOG.md` | ✓ |
| T004 | `RUBRIC.md` with §1 category definitions, §2 severity, §3 verdict, §4 checklist | ✓ |
| T005 | `RUBRIC.md` §5 worked example | ✓ |
| T006 | Schema match between §5 example and `data-model.md` | ✓ verified in analysis |
| T007 | `RUBRIC.md` §6 versioning + calibration | ✓ |
| T008 | `README.md` mirrors versioning discipline | ✓ |
| T009 | `RUBRIC.md` §8 H2 composition | ✓ |
| T010 | US3 acceptance scenarios satisfied | ✓ verified below |
| T011 | FR coverage map | ✓ this analyze.md contains it |
| T012 | Mock synthetic-transcript walkthrough | ✗ **not yet run** — deferred to Phase 2 gate validation closer to Phase 3 start |
| T013 | Grep check for live-session language | ✓ no matches |
| T014 | Grep check for agent-facing drift language | ✓ no matches |
| T015 | ROADMAP.md workstream row updated | ✓ |

**One intentional task deferral**: T012 (mock audit against a synthetic transcript) is deferred to the Phase 2 gate validation window, when Codex's transport-side slice is also ready. Running the mock now before Phase 3 session 1 is possible but may be redone if rubric calibrates. Deferral documented here and in the tasks.md Implementation Strategy.

## Implementation → spec

- All 6 drift categories defined with examples and audit questions. Each category is distinguishable at audit time.
- Severity disambiguation is grounded in FR-010 uninvolved-reviewer test; consistent across §1 and §2.
- Verdict table in §3 matches FR-007 rule exactly.
- Worked example in §5 conforms to `data-model.md` schema, verdict is correctly derived, `load_bearing_findings_count` matches findings-array content.
- LLM-judge prompt template outputs JSON that composes with the data-model schema.
- **No drift.**

## Cross-artifact consistency

### spec 005 ↔ spec 001 (session-bundle-skeleton)

- `drift-audit.json` path is `observations/sessions/<session-id>/drift-audit.json` — matches spec 001 FR-008.
- `Finding.turn_ref` is ISO-8601 timestamp per spec 001 FR-009 canonical turn key — matches.
- `rubric_version` commit-hash preferred, inline fallback — matches the pinned-rules-ref pattern from spec 001 FR-010.
- **No drift.**

### spec 005 ↔ spec 003 (pinned-rules-authoring)

- The rubric audits against the pinned rules at `pinned_rules_ref`. Spec 003's commit-hash-preferred contract is honored.
- Rubric versioning workflow is analogous to spec 003's pinned-rules workflow (discrete commits, commit-hash reference, operator-only authoring).
- `design/poc.md` session-break-on-pinned-rules-change is orthogonal to rubric changes; rubric changes happen between sessions per RUBRIC.md §6.4 (analogous rule).
- **No drift.**

### spec 005 ↔ `design/poc.md`

- H2 legibility observables list (new emoji, abbreviations, shorthand, hidden channels) maps 1-to-1 onto the rubric's 6 categories.
- Measurement-model row (manual → LLM-assisted post-calibration) is implemented exactly in RUBRIC.md §4 + §7.
- Per-session clear-definition for H2 consumes `drift-audit.json.verdict` directly per RUBRIC.md §8.
- **No drift.**

### spec 005 ↔ `design/architecture.md`

- Layer 3 capability: "A minimal failure taxonomy that distinguishes at least convergence failure, legibility failure, complementarity failure, and intervention dependence." The drift-audit rubric addresses the **legibility failure** slice of that taxonomy specifically.
- Layer 3 capability: "Episode records that support repeatable review." Achieved via rubric-version commit reproducibility.
- **No drift.**

### spec 005 ↔ Constitution v1.5.0

- **Principle I (Constitution canonical)**: ✓ rubric cites Principle VI + IV; no attempt to override or amend constitution.
- **Principle II (Transport is plumbing)**: ✓ rubric is pure Layer 3 content; no transport scope.
- **Principle III (Scratchpad first, then promotion)**: ✓ speckit promotion path followed (specify → clarify → plan → tasks → implement → analyze); rubric content is operator-only-promotable.
- **Principle IV (Human arbitration and explicit consent)**: ✓ FR-015 operator-wins-on-disagreement honors this; RUBRIC.md §7 explicitly states operator ratifies.
- **Principle V (Parallel work requires explicit ownership)**: ✓ slice assigned to Claude per #41; Codex cross-reviewer.
- **Principle VI (Human-legible, not over-protocolized)**: ✓ rubric's entire purpose serves this principle's legibility intent.
- **No drift.**

## Follow-up items surfaced by this analysis

- **T012 mock synthetic-transcript run** is intentionally deferred to Phase 2 gate validation. Logged here and in tasks.md. Not a finding; a planned deferral.
- **ROADMAP.md row cross-check**: while updating "Draft drift-audit rubric" to "Landed," I noticed "Session bundle skeleton" is still marked Open despite landing via `cc62e16`. Not this slice's responsibility to fix, but worth flagging for the next ROADMAP maintenance commit.

## Verdict

**No drift detected across the slice.** 18/18 FRs covered, all cross-artifact consistencies hold, constitution gates honored. Slice is ready for operator ratification + merge via PR.

One intentional task deferral (T012) documented.

## Coverage summary

| Area | Status |
|---|---|
| FR coverage | 18/18 ✓ |
| Success criteria | 5/5 ready ✓ |
| Spec ↔ plan | No drift ✓ |
| Plan ↔ tasks | No drift ✓ |
| Tasks ↔ implementation | T012 deferred intentionally; 14/15 complete ✓ |
| Implementation ↔ spec | No drift ✓ |
| Constitution gates | All 6 principles honored ✓ |
| Cross-artifact consistency (spec 001/003, design/poc, architecture) | No drift ✓ |

**Verdict: slice is ready for cross-review + operator merge decision.**
