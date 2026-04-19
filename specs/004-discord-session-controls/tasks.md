# Tasks: Discord Session Controls

**Input**: Design documents from `/specs/004-discord-session-controls/`
**Prerequisites**: `spec.md` (required), `plan.md` (required), `research.md`, `data-model.md`, `contracts/session-control-behavior.md`

**Tests**: Required for this slice. Session controls are a safety-critical part of the Phase 1 harness, so Discord-platform and core-session regression coverage must land with the implementation.

**Organization**: Tasks are grouped by user story so channel binding, operator controls, and runtime session-boundary behavior remain independently reviewable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: establish the new slice and shared config/documentation touchpoints.

- [ ] T001 Create/update the slice-local artifacts under `specs/004-discord-session-controls/` so the implementation and review trail is complete.
- [ ] T002 Update Discord config documentation in `cc-connect/config.example.toml` and `cc-connect/docs/discord.md` to reserve a clear place for the new bound `channel_id` behavior.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: core transport scaffolding that must exist before session-control behavior is implemented.

- [ ] T003 Add explicit Discord `channel_id` option parsing and storage in `cc-connect/platform/discord/discord.go`.
- [ ] T004 [P] Add helper logic in `cc-connect/platform/discord/discord.go` for deciding whether an inbound message or interaction is on the bound surface, including thread-parent handling when `thread_isolation = true`.
- [ ] T005 [P] Add runtime gate state to the Discord platform in `cc-connect/platform/discord/discord.go` so the bound surface can be `open` or `closed` independently of raw message receipt.

**Checkpoint**: Channel-binding and runtime-gate primitives exist; user story work can now proceed.

## Phase 3: User Story 1 - Bound Open-Floor Channel (Priority: P1) 🎯 MVP

**Goal**: only the designated Discord surface can enter the Phase 1 runtime.

**Independent Test**: a mention in the bound channel dispatches; a mention in an unbound channel does not.

### Tests for User Story 1

- [ ] T006 [P] [US1] Add Discord-platform tests in `cc-connect/platform/discord/discord_test.go` covering bound-channel acceptance and unbound-channel rejection for normal messages.
- [ ] T007 [P] [US1] Add Discord-platform tests in `cc-connect/platform/discord/discord_test.go` covering the same bound/unbound behavior for slash or component interaction entry points.

### Implementation for User Story 1

- [ ] T008 [US1] Enforce bound-channel filtering in the Discord message handler path in `cc-connect/platform/discord/discord.go` before dispatch into the engine.
- [ ] T009 [US1] Enforce bound-channel filtering in the Discord interaction handler path in `cc-connect/platform/discord/discord.go` before dispatch into the engine.
- [ ] T010 [US1] Fail closed when the configured bound surface cannot be resolved, with reviewable logging in `cc-connect/platform/discord/discord.go`.

**Checkpoint**: The bot is scoped to the designated Phase 1 Discord surface.

## Phase 4: User Story 2 - Safe Operator Stop/Resume (Priority: P1)

**Goal**: `!stop` closes safely and `!resume` opens a new session under operator control.

**Independent Test**: after `!stop`, peer posts do not continue the old session; after `!resume`, a new session opens.

### Tests for User Story 2

- [ ] T011 [P] [US2] Add Discord-platform tests in `cc-connect/platform/discord/discord_test.go` for operator `!stop` closing the current session and blocking later peer continuation.
- [ ] T012 [P] [US2] Add Discord-platform tests in `cc-connect/platform/discord/discord_test.go` for `!resume` creating a fresh session rather than reviving the stopped one.

### Implementation for User Story 2

- [ ] T013 [US2] Intercept operator `!stop` / `!resume` in `cc-connect/platform/discord/discord.go` before normal agent dispatch.
- [ ] T014 [US2] Reuse or adapt existing new-session/reset behavior in `cc-connect/core/engine.go` and/or `cc-connect/core/session.go` so `!resume` produces a fresh logical session.
- [ ] T015 [US2] Ensure peer posts while closed are rejected or ignored in `cc-connect/platform/discord/discord.go` rather than routed into the stopped session.

**Checkpoint**: Safe interrupt behavior matches the current POC session model.

## Phase 5: User Story 3 - Coherent Runtime Session Boundaries (Priority: P2)

**Goal**: runtime-visible state preserves clear channel/session boundaries for later review artifacts.

**Independent Test**: a dry run across open -> stop -> resume has unambiguous channel/session behavior in runtime state and logs.

### Tests for User Story 3

- [ ] T016 [P] [US3] Add or extend tests in `cc-connect/platform/discord/discord_test.go` for thread-isolation behavior under a bound parent channel.
- [ ] T017 [P] [US3] Add core-session regression coverage in `cc-connect/core/session_test.go` if the session-manager integration changes for fresh-session creation.

### Implementation for User Story 3

- [ ] T018 [US3] Ensure the runtime preserves stable channel identity for later `channel_id` artifact population, updating any needed metadata plumbing in `cc-connect/platform/discord/discord.go` and adjacent core helpers.
- [ ] T019 [US3] Make operator-only session opening explicit in runtime behavior: peer posts in a closed/not-yet-open session must not open it.
- [ ] T020 [US3] Update Discord docs and any transport-facing notes to reflect the new operator-only open / stop / resume semantics.

**Checkpoint**: Runtime state is coherent enough for the later transcript-export and session-bundle slices to consume.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T021 [P] Run `go test ./platform/discord ./core` from `cc-connect/` and record the exact verification command/results in the implementation-complete handoff.
- [ ] T022 Review config/docs wording in `cc-connect/config.example.toml` and `cc-connect/docs/discord.md` so the new binding and control semantics are legible without scratchpad context.
- [ ] T023 [P] Update slice-local `quickstart.md` if implementation details shift during coding.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup completion and blocks all user stories
- **User Stories (Phases 3–5)**: depend on Foundational completion
- **Polish (Phase 6)**: depends on desired user stories being complete

### User Story Dependencies

- **US1** starts immediately after Foundational; it is the MVP gate for the slice
- **US2** depends on the runtime gate from Foundational and should follow US1 closely
- **US3** depends on both US1 and US2 behavior being in place

### Parallel Opportunities

- T004 and T005 can run in parallel after T003
- T006 and T007 can run in parallel
- T011 and T012 can run in parallel
- T016 and T017 can run in parallel
- T021 and T022 can run in parallel once implementation stabilizes

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Setup and Foundational tasks
2. Implement and verify bound-channel filtering (US1)
3. Implement and verify `!stop` / `!resume` semantics (US2)
4. Stop and validate the Phase 1 dry-run control surface
5. Then finish US3 coherence / polish work before moving to transcript export
