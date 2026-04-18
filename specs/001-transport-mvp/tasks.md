# Tasks: Transport MVP

**Input**: Design documents from `/specs/001-transport-mvp/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/pilot-channel-contract.md`

**Tests**: Update downstream `cc-connect` unit and integration coverage because the spec defines independent verification criteria for both user stories.

**Organization**: Tasks are grouped by user story to keep the narrowed `001`
scope limited to fanout, self-loop suppression, and channel-scoped hard
interrupt behavior.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`)
- Every task includes exact file paths, even when the work lands in the
  downstream `cc-connect` repo

## Path Conventions

- Governance artifacts stay in `specs/001-transport-mvp/` in this repo
- Downstream implementation work targets `/Users/zmll/github/cc-connect/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the operator-visible config and doc surface for the
designated pilot channel before deeper code changes.

- [X] T001 Add designated pilot-channel configuration examples to `/Users/zmll/github/cc-connect/config.example.toml`
- [X] T002 [P] Document the narrowed pilot-channel transport scope in `/Users/zmll/github/cc-connect/docs/discord.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Introduce shared transport state for pilot designation and interrupt control.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [X] T003 Define pilot-channel configuration parsing and admitted-peer state in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [ ] T004 [P] Add engine-side interrupt state helpers for the designated pilot channel in `/Users/zmll/github/cc-connect/core/engine.go`, exposing a public `core` consumer surface other transport primitives can consult for `!stop` suppression checks.

**Checkpoint**: Shared pilot-channel state exists; story work can begin.

---

## Phase 3: User Story 1 - Let the Pilot Channel Run Open-Floor (Priority: P1) 🎯 MVP

**Goal**: Fan out qualifying ordinary pilot-channel messages to all admitted
peer agents while preserving non-pilot behavior and self-loop suppression.

**Independent Test**: Configure one designated pilot channel, send an ordinary
non-mentioned message there, verify admitted peers become eligible, verify a
non-pilot channel keeps its existing behavior, and confirm an agent does not
re-trigger on its own outbound pilot-channel message.

### Tests for User Story 1

- [X] T005 [P] [US1] Add Discord unit coverage for pilot-channel fanout, non-pilot fallback, and self-loop suppression in `/Users/zmll/github/cc-connect/platform/discord/discord_test.go`
- [ ] T006 [P] [US1] Add integration coverage for open-floor fanout in `/Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go`

### Implementation for User Story 1

- [X] T007 [US1] Implement designated pilot-channel fanout and non-pilot fallback in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [X] T008 [US1] Implement self-loop suppression for agent-authored outbound pilot-channel messages in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [X] T009 [US1] Update operator-facing pilot fanout examples in `/Users/zmll/github/cc-connect/config.example.toml` and `/Users/zmll/github/cc-connect/docs/discord.md`

**Checkpoint**: The designated pilot channel behaves as open-floor fanout
without reintroducing transport-side reply arbitration.

---

## Phase 4: User Story 2 - Halt and Resume the Pilot Channel Explicitly (Priority: P1)

**Goal**: Enforce operator-centered `!stop` / `!resume` semantics for the
designated pilot channel, including suppression of unsent outbound transport
effects and immediate application to future routing.

**Independent Test**: With active pilot-channel traffic, issue `!stop`, verify
unsent outbound transport effects are suppressed, confirm only the operator or
allowlisted delegate can interrupt, and verify `!resume` restores routing for
future turns.

### Tests for User Story 2

- [ ] T010 [P] [US2] Add unit coverage for interrupt authority, best-effort suppression, and designation-change behavior in `/Users/zmll/github/cc-connect/core/engine_test.go` and `/Users/zmll/github/cc-connect/platform/discord/discord_test.go`, including the case where designation changes mid-turn and only future routing adopts the new channel.
- [ ] T011 [P] [US2] Add integration coverage for channel-scoped `!stop` / `!resume` in `/Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go`, including the case where pilot designation changes while an existing turn completes under the old channel and only future routing adopts the new one.

### Implementation for User Story 2

- [ ] T012 [US2] Implement channel-scoped `!stop` / `!resume` authority and suppression semantics in `/Users/zmll/github/cc-connect/core/engine.go`
- [X] T013 [US2] Wire pilot-channel interrupt commands and designation-change handling in `/Users/zmll/github/cc-connect/platform/discord/discord.go`
- [X] T014 [US2] Update operator-facing interrupt documentation in `/Users/zmll/github/cc-connect/config.example.toml` and `/Users/zmll/github/cc-connect/docs/discord.md`

**Checkpoint**: The designated pilot channel can be explicitly stopped and
resumed without transport rewriting already-running turns beyond the defined
best-effort cancel semantics.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile the implementation handoff with the narrowed spec package.

- [ ] T015 [P] Refresh pilot-readiness notes in `specs/001-transport-mvp/quickstart.md`
- [ ] T016 Run the operator-visible contract against the final implementation task list in `specs/001-transport-mvp/contracts/pilot-channel-contract.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup; blocks both user stories
- **User Stories (Phases 3-4)**: Depend on Foundational completion
- **Polish (Phase 5)**: Depends on the chosen story scope being complete

### User Story Dependencies

- **US1 (P1)**: Starts immediately after Phase 2; defines open-floor fanout and self-loop behavior
- **US2 (P1)**: Starts immediately after Phase 2; defines interrupt authority and suppression behavior

### Within Each User Story

- Add or update tests before closing the implementation tasks for that story
- Platform routing changes land before operator documentation is updated
- Interrupt behavior updates land in `core/engine.go` before final Discord wiring/docs

### Parallel Opportunities

- T001 and T002 can run in parallel
- T003 and T004 can run in parallel once the narrowed scope is locked
- Within each story, unit and integration test work can proceed in parallel
- After Phase 2, US1 and US2 can be worked independently by different owners

---

## Parallel Example: User Story 1

```bash
# Parallelizable validation once foundations are ready:
Task: "Add Discord unit coverage for pilot-channel fanout, non-pilot fallback, and self-loop suppression in /Users/zmll/github/cc-connect/platform/discord/discord_test.go"
Task: "Add integration coverage for open-floor fanout in /Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go"
```

---

## Parallel Example: User Story 2

```bash
# Parallelizable validation once foundations are ready:
Task: "Add unit coverage for interrupt authority, best-effort suppression, and designation-change behavior in /Users/zmll/github/cc-connect/core/engine_test.go and /Users/zmll/github/cc-connect/platform/discord/discord_test.go"
Task: "Add integration coverage for channel-scoped !stop / !resume in /Users/zmll/github/cc-connect/tests/integration/agent_integration_test.go"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate open-floor fanout and self-loop suppression in the designated pilot channel

### Incremental Delivery

1. Land setup and foundational pilot-channel state
2. Deliver US1 fanout behavior and validate independently
3. Deliver US2 interrupt behavior and validate independently
4. Refresh quickstart and contract notes once both stories are complete

### Parallel Team Strategy

1. Complete Phase 1 and Phase 2 together
2. Split story ownership after foundations stabilize:
   - Owner A: US1 open-floor fanout and self-loop suppression
   - Owner B: US2 `!stop` / `!resume` authority and suppression
3. Reconcile docs/config changes after each story reaches its checkpoint

---

## Notes

- Tasks remain tracked in this governance repo even though most file paths point
  at `/Users/zmll/github/cc-connect/`
- The task graph preserves the designation split: no reaction, approval, pinned
  rule, or channel-policy tasks belong in active `001`
- Each user story is independently testable and ready for issue sync later if needed
