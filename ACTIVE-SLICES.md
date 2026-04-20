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
| `009-session-summary-workflow` | Claude | `.worktrees/session-summary-workflow` | `009-session-summary-workflow` | specify | active | 2026-04-20 | `.worktrees/session-summary-workflow/specs/009-session-summary-workflow/**` | Phase 2 evaluation-surface follow-on to merged spec 008; produces `summary.md` per spec 001 FR-012 from a closed session bundle |
| `060-github-apps-spike` | Codex | `.worktrees/github-apps-spike` | `codex-060-github-apps-spike` | spike | active | 2026-04-20 | `.worktrees/github-apps-spike/**` | Active patch train for issue #60; issue #61 is connected and claimed as a parked follow-on under the same owner |
| `007-session-bundle-init-cli` | Codex | `.worktrees/session-bundle-init-cli` | `007-session-bundle-init-cli` | review | active | 2026-04-19 | `.worktrees/session-bundle-init-cli/specs/007-session-bundle-init-cli/**`, `.worktrees/session-bundle-init-cli/AGENTS.md`, `.worktrees/session-bundle-init-cli/tools/peer_session/**`, `.worktrees/session-bundle-init-cli/tests/peer_session/**`, `.worktrees/session-bundle-init-cli/peer-session`, `.worktrees/session-bundle-init-cli/observations/sessions/defaults.example.toml` | Implementation complete; analyze artifact and targeted unittest verification done; ready for PR review |

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
