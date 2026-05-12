# Feature Specification: Discord Reply-to Context

**Feature Branch**: `[012-cc-connect-discord-reply-to]`
**Created**: 2026-05-05
**Status**: Draft
**Input**: User description: "Phase 1 baseline-substrate gap that's been quiet too long. cc-connect#5 filed 2026-04-22"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Forward Reply-to Content (Priority: P1)

As an operator, when I use Discord's native reply UI to reply to a previous message, I want the agent to receive the content and author of the message I'm replying to, so it has precise context for my new message without me needing to copy-paste the text.

**Why this priority**: Essential for Phase 1 baseline-substrate completion. Interrupt paths and precise context tracking depend on this native UI gesture.

**Independent Test**: Can be fully tested by replying to a user's message in Discord and verifying the agent receives the replied-to text.

**Acceptance Scenarios**:
1. **Given** a prior message in the channel, **When** the operator replies to it with a new message, **Then** the cc-connect transport forwards the original message's content + author to the agent along with the new message.

### User Story 2 - Agent Reply Awareness (Priority: P2)

As a peer-coordination agent, when I receive a message that replies to another bot's message, I want to know the identity of that bot so my read-the-room classifier can properly determine if I am being addressed or need to yield to a peer.

**Why this priority**: Required for multi-agent peer-coordination read-the-room logic.

**Independent Test**: Can be tested by having an operator reply to an agent message and verifying the forwarded context tags the author as a bot.

**Acceptance Scenarios**:
1. **Given** an agent message, **When** the operator replies to it, **Then** the forwarded context includes the bot authorship identity.

### Edge Cases

- What happens when the referenced message is extremely long?
- What happens when a reply points to a message in a different channel?
- What happens when a reply points to another reply (multi-hop chain)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extract the referenced message (`Message.ReferencedMessage` or equivalent) when an incoming Discord message is a reply.
- **FR-002**: System MUST append/prepend the referenced message content, author username, and author type (human vs bot) to the inbound payload forwarded to the agent.
- **FR-003**: System MUST format the forwarded context via [NEEDS CLARIFICATION: Format of forwarded reply context: prose preamble vs structured field vs both?]
- **FR-004**: System MUST handle multi-hop replies by [NEEDS CLARIFICATION: Multi-hop replies: pass the whole chain or just the immediate parent?]
- **FR-005**: System MUST truncate replied-to message content if it exceeds [NEEDS CLARIFICATION: Truncation policy: max characters, or use ID reference?]

### Key Entities

- **Discord Message Event**: Contains the new message text, author, and an optional reference to a parent message.
- **Forwarded Agent Payload**: The normalized message text sent to the LLM backend.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Discord replies correctly forward the immediate parent message's content and author to the agent context.
- **SC-002**: Integration test passes verifying an agent receives reply-to context from a simulated/real Discord reply.
- **SC-003**: The forwarded format is successfully parsed by the read-the-room classifier.

## Assumptions

- We are modifying the `mentatzoe/cc-connect` transport layer implementation for the Discord platform adapter.
- We assume `discordgo` provides the referenced message populated in `MessageCreate`, or it can be fetched if only the ID is provided.
- Cross-channel replies are explicitly ignored or treated as text-only context without fetching if the bot lacks access.
