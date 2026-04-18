# Feature Specification: Channel Policy and Presence

**Feature Branch**: `002-channel-policy-presence`
**Created**: 2026-04-18
**Status**: Draft
**Input**: User description: "Specify how per-channel policy — activation modes (mention-only / thread-initiator / open-floor), verbosity, user allowlists, and intentional bot presence — is declared, enforced, and changed, without pulling operational heuristics back into the constitution."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Declare a Channel's Activation Mode (Priority: P1)

As the operator, I want each channel to declare one activation mode —
mention-only, thread-initiator, or open-floor — so that routing behavior is
predictable and varies by channel purpose without reconfiguring the whole
deployment.

**Why this priority**: Activation mode is the primary switch that determines
whether agents reply at all, and whether the open-floor pilot (Transport MVP,
P1) can run in its designated channel while the rest of the deployment stays
quiet.

**Independent Test**: Can be fully tested by configuring one channel as
`open-floor` and another as `mention-only`, posting the same un-mentioned
message in both, and verifying that agents reply in the first and stay silent
in the second.

**Acceptance Scenarios**:

1. **Given** a channel configured as `mention-only`, **When** the operator
   posts a message without @-mentioning a bot, **Then** no agent replies.
2. **Given** a channel configured as `open-floor`, **When** the operator
   posts a message without @-mentioning a bot, **Then** eligible agents may
   reply per the Transport MVP Spec's routing rules.
3. **Given** a channel configured as `thread-initiator`, **When** the operator
   starts a new thread by @-mentioning one bot, **Then** subsequent messages
   in that thread route to the mentioned bot without re-mention.
4. **Given** a channel with no explicit mode, **When** an agent receives
   routing signals for that channel, **Then** the default mode (`mention-only`)
   applies.

---

### User Story 2 - Dial Channel Verbosity (Priority: P2)

As the operator, I want to set how much tool-trace and progress detail agents
render in a channel, so I can choose a conversational "coworker" register or a
detailed "tool" register per channel without changing the underlying agent or
running in two different harnesses.

**Why this priority**: Verbosity mismatch has already been a live pain point —
the `cc-connect` codex adapter's default tool-trace rendering (`💭 thinking`,
`🔧 Tool #N: Bash`, `🧾 Bash`, `🟢 Status`, `🔢 Exit`, full output) is
substantively more information than the `--channels` plugin surfaces, and the
difference changes the operator's perceived relationship with the agent. A
per-channel verbosity knob lets each channel declare the register that fits
its purpose (design brainstorm vs debugging vs stand-up) without forcing the
choice globally.

**Independent Test**: Can be fully tested by setting one channel to `compact`
verbosity and another to `trace` verbosity, performing the same multi-tool
agent task in each, and verifying that the rendered chat history differs
exactly along the tool-trace dimension — same substantive conclusion, different
visual surface.

**Acceptance Scenarios**:

1. **Given** a channel with verbosity set to `compact`, **When** an agent
   executes a multi-step task, **Then** only the final substantive response
   appears in the channel; intermediate tool calls are not rendered.
2. **Given** a channel with verbosity set to `trace`, **When** an agent
   executes the same task, **Then** tool calls, their status, and their
   key output are visible inline in the channel.
3. **Given** a channel with verbosity set to `silent`, **When** an agent
   performs background work triggered by that channel, **Then** no progress
   messages appear; only the final reply (or explicit status response) lands.
4. **Given** a channel with no explicit verbosity, **When** an agent performs
   work there, **Then** a documented default verbosity applies.

---

### User Story 3 - Allowlist Who Can Invoke an Agent in a Channel (Priority: P3)

As the operator, I want to restrict which users (beyond the operator) can
invoke agents in a given channel, so that public-facing channels can host
agents without exposing their approval surface to arbitrary participants.

**Why this priority**: The existing `access.json` policy already supports
per-channel allowlists at the transport layer for the Claude `--channels`
plugin; this user story generalizes that concept to all harnesses with a
consistent declaration format. Not blocking the first pilot because it ships
with a single-operator allowlist, but important for any broader rollout.

**Independent Test**: Can be fully tested by configuring a channel allowlist
that excludes a specific user, having that user @-mention an agent, and
verifying no response is produced.

**Acceptance Scenarios**:

1. **Given** a channel with an allowlist containing only the operator's user
   ID, **When** a non-allowlisted user @-mentions a bot in that channel,
   **Then** no agent replies.
2. **Given** a channel with no allowlist declared, **When** any user
   @-mentions a bot subject to the channel's activation mode, **Then** the
   mode's routing rules apply without additional filtering.
3. **Given** a channel with an allowlist, **When** the allowlisted operator
   @-mentions a bot, **Then** the bot responds per the channel's activation
   mode.

---

### User Story 4 - Declare Which Bots Are Present in Which Channels (Priority: P4)

As the operator, I want to declare intentional bot presence per channel in
a single config rather than relying only on Discord server-side role
permissions, so that a bot's channel reach matches its role (e.g., Dalgos
is ambient only in `#vault-keeper`, Vigil operates across the workspace)
regardless of whether server permissions also allow it elsewhere.

**Why this priority**: Discord-side permissions are coarse and operator-
hostile to audit. Declaring presence in the peer-coordination config makes
reach legible and gives agents a clear "am I supposed to be in this channel?"
signal that supplements (does not replace) platform permissions.

**Independent Test**: Can be fully tested by declaring that a specific bot
is admitted only to a named set of channels, posting in an admitted and a
non-admitted channel, and verifying the bot responds in the first and stays
silent in the second even when platform permissions would otherwise allow it.

**Acceptance Scenarios**:

1. **Given** a bot declared present in channels A and B, **When** the bot
   receives a message from channel C (where platform permissions still allow
   it to read), **Then** the bot does not respond or initiate work in C.
2. **Given** a bot declared present in channel A, **When** a message in A
   meets the channel's activation-mode criteria, **Then** the bot responds
   normally per that mode.
3. **Given** two bots both declared present in an `open-floor` channel,
   **When** a message meets the channel's mode criteria, **Then** both bots
   are eligible to respond per the Transport MVP Spec's routing rules.

### Edge Cases

- What happens when a channel's activation mode is changed while a session
  is mid-flight? Does the in-flight session finish under the old mode, or is
  the new mode applied immediately?
- What happens when verbosity is changed mid-session? Do in-flight tool calls
  still render under the old verbosity, or does the next outbound message
  switch?
- What happens when a channel's allowlist is empty (i.e., the list exists
  but contains no entries)? Does that deny-all or is it treated as "no
  allowlist declared"?
- What happens when platform permissions and the presence declaration
  disagree (bot admitted in config but not in server roles, or vice versa)?
- What happens when `thread-initiator` mode is applied to a channel without
  thread support?
- What happens when a bot is present in an `open-floor` channel but also
  subject to a per-bot verbosity override that conflicts with the channel's
  verbosity?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support three named channel activation modes:
  `mention-only`, `thread-initiator`, and `open-floor`.
- **FR-002**: The system MUST allow the operator to declare a channel's
  activation mode in a per-channel configuration record.
- **FR-003**: The system MUST treat `mention-only` as the default activation
  mode for channels with no explicit declaration.
- **FR-004**: The system MUST support a verbosity declaration per channel
  with at least three levels: `silent`, `compact`, and `trace`.
- **FR-005**: The system MUST apply channel verbosity to agent-authored
  outbound messages, hiding tool-trace and progress content at levels below
  `trace`.
- **FR-006**: The system MUST document and apply a default verbosity level
  for channels without explicit verbosity declaration.
- **FR-007**: The system MUST support a per-channel user allowlist that
  gates agent invocation independently of platform-level permissions.
- **FR-008**: The system MUST treat "no allowlist declared" and "empty
  allowlist declared" as distinct states, with an unambiguous documented
  rule for each.
- **FR-009**: The system MUST support a per-bot, per-channel presence
  declaration that specifies whether the bot is admitted to the channel.
- **FR-010**: The system MUST treat absence of presence declaration as
  "not admitted" — bots MUST NOT initiate activity in a channel where
  they are not explicitly admitted.
- **FR-011**: The system MUST preserve Principle II (transport is plumbing):
  this spec governs the per-channel mechanics and the declaration format;
  it MUST NOT encode the operational heuristics for how agents decide
  whether to reply inside a given mode.
- **FR-012**: The system MUST preserve Principle VI (coordination is
  human-legible): verbosity levels are a rendering concern, not an agent-
  capability concern. An agent's substantive conclusions MUST be accessible
  at every verbosity level; only the surface presentation varies.
- **FR-013**: The system SHOULD reflect policy changes (mode, verbosity,
  allowlist, presence) without requiring a full process restart. A short
  propagation latency is acceptable; a full daemon bounce is not.
- **FR-014**: The system MUST make the current effective policy for a
  channel inspectable (e.g., by query or by log line), so the operator can
  verify that a declaration was picked up correctly.

### Key Entities *(include if feature involves data)*

- **Channel Policy Record**: Per-channel configuration declaring activation
  mode, verbosity, allowlist, and bot presence. Owned by the operator.
- **Activation Mode**: One of `mention-only`, `thread-initiator`, `open-floor`
  (Transport MVP Spec defines the routing semantics; this spec defines the
  per-channel selection and default rules).
- **Channel Verbosity**: One of `silent`, `compact`, `trace` (levels as
  declared here; specific rendering rules belong in the Transport MVP Spec
  or harness documentation).
- **Channel Allowlist**: Set of user IDs permitted to invoke agents in the
  channel. Distinct from platform permissions.
- **Bot Presence Declaration**: Per-bot-per-channel flag indicating whether
  the bot is admitted to the channel.
- **Default Policy**: The documented fallback policy applied to channels
  with no explicit record, covering each of the four dimensions above.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The operator can change a channel's activation mode by editing
  a single configuration record, and the change takes effect within a
  bounded short propagation time without a full restart.
- **SC-002**: With verbosity set to `compact`, the same multi-tool task
  produces a chat surface that contains the final substantive answer and
  no tool-trace blocks; with verbosity set to `trace`, the same task
  produces both.
- **SC-003**: A non-allowlisted user's @-mention of a bot in an allowlist-
  gated channel does not produce an agent response.
- **SC-004**: A bot not admitted to a channel via presence declaration does
  not initiate replies or background work in that channel, even when
  platform permissions would otherwise allow it.
- **SC-005**: Every channel has a deterministic effective policy — either
  explicitly declared or inherited from documented defaults — that the
  operator can inspect.
- **SC-006**: No change in this spec elevates operational heuristics into
  constitutional territory; it remains possible to add, remove, or refine
  activation-mode-specific heuristics in the Transport MVP Spec without
  amending this spec.

## Assumptions

- The first implementation target is the `mentatzoe/cc-connect` transport
  repository; the `--channels` plugin for Claude Code is a secondary target
  that MAY adopt the same declaration format once this spec lands.
- The per-channel configuration format is a concern for the implementation
  plan (not this spec); the likely shape is an extension of the existing
  `access.json` / `config.toml` surfaces rather than a new top-level config.
- The operator remains the final arbiter of policy per constitution Principle
  IV; this spec defines the policy surface, not the approval workflow for
  changing policy.
- Activation-mode semantics (how each mode routes messages; when an agent
  "is eligible to respond") are defined in the Transport MVP Spec; this
  spec defines only the per-channel selection and default rules.
- Verbosity is a rendering concern. Agents MAY choose to adapt their own
  output style to verbosity hints they receive from transport, but transport
  is the final filter before messages land in the channel.
- Per-bot presence declaration complements but does not replace platform
  role/permission management. Operators who want hard enforcement SHOULD
  still use platform permissions as the outer gate.
