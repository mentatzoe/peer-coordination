# Data Model: Transport MVP

## ChannelMode

- **Purpose**: Declares how a channel routes or permits agent participation.
- **Fields**:
  - `name` — mode identifier such as `mention-only` or `open-floor`
  - `scope` — which channel or channel set the mode applies to
  - `default_behavior` — whether ordinary non-mentioned messages are eligible
    for agent handling

## InterruptState

- **Purpose**: Represents whether a channel is currently stopped or active.
- **Fields**:
  - `channel_id`
  - `state` — `active` or `stopped`
  - `set_by` — operator identity that issued the state change
  - `resume_required` — whether explicit resume is still outstanding

## ProposalMessage

- **Purpose**: Represents an agent-authored request that requires human
  approval before a state-changing action proceeds.
- **Fields**:
  - `message_id`
  - `channel_id`
  - `author_agent`
  - `proposed_action`
  - `approval_state` — pending, approved, expired, or cancelled

## ApprovalReaction

- **Purpose**: Represents the approval signal attached to a proposal message.
- **Fields**:
  - `message_id`
  - `reaction_symbol`
  - `applied_by`
  - `applied_at`
  - `is_authorized`

## PinnedRuleContext

- **Purpose**: Captures the rules injected into a new session from a channel's
  pinned messages.
- **Fields**:
  - `channel_id`
  - `rules_source_messages`
  - `captured_text`
  - `captured_at_session_start`

## Relationships

- A **ChannelMode** applies to one or more channels.
- A **ChannelMode** and **InterruptState** together determine whether an agent
  may respond in a channel.
- A **ProposalMessage** may have zero or more **ApprovalReaction** entries, but
  only authorized approval reactions may transition it to approved.
- A **PinnedRuleContext** is associated with a channel session at startup and
  influences how that session behaves.
