# Tasks: Transport MVP

**Input**: Design documents from `/specs/001-transport-mvp/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/pilot-channel-contract.md`

**Tests**: Add or update downstream `cc-connect` unit and integration coverage for each user story because the spec defines independent verification criteria per story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing while keeping this repo as the durable planning source of truth.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Every task includes exact file paths, even when the touched files live in the downstream `cc-connect` repo

## Path Conventions

- Governance artifacts remain in `specs/001-transport-mvp/` in this repo
- Downstream implementation work targets `/Users/zmll/github/cc-connect/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Define the operator-visible configuration surface for the pilot before code changes branch into separate stories.

- [ ] T001 Add Transport MVP pilot-channel configuration examples to `/Users/zmll/github/cc-connect/config.example.toml`
- [ ] T002 [P] Document pilot-channel setup, permissions, and rollout expectations in `/Users/zmll/github/cc-connect/docs/discord.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Introduce shared transport primitives that all user stories build on.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [ ] T003 Define shared Discord pilot-mode state and config parsing hooks in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [ ] T004 [P] Extend transport-facing platform/message interfaces for reactions and startup context in `/Users/zmll/github/cc-connect/core/interfaces.go` and `/Users/zmll/github/cc-connect/core/message.go`
- [ ] T005 Add engine-level support for channel-scoped interactive stop/resume state in `/Users/zmll/github/cc-connect/core/engine.go`

**Checkpoint**: Shared pilot primitives exist; user-story implementation can begin.

---

## Phase 3: User Story 1 - Run the Open-Floor Pilot Safely (Priority: P1) 🎯 MVP

**Goal**: Let both peer agents participate in one pilot channel without re-mentions while preserving channel-scoped `!stop` / `!resume` safety controls and self-loop protection.

**Independent Test**: Enable the pilot mode for one channel, send ordinary non-mentioned messages, verify eligible agents can respond, then confirm `!stop` suppresses outbound activity until `!resume`, with no agent self-triggering on its own output.

### Tests for User Story 1

- [ ] T006 [P] [US1] Add Discord unit coverage for open-floor gating, mention-only fallback, and self-loop suppression in `/Users/zmll/github/cc-connect/platform/discord/discord_test.go`
- [ ] T007 [P] [US1] Add integration coverage for channel-scoped `!stop` / `!resume` interruption in `/Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go`

### Implementation for User Story 1

- [ ] T008 [US1] Implement pilot-channel open-floor routing and mention-only fallback in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [ ] T009 [US1] Implement self-loop suppression for agent-authored outbound Discord messages in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [ ] T010 [US1] Implement channel-scoped `!stop` / `!resume` command handling and interrupt-state transitions in `/Users/zmll/github/cc-connect/platform/discord/discord.go` and `/Users/zmll/github/cc-connect/core/engine.go`
- [ ] T011 [US1] Update operator-facing pilot-channel examples for open-floor mode in `/Users/zmll/github/cc-connect/config.example.toml` and `/Users/zmll/github/cc-connect/docs/discord.md`

**Checkpoint**: The pilot channel can run open-floor mode safely with explicit stop/resume control.

---

## Phase 4: User Story 2 - Approve and Acknowledge with Reactions (Priority: P2)

**Goal**: Let agents acknowledge with emoji reactions and gate state-changing actions on an authorized approval reaction rather than extra text.

**Independent Test**: Have an agent add a reaction as acknowledgment, propose a state-changing action, verify it remains blocked until the configured approval reaction is added by the authorized operator, then confirm the action proceeds.

### Tests for User Story 2

- [ ] T012 [P] [US2] Add Discord unit coverage for reaction send, approval observation, and unauthorized approval rejection in `/Users/zmll/github/cc-connect/platform/discord/discord_test.go`
- [ ] T013 [P] [US2] Add integration coverage for approval-gated action release in `/Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go`

### Implementation for User Story 2

- [ ] T014 [US2] Implement reaction-send capabilities for acknowledgments and done signals in `/Users/zmll/github/cc-connect/core/interfaces.go` and `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [ ] T015 [US2] Implement approval-reaction observation and operator authorization checks in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [ ] T016 [US2] Gate state-changing actions on approval-reaction state in `/Users/zmll/github/cc-connect/core/engine.go`
- [ ] T017 [US2] Document approval reaction configuration and operator workflow in `/Users/zmll/github/cc-connect/config.example.toml` and `/Users/zmll/github/cc-connect/docs/discord.md`

**Checkpoint**: Reaction-based acknowledgement and approval flow works independently of pinned-rule ingestion.

---

## Phase 5: User Story 3 - Apply Channel Rules from Pinned Context (Priority: P3)

**Goal**: Inject channel-pinned rules into new sessions so operators can change channel policy without editing prompts by hand.

**Independent Test**: Pin one or more rules messages in the pilot channel, start a fresh session, verify the rules appear in session startup context, and confirm a channel with no pinned rules still starts cleanly.

### Tests for User Story 3

- [ ] T018 [P] [US3] Add Discord unit coverage for pinned-message capture ordering and empty-pin fallback in `/Users/zmll/github/cc-connect/platform/discord/discord_test.go`
- [ ] T019 [P] [US3] Add integration coverage for session-start pinned-rule injection in `/Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go`

### Implementation for User Story 3

- [ ] T020 [US3] Implement pinned-message fetch, filtering, and ordering for pilot sessions in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [ ] T021 [US3] Inject pinned-rule text into new-session startup context without mutating live sessions in `/Users/zmll/github/cc-connect/core/message.go` and `/Users/zmll/github/cc-connect/core/engine.go`
- [ ] T022 [US3] Document pinned-rule operator workflow and session-start behavior in `/Users/zmll/github/cc-connect/docs/discord.md` and `/Users/zmll/github/cc-connect/config.example.toml`

**Checkpoint**: Fresh sessions pick up pinned channel rules while already-running sessions remain stable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the final operator handoff and keep this governance spec aligned with the implementation plan.

- [ ] T023 [P] Refresh pilot-readiness guidance in `/Users/zmll/github/peer-coordination/.worktrees/transport-mvp-spec/specs/001-transport-mvp/quickstart.md`
- [ ] T024 Run the operator-visible contract against the final task list in `/Users/zmll/github/peer-coordination/.worktrees/transport-mvp-spec/specs/001-transport-mvp/contracts/pilot-channel-contract.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on whichever user stories are included in the pilot milestone

### User Story Dependencies

- **US1 (P1)**: Starts immediately after Phase 2; defines the MVP slice
- **US2 (P2)**: Starts after Phase 2; depends on shared reaction hooks from T004 but not on pinned-rule work
- **US3 (P3)**: Starts after Phase 2; depends on shared startup-context hooks from T004 but not on approval-reaction work

### Within Each User Story

- Add or update tests before closing implementation tasks for that story
- Platform wiring comes before engine gating or startup-context integration
- Docs/config updates land after behavior is implemented so examples reflect actual behavior

### Parallel Opportunities

- T001 and T002 can run in parallel
- T004 can run in parallel with T003 once the pilot-mode scope is agreed
- Within each user story, the test task and the main implementation task can be staffed independently if the implementer and reviewer coordinate on file ownership
- After Phase 2, US1, US2, and US3 can be developed by separate owners because their primary code paths are distinct

---

## Parallel Example: User Story 1

```bash
# Parallelizable prep once foundational work is done:
Task: "Add Discord unit coverage for open-floor gating, mention-only fallback, and self-loop suppression in /Users/zmll/github/cc-connect/platform/discord/discord_test.go"
Task: "Add integration coverage for channel-scoped !stop / !resume interruption in /Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go"
```

---

## Parallel Example: User Story 2

```bash
# Parallelizable prep once foundational work is done:
Task: "Add Discord unit coverage for reaction send, approval observation, and unauthorized approval rejection in /Users/zmll/github/cc-connect/platform/discord/discord_test.go"
Task: "Add integration coverage for approval-gated action release in /Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go"
```

---

## Parallel Example: User Story 3

```bash
# Parallelizable prep once foundational work is done:
Task: "Add Discord unit coverage for pinned-message capture ordering and empty-pin fallback in /Users/zmll/github/cc-connect/platform/discord/discord_test.go"
Task: "Add integration coverage for session-start pinned-rule injection in /Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the open-floor pilot channel before expanding scope

### Incremental Delivery

1. Land setup and foundational transport hooks
2. Deliver US1 as the first pilot-ready slice
3. Add US2 to replace noisy approval chatter with reaction workflows
4. Add US3 to make channel policy operator-editable via pins
5. Refresh quickstart and contract guidance once the chosen milestone is complete

### Parallel Team Strategy

1. Complete Phase 1 and Phase 2 together
2. Split ownership after foundations are stable:
   - Owner A: US1 open-floor and stop/resume
   - Owner B: US2 reactions and approval gating
   - Owner C: US3 pinned-rule ingestion
3. Reconcile docs/config changes after each story reaches its checkpoint

---

## Notes

- Tasks remain tracked in this governance repo, even though most file paths point at `/Users/zmll/github/cc-connect/`
- Each user story is independently testable and can become its own GitHub issue group
- The task graph preserves the constitutional boundary: transport behavior is specified here without moving governance back into the implementation repo
