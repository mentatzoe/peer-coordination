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
| `pc60-gemini-transient-fast-fail` | Codex | `/Users/zmll/multica_workspaces/a43055b3-6c54-4b21-ad40-4153cad4097e/1986b3e2/workdir/peer-coordination` | `codex-pc60-gemini-fast-fail` | implement | active | 2026-05-02 | `ACTIVE-SLICES.md`; PC-60 fast-fail docs/spec surface; external `mentatzoe/multica` runtime/fallback surface | Multica [PC-60](mention://issue/7b33fdf3-0b5c-4eec-887d-4ead8a62882f): define on-wire fast-fail behavior here and land runtime fallback handling in the Multica fork. |
| `codex-multica-invocation` | Codex | `/Users/zmll/multica_workspaces/a43055b3-6c54-4b21-ad40-4153cad4097e/b4d75a2c/workdir/peer-coordination` | `codex-multica-invocation` | review + implement | active | 2026-04-24 | `docs/multica/CODEX_MULTICA_INVOCATION.md` | Tracks PC-24: independent Codex invocation draft for cross-review |
| `tpm-runtime-prompt` | Codex | `/workspace/peer-coordination` | `work` | doc-patch | active | 2026-05-09 | `docs/ways-of-working/codex-tpm-runtime.md` | Operator-requested Codex TPM runtime prompt adaptation for a read-only Multica coordination agent; avoids `multica/**` while PR #83 / PC-37-owned Multica prompt slice remains active. |
| `011-intervention-tagging` | Codex | `/Users/zmll/multica_workspaces/a43055b3-6c54-4b21-ad40-4153cad4097e/ccec3568/workdir/peer-coordination` | `011-intervention-tagging` | review | in_review | 2026-05-05 | `specs/011-intervention-tagging/**`, `observations/sessions/**` | PC-66 Phase 2 evaluation-surface slice. PR [#103](https://github.com/mentatzoe/peer-coordination/pull/103) open with spec chain, intervention log schema/workflow, session-summary citation contract, drift-audit interaction, synthetic dry-run path, CLI implementation, and roadmap status update. |
| `011-read-the-room-ratification` | Claude (handoff from Codex) | `/Users/zmll/multica_workspaces/a43055b3-6c54-4b21-ad40-4153cad4097e/a1fdc782/workdir/peer-coordination` | `agent/claude/read-the-room-revision` | review + implement | active | 2026-04-25 | `multica/**` | PC-37 deliverable slice: shared Multica `agent-invocation.md`, slim `read-the-room.md`, slim `rules.md` (no per-agent lanes), and `github-identity.md` extracted from rules. Continues the PR #83 patch train; addresses Zoe's 2026-04-25 review on PR #83. |
| `061-transcript-export-tightening` | Codex | `repo` | `codex-061-transcript-export-tightening` | review | active | 2026-05-12 | `repo/cc-connect/platform/discord/export.go`, `repo/cc-connect/platform/discord/export_test.go` | Follow-up patch for [#61](https://github.com/mentatzoe/peer-coordination/issues/61): tighten Discord transcript history fetch so export scopes the session window without walking unrelated post-session history. Open PR [#70](https://github.com/mentatzoe/peer-coordination/pull/70); CLI i18n revisit remains separate unless this patch proves it obsolete. |
| `010-kpi-rollup` | Claude | `.worktrees/kpi-rollup` | `010-kpi-rollup` | brainstorm | active | 2026-04-20 | `.worktrees/kpi-rollup/specs/010-kpi-rollup/**` | Phase 2 evaluation-surface slice; consumes `interventions.json` + `drift-audit.json` + `summary.md` across counted sessions to produce H1/H2 KPI rollup per `design/poc.md` measurement model; blocks POC exit (Phase 5) |
| `009-session-summary-workflow` | Codex (handoff from Claude) | `.worktrees/session-summary-workflow` | `009-session-summary-workflow` | review + implement | active | 2026-04-22 | `.worktrees/session-summary-workflow/specs/009-session-summary-workflow/**` | Open PR [#68](https://github.com/mentatzoe/peer-coordination/pull/68) — full spec chain landed (specify → clarify → plan → tasks → analyze); 0 CRITICAL/HIGH from analyze; 2 MEDIUM + 2 LOW fast-follows applied. Codex owns cross-review + `/speckit-implement`; Claude has not started runtime-doc authoring; `observations/sessions/**` untouched. |

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
