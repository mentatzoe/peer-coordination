# Analysis: cc-connect Peer System Notice Isolation

## Consistency Check

- Spec, plan, and tasks are aligned on the narrow PC-76 scope: preserve allowlisted peer-bot content while keeping bridge-generated operational notices out of peer runtimes.
- Implementation covers the required provenance fields, Discord system-notice ID tracking, and silent peer-bot queue/rate-limit/overflow behavior.
- Human/operator feedback is preserved through the normal reply paths, with operational replies routed through the optional system-notice capability where supported.

## Verification

- `go test ./core -run 'TestQueueMessageForBusySession_PeerBotQueuesSilently|TestQueueMessageOverflow_PeerBotRejectsSilently|TestHandleMessage_RateLimitedPeerBotRepliesSilently'` passed.
- `go test ./platform/discord -run 'TestHandleMessageCreate_(DispatchesAllowlistedPeerBotWithoutMention|IgnoresRecordedSystemNoticeFromAllowlistedPeerBot)'` passed.
- `go test ./core -run 'TestQueueMessage|TestRateLimit|TestHandleMessage'` passed.
- `go test ./platform/discord` passed.
- `git diff --check` passed.
- `go build -tags no_web -o /tmp/cc-connect-pc76-test ./cmd/cc-connect` passed.

## Known Unrelated Baseline Failures

- `go test ./core` still fails on pre-existing macOS path-format assertions:
  - `TestProcessInteractiveEvents_AppendsReplyFooterWhenEnabled`
  - `TestProcessInteractiveEvents_ReplyFooterPrefersSessionRuntimeState`
  - `TestResolveLocalDirPath_AcceptsSubdir`

## Live Runtime Check

- Installed the patched `no_web` binary over the launchd target after backing up the previous binary.
- Updated Dalgos, Vigil, and Castor pilot `channel_id` values to `1503873998591627286` after backing up the config.
- Restarted `com.cc-connect.service`; startup logs show all three Discord projects connected and `cc-connect is running`.
