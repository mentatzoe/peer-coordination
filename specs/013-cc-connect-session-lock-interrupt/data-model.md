# Data Model: cc-connect Session-Lock Interrupt

This slice does not add persisted data. The entities below are runtime concepts already present in cc-connect.

## Session

- **Source**: `cc-connect/core/session.go`
- **Fields used**:
  - `busy`: in-memory lock flag; not persisted.
  - `UpdatedAt`: touched by normal unlock.
- **Invariant**: interrupt must cause the active event loop to release `busy` through existing unlock flow.

## Interactive State

- **Source**: `cc-connect/core/engine.go`
- **Fields used**:
  - `agentSession`: process/session bridge to the agent harness.
  - `stopCh` / `stopped`: operator interrupt signal.
  - `pending`: pending permission request.
  - `pendingMessages`: queued inbound messages waiting for the current turn to finish.
- **Invariant**: interrupt marks the state stopped, resolves pending permission, drops pending messages, and closes the agent asynchronously.

## Pending Send

- **Source**: local `sendDone <-chan error` in `processInteractiveEvents`.
- **Meaning**: completion channel for the goroutine running `AgentSession.Send`.
- **Invariant**: waits on this channel after `EventResult` must also select on stop and engine cancellation.

## Interrupt Command

- **Canonical command**: `/stop`
- **Aliases**: `/cancel`, `/interrupt`
- **Discord bang controls**: `!stop`, `!cancel`, `!interrupt` -> `/stop`
- **Observable output**: execution-stopped acknowledgement in the platform transcript.
