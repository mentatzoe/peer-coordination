# Feature Specification: Agent-Initiated Emoji Reactions

**Feature Branch**: `003-agent-initiated-reactions`
**Created**: 2026-04-18
**Status**: Draft
**Input**: User description: "Transport primitive that lets an agent session add an emoji reaction to a specific channel message, as a lightweight signal that does not require a text reply. This is MVP item 3 from the peer-coordination agreement. Atomic scope: the emit side only — observation of reactions (including approval-via-react workflows) lives in a separate spec."
**Owner**: Dalgos (Claude), per MVP implementation assignment.

## Clarifications

### Session 2026-04-18

- **Q:** Should reaction removal be in scope for this spec?
  **A:** Yes. Removal is in scope alongside emission (Option A). Same primitive direction, same permission model, same failure modes; splitting add/remove would create overhead without design benefit, and several downstream heuristics (e.g. "clear 👀 after done") require removal.
- **Q:** When `!stop` is active in a channel, should reaction emissions and removals also be suppressed?
  **A:** Yes. `!stop` suppresses ALL outbound transport activity in the channel, including reactions (Option A). Consistent mental model: stopped means silent across all outbound channels.
- **Q:** How should reaction-operation failures be surfaced to the operator?
  **A:** Structured log events plus an emitted metric (Option D). Structured log event at WARN level with fields `{action, channel_id, message_id, emoji, reason}` so failures are greppable and pipe-friendly. Additionally, a failure-rate metric per channel and per agent so trends are monitorable without reading logs.
- **Q:** Should the spec define a restricted emoji palette agents are allowed to emit, or stay permissive?
  **A:** Stay permissive (Option A). Any valid emoji is allowed at transport level. Palette conventions (✅👀🤔🚫⏸️) are operational policy per constitution Principle VI and live in follow-on operational specs, not here.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Signal lightweight state via emoji (Priority: P1)

As the operator, I want agents to be able to add emoji reactions to
specific channel messages in response to what they see, so that low-
content signals — "seen", "thinking", "done", "disagree" — appear as
reactions on the triggering message instead of new text messages that
lengthen the channel.

**Why this priority**: This is the atomic emit primitive. Every
downstream reaction-based workflow — acknowledgment patterns,
approval-via-react, observed coordination heuristics from the operational
spec — depends on agents being able to emit reactions in the first place.
Without it, text is the only signalling medium agents have.

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

---

### User Story 2 - Revoke a prior reaction signal (Priority: P1)

As the operator, I want agents to be able to remove their own previously
added emoji reactions from specific channel messages, so that signals
like "thinking" (👀) can be cleared when the agent moves to a final
state — without leaving stale state in the channel.

**Why this priority**: Add and remove are symmetric primitives for
managing the agent's own reaction state. Several downstream heuristics
(clear 👀 once done, clear 🤔 once decided) become impossible if removal
isn't supported at this layer. Same implementation complexity as add;
grouping them in one spec avoids an artificial atomic split.

**Independent Test**: Can be fully tested by having an agent emit a
reaction on a message, then having the agent request removal of that
reaction, and confirming the reaction no longer appears on the target
message attributed to the agent's identity.

**Acceptance Scenarios**:

1. **Given** an agent has previously added a reaction to a message,
   **When** the agent requests removal of that reaction, **Then** the
   reaction attributed to the agent is no longer visible on the message.
2. **Given** an agent has NOT added a reaction to a message, **When** the
   agent requests removal of that reaction anyway, **Then** the system
   treats the request as idempotent — no error, no state change.
3. **Given** a reaction was added by a user other than the requesting
   agent, **When** the agent requests removal of that reaction, **Then**
   the system does not remove it; agents may only remove their own
   reactions via this primitive.

### Edge Cases

- What happens when the target message has been deleted between the agent
  deciding to react (or un-react) and the request being emitted? Expected
  behavior is a logged failure, not a raised exception into agent logic.
  Applies symmetrically to add and remove.
- What happens when the agent lacks permission to add reactions in the
  channel (platform-level permission missing)? Expected behavior is a
  logged failure and a documented hint to the operator; the session
  continues. Applies symmetrically to add and remove.
- What happens when the agent requests a reaction with an emoji that is
  not a valid unicode emoji and not a guild custom emoji the bot can use?
  Expected behavior is a logged failure with the offending emoji surfaced
  in the error detail.
- What happens when the platform rate-limits reaction emissions or
  removals? Expected behavior is bounded retry with backoff; eventual
  drop of the request is acceptable if the channel is itself saturated.
- What happens when the agent reacts to (or un-reacts from) its own
  earlier message? Expected behavior is allowed — the agent is a valid
  reacting user on any message it can see, including messages it
  authored.
- What happens when the agent requests removal of a reaction it never
  added? Expected behavior is idempotent no-op — no error, no state
  change (per US2 acceptance scenario 2).
- What happens when the agent requests removal of a reaction added by a
  different user? Expected behavior is rejected — agents may only manage
  their own reactions via this primitive. Moderation-style mass-removal
  is explicitly out of scope.
- What happens when a reaction add or remove is attempted while the
  channel is in `!stop` state? Expected behavior is suppressed at the
  transport layer (FR-012), with the request logged as a no-op-due-to-
  stop. Whether suppressed requests queue-and-fire on `!resume` or drop
  silently is a plan-phase decision.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose to agent sessions an operation that
  takes (channel identifier, message identifier, emoji) and attempts to
  add that emoji as a reaction to the identified message.
- **FR-002**: The system MUST expose to agent sessions an operation that
  takes (channel identifier, message identifier, emoji) and attempts to
  remove that emoji reaction from the identified message, scoped to the
  requesting agent's own prior reaction.
- **FR-003**: The system MUST accept both unicode emoji (as direct
  characters) and guild custom emoji (in the platform-native reference
  form) as valid inputs for both add and remove operations. The
  transport layer MUST remain permissive: any emoji the platform itself
  accepts is allowed here. Restricted palettes, if operators want them,
  are operational policy and belong in follow-on specs, consistent with
  Principle VI.
- **FR-004**: The system MUST record the reaction under the agent's own
  platform identity, not spoofed as the operator or another agent.
- **FR-005**: The system MUST scope reaction removal to the requesting
  agent's own previously added reactions. Requests to remove reactions
  added by other users MUST NOT succeed via this primitive, even when the
  bot holds platform-level permission to manage other users' reactions.
- **FR-006**: The system MUST treat duplicate add requests (same agent,
  same message, same emoji, reaction already present) as idempotent: no
  duplicate visible reaction, no hard error.
- **FR-007**: The system MUST treat remove requests for reactions the
  agent never added (or has already removed) as idempotent: no error, no
  state change.
- **FR-008**: The system MUST NOT block or fail an agent session because
  a reaction add or remove fails; failures MUST be reported through a
  structured log event at WARN level with fields `{action, channel_id,
  message_id, emoji, reason}`, without interrupting in-flight agent work.
- **FR-008a**: The system MUST emit a monitoring metric tracking reaction-
  operation failure rate, broken down at minimum by channel and by agent
  identity, so the operator can observe failure trends without reading
  raw logs.
- **FR-009**: The system MUST apply platform rate-limit handling
  (backoff, bounded retry) internally to reaction add and remove
  operations; the agent session MUST NOT be expected to implement
  rate-limit logic on top of this primitive.
- **FR-010**: The system MUST remain scoped to the agent managing its
  own reactions. Observing reactions added by other parties (including
  the operator) is out of scope for this spec and belongs in the separate
  Approval-via-Reaction Spec covering MVP item 4.
- **FR-011**: The system MUST preserve constitution Principle VI: these
  primitives are the atomic mechanism; they do NOT themselves encode
  coordination heuristics like "react with 👀 on inbound" or "clear 🤔
  once decided". Those heuristics are operational policy and live in
  follow-on specs.
- **FR-012**: The system MUST treat reaction add and remove operations
  as outbound transport activity for the purposes of the channel-wide
  safety interrupt. When a channel is in `!stop` state per the Transport
  MVP Spec (MVP item 1, Vigil's ownership), reaction operations MUST be
  suppressed until the channel enters `!resume`. Consistent semantics
  with text-message suppression under `!stop`.

### Key Entities

- **Reaction Request**: The tuple an agent session emits — (direction,
  channel identifier, message identifier, emoji reference) — where
  direction is add or remove, representing the intent to manage a
  reaction on the target message. A request may succeed (reaction state
  changed), silently succeed (idempotent no-op on duplicate-add or
  already-absent remove), or fail (with a reason surfaced to the session
  log).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An agent can emit a reaction to a message with a single
  call; the reaction is visible on the target message within the
  platform's standard reaction propagation time.
- **SC-002**: An agent can remove its own prior reaction from a message
  with a single call; the reaction is no longer visible (attributed to
  that agent) within the platform's standard propagation time.
- **SC-003**: Reaction add/remove failures (deleted target, permission
  denied, invalid emoji, rate-limit saturation, cross-user removal
  attempt, `!stop`-suppressed) surface as structured WARN-level log
  events with the documented field set, without interrupting the
  agent's session.
- **SC-004**: The failure-rate metric is queryable per channel and per
  agent identity, so the operator can detect a rising failure trend in
  one channel or from one bot without reading logs.
- **SC-005**: The spec does not encode any coordination heuristic about
  *when* to emit or remove a reaction — heuristics remain spec-level per
  Principle VI and stay in follow-on operational specs.

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
- Moderation-style removal of reactions added by other users. Even when
  the bot holds platform-level permission to remove any user's reaction,
  the agent-session primitive in this spec is scoped to the agent's own
  reactions only. A moderation surface (if ever needed) is a different
  spec with a different permission model.
- Operational heuristics about *which* emoji to use for *which* signals.
  Stays in follow-on spec or agent policy.
