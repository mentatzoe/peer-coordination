# Quickstart: Agent-Initiated Emoji Reactions

**Feature**: 003-agent-initiated-reactions
**Audience**: Agent session authors and cc-connect platform implementers.

## For agent session authors

### 1. Check for Reactor capability

Not every platform supports reactions. Type-assert before calling.

```go
reactor, ok := platform.(core.Reactor)
if !ok {
    // Fallback: text reply, or just skip the ack entirely (silence is OK).
    return
}
```

### 2. Emit a reaction

```go
result := reactor.AddReaction(ctx, core.ReactionRequest{
    Direction: core.ReactionDirectionAdd,
    ChannelID: msg.ChannelID,
    MessageID: msg.ID,
    Emoji:     "👀",              // or a custom emoji ref like "sparkle:123456789"
    SessionID: session.ID(),
})
// Do NOT block the session on `result`. Either fire-and-forget or observe
// asynchronously (see next step).
```

### 3. Observe the outcome (optional)

```go
go func() {
    r := <-result
    switch r.Outcome {
    case core.ReactionOutcomeApplied, core.ReactionOutcomeIdempotentPresent:
        // Success or harmless duplicate.
    case core.ReactionOutcomeFail:
        slog.Warn("reaction failed",
            "reason", string(*r.Reason),
            "channel_id", msg.ChannelID,
            "message_id", msg.ID)
    }
}()
```

### 4. Remove a prior reaction

```go
reactor.RemoveReaction(ctx, core.ReactionRequest{
    Direction: core.ReactionDirectionRemove,
    ChannelID: msg.ChannelID,
    MessageID: msg.ID,
    Emoji:     "👀",
    SessionID: session.ID(),
})
// Idempotent: removing a reaction that isn't there returns
// ReactionOutcomeIdempotentAbsent, no error.
```

### 5. Do not encode heuristics in agent code that belong in policy

Per Principle VI, agent code should not make semantic decisions like "always react with 👀 on any inbound message." Those decisions come from operational policy (prompt context, operational spec), not hard-coded logic in agent sessions.

## For platform implementers

### When to implement Reactor

Implement `core.Reactor` if and only if the platform has a native reaction API. For Discord, that's `discordgo.Session.MessageReactionAdd` / `MessageReactionRemoveMe`. For platforms without a native reaction concept, do not implement Reactor — consumers detect absence via type assertion.

### Required behaviors

1. **Agent identity attribution (FR-004).** The reaction MUST be attributed to the bot identity the platform was constructed with. Never spoof.
2. **Own-reactions-only for remove (FR-005).** Use the platform API that targets "my own" reaction (`RemoveMe` in discordgo), not the generic remove-by-user-id API.
3. **Idempotency (FR-006, FR-007).** Duplicate add / already-absent remove both return `ReactionOutcomeIdempotent*`, not failure.
4. **Non-blocking (FR-008).** Return the result channel immediately. Execute the API call in a goroutine.
5. **Internal rate-limit handling (FR-010).** Trust `discordgo`'s built-in backoff; don't layer a second one on top.
6. **`!stop` suppression (FR-013).** Check the channel's `InterruptState` before calling the platform API. On `stopped`, return `ReactionOutcomeFail` with `Reason = FailureReasonStopSuppressed`.

### Must NOT do

- Emit reactions the agent did not request ("helpful" auto-reactions from the platform adapter). The Reactor is a passthrough.
- Remove reactions added by other users via this primitive (even when the bot has `MANAGE_MESSAGES` permission). That's a moderation surface, explicitly out of scope.
- Log sensitive content in failure events. `emoji`, `channel_id`, `message_id` are fine; message body is not.

## Testing

### Unit tests (`platform/discord/reactions_test.go`)

- Happy-path add, happy-path remove, idempotent-add, idempotent-remove.
- Each `FailureReason` path, with a stub `discordgo.Session` that injects the corresponding HTTP response.
- `!stop` suppression — stub `InterruptState` to stopped, verify `stop_suppressed` without calling the platform API.

### Integration tests (`tests/integration/reactions_test.go`)

- Agent session calls `AddReaction`, verifies the structured log event appears with the documented field set.
- Agent session calls `RemoveReaction` after a prior add, verifies idempotent behavior on a second remove.
- Rolling-window metric event emission (deferred implementation detail; assert shape if implemented by tasks phase).

## Operator cheat sheet

| Symptom | Likely cause | Log grep |
|---|---|---|
| Agent reacts but nothing shows | Permission missing in channel. | `reason=permission_denied` |
| Reaction occasionally missing | Rate-limit saturation, probably chatty channel. | `reason=rate_limit_exceeded` |
| Custom emoji fails silently | Bot not in the guild that owns the emoji, or emoji ID is wrong. | `reason=invalid_emoji` |
| No reactions during a freeze | `!stop` is active on that channel. | `reason=stop_suppressed` |
