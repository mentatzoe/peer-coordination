# Phase 0 Research: Agent-Initiated Emoji Reactions

**Feature**: 003-agent-initiated-reactions
**Date**: 2026-04-18

## Purpose

Resolve the NEEDS CLARIFICATION items from the Technical Context and document the external API surface the implementation depends on. No open ambiguities remain in the spec after the clarify pass; this research focuses on platform-API specifics that inform the Phase 1 design.

## 1. `discordgo` reaction API surface

**Library**: `github.com/bwmarrin/discordgo` (already a direct dependency of cc-connect's Discord platform adapter).

### Relevant methods

| Method | Purpose | Maps to |
|---|---|---|
| `Session.MessageReactionAdd(channelID, messageID, emojiID string) error` | Add a reaction on the bot's behalf. | FR-001 (add). |
| `Session.MessageReactionRemoveMe(channelID, messageID, emojiID string) error` | Remove the bot's *own* reaction. | FR-002 (remove, own-only). |
| `Session.MessageReactionRemove(channelID, messageID, emojiID, userID string) error` | Remove a specific user's reaction (requires `MANAGE_MESSAGES`). | Explicitly NOT used — out of scope per spec. |

### Emoji reference format

- Unicode emoji: pass the unicode character directly (e.g. `"👀"`).
- Guild custom emoji: pass `"name:id"` (without the `<:`/`:>` wrapper).

Decision: accept both forms at the `core` boundary. The Discord adapter handles format translation where needed (most callers will pass unicode; custom emoji is the niche path).

### Rate limiting

`discordgo` handles Discord's 5-req/sec-per-channel reaction rate limit internally via its built-in backoff. No additional rate-limit layer required in `platform/discord/reactions.go`. FR-010's "internal retry with backoff" is satisfied by `discordgo`'s default behavior.

## 2. Failure taxonomy

Each reaction operation may fail with one of a small set of reasons. Mapping:

| `discordgo` signal | Our `reason` value | Notes |
|---|---|---|
| HTTP 404 on target message | `message_deleted` | Expected in chatty channels; WARN, not ERROR. |
| HTTP 403 | `permission_denied` | Bot lacks reaction permission in channel. Logged once per channel to avoid spam. |
| HTTP 400 (invalid emoji) | `invalid_emoji` | Caller bug or unsupported emoji. Offending emoji included in log event. |
| HTTP 429 after backoff exhausted | `rate_limit_exceeded` | `discordgo` retry saturated. Drop is acceptable per FR-010. |
| Internal "channel stopped" check | `stop_suppressed` | FR-013 — channel in `!stop` state, request suppressed at transport. |
| `RemoveMe` on non-existent own reaction | `already_absent` (idempotent success) | Per FR-007, logged at DEBUG not WARN. |
| `MessageReactionAdd` on already-present own reaction | `already_present` (idempotent success) | Per FR-006, logged at DEBUG not WARN. |

## 3. Agent identity attribution

In cc-connect, multiple projects can share a daemon but each project has its own bot token and Discord identity. The reacting user for `MessageReactionAdd`/`RemoveMe` is always the bot whose token created the `discordgo.Session` — i.e. the project's configured Discord bot identity. No spoofing possible (FR-004 satisfied by the platform API surface itself).

For the peer-coordination pilot:
- Dalgos (the `vault-keeper` project bot) reacts as `<Dalgos bot user>`.
- Vigil (the `personal-agent-setup-vigil` project bot) reacts as `<Vigil bot user>`.

Each has its own `discordgo.Session` in the cc-connect daemon.

## 4. Metric emission

cc-connect uses Go's `log/slog` for structured logs. For metrics, the codebase does not currently emit Prometheus-style counters — the observability stack is log-based.

Decision: FR-009's failure-rate metric is implemented as a structured log event at INFO level with `event=reaction_failure_rate` and fields for `{channel_id, agent_identity, window, failure_count, success_count}`, emitted on a rolling window (e.g. every 1 minute or on interval-aligned ticks). This keeps observability consistent with cc-connect's existing log-based pattern while giving the operator a greppable/pipeable metric source. If Prometheus emission is added to cc-connect later, this metric maps cleanly onto a counter.

Deferred to tasks.md:
- Exact window size (30s vs 60s vs 5min)
- Whether to emit on zero-activity windows

## 5. Interaction with `!stop` (Transport MVP Spec, item 1)

Vigil's `001-transport-mvp/spec.md` FR-008 says "not-yet-sent outbound messages... MUST be suppressed" under `!stop`, and the spec's Key Entities include an `Interrupt State` per channel.

Decision for item 3: the reaction-path implementation checks `InterruptState` for the target channel before calling `discordgo`'s reaction API. On `stopped`, the request is rejected with `reason=stop_suppressed` per Section 2. This honors FR-013.

Edge: whether suppressed requests queue for `!resume` or drop is a cc-connect-level concern. Spec defers this to plan-phase; plan decision: **drop**. Rationale: queuing across `!stop`/`!resume` boundaries creates stale state (the agent that requested the reaction may have moved on); dropping is consistent with the "best-effort cancel" framing in Vigil's FR-008.

## 6. Open items — none

All spec NEEDS CLARIFICATION markers were resolved in the clarify pass. This research confirms no new ambiguities were introduced by the technical context.
