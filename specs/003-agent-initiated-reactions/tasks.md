# Tasks: Agent-Initiated Emoji Reactions

**Input**: Design documents from `/specs/003-agent-initiated-reactions/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Implementation target**: `mentatzoe/cc-connect` (Go). Tasks track work that lands in that repo, not in `peer-coordination`. PRs there reference this tasks file by URL.

**Tests**: Included — FR-008 (structured log on failure), FR-009 (failure-rate metric), and Principle V (acceptance criteria before overlapping implementation) all make tests first-class here.

**Organization**: Tasks are grouped by user story. Both user stories are P1 and independently testable. US1 (add) and US2 (remove) share a file (`platform/discord/reactions.go`) but address separate Go methods, so they parallelize at the sub-task level.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files OR independent methods with no shared in-file state).
- **[Story]**: `US1`, `US2`, or omitted for shared/foundational tasks.
- File paths are relative to the `mentatzoe/cc-connect` repository root.

## Path Conventions

- Go source: `core/`, `platform/discord/` in the cc-connect repo.
- Tests co-located per cc-connect convention: `*_test.go` alongside source.
- Integration tests: `tests/integration/` if the cc-connect repo has one; otherwise `core/engine_test.go` style stub-platform test.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the cc-connect repo for item-3 work. Minimal because most infra already exists.

- [ ] T001 Create feature branch `003-agent-initiated-reactions` in `mentatzoe/cc-connect` from current `main`. File: `.git/HEAD`.
- [ ] T002 [P] Confirm `go test ./...`, `go vet ./...`, and `go build ./...` all pass on main before any new code lands. File: CI check on baseline.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core interface types and cross-cutting plumbing that both user stories need.

**⚠️ CRITICAL**: No US1 or US2 work can begin until this phase is complete.

- [ ] T003 [P] Add `Reactor` interface + supporting types (`ReactionRequest`, `ReactionDirection`, `ReactionOutcome`, `FailureReason`, `ReactionResult`) per `contracts/agent-session-reactor.md`. File: `core/agent.go` (or new `core/reactor.go` if clearer).
- [ ] T004 [P] Add capability-detection helper `ReactorFor(platform)` returning `(Reactor, bool)` via type assertion. File: `core/capabilities.go` (may already exist; extend if so).
- [ ] T005 [P] Export a stable `FailureReason` string set (match `data-model.md` exactly) and add godoc comments linking each reason to its source FR. File: `core/agent.go` or `core/reactor.go`.
- [ ] T006 **BLOCKED externally**: Wire `InterruptState` lookup from the Transport MVP (Vigil's `001-transport-mvp` work in `mentatzoe/cc-connect`). If `InterruptState` is not yet exposed at the `core/` level, coordinate with Vigil before proceeding. File: integration point TBD.
- [ ] T007 [P] Extend the core test-helper stub platform with a `StubReactor` that records `ReactionRequest` calls and returns configurable `ReactionResult` values. File: `core/testhelpers_test.go` or `core/stubs.go`.

**Checkpoint**: Foundation ready — US1 and US2 may now proceed (parallel at the method level, serial at the file level since both touch `platform/discord/reactions.go`).

---

## Phase 3: User Story 1 - Signal lightweight state via emoji (Priority: P1) 🎯 MVP

**Goal**: Agent sessions can emit emoji reactions on messages through a non-blocking transport primitive.

**Independent Test**: With a live Discord channel the bot has reaction permission in, an agent session calls `AddReaction` and the reaction appears on the target message attributed to the bot; repeat the call idempotently returns `ReactionOutcomeIdempotentPresent` without a duplicate visible reaction.

### Tests for US1

- [ ] T008 [P] [US1] Unit test: happy-path add produces `ReactionOutcomeApplied` and calls `discordgo.Session.MessageReactionAdd` exactly once. File: `platform/discord/reactions_test.go`.
- [ ] T009 [P] [US1] Unit test: duplicate add (reaction already present) returns `ReactionOutcomeIdempotentPresent`, no hard error. File: `platform/discord/reactions_test.go`.
- [ ] T010 [P] [US1] Unit tests: each `FailureReason` on the add path — `message_deleted`, `permission_denied`, `invalid_emoji`, `rate_limit_exceeded`, `stop_suppressed`. Use stub `discordgo` session that injects the corresponding HTTP response / state. File: `platform/discord/reactions_test.go`.
- [ ] T011 [P] [US1] Integration test: stub-platform agent session calls `AddReaction`, assert structured WARN log event appears with field set `{action, channel_id, message_id, emoji, reason, session_id, agent_identity}` on failure paths. File: `core/engine_test.go` or `tests/integration/reactions_test.go`.

### Implementation for US1

- [ ] T012 [US1] Implement `Discord.AddReaction(ctx, req) <-chan ReactionResult` in the Discord platform adapter. Non-blocking, launches a goroutine, returns a buffered size-1 channel. Calls `discordgo.Session.MessageReactionAdd`. File: `platform/discord/reactions.go` (new).
- [ ] T013 [US1] Implement `!stop` pre-check in `AddReaction`: consult `InterruptState` from T006; on `stopped`, return `ReactionOutcomeFail / FailureReasonStopSuppressed` without calling the Discord API. File: `platform/discord/reactions.go`.
- [ ] T014 [US1] Map `discordgo` error responses to `FailureReason` values per `research.md` §2. File: `platform/discord/reactions.go`.
- [ ] T015 [US1] Emit structured WARN log event on `fail_with_reason` outcomes (schema from `data-model.md` — `ReactionFailureLogEvent`). File: `platform/discord/reactions.go`.

**Checkpoint**: US1 delivers an independently testable MVP. Agents can emit reactions; failure paths are observable; `!stop` suppression works. Ship to a test channel and exercise before moving to US2.

---

## Phase 4: User Story 2 - Revoke a prior reaction signal (Priority: P1)

**Goal**: Agent sessions can remove their own previously added reactions, enabling "clear 👀 when done" patterns in operational specs.

**Independent Test**: With a channel where the agent has previously added a reaction, the agent calls `RemoveReaction` and the reaction attributed to that agent is no longer visible on the message. Removing a reaction the agent never added returns `ReactionOutcomeIdempotentAbsent` without error. Attempting to remove another user's reaction returns `FailureReasonCrossUserRemovalRejected`.

### Tests for US2

- [ ] T016 [P] [US2] Unit test: happy-path remove of an agent's own prior reaction produces `ReactionOutcomeApplied` and calls `discordgo.Session.MessageReactionRemoveMe` exactly once. File: `platform/discord/reactions_test.go`.
- [ ] T017 [P] [US2] Unit test: remove on already-absent reaction returns `ReactionOutcomeIdempotentAbsent`, no hard error. File: `platform/discord/reactions_test.go`.
- [ ] T018 [P] [US2] Unit test: attempted cross-user removal (caller passes a user ID that isn't the bot's) returns `FailureReasonCrossUserRemovalRejected` without calling the generic `MessageReactionRemove` API. File: `platform/discord/reactions_test.go`.
- [ ] T019 [P] [US2] Unit tests: each applicable `FailureReason` on the remove path (`message_deleted`, `permission_denied`, `invalid_emoji`, `rate_limit_exceeded`, `stop_suppressed`). File: `platform/discord/reactions_test.go`.
- [ ] T020 [P] [US2] Integration test: agent calls `AddReaction` then `RemoveReaction`, assert final platform state matches no-reaction-for-this-agent. File: `tests/integration/reactions_test.go` or equivalent.

### Implementation for US2

- [ ] T021 [US2] Implement `Discord.RemoveReaction(ctx, req) <-chan ReactionResult` in the Discord platform adapter. Calls `discordgo.Session.MessageReactionRemoveMe` (never the generic cross-user remove). File: `platform/discord/reactions.go` (extends T012's file).
- [ ] T022 [US2] Implement `!stop` pre-check in `RemoveReaction`, same pattern as T013. File: `platform/discord/reactions.go`.
- [ ] T023 [US2] Add cross-user-rejection guard: if a caller somehow constructs a request implying another user's reaction, reject with `FailureReasonCrossUserRemovalRejected` without making a Discord call. File: `platform/discord/reactions.go`.
- [ ] T024 [US2] Share error mapping (T014) and log-event emission (T015) between add and remove; refactor to a single internal helper. File: `platform/discord/reactions.go`.

**Checkpoint**: US2 delivers the full reaction primitive. Add and remove are symmetric, the own-reactions-only invariant holds, and moderation-style cross-user removal is explicitly rejected.

---

## Phase 5: Polish & Cross-cutting

- [ ] T025 Implement `ReactionFailureRateMetricEvent` rolling-window emission (schema from `data-model.md`). Window size: start with 60 seconds; make it a configurable knob in `config.toml` with a sensible default. File: `platform/discord/reactions_metric.go` (new) or extension of `reactions.go`.
- [ ] T026 [P] Update cc-connect documentation (README and/or CLAUDE.md) with a short "Reactions" section pointing at this spec in the peer-coordination repo. File: `README.md` and/or `CLAUDE.md` in cc-connect.
- [ ] T027 [P] Traceability matrix: verify each FR (FR-001 through FR-013) is exercised by at least one test listed above. Produce a table in `specs/003-agent-initiated-reactions/traceability.md` in this repo (not cc-connect) if any gap is found. File: `specs/003-agent-initiated-reactions/traceability.md` (this repo).
- [ ] T028 Run full `go test ./... -race` on the cc-connect branch; all pass before merge. File: CI green.
- [ ] T029 Code review round on the cc-connect PR, with Codex (Vigil) as the independent reviewer per constitution Governance §independent-review. File: PR review comments.

---

## Dependencies Graph

```
T001 → T002 → [T003, T004, T005, T007]  (parallel)
                      ↓
                     T006 (external block on Vigil's 001)
                      ↓
              Foundation complete
                      ↓
         ┌────────────┴────────────┐
         ↓                         ↓
      US1 tests (T008-T011)    US2 tests (T016-T020)
         ↓                         ↓
      US1 impl (T012-T015)      US2 impl (T021-T024)
                      ↓
                Polish (T025-T029)
```

## Parallel execution examples

**Within Phase 2 (Foundational):** T003, T004, T005, T007 can all run in parallel — different files or independent sections of `core/`.

**Within US1 tests:** T008, T009, T010 all edit the same test file but independent test functions; can be written in parallel by different agents/sessions with merge discipline.

**Across US1 and US2:** Tests can be written in parallel. Implementation tasks (T012-T015 vs T021-T024) touch the same file (`platform/discord/reactions.go`); must be serialized unless split into separate files.

**Polish Phase 5:** T026 and T027 parallelize cleanly (different files). T028 and T029 are sequential closers.

## Implementation Strategy (MVP incremental)

1. **MVP = US1 only.** Ship add-reactions first. Agents can signal state; removal comes next.
2. **US2 adds symmetry.** Remove-reactions completes the primitive; enables "clear 👀 after done" patterns.
3. **Polish is optional for MVP landing** but required before the open-floor pilot counts this item as "done" per the roadmap tracker (#4).

## Independent test criteria summary

- **US1 MVP test**: Agent emits `AddReaction`, reaction appears on message, duplicate add is idempotent.
- **US2 completion test**: Agent `AddReaction` then `RemoveReaction`, final state has no agent-attributed reaction; cross-user removal attempt rejected.
- **Cross-cutting**: `!stop`-suppressed operations do not reach the Discord API and surface as `FailureReasonStopSuppressed`.

## Task count summary

| Phase | Tasks | Parallelizable |
|---|---|---|
| 1 Setup | 2 | 1 |
| 2 Foundational | 5 | 4 |
| 3 US1 (tests + impl) | 8 | 4 |
| 4 US2 (tests + impl) | 9 | 5 |
| 5 Polish | 5 | 2 |
| **Total** | **29** | **16** |

## Format validation

All tasks above use the required `- [ ] TXXX [P?] [US?] Description` format with exact file paths. Independent test criteria for each user story are stated. Dependencies graph and parallelization notes are present.
