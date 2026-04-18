# Contract: Agent-Session Reactor Interface

**Feature**: 003-agent-initiated-reactions
**Layer**: `core/` in cc-connect
**Pattern**: Optional capability interface, consistent with cc-connect's existing `CardSender`, `InlineButtonSender`, `ProviderSwitcher` pattern.

## Go interface

```go
// Package core in cc-connect.

// Reactor is an optional capability implemented by platforms that support
// message-level emoji reactions emitted by the bot identity. Agent sessions
// obtain a Reactor by type-asserting against the current Platform.
//
// Reactor operations are non-blocking for the agent session: Add and Remove
// return immediately; the agent may await the returned channel or ignore it.
// Failures surface as ReactionResult with a populated Reason (see data-model.md).
type Reactor interface {
    // AddReaction emits a reaction on the given message, attributed to the
    // bot identity of the calling platform.
    AddReaction(ctx context.Context, req ReactionRequest) <-chan ReactionResult

    // RemoveReaction removes the bot's own previously added reaction on the
    // given message. Never removes reactions belonging to other users.
    RemoveReaction(ctx context.Context, req ReactionRequest) <-chan ReactionResult
}

type ReactionRequest struct {
    Direction ReactionDirection
    ChannelID string
    MessageID string
    Emoji     string
    SessionID string
}

type ReactionDirection int

const (
    ReactionDirectionAdd ReactionDirection = iota
    ReactionDirectionRemove
)

type ReactionResult struct {
    Outcome    ReactionOutcome
    Reason     *FailureReason // non-nil iff Outcome == ReactionOutcomeFail
    ObservedAt time.Time
}

type ReactionOutcome int

const (
    ReactionOutcomeApplied ReactionOutcome = iota
    ReactionOutcomeIdempotentPresent // add on already-present
    ReactionOutcomeIdempotentAbsent  // remove on already-absent
    ReactionOutcomeFail
)

type FailureReason string

const (
    FailureReasonMessageDeleted         FailureReason = "message_deleted"
    FailureReasonPermissionDenied       FailureReason = "permission_denied"
    FailureReasonInvalidEmoji           FailureReason = "invalid_emoji"
    FailureReasonRateLimitExceeded      FailureReason = "rate_limit_exceeded"
    FailureReasonCrossUserRemovalRejected FailureReason = "cross_user_removal_rejected"
    FailureReasonStopSuppressed         FailureReason = "stop_suppressed"
)
```

## Usage pattern (agent side)

```go
// From an agent session, typically during or after processing an inbound message.

if reactor, ok := platform.(core.Reactor); ok {
    resultCh := reactor.AddReaction(ctx, core.ReactionRequest{
        Direction: core.ReactionDirectionAdd,
        ChannelID: msg.ChannelID,
        MessageID: msg.ID,
        Emoji:     "👀",
        SessionID: session.ID(),
    })

    // Optional: await result for logging. Do not block substantive work on it.
    go func() {
        select {
        case r := <-resultCh:
            if r.Outcome == core.ReactionOutcomeFail {
                slog.Warn("reaction failed", "reason", *r.Reason)
            }
        case <-ctx.Done():
        }
    }()
}
```

## Capability detection

Platforms advertise Reactor support via type assertion only — no separate `SupportsReactions()` bool. Consistent with how `CardSender`, `InlineButtonSender` work. Agent sessions gracefully degrade (e.g. fall back to text) when the platform does not implement Reactor.

## Thread-safety

`Reactor` implementations MUST be safe for concurrent use from multiple agent sessions. A single `ReactionRequest` is owned by its caller; the returned channel is buffered (size 1) and closed after the result is sent.

## Error propagation vs failure reporting

- Transport-level errors (network timeout, auth expired, etc.) that the implementation cannot classify into `FailureReason` are rare; when they occur, `Outcome = ReactionOutcomeFail` with `Reason = nil` is NOT permitted. Such errors are mapped to `FailureReasonRateLimitExceeded` if retryable or logged at ERROR and surfaced as `ReactionOutcomeFail` with a close-match reason.
- `ctx` cancellation mid-request does not produce a `ReactionResult`; the channel is closed without a value.

## What the contract does NOT specify

- Exact wire format of the Discord API call (implementation detail of `platform/discord/reactions.go`).
- Queue / drop policy for requests arriving during `!stop` (deferred to tasks.md; `research.md` §5 leans drop).
- Metric emission cadence (deferred to tasks.md).
- Fallback behavior when the platform does not implement `Reactor` (consumer's concern).
