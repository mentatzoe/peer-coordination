# Active Slices

Durable ownership and collision-avoidance registry for live or parked
slice-owned patch trains.

Use this file to answer:

- who owns a slice right now
- which worktree and branch are in play
- what phase the slice is in
- which surfaces another fresh session should avoid touching

This file is **not** a roadmap or historical archive. Keep only live,
parked-but-resumable, or review-stage work here.

Seeded from live worktree state, open PRs, and the current handoff on
2026-04-19. If a field is unknown for a legacy row, mark it explicitly and
update it on next touch.

Freshness matters. If a row no longer matches reality, it should be marked
stale rather than silently trusted.

| Slice / patch | Owner | Worktree | Branch | Phase | Status | Last confirmed | Do-not-touch surfaces | Notes |
|---|---|---|---|---|---|---|---|---|
| `session-reentry-protocol` | Codex | `.worktrees/session-reentry-protocol` | `codex-session-reentry-protocol` | implement | active | 2026-04-19 | `docs/ways-of-working/session-reentry.md`, `ACTIVE-SLICES.md`, `AGENTS.md`, `CLAUDE.md`, `docs/ways-of-working/pull-requests.md` | First-pass landing patch for discussion #55 |
| `007-session-bundle-init-cli` | Codex | `.worktrees/session-bundle-init-cli` | `007-session-bundle-init-cli` | plan complete; tasks next | active | 2026-04-19 | `.worktrees/session-bundle-init-cli/specs/007-session-bundle-init-cli/**`, `.worktrees/session-bundle-init-cli/AGENTS.md` | Clarify complete; planning artifacts written; implementation not started |
| `006-discord-transcript-export` | Codex | `.worktrees/006-discord-transcript-export` | `006-discord-transcript-export` | review | active | 2026-04-19 | `cc-connect/cmd/cc-connect/**`, `cc-connect/platform/discord/**`, `specs/006-*` (branch-local) | Draft PR [#52](https://github.com/mentatzoe/peer-coordination/pull/52); addressing Claude review |
| `002-cc-connect-relocation` | Codex | `.worktrees/cc-connect-relocation-impl` | `codex-002-cc-connect-relocation-impl` | implement follow-on | parked | 2026-04-19 | `.worktrees/cc-connect-relocation-impl/cc-connect/**`, `.worktrees/cc-connect-relocation-impl/specs/002-cc-connect-relocation/**` | Existing isolated Codex worktree; update on next touch if ownership/status changes |

## Update rules

Before substantive work on a slice:

1. update or confirm the row
2. claim ownership if you are taking the slice
3. set the phase and status truthfully
4. update `Last confirmed`
5. keep the do-not-touch surface specific enough for another fresh session

Mark a row `stale-needs-confirmation` before proceeding if any of these are
true:

- the listed worktree no longer exists
- the listed branch no longer exists
- the linked PR has merged or closed
- the row appears materially out of date to the fresh session

Do not take over a slice owned by another agent without recording a handoff note
in this file, the slice PR, or the slice discussion thread when one exists.
