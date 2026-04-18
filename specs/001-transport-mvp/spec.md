# Feature Specification: Transport MVP

**Feature Branch**: `001-transport-mvp`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "Specify the Transport MVP for peer coordination, covering open-floor mode, channel-wide stop/resume, agent-initiated emoji reacts, approval-via-react, pinned-rules ingestion, and the governance boundary that heuristics remain spec-level while preserving Principle VI."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the Open-Floor Pilot Safely (Priority: P1)

As the operator, I want a transport mode where two peer agents can both
participate in one pilot channel without constant re-mentioning, while still
retaining a hard channel-wide stop control, so the first open-floor pilot is
both useful and safe.

**Why this priority**: Open-floor participation plus hard interrupt support is
the minimum slice that turns "two bots in one channel" into an actual
peer-coordination pilot.

**Independent Test**: Can be fully tested by enabling the pilot mode for one
channel, letting both agents observe and answer channel traffic, then verifying
that `!stop` halts channel activity and `!resume` restores it.

**Acceptance Scenarios**:

1. **Given** a channel configured for open-floor mode, **When** an operator
   posts an ordinary message without mentioning a bot, **Then** either eligible
   agent may reply in that channel without additional routing intervention.
2. **Given** an open-floor channel with active agent sessions, **When** the
   operator sends `!stop`, **Then** outbound agent activity in that channel is
   suspended until the operator explicitly sends `!resume`.
3. **Given** an agent's own prior outbound message in an open-floor channel,
   **When** transport routing evaluates that message for delivery, **Then** the
   same agent is not triggered by its own output.

---

### User Story 2 - Approve and Acknowledge with Reactions (Priority: P2)

As the operator, I want agents to acknowledge and await approval through emoji
reactions instead of extra text messages, so channel coordination stays legible
and low-noise.

**Why this priority**: Reaction support is the smallest usable surface for both
acknowledgment and approval gating, and it keeps the pilot from collapsing into
ack-loop chatter.

**Independent Test**: Can be fully tested by having an agent react to a
message, propose a state-changing action, wait for an approval reaction, and
then proceed only after the required approval appears.

**Acceptance Scenarios**:

1. **Given** an agent session with permission to react, **When** the agent
   needs to acknowledge a message without substantive text, **Then** it can add
   a reaction to the target message.
2. **Given** an agent has proposed a state-changing action that requires human
   approval, **When** the required approval reaction has not been applied,
   **Then** the action remains blocked.
3. **Given** an approval-gated action is pending, **When** the operator adds
   the configured approval reaction to the proposal message, **Then** the agent
   may proceed with the previously proposed action.

---

### User Story 3 - Apply Channel Rules from Pinned Context (Priority: P3)

As the operator, I want channel-pinned rules to be injected into agent session
context automatically, so channel-specific operating rules can change without
editing agent prompts by hand.

**Why this priority**: Pinned-rules ingestion makes channel policy portable and
visible, but it is less foundational than open-floor routing and stop/resume.

**Independent Test**: Can be fully tested by pinning a rules message in a
channel, starting a fresh agent session, and verifying that the session sees
the pinned rules as part of its initial channel context.

**Acceptance Scenarios**:

1. **Given** a channel with one or more pinned rules messages, **When** a new
   agent session begins for that channel, **Then** the pinned rules are made
   available in session context before the agent responds.
2. **Given** a channel with no pinned rules messages, **When** a new session
   begins, **Then** session startup still succeeds without injected rule text.
3. **Given** pinned rules change between sessions, **When** a later session
   starts, **Then** the later session receives the updated pinned rules rather
   than stale prior content.

### Edge Cases

- What happens when `!stop` is issued while one or more agent actions are
  already in flight?
- How does the system behave when the transport can add reactions but cannot
  observe approval reactions reliably?
- What happens when multiple pinned messages exist and their ordering matters?
- How does open-floor routing behave in channels that are not explicitly marked
  for pilot behavior?
- What happens when an approval reaction is added by someone other than the
  authorized operator?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support a channel-scoped open-floor mode in which
  eligible agents may respond to ordinary channel messages without explicit
  mentions.
- **FR-002**: The system MUST preserve mention-only behavior for channels that
  are not configured for open-floor mode.
- **FR-003**: The system MUST prevent an agent from being triggered by its own
  outbound message in an open-floor channel.
- **FR-004**: The system MUST support a channel-wide hard interrupt activated by
  `!stop` and released only by explicit `!resume`.
- **FR-005**: The system MUST attempt to halt or suppress in-flight agent
  activity in the stopped channel as part of the hard-interrupt behavior.
- **FR-006**: The system MUST allow an agent session to add an emoji reaction to
  a specific message.
- **FR-007**: The system MUST allow an agent session to detect configured
  approval reactions on a specific proposal message.
- **FR-008**: The system MUST support approval-gated actions that remain blocked
  until the configured human approval reaction is present.
- **FR-009**: The system MUST ingest pinned rules from a channel at session
  start and make that content available in the session context.
- **FR-010**: The system MUST continue to start a session successfully when a
  channel has no pinned rules.
- **FR-011**: The system MUST keep transport concerns at the transport layer and
  MUST NOT encode the full coordination heuristics as hard transport rules,
  except for explicit safety or self-loop constraints.
- **FR-012**: The system MUST preserve Principle VI from the constitution by
  leaving acknowledgment style, turn-taking, and most loop-management behavior
  to follow-on operational specs rather than hard-coding them here.
- **FR-013**: The system MUST support the first live pilot with two peer agents
  in one designated pilot channel.

### Key Entities *(include if feature involves data)*

- **Channel Mode**: The declared operating mode for a channel, such as
  mention-only or open-floor.
- **Interrupt State**: The current stopped or resumed state for a channel,
  including whether outbound agent activity is allowed.
- **Proposal Message**: An agent-authored message that requests operator
  approval before a state-changing action may proceed.
- **Approval Reaction**: A configured emoji reaction applied by the operator to
  signal approval for a pending proposal message.
- **Pinned Rule Context**: The set of pinned channel rules injected into an
  agent session when that session begins.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In the pilot channel, both peer agents can participate in
  open-floor mode without requiring explicit mentions on ordinary operator
  messages.
- **SC-002**: `!stop` suppresses further outbound agent activity in the target
  channel until `!resume` is issued, with no unintended auto-resume behavior.
- **SC-003**: Approval-gated actions do not execute before the configured
  approval reaction is observed on the proposal message.
- **SC-004**: A fresh session in a channel with pinned rules starts with those
  rules available in context without manual prompt editing.
- **SC-005**: The MVP can be piloted without hard-coding the full coordination
  heuristics into transport logic, leaving those heuristics to follow-on specs.

## Assumptions

- The first implementation target for this specification is the
  `mentatzoe/cc-connect` transport repository.
- The initial pilot uses two peer agents in one designated pilot channel rather
  than generalized multi-agent rollout across all channels.
- The operator remains the approval authority for state-changing actions in the
  pilot environment.
- The detailed coordination heuristics already captured in the scratchpad will
  be carried into the Transport MVP implementation planning and/or a follow-on
  operational spec rather than reintroduced as transport mandates here.
