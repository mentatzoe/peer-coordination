# Research: Transport MVP

## Decision 1: Keep `001` limited to routing and interrupt semantics

- **Decision**: Limit active `001` to designated pilot-channel open-floor
  routing, self-loop suppression, and channel-scoped hard interrupt behavior.
- **Rationale**: The designation split is already embodied in sibling specs:
  `002` owns channel policy/presence and `003` owns agent-initiated reaction
  emission. Keeping `001` narrow prevents scope drift and preserves review
  boundaries.
- **Alternatives considered**:
  - Re-expand `001` to include reactions and pinned rules: rejected because it
    recreates the boundary violation already corrected on this branch.
  - Leave `001` too minimal to mention fanout or interrupt semantics: rejected
    because those are the core transport mechanics this spec actually owns.

## Decision 2: Fan out pilot-channel messages to all admitted peers

- **Decision**: Fan out each qualifying ordinary message in the designated
  pilot channel to all admitted peer agents.
- **Rationale**: Transport should determine eligibility, not social turn-taking.
  Fanout preserves the governance boundary by leaving actual reply selection to
  higher-level coordination heuristics.
- **Alternatives considered**:
  - Transport chooses a single peer: rejected because it smuggles arbitration
    policy into transport.
  - First-responder locking: rejected because it is coordination policy, not
    transport plumbing.

## Decision 3: Treat `!stop` as immediate best-effort suppression

- **Decision**: `!stop` suppresses not-yet-sent outbound messages and other
  transport-mediated side effects immediately, while already-sent partial output
  remains visible.
- **Rationale**: This is the strongest safety behavior transport can enforce
  without pretending it can retract delivered side effects.
- **Alternatives considered**:
  - Let the current turn finish: rejected because it weakens the operator's
    safety interrupt in the first live pilot.
  - Treat `!stop` as advisory only: rejected because it undermines Principle IV
    and the explicit safety role of the operator.

## Decision 4: Keep interrupt authority operator-centered

- **Decision**: Allow `!stop` / `!resume` only from the operator or an explicit
  allowlisted delegate; the current pilot defaults effectively to the operator
  alone.
- **Rationale**: This keeps safety authority legible while permitting a future
  expansion path that does not require rethinking the spec.
- **Alternatives considered**:
  - Any admitted participant can interrupt: rejected because it broadens the
    safety surface before the channel-policy spec defines broader authority
    semantics.
  - Platform moderators only: rejected because it couples interrupt authority to
    platform permissions rather than peer-coordination policy.

## Decision 5: Apply designation changes to future routing only

- **Decision**: If the designated pilot channel changes or is removed, the new
  designation applies immediately to future routing decisions, but already-
  running turns are not retroactively rewritten beyond existing `!stop`
  behavior.
- **Rationale**: This gives policy changes immediate effect without creating
  hidden turn mutation semantics.
- **Alternatives considered**:
  - Let sessions keep the old designation until completion: rejected because it
    delays operator intent.
  - Auto-hard-stop on designation change: rejected because it conflates policy
    change with explicit interrupt.
