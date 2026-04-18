# Feature Specification: Transport MVP

**Feature Branch**: `001-transport-mvp`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Specify only the Transport MVP slice assigned to Vigil/Codex after the designation split: designated open-floor pilot routing, self-loop suppression, and channel-scoped hard interrupt semantics. Channel policy declaration, agent-initiated reactions, approval-via-react, and pinned-rules ingestion are separate scopes."
**Owner**: Vigil (Codex)

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
2. **Given** a channel that is not the designated pilot channel, **When** the
   operator posts the same ordinary non-mentioned message, **Then** transport
   does not grant open-floor behavior merely because the pilot exists.
3. **Given** an agent's own prior outbound message in the pilot channel,
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

- What happens when `!stop` is issued while one or more agent actions are
  already in flight?
- What happens when both peer agents are eligible to respond to the same
  operator message in the pilot channel?
- What happens when the designated pilot channel is reconfigured or removed
  while a session is already active there?
- What happens when a user who is not the operator attempts to issue `!stop`
  or `!resume`?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support one designated pilot channel in which
  admitted peer agents may respond to ordinary channel messages without
  explicit mentions.
- **FR-002**: The system MUST preserve the existing non-pilot routing behavior
  for channels outside the designated pilot channel.
- **FR-003**: The system MUST prevent an agent from being triggered by its own
  outbound message in the designated pilot channel.
- **FR-004**: The system MUST support a channel-scoped hard interrupt for the
  designated pilot channel, activated by `!stop`.
- **FR-005**: The system MUST require an explicit `!resume` to restore outbound
  agent activity after the pilot channel has been stopped.
- **FR-006**: The system MUST attempt to halt or suppress in-flight outbound
  agent activity in the pilot channel when `!stop` is issued.
- **FR-007**: The system MUST keep this feature scoped to transport routing and
  safety semantics; it MUST NOT absorb channel policy declaration, reaction
  workflows, approval gating, or pinned-rules ingestion.
- **FR-008**: The system MUST preserve Principle VI by leaving conversational
  turn-taking and reaction heuristics to their designated follow-on specs
  rather than hard-coding them here.

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
- **SC-002**: `!stop` suppresses further outbound agent activity in the
  designated pilot channel until explicit `!resume` is issued.
- **SC-003**: An agent never re-triggers itself from its own outbound pilot
  channel message.
- **SC-004**: The feature remains cleanly bounded to transport routing and
  safety semantics, with reaction emission, approval-via-react, pinned-rules
  ingestion, and channel policy declaration left in their designated specs.

## Assumptions

- The first implementation target for this specification is the
  `mentatzoe/cc-connect` transport repository.
- The pilot initially involves two peer agents in one designated channel.
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
