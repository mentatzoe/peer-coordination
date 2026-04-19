# Research: Discord Session Controls

## Decision 1: Channel binding belongs in the Discord platform adapter

- **Why**: binding is substrate-specific. The POC wants one designated
  open-floor channel, and the current missing behavior is that the Discord
  adapter has no explicit `channel_id` gate.
- **Decision**: add an explicit Discord platform option for the bound channel
  and enforce it before dispatch in both message and slash/component paths.
- **Rejected alternative**: engine-level filtering. That would push a
  Discord-only concern into shared core logic.

## Decision 2: Session open/closed state is a transport gate

- **Why**: `design/poc.md` says the operator is the only session opener and
  that `!stop` / `!resume` are runtime controls. This is Layer 1 behavior.
- **Decision**: represent "open vs closed" as Discord runtime state keyed to
  the bound surface.
- **Rejected alternative**: infer session openness only from existing agent
  session persistence. That would let peer posts implicitly reopen sessions.

## Decision 3: Reuse existing session-manager fresh-session behavior

- **Why**: `!resume` must open a new session, not reactivate the stopped one.
  `cc-connect/core` already has primitives for creating a new logical session
  and clearing persisted agent-session IDs.
- **Decision**: reuse existing session reset/new-session patterns rather than
  adding a second session lifecycle implementation.
- **Rejected alternative**: keep one session key forever and only add a boolean
  `stopped` flag. That would make "new session" semantics too implicit.

## Decision 4: Thread isolation must remain subordinate to the bound surface

- **Why**: current Discord support can create/use threads as session boundaries.
  Channel binding cannot accidentally be bypassed by moving into an unrelated
  thread.
- **Decision**: if thread isolation is enabled, only the configured bound
  channel and the threads rooted under it are eligible for dispatch.
- **Rejected alternative**: exact-channel-only matching with no thread-parent
  allowance. That would break the existing thread-isolation feature.

## Decision 5: Transcript export stays out of scope

- **Why**: transcript export is the next transport slice and would enlarge this
  one substantially.
- **Decision**: this slice only has to preserve coherent runtime behavior and
  stable channel/session boundaries that transcript export can later consume.
