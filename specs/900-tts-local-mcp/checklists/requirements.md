# Specification Quality Checklist: Local TTS + Affect-Aware STT MCP for Operator ↔ Agent Voice

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-04-20
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) beyond what tonight's validation evidence locks in as load-bearing (VoxCPM2-4bit, mlx-audio PR #641, SenseVoiceSmall, emotion2vec_plus_large, fsmn-vad) — engine choices are named because they're validation-grounded, not speculative; per-stage algorithms, data schemas, and code structure are deferred to `/speckit.plan`
- [x] Focused on user value and business needs (operator ↔ agent affect-channel symmetry; voice-mode UX; graceful degradation)
- [x] Written for the operator + implementing agent (Claude); not a business-stakeholder doc but scope is operator-personal infrastructure, so this is appropriate
- [x] All mandatory sections completed: User Scenarios & Testing, Requirements (Functional + Key Entities), Success Criteria, Assumptions, Dependencies, plus the peer-coord-flavor Context block up top

## Requirement Completeness

- [x] No `[NEEDS CLARIFICATION]` markers remain — all informed guesses were made from the scratchpad + tonight's validation + repo conventions, and documented in Assumptions
- [x] Requirements are testable and unambiguous — each FR has either a concrete guardrail number (FR-006 3 s, FR-008 8 MB), a concrete behavior (FR-011 closed taxonomy, FR-016 fixed "(voice unavailable)" marker), or a concrete input/output contract (FR-005 per-chunk record shape)
- [x] Success criteria are measurable — SC-001 through SC-008 carry percentages, counts, wall-clock budgets, or reproducible binary outcomes
- [x] Success criteria are mostly technology-agnostic at the outcome level; SC-004 and SC-005 reference validation-clip artifacts which is acceptable because they anchor the measurement to tonight's ground truth rather than leaking implementation
- [x] All acceptance scenarios are defined — every User Story has 2–3 Given/When/Then scenarios
- [x] Edge cases are identified — empty input, extremely long input, silent audio, multi-speaker, mid-composition toggle, concurrent calls, partial-match deny-list
- [x] Scope is clearly bounded — In scope / Out of scope / Non-goals explicitly enumerated in Context, and non-goals are re-affirmed in Dependencies (cc-connect adapter, agent-to-agent voice, cloud-TTS fallback)
- [x] Dependencies and assumptions identified — Dependencies section names upstream model artifacts with exact install paths, downstream follow-on slices, and constitutional posture; Assumptions section captures the 9 defaults (harness = Claude Code Discord plugin, Station sole v1 consumer, M4 reference substrate, etc.)

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria — each FR maps to at least one Acceptance Scenario or SC entry
- [x] User scenarios cover primary flows — US1 outbound synth, US2 voice-mode toggle, US3 inbound affect pipeline, US4 graceful degradation, US5 reproducibility
- [x] Feature meets measurable outcomes defined in Success Criteria — SC-001..SC-008 are each traceable to one or more FRs
- [x] No implementation details leak into the spec beyond the validated engine-choice facts (which are load-bearing context, not implementation leakage — the actual wiring, file layout, and MCP plumbing are deferred to `/speckit.plan`)

## Notes

- All checklist items pass on first iteration. No spec updates required before `/speckit.clarify` or `/speckit.plan`.
- Engine-choice specificity (VoxCPM2-4bit, SenseVoiceSmall, etc.) is intentionally in the spec rather than deferred to plan, because tonight's validation is the evidence that grounds those choices; deferring them would lose the motivation for why this feature is scoped as-is.
- The 9xx reserved-block posture and graduation-path hygiene are captured in Context + Dependencies; the constitution is not amended by this slice.
