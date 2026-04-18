# Phase 1 Data Model: Agent-Initiated Emoji Reactions

**Feature**: 003-agent-initiated-reactions
**Date**: 2026-04-18

Reactions are platform-authoritative state. The agent side is stateless; these entities describe the request/response shape at the cc-connect `core` boundary.

## Entities

### `ReactionRequest`

Represents an agent's intent to manage one reaction on one message.

| Field | Type | Required | Notes |
|---|---|---|---|
| `Direction` | enum `add` \| `remove` | ✓ | FR-001 (add) or FR-002 (remove). |
| `ChannelID` | `string` | ✓ | Platform-native channel identifier. |
| `MessageID` | `string` | ✓ | Platform-native message identifier. |
| `Emoji` | `string` | ✓ | Unicode emoji (direct char) or guild custom emoji ref (`name:id`). |
| `SessionID` | `string` | ✓ | Originating agent-session ID. Used for observability and for routing the response back. |

### `ReactionOutcome`

The transport's response to a `ReactionRequest`. Used internally by cc-connect; the agent session sees `ReactionResult` (below).

| Value | When | FR mapping |
|---|---|---|
| `ok_applied` | State changed as requested. | FR-001, FR-002 |
| `ok_idempotent_present` | Add requested, reaction already present for this agent. | FR-006 |
| `ok_idempotent_absent` | Remove requested, reaction already absent for this agent. | FR-007 |
| `fail_with_reason` | Request failed; see `FailureReason`. | FR-008 |

### `FailureReason`

Enumerated reasons for `ReactionOutcome = fail_with_reason`. Exact string values are stable for log-parsing.

| Value | Source | FR mapping |
|---|---|---|
| `message_deleted` | Target message deleted between decision and API call. | Edge case |
| `permission_denied` | Bot lacks reaction permission in channel. | Edge case |
| `invalid_emoji` | Emoji not unicode and not a usable guild custom emoji. | Edge case |
| `rate_limit_exceeded` | `discordgo` retry backoff saturated. | FR-010 |
| `cross_user_removal_rejected` | Caller tried to remove another user's reaction via this primitive. | FR-005 |
| `stop_suppressed` | Channel is in `!stop` state. | FR-013 |

### `ReactionResult`

Shape of the response surfaced to the calling agent session. Non-blocking per FR-008 — the agent session may await this, but MUST NOT be blocked on it.

| Field | Type | Notes |
|---|---|---|
| `Outcome` | `ReactionOutcome` | See above. |
| `Reason` | `*FailureReason` | Populated only when `Outcome = fail_with_reason`. Nullable. |
| `ObservedAt` | `time.Time` | When cc-connect dispatched or observed the result. |

### `ReactionFailureLogEvent` (observability)

Shape of the structured log event emitted on `fail_with_reason` outcomes. Matches FR-008's field set verbatim.

```text
level=WARN event=reaction_failure
  action={add|remove}
  channel_id=<string>
  message_id=<string>
  emoji=<string>
  reason=<FailureReason>
  session_id=<string>
  agent_identity=<string>
```

### `ReactionFailureRateMetricEvent` (observability)

Rolling-window aggregate event emitted per FR-009. Log-based per `research.md` §4.

```text
level=INFO event=reaction_failure_rate
  window_seconds=<int>
  channel_id=<string>
  agent_identity=<string>
  failure_count=<int>
  success_count=<int>
  idempotent_count=<int>
```

Exact `window_seconds` value deferred to tasks.md.

## Relationships

- One `ReactionRequest` produces exactly one `ReactionResult`.
- Many `ReactionResult` values aggregate into one `ReactionFailureRateMetricEvent` per `{window, channel, agent}` triple.
- `ReactionRequest` does not compose with `ApprovalProposal` entities from the separate item-4 spec; cross-spec linkage is the consumer's concern.

## Lifecycle

`ReactionRequest` is ephemeral: created when the agent calls the API, consumed when the platform dispatches the call, retained only until `ReactionResult` is produced. No persistence.

## Invariants

- `ReactionRequest.Emoji` MUST be non-empty.
- `ReactionRequest.ChannelID`, `.MessageID`, `.SessionID` MUST be non-empty.
- If `Outcome = fail_with_reason`, `Reason` MUST be non-nil.
- If `Outcome ≠ fail_with_reason`, `Reason` MUST be nil.
