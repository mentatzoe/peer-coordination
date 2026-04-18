# Feature Specification: Transport MVP

**Feature Branch**: `001-transport-mvp`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Specify only the Transport MVP slice assigned to Vigil/Codex after the designation split: designated open-floor pilot routing, self-loop suppression, and channel-scoped hard interrupt semantics. Channel policy declaration, agent-initiated reactions, approval-via-react, and pinned-rules ingestion are separate scopes."
**Owner**: Vigil (Codex)

## Clarifications

### Session 2026-04-18

- Q: In open-floor mode, should transport fan out a qualifying pilot-channel message to all admitted peer agents or choose a single recipient? → A: Fan out to all admitted peer agents; reply selection stays in higher-level coordination heuristics.
- Q: Who can issue `!stop` and `!resume` for the pilot channel? → A: The operator and any explicitly allowlisted delegate; current pilot defaults to the operator alone because the server is single-user.
- Q: What should happen to in-flight work when `!stop` is issued? → A: Best-effort cancel immediately; suppress any not-yet-sent outbound messages, but leave already-sent partial output in place.
- Q: If the designated pilot channel is changed or removed while sessions are already active, how should transport behave? → A: Apply the new designation immediately to future routing decisions, but do not retroactively rewrite already-running turns.
- Q: Should transport arbitrate between peer replies once a message has been fanned out? → A: No; both peers may reply, and any overlap is handled by higher-level coordination heuristics rather than transport.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Let the Pilot Channel Run Open-Floor (Priority: P1)

As the operator, I want one designated pilot channel where admitted peer agents
can answer ordinary channel messages without constant re-mentioning, so the
first live peer-coordination pilot can behave like a shared workroom rather
than a mention-only bot lane.

**Why this priority**: This is the core transport slice assigned here. Without
open-floor routing in the designated pilot channel, the pilot cannot exercise
the peer-coordination model at all.

**Independent Test**: Configure one designated pilot channel for open-floor
operation, send an ordinary non-mentioned operator message there, and verify
that admitted peer agents are eligible to respond while the same message in a
non-pilot channel still follows that channel's existing activation behavior.

**Acceptance Scenarios**:

1. **Given** a designated pilot channel, **When** the operator posts an
   ordinary message without mentioning a bot, **Then** admitted peer agents may
   respond in that channel without additional routing intervention.
2. **Given** multiple admitted peer agents in the designated pilot channel,
   **When** the operator posts one qualifying ordinary message, **Then**
   transport fans that message out to all admitted peers rather than choosing a
   single recipient.
3. **Given** a channel that is not the designated pilot channel, **When** the
   operator posts the same ordinary non-mentioned message, **Then** transport
   does not grant open-floor behavior merely because the pilot exists.
4. **Given** an agent's own prior outbound message in the pilot channel,
   **When** transport evaluates that message for routing, **Then** the same
   agent is not triggered by its own output.

---

### User Story 2 - Halt and Resume the Pilot Channel Explicitly (Priority: P1)

As the operator, I want a channel-scoped hard interrupt for the pilot channel,
so I can stop outbound agent activity immediately and resume it only when I am
ready.

**Why this priority**: Open-floor routing without an explicit safety kill-switch
is not acceptable for a first live pilot with multiple agents in one channel.

**Independent Test**: With open-floor activity running in the designated pilot
channel, issue `!stop`, verify outbound agent activity is suppressed, then
issue `!resume` and verify normal routing returns.

**Acceptance Scenarios**:

1. **Given** an active designated pilot channel, **When** the operator sends
   `!stop`, **Then** outbound agent activity in that channel is suspended.
2. **Given** a stopped pilot channel, **When** the operator has not yet sent
   `!resume`, **Then** transport does not auto-resume on subsequent ordinary
   messages.
3. **Given** a stopped pilot channel, **When** the operator sends `!resume`,
   **Then** outbound agent activity in that channel becomes eligible again.

### Edge Cases

- What happens when a user who is not the operator or an explicitly allowlisted
  delegate attempts to issue `!stop` or `!resume`?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support one designated pilot channel in which
  admitted peer agents may respond to ordinary channel messages without
  explicit mentions.
- **FR-002**: The system MUST fan out each qualifying ordinary message in the
  designated pilot channel to all admitted peer agents, without transport
  choosing a single recipient.
- **FR-003**: The system MUST preserve the existing non-pilot routing behavior
  for channels outside the designated pilot channel.
- **FR-004**: The system MUST prevent an agent from being triggered by its own
  outbound message in the designated pilot channel.
- **FR-005**: The system MUST support a channel-scoped hard interrupt for the
  designated pilot channel, activated by `!stop`.
- **FR-006**: The system MUST require an explicit `!resume` to restore outbound
  agent activity after the pilot channel has been stopped.
- **FR-007**: The system MUST accept `!stop` and `!resume` only from the
  operator or an explicitly allowlisted delegate for the pilot channel; the
  default initial pilot configuration MAY contain only the operator.
- **FR-008**: The system MUST treat `!stop` as an immediate best-effort cancel:
  not-yet-sent outbound messages and other transport-mediated side effects in
  the pilot channel MUST be suppressed, while already-sent partial output MAY
  remain visible.
- **FR-009**: The system MUST keep this feature scoped to transport routing and
  safety semantics; it MUST NOT absorb channel policy declaration, reaction
  workflows, approval gating, or pinned-rules ingestion.
- **FR-010**: The system MUST preserve Principle VI by leaving conversational
  turn-taking and reaction heuristics to their designated follow-on specs
  rather than hard-coding them here.
- **FR-011**: If the designated pilot channel is changed or removed, the new
  designation MUST apply immediately to future routing decisions, but the
  system MUST NOT retroactively rewrite already-running turns beyond the
  existing `!stop` semantics.
- **FR-012**: The system MUST NOT introduce transport-level arbitration between
  admitted peer agents once a qualifying message has been fanned out; overlap
  in replies is left to higher-level coordination heuristics.

### Key Entities *(include if feature involves data)*

- **Designated Pilot Channel**: The single channel (or explicit channel set, if
  later generalized) where open-floor routing is enabled for the pilot.
- **Interrupt State**: The current active or stopped state for the designated
  pilot channel, including whether outbound agent activity is permitted.
- **Eligible Agent**: A peer agent that is admitted to the designated pilot
  channel and therefore may be considered for open-floor routing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In the designated pilot channel, admitted peer agents can respond
  to ordinary operator messages without requiring explicit mentions.
- **SC-002**: A qualifying ordinary message in the designated pilot channel is
  delivered to all admitted peer agents without transport choosing a single
  recipient.
- **SC-003**: `!stop` suppresses further outbound agent activity in the
  designated pilot channel until explicit `!resume` is issued.
- **SC-004**: An agent never re-triggers itself from its own outbound pilot
  channel message.
- **SC-005**: The feature remains cleanly bounded to transport routing and
  safety semantics, with reaction emission, approval-via-react, pinned-rules
  ingestion, and channel policy declaration left in their designated specs.
- **SC-006**: The system does not introduce transport-side first-responder
  locking or peer arbitration after fan-out.

## Assumptions

- The first implementation target for this specification is the
  `mentatzoe/cc-connect` transport repository.
- The pilot initially involves two peer agents in one designated channel.
- The current pilot server is effectively single-user, so the initial interrupt
  allowlist may contain only the operator even though the model allows explicit
  delegates later.
- Per-channel policy declaration (including how a channel becomes designated for
  open-floor use) is defined in the Channel Policy and Presence Spec.
- Agent-initiated emoji reaction emission is defined in the
  Agent-Initiated Emoji Reactions Spec.
- Approval-via-react and pinned-rules ingestion are separate scopes and should
  not be re-imported into this spec during clarification or planning.

## Out of Scope

- Declaring channel activation modes, verbosity, allowlists, or bot presence
- Agent-initiated emoji reaction emission
- Approval-via-react workflows or reaction observation
- Pinned-rules ingestion at session start
- Operational heuristics about when agents should reply, defer, or acknowledge
