# Research: Transport MVP

## Decision 1: Keep the MVP scoped to the five pilot-blocking transport capabilities

- **Decision**: Scope the MVP to open-floor mode, `!stop` / `!resume`,
  agent-initiated emoji reacts, approval-via-react, and pinned-rules
  ingestion.
- **Rationale**: These are the only capabilities explicitly identified as
  blocking the first open-floor pilot.
- **Alternatives considered**:
  - Include channel policy, presence, and workspace binding in the MVP: rejected
    because those concerns already have later roadmap slots.
  - Keep the MVP informal in the scratchpad only: rejected because later task
    generation and issue tracking need a durable feature spec.

## Decision 2: Preserve the constitutional boundary by leaving heuristics as spec-level policy

- **Decision**: Keep operator-facing coordination heuristics and most
  loop-management choices out of transport mandates, except for explicit safety
  and self-loop constraints.
- **Rationale**: The constitution now explicitly requires human-legible
  coordination and rejects collapsing all social heuristics into transport
  enforcement.
- **Alternatives considered**:
  - Reintroduce the full heuristics as transport requirements: rejected because
    that would undo the governance/spec split restored in `v1.1.1`.

## Decision 3: Treat approval-via-react as transport-observable state, not prompt convention

- **Decision**: Model approval-via-react as a transport capability that can
  observe reactions on a proposal message and unblock an action only when the
  configured approval signal appears.
- **Rationale**: The operator wants low-noise, reaction-based approval in the
  pilot, and transport observation is the cleanest place to make that reliable.
- **Alternatives considered**:
  - Treat approval as text-only or prompt-only convention: rejected because it
    does not satisfy the desired reaction-based UX.

## Decision 4: Treat pinned rules as session-start context injection

- **Decision**: Pinned-rules ingestion occurs at session start and provides
  channel-specific context to the agent before the session responds.
- **Rationale**: This keeps channel policy editable by operators without
  requiring prompt rewrites or code changes for every channel rule tweak.
- **Alternatives considered**:
  - Read pinned rules lazily on every message: rejected as noisier and less
    deterministic for session initialization.
  - Keep rules only in prompts: rejected because it couples channel policy to
    agent configuration.

## Decision 5: Use a lightweight operator/channel contract document

- **Decision**: Capture the MVP external interface as a markdown contract under
  `contracts/` rather than introducing implementation-specific API schemas in
  this repo.
- **Rationale**: The repo is a governance/spec repo, so the important contract
  here is operator-visible behavior and state transitions, not code-level API
  signatures.
- **Alternatives considered**:
  - No contract artifact: rejected because task generation benefits from a
    stable interface definition.
  - Implementation-level API contracts: rejected because that belongs in the
    downstream implementation repo once technical interfaces solidify.
