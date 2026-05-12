# Feature Specification: cc-connect Session-Lock Interrupt

**Feature Branch**: `codex-013-cc-connect-session-lock-interrupt`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: [PC-68](mention://issue/45e33f03-3555-4476-bc6b-62cc1647635a) / upstream [`mentatzoe/cc-connect#3`](https://github.com/mentatzoe/cc-connect/issues/3): a long-running Bash/tool turn can leave a cc-connect session busy until the 2h idle timeout, and operator interrupt must release the lock within seconds.

## Clarifications

### Session 2026-05-05

- Q: Where does the lock live? -> A: In cc-connect `core.Session.busy`. Discord only gates/open-closes the surface, and Claude Code owns the underlying tool process, but the queue/fail behavior is caused by cc-connect refusing `Session.TryLock()` while the engine event loop still holds the busy flag.
- Q: What exact root cause is fixed in this slice? -> A: `processInteractiveEvents` could leave the stop-select loop after `EventResult` and then block on `pendingSend` (`AgentSession.Send`) before unlocking. If `Send` did not return after the visible result, `/stop` could mark state stopped but not release the busy lock until `Send` returned or idle recovery killed the session.
- Q: What is the interrupt scope? -> A: Per agent session key. In the Phase 3 two-peer pilot, interrupting agent A must stop only A's cc-connect session for that Discord session key; it must not stop another peer bot sharing the channel.
- Q: What does the operator type? -> A: `/stop` remains canonical. `/cancel` and `/interrupt` are accepted aliases for the same command. Discord session-control shorthands `!stop`, `!cancel`, and `!interrupt` normalize to `/stop`.
- Q: What is the cancel-ack semantics? -> A: The platform transcript receives the existing execution-stopped acknowledgement. The interrupted agent process is closed; queued messages are rejected with session-reset errors rather than silently replayed into a fresh turn. The next user message starts a new live turn against the same logical session key.
- Q: Does reply-to context survive? -> A: The interrupt command's own reply context is only used for the acknowledgement. Queued message reply contexts are dropped with reset notifications. PC-67 reply-to work can still preserve normal reply context on subsequent fresh messages; this slice does not reinterpret reply-to semantics.
- Q: What about agent-side crash? -> A: Same recovery principle: abnormal event-loop exit must drop queued messages, clean interactive state, and release `Session.busy`. This slice adds a regression around the stuck-send case and relies on existing channel-closed/error cleanup for crash paths.

## User Scenarios & Testing

### User Story 1 - Operator cancels a stuck long-running turn (Priority: P1)

As the operator, when a cc-connect-backed agent appears stuck after a long Bash/tool run, I can send `/stop`, `/cancel`, or `/interrupt` and get an acknowledgement in the transcript while the session lock releases quickly enough for the next message to start a new turn.

**Independent Test**: simulate an agent session that emits `EventResult` but whose `Send` call remains blocked; verify `/stop` releases `core.Session.busy` within seconds without waiting for `Send`.

**Acceptance Scenarios**:

1. **Given** a session is busy and its event loop is waiting for agent send completion after delivering a result, **When** the operator sends `/stop`, **Then** the event loop observes the stop signal and releases the session lock without waiting for that send to return.
2. **Given** `/cancel` or `/interrupt` is sent, **When** command matching runs, **Then** the command maps to the same stop behavior as `/stop`.
3. **Given** Discord session control is enabled, **When** the operator sends `!stop`, `!cancel`, or `!interrupt`, **Then** the platform closes the Discord session gate and dispatches `/stop` to the engine.

### User Story 2 - Queued messages do not replay after an interrupt (Priority: P1)

As the operator, when I interrupt a stuck session, messages that queued behind the stuck turn should not be replayed into a newly created turn without explicit user intent.

**Independent Test**: queue messages behind a running state, stop it, and verify pending queue entries are drained with reset notifications.

**Acceptance Scenarios**:

1. **Given** pending messages exist for the busy session, **When** interrupt fires, **Then** cc-connect sends reset/error notifications for those queued contexts.
2. **Given** the operator sends a new prompt after the stop acknowledgement, **When** the lock has released, **Then** it starts as a new turn rather than consuming stale queued content.

### User Story 3 - Pilot transcript shows explicit operator cancellation (Priority: P2)

As a Phase 3 reviewer, I can inspect the transcript and tell that the operator cancelled a stuck turn instead of waiting for the 2h idle timeout.

**Independent Test**: run a stop command during a simulated stuck turn and verify the platform receives the execution-stopped acknowledgement.

## Requirements

### Functional Requirements

- **FR-001**: cc-connect MUST treat `/stop`, `/cancel`, and `/interrupt` as equivalent interrupt commands for the current session key.
- **FR-002**: Discord MUST normalize `!stop`, `!cancel`, and `!interrupt` to `/stop` when session controls are enabled.
- **FR-003**: Interrupt MUST release `core.Session.busy` without waiting for a blocked `AgentSession.Send` completion after `EventResult`.
- **FR-004**: Interrupt MUST close or detach the active `AgentSession` asynchronously so the acknowledgement path does not wait on agent process shutdown.
- **FR-005**: Interrupt MUST drop pending queued messages with explicit reset/error notifications rather than replaying stale content into a post-interrupt turn.
- **FR-006**: Interrupt MUST surface a cancel acknowledgement in the platform transcript using the existing execution-stopped message or a semantically equivalent localized message.
- **FR-007**: Idle timeout MUST remain as a fallback, but the primary recovery path for operator-visible stuck sessions MUST be the explicit interrupt command.
- **FR-008**: The regression test MUST cover the root-cause shape from this slice: result emitted, send completion blocked, stop command releases lock within seconds.
- **FR-009**: The implementation MUST preserve existing queue behavior for normal busy sessions where no interrupt is issued.
- **FR-010**: The implementation MUST preserve per-session-key scope in multi-agent / multi-workspace contexts; an interrupt for one session key MUST NOT stop another peer's session.

### Key Entities

- **Session lock**: `core.Session.busy`, set by `TryLock()` and released by `Unlock()` / `UnlockWithoutUpdate()`.
- **Interactive state**: `core.interactiveState`, the per-session engine state containing `agentSession`, stop signal, pending permission, and queued messages.
- **Pending send**: the asynchronous completion channel wrapping `AgentSession.Send`. This was the root-cause wait point made interruptible in this slice.
- **Interrupt command**: `/stop` and aliases `/cancel` / `/interrupt`; Discord bang shorthands normalize to `/stop`.

## Success Criteria

- **SC-001**: Regression test proves `/stop` releases a stuck session lock in under 2 seconds when `AgentSession.Send` is still blocked after `EventResult`.
- **SC-002**: Existing stop behavior still acknowledges with `MsgExecutionStopped` and does not wait for slow agent process close.
- **SC-003**: Targeted core and Discord tests pass.
- **SC-004**: Upstream `cc-connect#3` can be closed with a cross-reference to the merged fix.

## Dependencies

- `design/poc.md` Phase 1 interrupt path deliverable.
- `design/architecture.md` Layer 1 hard interrupt / recovery primitive.
- Existing cc-connect queueing and `/stop` command implementation in `cc-connect/core/engine.go`.
- PC-67 reply-to context is adjacent but not a blocking dependency; this slice does not change reply-to rendering.
