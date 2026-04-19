# Tasks: Discord Transcript Export

**Input**: Design documents from `/specs/006-discord-transcript-export/`
**Prerequisites**: `spec.md` (required), `plan.md` (required), `research.md`, `data-model.md`, `contracts/transcript-export-behavior.md`, `quickstart.md`

**Tests**: Required for this slice. Transcript export is a contract-bearing Phase 1 transport surface; rendering, provenance, and failure-path behavior need automated coverage.

**Organization**: Tasks are grouped by user story so preferred export, fallback/provenance, and turn-reference stability remain independently reviewable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: establish slice-local artifacts and reserve the command/documentation touchpoints.

- [ ] T001 Create/update the slice-local artifacts under `specs/006-discord-transcript-export/` so the review trail is complete.
- [ ] T002 Reserve the transcript-export command/documentation touchpoints in `cc-connect/cmd/cc-connect/main.go` and `cc-connect/docs/discord.md`.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: build the shared export/rendering primitives before user-story behavior branches.

- [ ] T003 Add a bounded transcript-export command entrypoint in `cc-connect/cmd/cc-connect/main.go` and a new command file under `cc-connect/cmd/cc-connect/`.
- [ ] T004 [P] Add bundle-metadata loading and transcript-source update helpers in the new `cc-connect/cmd/cc-connect/` transcript export command file.
- [ ] T005 [P] Add reusable Discord history fetch and transcript-render helpers in `cc-connect/platform/discord/` or another slice-local helper file under `cc-connect/`.
- [ ] T006 [P] Add test fixtures/helpers for transcript rendering and bundle metadata updates in `cc-connect/cmd/cc-connect/` and/or `cc-connect/platform/discord/` tests.

**Checkpoint**: export command scaffolding, bundle metadata helpers, and rendering helpers exist; story-specific behavior can now be implemented.

## Phase 3: User Story 1 — Preferred export produces bundle-compatible `transcript.md` (Priority: P1) 🎯 MVP

**Goal**: operator can export Discord session history into a valid bundle transcript with truthful `transcript_source: "export"`.

**Independent Test**: given a bundle with Discord `channel_id`, `opened_at`, and `closed_at`, run the export command and verify `transcript.md` is written in chronological order with author + timestamp turns and `meta.json.transcript_source == "export"`.

### Tests for User Story 1

- [ ] T007 [P] [US1] Add transcript-render tests in `cc-connect/platform/discord/discord_test.go` or a new focused test file covering chronological ordering and author/timestamp formatting.
- [ ] T008 [P] [US1] Add command-level tests in `cc-connect/cmd/cc-connect/` covering successful export into an existing session bundle and `meta.json.transcript_source = "export"`.

### Implementation for User Story 1

- [ ] T009 [US1] Implement the export command flow in `cc-connect/cmd/cc-connect/` to read bundle `meta.json`, fetch the Discord history for the session window, and write `observations/sessions/<session-id>/transcript.md`.
- [ ] T010 [US1] Implement transcript rendering in `cc-connect/platform/discord/` so each turn is chronological, human-readable, and includes author + canonical timestamp.
- [ ] T011 [US1] Update `meta.json.transcript_source` handling in the command flow so successful preferred export records `export`.

**Checkpoint**: preferred export path works end-to-end for a bounded Discord-backed session bundle.

## Phase 4: User Story 2 — Explicit fallback when export is unavailable or incomplete (Priority: P1)

**Goal**: export failure or repair does not silently corrupt provenance; operator can still finish the bundle with `reauthored` or `hybrid`.

**Independent Test**: simulate export failure or incomplete export, run the operator-facing fallback/update path, and verify the bundle remains valid with truthful provenance.

### Tests for User Story 2

- [ ] T012 [P] [US2] Add command-level tests in `cc-connect/cmd/cc-connect/` covering explicit export failure and operator-directed fallback behavior.
- [ ] T013 [P] [US2] Add provenance-update tests in `cc-connect/cmd/cc-connect/` for `reauthored` and `hybrid` transitions.

### Implementation for User Story 2

- [ ] T014 [US2] Make preferred export fail explicitly in the transcript export command when the fetched history cannot produce a trustworthy transcript.
- [ ] T015 [US2] Implement the provenance-update path in `cc-connect/cmd/cc-connect/` so fallback outcomes are recorded as `reauthored` or `hybrid` rather than falsely `export`.
- [ ] T016 [US2] Update operator-facing guidance in `cc-connect/docs/discord.md` and/or slice docs so fallback use is explicit and reviewable.

**Checkpoint**: export failure does not masquerade as success; bundle provenance remains trustworthy.

## Phase 5: User Story 3 — Stable turn references for downstream artifacts (Priority: P2)

**Goal**: exported transcripts preserve unique turn keys compatible with `interventions.json.target_turn` and `drift-audit.json.turn_ref`.

**Independent Test**: generate an exported transcript where close-together messages would collide at second precision, and verify downstream references still resolve uniquely.

### Tests for User Story 3

- [ ] T017 [P] [US3] Add rendering tests in `cc-connect/platform/discord/discord_test.go` or a focused export test file covering same-second message uniqueness and canonical timestamp stability.
- [ ] T018 [P] [US3] Add command/integration tests in `cc-connect/cmd/cc-connect/` verifying downstream artifact references can resolve against the exported transcript.

### Implementation for User Story 3

- [ ] T019 [US3] Implement canonical timestamp normalization/disambiguation in the transcript renderer so every turn key is ISO-8601 and unique within the session.
- [ ] T020 [US3] Ensure the export command only includes the intended session window from the bound channel rather than surrounding chatter.
- [ ] T021 [US3] Document the turn-key behavior and bundle-compatibility guarantees in `cc-connect/docs/discord.md` and slice-local `quickstart.md` if implementation details sharpen them.

**Checkpoint**: downstream bundle artifacts can safely anchor to exported transcript turns.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T022 [P] Run the targeted export-related Go tests under `cc-connect/` and record the exact verification commands/results for review.
- [ ] T023 Review the slice for cross-artifact consistency against `specs/001-session-bundle-skeleton/spec.md`; log any necessary fast-follow wording cleanup separately rather than silently mutating unrelated contracts.
- [ ] T024 [P] Update `specs/006-discord-transcript-export/quickstart.md` if operator workflow details shift during implementation.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup completion and blocks all user stories
- **User Stories (Phases 3–5)**: depend on Foundational completion
- **Polish (Phase 6)**: depends on desired user stories being complete

### User Story Dependencies

- **US1** starts immediately after Foundational; it is the MVP gate for the slice
- **US2** depends on the export command and metadata helpers from US1
- **US3** depends on the renderer and bounded-window behavior from US1, and should account for provenance behavior from US2

### Parallel Opportunities

- T004, T005, and T006 can run in parallel after T003
- T007 and T008 can run in parallel
- T012 and T013 can run in parallel
- T017 and T018 can run in parallel
- T022 and T024 can run in parallel once implementation stabilizes

## Implementation Strategy

### MVP First (US1 only)

1. Complete Setup and Foundational tasks
2. Implement and verify the preferred export path (US1)
3. Stop and validate that a Discord-backed session bundle can now produce a reviewable `transcript.md`
4. Then complete fallback/provenance (US2) and turn-key stability/windowing (US3)

### Incremental Delivery

1. Land export command scaffolding + renderer primitives
2. Land US1 end-to-end preferred export
3. Land explicit failure/fallback provenance handling
4. Land turn-key uniqueness and bounded-window tightening
