# Interrupt Contract

## C1 - Operator command contract

`/stop`, `/cancel`, and `/interrupt` MUST resolve to the same command id and execute the same interrupt path. Implementations MUST NOT create separate cancel semantics for these aliases.

## C2 - Discord control contract

Discord `!stop`, `!cancel`, and `!interrupt` MUST normalize to `/stop`. If a bound session gate is enabled and the author is the operator, these controls close the gate before dispatching the stop command.

## C3 - Lock-release contract

When an interrupt is issued for an active interactive state, cc-connect MUST release the associated `Session.busy` lock without waiting for:

- `AgentSession.Send` to return after `EventResult`
- agent process `Close()` to finish
- the 2h event idle timeout

## C4 - Queue contract

Queued messages behind an interrupted turn MUST be notified as reset/error and MUST NOT be replayed into a future turn automatically.

## C5 - Transcript contract

The operator-visible platform transcript MUST include an interrupt acknowledgement. The existing localized execution-stopped message satisfies this contract.
