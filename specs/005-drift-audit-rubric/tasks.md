# Tasks: Drift-Audit Rubric

**Input**: Design documents from `/specs/005-drift-audit-rubric/`
**Prerequisites**: [`spec.md`](spec.md), [`plan.md`](plan.md), [`research.md`](research.md), [`data-model.md`](data-model.md), [`contracts/drift-audit-output.md`](contracts/drift-audit-output.md), [`quickstart.md`](quickstart.md)
**Tests**: Not required for this slice — content scaffolding only; no runtime code. Validation is by inspection + cross-auditor agreement (SC-002) applied when Phase 3 sessions begin.
**Organization**: Tasks grouped by user story to enable independent implementation and review per story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependencies)
- **[Story]**: user story (US1 / US2 / US3)
- File paths are relative to repo root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: establish the evaluation-surface directory for the rubric.

- [ ] **T001** Create directory `observations/drift-audits/` at repo root per spec FR-013 (implicit via first file committed).

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: baseline workflow + changelog infrastructure; blocks all user stories.

- [ ] **T002** Author `observations/drift-audits/README.md` with:
  - directory purpose (Layer 3 evaluation surface scope)
  - authoring workflow (who commits to RUBRIC.md, commit message convention `drift-audit-rubric: <summary>` per FR-013/014)
  - commit-hash reference contract (per-session `drift-audit.json.rubric_version` resolves to a RUBRIC.md commit)
  - cross-references to spec 005, `design/poc.md` measurement model, constitution Principle VI
- [ ] **T003** [P] Author `observations/drift-audits/CHANGELOG.md` stub with a "2026-04-19 — v1 seed" entry.

**Checkpoint**: workflow + versioning infrastructure in place; user story work can proceed.

## Phase 3: User Story 1 — Operator manual audit produces valid `drift-audit.json` (Priority: P1) 🎯 MVP

**Goal**: an operator can walk `RUBRIC.md` on a session bundle and produce a `drift-audit.json` that conforms to the `data-model.md` schema and the `contracts/drift-audit-output.md` contract.

**Independent Test**: given a Phase 3 (or synthetic) session bundle, operator applies `RUBRIC.md` step by step and produces a valid `drift-audit.json`; a cross-reviewer validates schema conformance and guarantees 1–5 from the contract.

### Implementation for User Story 1

- [ ] **T004** [US1] Author the bulk of `observations/drift-audits/RUBRIC.md` covering:
  - category definitions: one section per category (`undeclared_emoji`, `undeclared_abbreviation`, `private_shorthand`, `hidden_channel_reference`, `off_palette_load_bearing`, `other`) with concrete examples and the FR-010 uninvolved-reviewer test for `private_shorthand`
  - severity definitions (`info`, `warn`, `finding`) with disambiguation guidance
  - verdict logic (restating FR-007 — deterministic from findings)
  - manual-audit checklist — the 4-step walkthrough from `quickstart.md` with the turn-by-turn scan pattern
- [ ] **T005** [US1] Add a "How to author `drift-audit.json`" section to `RUBRIC.md` with a worked example: given a 3-finding session, show the exact JSON shape produced. Must match `data-model.md` schema.
- [ ] **T006** [US1] Verify schema match: inline JSON example in `RUBRIC.md` must match the `Drift-Audit Output` and `Finding` validation rules from `data-model.md`. Cross-check both `load_bearing_findings_count` consistency (FR-007 + data-model Guarantee 5) and `turn_ref` format (ISO-8601 per FR-006).

**Checkpoint**: operator can run manual audits end-to-end against the rubric. FR-001 through FR-008 covered at the implementation level; FR-011 (post-session only) and FR-012 (blocked-path) covered by rubric procedure.

## Phase 4: User Story 2 — Rubric supports calibration between sessions (Priority: P1)

**Goal**: rubric updates land as discrete git commits; past audits remain reproducible against their own `rubric_version`.

**Independent Test**: make a dummy rubric change (e.g., tighten a category definition), commit with `drift-audit-rubric: <summary>` message, verify `git show <prior-commit>:observations/drift-audits/RUBRIC.md` still reads the pre-change content.

### Implementation for User Story 2

- [ ] **T007** [US2] Add a "Versioning and calibration" section to `RUBRIC.md` documenting:
  - discrete-commit rule per FR-014 (one logical change per commit, `drift-audit-rubric: <summary>` message)
  - rubric-version reachability rule (`rubric_version` in each `drift-audit.json` must resolve to a main-branch commit)
  - calibration trigger rules (when agreement tolerance FR-016 is exceeded, that's a calibration signal)
  - the "rubric changes between sessions, not during a session" rule (analog to spec 003's session-break-on-rules-change)
- [ ] **T008** [US2] Mirror the same versioning discipline in `observations/drift-audits/README.md` (from T002) so workflow is legible without reading the full `RUBRIC.md`.

**Checkpoint**: FR-013 and FR-014 covered; calibration workflow documented; reviewers can reproduce past audits against their own rubric version.

## Phase 5: User Story 3 — Rubric composes with H2 per-session clear definition (Priority: P2)

**Goal**: H2 judges can use `drift-audit.json.verdict` + `load_bearing_findings_count` + selected `findings[]` as direct input to the H2 fresh-reader-pass clear-definition from `design/poc.md`.

**Independent Test**: given a `drift-audit.json` with mixed findings, a reviewer computes the H2 per-session clear-definition using only the drift-audit content (+ the H2 definition in `design/poc.md`) without re-deriving findings from the transcript.

### Implementation for User Story 3

- [ ] **T009** [US3] Add a "Composing with H2 clear-definition" section to `RUBRIC.md` referencing `design/poc.md`'s H2 per-session clear-definition; explicitly state how each of the three verdict values (`no_drift`, `minor_drift`, `load_bearing_drift`) feeds into the H2 judgment.
- [ ] **T010** [US3] Cross-check that `spec.md` US3 acceptance scenarios are satisfied by the rubric content; update `RUBRIC.md` if any scenario would require re-deriving findings from scratch (should not — the contract guarantees 1/2/4 exist precisely to prevent that).

**Checkpoint**: downstream H2 judgment has `drift-audit.json` as a direct input; no re-derivation.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: close out FR coverage and validate the full slice.

- [ ] **T011** [P] Verify all 18 FRs in `spec.md` are addressed by the rubric + workflow docs. Map each FR to the artifact section that covers it; log the mapping in the analyze.md from `/speckit.analyze` (next stage).
- [ ] **T012** [P] Run the mock synthetic-transcript walkthrough from `quickstart.md` section "Mock audit against a synthetic transcript". Goal: validate the rubric end-to-end without needing a real Phase 3 session. Produce a mock `drift-audit.json` output and verify it passes schema and contract guarantees. Record the mock run at `observations/drift-audits/RUBRIC.md` in an "Examples" section, OR leave the mock transcript uncommitted if it's too large.
- [ ] **T013** Verify no live-session instrumentation language crept in (FR-018). Grep `observations/drift-audits/RUBRIC.md` for words like "during session", "live", "real-time" and confirm any occurrences are in proper context (e.g., "not during session").
- [ ] **T014** Verify no agent-facing drift feedback language crept in (FR-018). Rubric is for auditors (operator + agents doing the audit post-session), never for peers during the session.
- [ ] **T015** [P] Update `ROADMAP.md` workstream row for "Evaluation surface build" — specifically "Draft drift-audit rubric" in the missing-outputs column moves from Open to Landed.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup
- **User Stories (Phases 3–5)**: depend on Foundational
  - US1, US2, US3 can run in parallel after Foundational in principle, but T004 (main rubric authoring) covers so much of the rubric that US2 and US3 naturally follow US1's sections. Pragmatically: US1 → US2 → US3 sequential is cleanest.
- **Polish (Phase 6)**: depends on all user stories complete

### User Story Dependencies

- **US1** is the MVP; rubric doesn't function without it
- **US2** depends on the base rubric from US1 (versioning section appends to RUBRIC.md)
- **US3** depends on the base rubric from US1 (H2 composition section appends to RUBRIC.md)

### Parallel Opportunities

- T003 runs in parallel with T002 (different file)
- T011, T012, T015 in Phase 6 can run in parallel (T011 and T015 touch different files; T012 is standalone)

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 1 Setup + Phase 2 Foundational
2. Complete Phase 3 (US1) — operator can manually audit sessions
3. **Stop and optionally validate the Phase 2 gate** via the mock synthetic-transcript walkthrough (T012)
4. Continue to Phase 4 (US2) and Phase 5 (US3) if slice capacity allows

### Subsequent iterations (after MVP)

- US2 calibration lands next; supports rubric evolution over Phase 3 sessions
- US3 H2 composition lands last; depends on US1+US2 rubric being stable
- Polish (Phase 6) validates the full slice against all 18 FRs

### Post-merge cadence

- First substantive rubric amendments expected after Phase 3 session 1 or 2 (per `design/poc.md` measurement model calibration step)
- Amendments follow FR-013/014 workflow: discrete `drift-audit-rubric: <summary>` commits, `drift-audit.json.rubric_version` references remain valid against their own commit

## Verification checklist

- [ ] All 18 FRs from `spec.md` mapped to at least one task
- [ ] All 3 user stories have ≥1 task tagged with their story ID
- [ ] Each story's "Independent Test" can run against the produced artifacts without needing runtime code
- [ ] Schema-consistency tasks (T006) explicitly cross-link `RUBRIC.md` examples to `data-model.md` validation rules
- [ ] No test-infrastructure tasks (none required per spec Technical Context)
- [ ] No code-implementation tasks (slice is pure content authoring)
- [ ] Phase 6 polish validates FR-011 (post-session only) and FR-018 (no live instrumentation, no agent-facing drift feedback) explicitly
