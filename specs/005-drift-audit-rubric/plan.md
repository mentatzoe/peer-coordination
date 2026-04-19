# Implementation Plan: Drift-Audit Rubric

**Branch**: `005-drift-audit-rubric` | **Date**: 2026-04-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-drift-audit-rubric/spec.md`

## Summary

Define the drift-audit rubric artifact, audit procedure, and calibration workflow that produces `drift-audit.json` per session bundle. Phase 2 Claude slice feeding H2 legibility evaluation per `design/poc.md`. Implementation is prose (rubric doc + procedure doc + output JSON schema) plus a seed rubric content file. No runtime code; no tooling. Calibration against real sessions happens in Phase 3, outside this slice.

## Technical Context

**Language/Version**: N/A — rubric is prose (markdown) + a JSON schema for the output shape. No runtime code in this slice.
**Primary Dependencies**: `design/poc.md` (H2 observables, measurement model), `specs/001-session-bundle-skeleton/spec.md` (`drift-audit.json` consumer contract), `specs/003-pinned-rules-authoring/spec.md` (rules artifact being audited against).
**Storage**: Git — the rubric lives at `observations/drift-audits/RUBRIC.md` with version history via git commits (analogous to `pinned-rules/current.md`). Per-session audit outputs land at `observations/sessions/<session-id>/drift-audit.json` per spec 001 FR-008.
**Testing**: Not required for this slice. Validation is by inspection + cross-auditor agreement (SC-002) applied when Phase 3 sessions begin. An optional mock-audit against a synthetic transcript is planned but belongs in `quickstart.md`, not test infrastructure.
**Target Platform**: Repo-local documentation + JSON artifact; no deployment surface.
**Project Type**: Documentation / specification slice within an existing repo.
**Performance Goals**: SC-005 target: ≤15 operator-minutes per session manual audit.
**Constraints**: Must remain post-session only (FR-011, observer-effect constraint). Must stay in scope — no live-session instrumentation (FR-018), no agent-facing drift feedback (FR-018).
**Scale/Scope**: Small-N POC — 3–5 baseline Phase 3 sessions + optional 1–2 Phase 4 Gemini sessions. Rubric is not designed for unbounded scale; Phase 2+ may need automation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.specify/memory/constitution.md` v1.5.0 principles:

- **I. Constitution Is Canonical**: ✓ no attempt to override or amend the constitution; rubric cites Principle VI + Principle IV by reference. 
- **II. Transport Is Plumbing, Not Governance**: ✓ rubric is pure Layer 3 evaluation content; no transport scope. Architecture reference in spec notes this is a Layer 3 artifact per architecture.md.
- **III. Scratchpad First, Then Promotion**: ✓ spec/plan/tasks/implementation follow the speckit promotion path; rubric content is promotable-by-operator only.
- **IV. Human Arbitration and Explicit Consent**: ✓ FR-015 operator-wins-on-disagreement honors this principle explicitly.
- **V. Parallel Work Requires Explicit Ownership**: ✓ slice assigned to Claude per #41 staffing; Codex cross-reviewer at implementation-complete.
- **VI. Coordination Is Human-Legible, Not Over-Protocolized**: ✓ rubric targets undeclared-convention detection — directly serves Principle VI's legibility intent.

No constitution gates violated. No Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```text
specs/005-drift-audit-rubric/
├── spec.md              # /speckit.specify output
├── plan.md              # this file (/speckit.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output — drift-audit.json schema + Finding / Auditor entities
├── quickstart.md        # Phase 1 output — operator manual-audit walkthrough
├── contracts/
│   └── drift-audit-output.md  # Phase 1 output — the output artifact contract
├── checklists/
│   └── requirements.md  # /speckit.specify quality checklist
└── tasks.md             # /speckit.tasks output (next stage)
```

### Source Code (repository root)

This slice produces content, not code. The artifacts created outside the `specs/` directory by `/speckit.implement`:

```text
observations/
└── drift-audits/
    ├── README.md         # directory purpose + authoring workflow + cross-refs
    ├── RUBRIC.md         # the substantive procedure — category definitions, severity rules, verdict logic, manual checklist, LLM-judge prompt template
    └── CHANGELOG.md      # convenience human-readable version log (git log is authoritative)
```

No `src/` or `tests/` — this slice is pure content scaffolding analogous to spec 003 (`pinned-rules/`).

**Structure Decision**: Content-scaffolding slice with no runtime code. Artifacts live at:
- `observations/drift-audits/` for the runtime-referenced rubric (analog to `pinned-rules/` from spec 003)
- `observations/sessions/<session-id>/drift-audit.json` per spec 001 FR-008 (per-session consumer path)

## Phase 0: Outline & Research

No NEEDS CLARIFICATION markers in the spec (all resolved in `/speckit.clarify`). Research surface is small: check that the proposed rubric categories + severity model + verdict rules are consistent with similar evaluation-rubric patterns and don't duplicate existing work.

See `research.md` for:
- Prior-art scan (similar drift / legibility audit rubrics in other multi-agent or human-legibility research)
- Category-enum sizing rationale (why 5+1 and not more)
- Verdict-determinism choice (why automatic and not auditor-assigned)
- Calibration strategy (how manual bootstraps LLM-assistance)

## Phase 1: Design & Contracts

See:
- `data-model.md` — `drift-audit.json` schema + `Finding` / `Auditor` entity definitions + validation rules
- `contracts/drift-audit-output.md` — artifact contract: what a valid `drift-audit.json` must satisfy for Phase 2 / Phase 3 consumers
- `quickstart.md` — operator manual-audit walkthrough, with the synthetic-transcript mock run

Agent context update: none. This slice doesn't change agent behavior; CLAUDE.md's speckit marker points at the current plan per the standard pattern.

## Phase 2: Task Planning Approach

*This section describes what the `/speckit.tasks` command will do. DO NOT execute during /speckit.plan.*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as the base.
- Derive tasks from the three user stories (US1 operator audit, US2 calibration, US3 H2 composition).
- Each functional requirement (FR-001 through FR-018) maps to at least one task.
- Content-scaffolding slice: tasks are file-authoring steps, not code implementation.

**Task Categorization**:
- Setup: create `observations/drift-audits/` directory.
- Foundational: author `observations/drift-audits/README.md` (workflow), `RUBRIC.md` (procedure), `CHANGELOG.md` (stub).
- US1 (operator audit): author the manual-audit checklist in `RUBRIC.md`; validate schema match between manual output and `data-model.md` schema.
- US2 (calibration): author the commit-discipline + rubric-versioning section in `README.md`; verify git-log-based versioning works.
- US3 (H2 composition): add cross-reference to `design/poc.md` H2 per-session clear-definition in `RUBRIC.md`; ensure rubric output plugs into H2 KPI judgment.
- Polish: verify all FRs mapped; no live-session instrumentation; no agent-facing drift feedback.

**Estimated Output**: ~10–15 tasks in `tasks.md`, grouped by user story.

**IMPORTANT**: This phase is executed by `/speckit.tasks`, not `/speckit.plan`.

## Complexity Tracking

No violations; this table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| — | — | — |
