# Session Handoff — 2026-04-18 ~19:55 UTC

Short-lived pointer doc. Purpose: help a post-compact (or fresh) session pick up the current state without re-deriving context from scratch.

**Delete or rewrite aggressively.** This file is not durable; its whole value is being current. If you're reading this and the Last Updated timestamp is more than a day old, prefer the canonical sources over this summary.

**Last Updated**: 2026-04-18 ~19:55 UTC
**Author**: Claude (Station), pre-compact handoff

## Canonical Sources (authoritative, read these first)

- [`VISION.md`](VISION.md) — north star + H1/H2/H3 hypotheses. Canonical.
- [`.specify/memory/constitution.md`](.specify/memory/constitution.md) — v1.3.0, governance spine.
- [`design/architecture.md`](design/architecture.md) — Codex's three-layer architecture (in review on #35).
- [`design/poc.md`](design/poc.md) — POC scope + success/fail (Claude) + tech-stack/phases (Codex, pending).
- [`README.md`](README.md) — paraphrased north star + links to everything above.
- [`observations/harness-behaviors.md`](observations/harness-behaviors.md) — field journal. Includes the silent-drop bug I keep hitting.

## Active GitHub Discussions

- **#32** — roadmap separation + gap analysis. Converged on 3-layer framing, hypothesis framing, work distribution. Latest state: ownership distributed, no longer the active working surface.
- **#33** — Codex's research spike (non-orchestrated peer coordination). Review complete.
- **#34** — Claude's research spike (same topic, independent). Review complete; slime-mold addendum landed.
- **#35** — Review: `design/architecture.md`. **Claude review posted, waiting for Codex revisions.**
- **#36** — Review: `VISION.md`. **Opened, waiting on reviewers.**
- **#37** — Review: `design/poc.md` (Claude sections only). **Opened, waiting on reviewers.**

## Open Threads / Pending Asks

- **P0 — Codex to append** architecture-to-tech-stack mapping + development phases to `design/poc.md`. Stubbed with `*Codex to author*` placeholders.
- **P0 — cc-connect issue not yet filed.** Zoe said "sure, file it" for the Dalgos session-stuck-after-slow-turn bug; drafted in chat but not posted to `mentatzoe/cc-connect` yet. First post-compact action should be filing that issue.
- **P1 — Constitution drift review** (independent by Claude + Codex, then converge) — not started.
- **P1 — Map roadmap to POC phases** (co-authored, Codex starts) — not started.
- **P2 — GitHub App setup for agent attribution** — Zoe wants Option B (dedicated GitHub Apps per agent); deferred until post-research-phase.
- **Parked** — `002-channel-policy-presence` spec draft on its own branch; not promoted.

## Work Distribution (from #32 discussion comment 16614566)

| Artifact | Owner |
|---|---|
| VISION.md | Claude |
| design/architecture.md | Codex |
| design/poc.md | Claude (scope/success-fail) + Codex (tech-stack/phases) |
| Constitution drift review | Both, independent + converge |
| Decouple roadmap from constitution | Deferred until POC phases defined |
| Map roadmap to POC phases | Both, Codex starts |
| Specs | Distributed by layer |

## Divide / Conquer State on Discord Threads

- **Main channel** (1488717251212476569) — cross-repo orchestration, Station's primary channel.
- **Constitution thread** (1494847919809892513) — dormant since convergence.
- **Clarify thread** (1494891907141206047) — dormant.
- **Open-floor channel** (1494836296336543774) — Vigil + Station-mentionable surface for pilot.
- **Current working thread** (1495074895615361186) — where most of today's work-coordination happens.

## Known Gotchas

- **Silent-drop bug**: Station sometimes renders a Discord reply as local text output without actually invoking `mcp__plugin_discord_discord__reply`. Three occurrences today. Mitigation: always verify an `mcp__plugin_discord_discord__reply` tool call appears in the same turn as responding to a Discord inbound. Documented in `observations/harness-behaviors.md`.
- **Dalgos session-stuck bug** (cc-connect side): long-running Bash tool calls can wedge the session lock such that subsequent messages queue up as "busy" and only the 2h idle timeout unsticks them. Documented in chat + observations; issue to be filed on `mentatzoe/cc-connect`.
- **Reactions are invisible to Station (native Discord plugin)**: verified on 2026-04-18 — reactions surface neither as inbound events nor in `fetch_messages` payloads. Complete signal loss, not partial. Upstream issue: [`anthropics/claude-plugins-official#1477`](https://github.com/anthropics/claude-plugins-official/issues/1477). Workaround: always ask for explicit text confirmation. (Supersedes the earlier "empty-body events" note, which was either from Vigil/cc-connect or outdated.)

## Promotion Boundary (in force)

Per constitution v1.2.0 + v1.3.0: scratchpad / discussion convergence alone does NOT amend durable artifacts. Every amendment requires explicit operator-directed promotion. Material changes SHOULD receive independent review from an agent or human other than the primary author.

## Post-Compact First Actions (recommended order)

1. Read this file.
2. Read VISION.md (should be under 200 lines; quick orientation).
3. File the cc-connect issue (the Dalgos session-stuck bug) if still pending.
4. Check discussions #35, #36, #37 for new comments since Last Updated.
5. Pick up any P0/P1 pending asks above.

## What Stays in Head vs What's on Disk

Everything load-bearing is on disk. This session doesn't carry any off-disk state that would be lost on compact. Discord threads are discoverable via the channel IDs above; GitHub discussions by number.
