# Feature Specification: Agent-Initiated Emoji Reactions

**Feature Branch**: `003-agent-initiated-reactions`
**Created**: 2026-04-18
**Status**: Draft
**Input**: User description: "Transport primitive that lets an agent session add an emoji reaction to a specific channel message, as a lightweight signal that does not require a text reply. This is MVP item 3 from the peer-coordination agreement. Atomic scope: the emit side only — observation of reactions (including approval-via-react workflows) lives in a separate spec."
**Owner**: Dalgos (Claude), per MVP implementation assignment.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Signal lightweight state via emoji, not text (Priority: P1)

As the operator, I want agents to be able to add emoji reactions to
specific channel messages in response to what they see, so that low-
content signals — "seen", "thinking", "done", "disagree" — appear as
reactions on the triggering message instead of new text messages that
lengthen the channel.

**Why this priority**: This is the atomic primitive. Every downstream
reaction-based workflow — acknowledgment patterns, approval-via-react,
observed coordination heuristics from the operational spec — depends on
agents being able to emit reactions in the first place. Without it, text
is the only signalling medium agents have.

**Independent Test**: Can be fully tested by having an agent session
receive a message in a channel where it has reaction permission, then
having the agent emit a reaction, and confirming the reaction appears on
the target message with the agent's identity as the reacting user.

**Acceptance Scenarios**:

1. **Given** an agent session and a visible channel message, **When** the
   agent requests a reaction with a valid emoji (unicode or a guild custom
   emoji it has access to) on that message, **Then** the reaction appears
   on the target message attributed to the agent's identity.
2. **Given** an agent has already added the same reaction to the same
   message, **When** the agent requests the same reaction again, **Then**
   the system does not create a duplicate reaction and does not error out
   noisily.
3. **Given** an agent is about to emit a reaction, **When** the request
   reaches the transport layer, **Then** the agent does not block its own
   session on the react succeeding — reactions are a signal, not a
   synchronization primitive.

### Edge Cases

- What happens when the target message has been deleted between the agent
  deciding to react and the reaction being emitted? Expected behavior is
  a logged failure, not a raised exception into agent logic.
- What happens when the agent lacks permission to add reactions in the
  channel (platform-level permission missing)? Expected behavior is a
  logged failure and a documented hint to the operator; the session
  continues.
- What happens when the agent requests a reaction with an emoji that is
  not a valid unicode emoji and not a guild custom emoji the bot can use?
  Expected behavior is a logged failure with the offending emoji surfaced
  in the error detail.
- What happens when the platform rate-limits reaction emissions? Expected
  behavior is bounded retry with backoff; eventual drop of the reaction
  is acceptable if the channel is itself saturated.
- What happens when the agent reacts to its own earlier message (e.g.,
  marking a proposal as "done")? Expected behavior is allowed — the agent
  is a valid reacting user on any message it can see.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose to agent sessions an operation that
  takes (channel identifier, message identifier, emoji) and attempts to
  add that emoji as a reaction to the identified message.
- **FR-002**: The system MUST accept both unicode emoji (as direct
  characters) and guild custom emoji (in the platform-native reference
  form) as valid inputs.
- **FR-003**: The system MUST record the reaction under the agent's own
  platform identity, not spoofed as the operator or another agent.
- **FR-004**: The system MUST treat duplicate reaction requests (same
  agent, same message, same emoji) as idempotent: no duplicate visible
  reaction, no hard error.
- **FR-005**: The system MUST NOT block or fail an agent session because
  a reaction emission fails; failures MUST be reported through the
  session's log/error surface without interrupting in-flight agent work.
- **FR-006**: The system MUST apply platform rate-limit handling
  (backoff, bounded retry) internally to reaction emissions; the agent
  session MUST NOT be expected to implement rate-limit logic on top of
  this primitive.
- **FR-007**: The system MUST remain scoped to emission only. Observing
  reactions added by other parties (including the operator) is out of
  scope for this spec and belongs in the separate Approval-via-Reaction
  Spec covering MVP item 4.
- **FR-008**: The system MUST preserve constitution Principle VI: this
  primitive is the atomic mechanism; it does NOT itself encode
  coordination heuristics like "react with 👀 on inbound" or "react with
  ✅ to approve". Those heuristics are operational policy and live in
  follow-on specs.

### Key Entities

- **Reaction Request**: The tuple an agent session emits — (channel
  identifier, message identifier, emoji reference) — representing the
  intent to add a reaction. A request may succeed (reaction visible on
  the target message), silently succeed (no-op on duplicate), or fail
  (with a reason surfaced to the session log).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An agent can emit a reaction to a message with a single
  call; the reaction is visible on the target message within the
  platform's standard reaction propagation time.
- **SC-002**: Reaction emission failures (deleted target, permission
  denied, invalid emoji, rate-limit saturation) surface as structured
  log/error output without interrupting the agent's session.
- **SC-003**: The spec does not encode any coordination heuristic about
  *when* to emit a reaction — heuristics remain spec-level per Principle
  VI and stay in follow-on operational specs.

## Assumptions

- The first implementation target is the `mentatzoe/cc-connect` transport
  repository's Discord adapter. The `--channels` plugin for Claude Code
  MAY adopt the same shape later; not required for this spec.
- The platform (Discord) provides a reaction API that the transport layer
  can call on behalf of an agent. Specific API details are implementation
  concerns for the plan phase, not this spec.
- The emoji palette in the peer-coordination discussion (✅ 👀 🤔 🚫 ⏸️)
  is operational policy, not a normative part of this spec. This spec
  defines what "add any reaction" means; which emoji are conventional is
  a different concern.
- The agent session determines *when* to emit a reaction based on its own
  policy or operator instructions. This spec does not attempt to constrain
  that choice beyond the per-spec invariants (Principle VI).

## Out of Scope

- Observing reactions (added by the operator, by another agent, or by
  any non-bot user). This is MVP item 4, covered in a separate spec.
- Approval-via-reaction workflows (the composite of observing reactions
  on a proposal message and gating actions on them). MVP item 4, separate
  spec.
- Pinned-rules ingestion at session start. MVP item 5, separate spec.
- Operational heuristics about *which* emoji to use for *which* signals.
  Stays in follow-on spec or agent policy.
