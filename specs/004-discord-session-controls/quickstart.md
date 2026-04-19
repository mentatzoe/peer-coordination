# Quickstart: Discord Session Controls

## Goal

Verify that the Discord transport now honors:

- explicit channel binding
- operator-only session opening
- `!stop` closes the current session
- `!resume` opens a new session

## Pre-flight

1. Configure the Discord platform with:
   - a valid `token`
   - `allow_from` with the operator listed first
   - `guild_id` if using per-guild slash registration
   - the new bound `channel_id`
2. Start `cc-connect` against the Phase 1 project config.
3. Ensure the bot can see both the bound channel and at least one unbound
   channel for negative testing.

## Dry-run checks

1. Post from the operator in an **unbound** channel.
Expected: no runtime dispatch into the peer-coordination session.

2. Post from a peer in the **bound** channel before the operator opens a
session.
Expected: no implicit session open.
Suggested setup: include that peer's Discord user ID in `allow_from` after the
operator so this check is validating the session gate rather than raw auth.

3. Post the operator seed in the **bound** channel.
Expected: a session opens and normal dispatch begins.

4. Issue `!stop`.
Expected: current session closes immediately.

5. Post from a peer again in the bound channel.
Expected: no continuation of the stopped session.

6. Issue `!resume`.
Expected: a new session opens.

7. Post from a peer in the bound channel.
Expected: the post is routed into the new session, not the stopped one.

## Verification commands

Run at minimum:

```bash
cd cc-connect
go test ./platform/discord ./core
```

If Discord-specific tests are split further during implementation, run the
narrower package set and record it in the implementation-complete handoff.
