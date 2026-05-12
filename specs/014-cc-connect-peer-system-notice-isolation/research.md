# Research: cc-connect Peer System Notice Isolation

## Decision 1: Add core author provenance

**Decision**: Add a `MessageAuthorKind` marker to `core.Message`, with a `peer_bot` value set by platform adapters that intentionally admit bot authors as conversational peers.

**Rationale**: Core is where rate-limit, queue, overflow, and previous-processing guardrails are emitted. It cannot safely infer author class from platform user IDs alone, and content-prefix filtering would not distinguish human input from peer bot input.

**Alternatives considered**:

- Content-prefix filters for known guardrail strings: rejected as brittle, locale-dependent, and explicitly out of scope as the primary fix.
- Discord-only suppression in the adapter: insufficient because core still emits queue/rate-limit replies when a peer-bot-originated message reaches busy paths.

## Decision 2: Treat allowlisted peer bot Discord replies as bridge notices

**Decision**: In the Discord adapter, ignore messages authored by allowlisted peer bots when they are Discord replies.

**Rationale**: cc-connect guardrail feedback is emitted through reply-style delivery for queue/rate-limit/previous-processing paths. Normal final peer output is emitted as a channel send. This uses transport metadata rather than matching localized notice text.

**Alternatives considered**:

- Hidden sentinel characters in outgoing system notices: rejected for this slice because it would alter emitted message content and still require content scanning.
- Ignore all messages from allowlisted bots matching specific English strings: rejected as broad prefix/content filtering.

## Decision 3: Suppress peer-bot guardrail feedback in core

**Decision**: Core keeps processing peer-bot messages where useful, including silent queueing, but suppresses sender-facing guardrail notices when `Message.AuthorKind == peer_bot`.

**Rationale**: Peer-bot input should not cause bridge feedback loops. Human/operator input still requires feedback for recovery and legibility.

**Alternatives considered**:

- Drop all peer-bot messages while busy: rejected because queued peer output may still be useful once the current turn finishes.
- Disable rate limiting for peer bots: rejected because it changes admission semantics more than needed; silent drop on rate limit is enough to prevent loops.
