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
| `008-drift-audit-workflow` | Claude | `.worktrees/drift-audit-workflow` | `008-drift-audit-workflow` | specify complete; clarify/plan next | active | 2026-04-20 | `.worktrees/drift-audit-workflow/specs/008-drift-audit-workflow/**` | Spec + checklist landed on branch; 2 clarifications resolved inline (FR-008 arbitration signal, FR-012 POC-exit sweep); direct follow-on from merged spec 005 |
| `007-session-bundle-init-cli` | Codex | `.worktrees/session-bundle-init-cli` | `007-session-bundle-init-cli` | review | active | 2026-04-19 | `.worktrees/session-bundle-init-cli/specs/007-session-bundle-init-cli/**`, `.worktrees/session-bundle-init-cli/AGENTS.md`, `.worktrees/session-bundle-init-cli/tools/peer_session/**`, `.worktrees/session-bundle-init-cli/tests/peer_session/**`, `.worktrees/session-bundle-init-cli/peer-session`, `.worktrees/session-bundle-init-cli/observations/sessions/defaults.example.toml` | Implementation complete; analyze artifact and targeted unittest verification done; ready for PR review |
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
