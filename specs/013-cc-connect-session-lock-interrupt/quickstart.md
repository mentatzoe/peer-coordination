# Quickstart: Verify cc-connect Session-Lock Interrupt

## Targeted Regression

Run from `cc-connect/`:

```bash
go test ./core -run 'TestCmdStop_ReleasesSessionLockWhenSendDoesNotReturnAfterResult|TestCmdStop_ReturnsWhileCloseBlockedAndStopsEventLoop'
```

Expected: both tests pass. The new regression simulates the root-cause shape from this slice: `EventResult` has been delivered, `AgentSession.Send` remains blocked, and `/stop` must release `Session.busy` without waiting for send completion.

## Broader Test Set

Run from `cc-connect/`:

```bash
go test ./core ./platform/discord
```

Before PR, run:

```bash
go test ./...
```

## Manual Pilot Check

1. Start cc-connect with Discord session controls enabled.
2. Send a long-running prompt to a peer bot.
3. Send `/stop` or `!stop` as the operator while the turn is still active.
4. Confirm the transcript shows the execution-stopped acknowledgement.
5. Send a new prompt.
6. Confirm the new prompt is processed without waiting for the 2h idle timeout.

Alias checks:

- `/cancel` and `/interrupt` should behave like `/stop`.
- `!cancel` and `!interrupt` should behave like `!stop` on Discord.
