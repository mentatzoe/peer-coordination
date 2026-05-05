# Research: cc-connect Session-Lock Interrupt

## Decision R1: Root cause is a cc-connect engine wait, not Discord

**Decision**: The lock that blocks later messages is `core.Session.busy`. The failure mode fixed here is an uninterruptible post-result wait on `pendingSend` inside `processInteractiveEvents`.

**Rationale**: `handleMessage` queues messages when `Session.TryLock()` fails. `processInteractiveMessageWith` releases the lock only after `processInteractiveEvents` returns and pending messages are drained. In the result path, the event loop can leave the main select and block on `<-pendingSend>` after the visible result is already processed. That wait did not select on `state.stopSignal()`, so `/stop` could mark the state stopped without releasing `Session.busy`.

**Alternatives considered**:

- Force-unlock the `Session` directly in `cmdStop`: rejected as the primary fix because it can allow a new turn while the old event loop is still mutating response state. The narrower fix makes the old loop exit through its existing cleanup path.
- Shorten the 2h idle timeout: rejected as primary recovery. It improves worst-case wait but leaves operator interrupt non-deterministic.

## Decision R2: `/stop` is canonical; `/cancel` and `/interrupt` are aliases

**Decision**: Keep `/stop` as the canonical command and add `/cancel` / `/interrupt` aliases. Discord bang controls `!cancel` and `!interrupt` normalize to `/stop`.

**Rationale**: Existing docs and i18n already expose `/stop`; adding aliases satisfies operator vocabulary without multiplying command implementations or transcript semantics.

## Decision R3: Queued messages are dropped on interrupt

**Decision**: Preserve existing stop behavior: pending queued messages receive reset/error notifications and are not replayed after interrupt.

**Rationale**: Replaying messages after an operator cancel could apply stale context to a fresh agent process. A new post-cancel prompt should be explicit.

## Decision R4: Cancel acknowledgement stays the existing execution-stopped message

**Decision**: Use `MsgExecutionStopped` for the transcript acknowledgement.

**Rationale**: It is already localized and covered by stop tests. The important observable is an explicit cancel ack in the transcript; new strings are unnecessary for this slice.
