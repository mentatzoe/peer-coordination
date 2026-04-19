# Contract: Discord Session Control Behavior

## Bound surface

- The Discord bot only dispatches runtime messages from the configured bound
  channel.
- If `thread_isolation = true`, a thread is in scope only if it is rooted under
  that bound channel.
- Messages from other channels are ignored or rejected before dispatch.

## Session state

- The bound surface starts **closed** until the operator opens a session.
- A session opens when the operator posts the seed message or sends `!resume`.
- `!stop` always closes the current session.
- `!resume` always opens a **new** session. It does not revive the prior one.
- The 1-hour idle threshold in `design/poc.md` is operator-facing only for this
  slice; the runtime does not implement time-based idle detection here.

## While closed

- Peer messages do not reopen the session.
- Peer messages are not routed into the previously active session.
- Operator messages that are not an opening action should not silently create a
  peer session continuation.

## Safety

- If channel binding cannot be resolved, fail closed.
- If operator identity is not authorized, control commands have no effect.
- For the current Phase 1 Discord probe, the operator is the first Discord user
  ID listed in `allow_from`.

## Downstream artifact expectations

- Operator `!stop` / `!resume` events should be captured downstream as
  `close_or_resume` interventions in the session bundle's
  `interventions.json`, per spec 001.
- A session closed by `!stop` maps downstream to `close_reason =
  stop_no_resume` in session-bundle metadata. A later `!resume` opens a new
  session; it does not change the prior session's close reason.

## Out of scope

- Transcript export
- Session bundle file generation
- Pinned-rules synchronization
