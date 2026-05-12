# Quickstart: cc-connect Peer System Notice Isolation

## Focused verification

From `cc-connect/`:

```bash
go test ./core -run 'TestHandleMessage_PeerBotRateLimitIsSilent|TestHandleMessage_HumanRateLimitStillReplies|TestQueueMessageForBusySession_PeerBotQueuedSilently|TestHandleMessage_PeerBotBusyOverflowIsSilent|TestHandleMessage_HumanBusyOverflowStillReplies|TestNotifyDroppedQueuedMessages_SkipsPeerBotSenders'
go test ./platform/discord -run 'TestHandleMessageCreate_DispatchesAllowlistedPeerBotWithoutMention|TestHandleMessageCreate_IgnoresAllowlistedPeerBotReplyNotice'
```

## Manual smoke after rebuild/restart

1. Rebuild and restart the contained `cc-connect` daemon.
2. In the PC-7 parent channel, confirm both Dalgos and Vigil are configured in each other's `allow_from_bots`.
3. Send an operator seed while both peers are idle.
4. Confirm both peer final replies appear in the parent channel.
5. Confirm each peer runtime ingests the other peer final reply.
6. Trigger a busy or rate-limit path from a peer-bot-originated message.
7. Confirm no queue, rate-limit, previous-processing, or dropped-queue notice is ingested by either peer runtime.

The counted clock and non-counted preflight remain out of scope for this slice.
