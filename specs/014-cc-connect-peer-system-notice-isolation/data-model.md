# Data Model: cc-connect Peer System Notice Isolation

## MessageAuthorKind

Core enum-like string identifying the class of inbound message author.

| Value | Meaning |
|---|---|
| `""` / unset | Legacy default. Treated as human/operator input. |
| `human` | Explicit human/operator input. Reserved for adapters that want to mark it. |
| `peer_bot` | Input authored by a bot account intentionally allowlisted as a peer. |

## core.Message

Adds:

- `AuthorKind MessageAuthorKind`

Derived helper:

- `FromPeerBot() bool`: true when `AuthorKind == MessageAuthorPeerBot`.

## queuedMessage

Adds:

- `authorKind MessageAuthorKind`

This preserves peer-bot provenance when a busy-session message is queued for a later turn, so later drop notifications can be suppressed for peer senders.

## Discord inbound message classification

| Discord event | allow_from_bots? | Reply? | Core behavior |
|---|---:|---:|---|
| Human/operator message | no | either | Dispatch as existing human/operator input. |
| Allowlisted peer bot final output | yes | no | Dispatch with `AuthorKind: peer_bot`. |
| Allowlisted peer bot bridge reply | yes | yes | Ignore before core dispatch. |
| Unallowlisted bot | no | either | Ignore as before. |
