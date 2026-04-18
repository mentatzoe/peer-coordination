# Quickstart: Transport MVP

## Purpose

This quickstart describes how to use the narrowed Transport MVP spec as the
source of truth for the Codex-owned routing and interrupt slice.

## Read in this order

1. `spec.md` — active scope, clarified boundaries, and success criteria
2. `plan.md` — technical context and constitution check
3. `research.md` — narrowed design decisions and rejected alternatives
4. `data-model.md` — entities and routing/interrupt state
5. `contracts/pilot-channel-contract.md` — operator-visible behavior contract

## Use this plan to prepare implementation work

1. Confirm the implementation target is still `mentatzoe/cc-connect`.
2. Limit implementation planning to:
   - designated pilot-channel fanout
   - self-loop suppression
   - `!stop` / `!resume` semantics, including suppression of other
     transport-mediated side effects
3. Keep these out of scope for `001` planning:
   - channel policy declaration (`002`)
   - reaction emission (`003`)
   - approval-via-react
   - pinned-rules ingestion
4. Generate `tasks.md` only after this narrowed plan is reviewed and accepted.

## Pilot readiness checks

Before declaring the `001` slice ready for implementation handoff:

1. The designated pilot channel fans out qualifying ordinary messages to all
   admitted peers.
2. Non-pilot channels keep their existing routing behavior.
3. An agent never re-triggers itself from its own outbound pilot-channel
   message.
4. `!stop` suppresses not-yet-sent outbound messages and other transport-
   mediated side effects until explicit `!resume`.
5. Transport does not introduce first-responder locking or peer arbitration.
