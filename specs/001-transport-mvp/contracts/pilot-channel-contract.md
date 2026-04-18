# Contract: Pilot Channel Behavior

## Scope

This contract defines the operator-visible behavior for the Transport MVP in the
first open-floor pilot channel.

## Channel Mode Contract

- The pilot channel can be configured for `open-floor` mode.
- In `open-floor` mode, ordinary operator messages are eligible for agent
  responses without explicit mentions.
- Channels outside the pilot configuration continue to behave according to their
  declared mode, including mention-only behavior where applicable.

## Interrupt Contract

- `!stop` is a channel-wide hard interrupt.
- After `!stop`, further outbound agent activity in that channel is suppressed
  until `!resume`.
- `!resume` is explicit; the channel does not auto-resume.

## Reaction Contract

- An agent can add a reaction to a target message as a low-noise acknowledgment
  or workflow signal.
- A state-changing proposal can remain pending until the configured approval
  reaction appears on the proposal message.
- Approval is tied to the proposal message being approved, not to ambient
  channel state.

## Pinned Rules Contract

- At session start, the channel's pinned rules are made available to the new
  session as startup context.
- If no pinned rules exist, session startup still succeeds.
- Updated pins affect later sessions rather than retroactively mutating already
  running session state.

## Boundary Contract

- Transport enforces safety and explicit routing mechanics such as hard
  interrupt and self-loop avoidance.
- Detailed coordination heuristics remain spec-level and policy-level guidance,
  not a mandatory transport handshake protocol.
