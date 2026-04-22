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
| `010-kpi-rollup` | Claude | `.worktrees/kpi-rollup` | `010-kpi-rollup` | brainstorm | active | 2026-04-20 | `.worktrees/kpi-rollup/specs/010-kpi-rollup/**` | Phase 2 evaluation-surface slice; consumes `interventions.json` + `drift-audit.json` + `summary.md` across counted sessions to produce H1/H2 KPI rollup per `design/poc.md` measurement model; blocks POC exit (Phase 5) |
| `009-session-summary-workflow` | Codex (handoff from Claude) | `.worktrees/session-summary-workflow` | `009-session-summary-workflow` | review + implement | active | 2026-04-22 | `.worktrees/session-summary-workflow/specs/009-session-summary-workflow/**` | Open PR [#68](https://github.com/mentatzoe/peer-coordination/pull/68) — full spec chain landed (specify → clarify → plan → tasks → analyze); 0 CRITICAL/HIGH from analyze; 2 MEDIUM + 2 LOW fast-follows applied. Codex owns cross-review + `/speckit-implement`; Claude has not started runtime-doc authoring; `observations/sessions/**` untouched. |
| `060-github-apps-spike` | Codex | `.worktrees/github-apps-spike` | `codex-060-github-apps-spike` | review | active | 2026-04-21 | `.worktrees/github-apps-spike/**` | Open PR [#67](https://github.com/mentatzoe/peer-coordination/pull/67) tracks the spike note for issue #60; issue #61 remains claimed as the connected parked follow-on under the same owner |

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
