# Contract: Peer System Notice Isolation

## Inbound peer final output

Given a Discord message:

- author is a bot
- author ID appears in `allow_from_bots`
- message is on the bound surface
- message is not a Discord reply

Then the Discord adapter dispatches exactly one `core.Message` with:

- `UserID` equal to the peer bot ID
- `Content` unchanged
- `AuthorKind == peer_bot`

## Inbound peer bridge notice

Given a Discord message:

- author is a bot
- author ID appears in `allow_from_bots`
- message is a Discord reply

Then the Discord adapter does not dispatch a `core.Message`.

## Core guardrail feedback

Given a `core.Message` with `AuthorKind == peer_bot`, core must not send sender-facing guardrail feedback for:

- rate limit rejection
- busy-session queue acknowledgement
- busy-session queue overflow / previous-processing fallback
- queued-message drop notification

Given a `core.Message` without peer-bot provenance, the existing feedback behavior remains unchanged.
