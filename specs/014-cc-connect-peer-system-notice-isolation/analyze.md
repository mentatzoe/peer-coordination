# Analysis: cc-connect Peer System Notice Isolation

**Feature**: `014-cc-connect-peer-system-notice-isolation`  
**Date**: 2026-05-12  
**Input**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/peer-system-notice-isolation.md`, `quickstart.md`, `tasks.md`, and implementation diff in `cc-connect/`.

## Summary

No blocking artifact consistency findings for the PC-76 implementation diff.

The branch implements the narrow Layer 1 fix described in the spec: Discord
marks allowlisted peer-bot messages with explicit provenance, drops
allowlisted peer-bot reply notices before core dispatch, and core suppresses
sender-facing guardrail replies for peer-bot-originated rate-limit, busy queue,
overflow, and queued-drop paths while preserving human/operator feedback.

## Findings

- **CRITICAL**: none.
- **HIGH**: none.
- **MEDIUM**: none.
- **LOW**: broader existing test-suite caveats remain outside this slice:
  full core/package runs on this macOS temp-path environment still fail
  pre-existing path-format expectations, and full `./...` also requires built
  web assets for packages importing `web/embed.go`.

## Requirements Trace

| Requirement | Evidence |
|---|---|
| FR-001 | `core.Message` now carries `AuthorKind MessageAuthorKind` and exposes `FromPeerBot()`. |
| FR-002 | Discord sets `AuthorKind: core.MessageAuthorPeerBot` only when `isAllowedPeerBot(m.Author)` is true. |
| FR-003 | Existing allowlisted peer-bot final-output dispatch remains covered and now asserts peer-bot provenance. |
| FR-004 | New Discord test covers allowlisted peer-bot reply notice suppression before core dispatch. |
| FR-005 | New core rate-limit peer-bot test proves no rate-limit reply is emitted. |
| FR-006 | New core busy queue peer-bot test proves queueing is silent while preserving queued message metadata. |
| FR-007 | New core busy overflow peer-bot test proves no previous-processing reply is emitted. |
| FR-008 | New core queued-drop test proves peer-bot queued messages are skipped while human queued drops still notify. |
| FR-009 | New core human/operator rate-limit and busy overflow tests prove existing feedback remains visible. |
| FR-010 | The implementation uses provenance plus Discord reply metadata; it does not add broad content-prefix filtering. |

## Verification

- RED confirmed:
  - `go test ./core -run 'TestHandleMessage_PeerBotRateLimitIsSilent|TestHandleMessage_HumanRateLimitStillReplies|TestQueueMessageForBusySession_PeerBotQueuedSilently|TestHandleMessage_PeerBotBusyOverflowIsSilent|TestHandleMessage_HumanBusyOverflowStillReplies|TestNotifyDroppedQueuedMessages_SkipsPeerBotSenders'` failed before implementation because `AuthorKind`, `MessageAuthorPeerBot`, and queued-message provenance were missing.
  - `go test ./platform/discord -run 'TestHandleMessageCreate_DispatchesAllowlistedPeerBotWithoutMention|TestHandleMessageCreate_IgnoresAllowlistedPeerBotReplyNotice'` failed before implementation because Discord messages lacked peer-bot provenance.
- GREEN confirmed:
  - `gofmt -w core/message.go core/engine.go platform/discord/discord.go core/engine_test.go platform/discord/discord_test.go`
  - `go test ./core -run 'TestHandleMessage_PeerBotRateLimitIsSilent|TestHandleMessage_HumanRateLimitStillReplies|TestQueueMessageForBusySession_PeerBotQueuedSilently|TestHandleMessage_PeerBotBusyOverflowIsSilent|TestHandleMessage_HumanBusyOverflowStillReplies|TestNotifyDroppedQueuedMessages_SkipsPeerBotSenders'` -> pass.
  - `go test ./platform/discord -run 'TestHandleMessageCreate_DispatchesAllowlistedPeerBotWithoutMention|TestHandleMessageCreate_IgnoresAllowlistedPeerBotReplyNotice'` -> pass.
  - `git diff --check` -> pass.
- Broader attempted:
  - `go test ./core ./platform/discord` -> Discord package passes; core package still fails unrelated path-format tests:
    `TestProcessInteractiveEvents_AppendsReplyFooterWhenEnabled`,
    `TestProcessInteractiveEvents_ReplyFooterPrefersSessionRuntimeState`,
    `TestResolveLocalDirPath_AcceptsSubdir`.
  - `go test ./...` -> same core caveats plus setup failures in
    `cmd/cc-connect` and `web` because `web/embed.go` expects `dist` assets
    (`pattern all:dist: no matching files found`).

## Constitution Alignment

Implementation remains aligned with the initial constitution check. The diff is
confined to the transport implementation surface and slice-owned Speckit
artifacts, preserves the governance/transport boundary, and does not add new
coordination policy.
