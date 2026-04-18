# Contract: Pilot Channel Behavior

## Scope

This contract defines the operator-visible behavior for the narrowed Transport
MVP slice in the designated pilot channel.

## Open-Floor Contract

- The designated pilot channel can run in open-floor mode for admitted peer
  agents.
- A qualifying ordinary message in that channel is fanned out to all admitted
  peers.
- Transport does not choose a single recipient and does not introduce a
  first-responder lock.

## Self-Loop Contract

- An agent is not re-triggered by its own outbound message in the designated
  pilot channel.

## Interrupt Contract

- `!stop` is a channel-scoped hard interrupt for the designated pilot channel.
- Only the operator or an explicitly allowlisted delegate may issue `!stop` or
  `!resume`.
- `!stop` suppresses not-yet-sent outbound messages and other transport-
  mediated side effects in the pilot channel.
- Already-sent partial output may remain visible.
- `!resume` is explicit; the channel does not auto-resume.
- Interrupt state is exposed through a `core`-level consumer surface so other
  transport primitives can honor `!stop` without reimplementing pilot-channel
  state lookup.

## Reconfiguration Contract

- If the designated pilot channel changes or is removed, the new designation
  applies immediately to future routing decisions.
- Already-running turns are not retroactively rewritten beyond existing
  `!stop` semantics.

## Boundary Contract

- This spec does not define channel policy declaration, reaction emission,
  approval-via-react, or pinned-rules ingestion.
- Reply overlap is handled by higher-level coordination heuristics, not by
  transport.
