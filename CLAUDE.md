# peer-coordination Project Guidance

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

## Purpose

This repository is the home for the peer-coordination standard.
It exists to define how multiple agents collaborate, not to host the transport
implementation itself.

## Scope Boundaries

- Keep constitutions, specs, coordination docs, and decision records at the
  repo root.
- Treat the contained `cc-connect/` workspace as an implementation surface
  inside this repo (subordinate to repo-root governance/design), and downstream
  repos such as `personal-agent-setup` as consumers of this standard.
- Do not let implementation details silently redefine the governance layer.

## Working Norms

- Use `ideas/peer-coordination.md` as the current live scratchpad until its
  stable decisions are promoted into the constitution or follow-on specs.
- Prefer explicit documentation of decisions, open questions, manual steps,
  and ownership boundaries.
- Keep governance separate from transport plumbing.
- Let agent style differences drift organically unless the operator asks for a
  formal rule.
- For spec slices and slice-owned follow-on patches, follow the Speckit
  git-hook branch workflow when available, and merge via PR by default. See
  `docs/ways-of-working/pull-requests.md`. Direct-to-`main` should be limited
  to trivial fixes or explicit operator instruction.

## Speckit Flow

- Start with `/speckit-constitution`.
- Use `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, and
  `/speckit-tasks` for scoped follow-on work.
- Keep specification work at the repo root. Code changes land in the
  implementation surface they belong to — including the contained
  `cc-connect/` workspace for transport-side work (subordinate to repo-root
  governance).

## Collaborators & Harnesses

- **Zoe Lopez-Latorre** — operator. Uses **they/them** pronouns (hard rule; never she/her or he/him). Expressive, often reaches out via Discord voice messages — transcripts flatten affect, ask when tone is ambiguous.
- **Claude** (this agent) — reachable via three surfaces:
  - **Station** — Claude Code `--channels` / personal agent. Terminal-only for cross-project work (vault-keeper, shani, personal-agent-setup, etc.). Retains Discord `--channels` allowlist for peer-coord + vault-keeper channels as a debug/relay surface when Dalgos/Vigil drop the ball.
  - **Dalgos** — cc-connect bot, Claude-Code-powered, **peer-coordination scope** (as of 2026-04-19 agent swap; moved off vault-keeper). Runs in `yolo` mode (unrestricted tool access) to eliminate the permission-prompt freeze class observed 2026-04-19. Identified by Discord user ID `1494761296686481509`. Project-bound: `work_dir=/Users/zmll/github/peer-coordination`.
  - **Direct terminal sessions**.
- **Codex** — runs in the standalone Codex app (not CLI). Peer collaborator, not ambient.
  - **Vigil** — cc-connect bot, Codex-powered, peer-coordination scope. Live since 2026-04-17 via launchd daemon. As of 2026-04-19, project-bound to `/Users/zmll/github/peer-coordination` (no more `/workspace bind` per session). Runs in `yolo` mode.
- Treat Claude and Codex as **co-primary peers**, not primary/secondary. Different access surfaces, peer authority.
- **2026-04-19 agent-swap**: Dalgos took over peer-coordination work from Station (always-on session via cc-connect + Yolo mode avoids session freezes); Station moved to terminal-only coverage for vault-keeper and other projects. Vault-keeper is no longer bound to cc-connect; reach Station via terminal.

## Related Repos

- **`mentatzoe/cc-connect`** (private fork of `chenhg5/cc-connect`) — source fork
  for the contained `cc-connect/` workspace now living under this repo. Active
  Phase 1 transport MVP changes land in `cc-connect/` here; lineage remains
  `origin=mentatzoe`, `upstream=chenhg5`.
- **`personal-agent-setup`** — agent configuration hub. The scratchpad originated there and was archived to `archive/from-personal-agent-setup/` when this repo was created.
- **`vault-keeper`** — Dalgos's target project; reference for file-level multi-agent conventions (`docs/multi-agent-parallel-work.md`).

## Current State

*[`ROADMAP.md`](ROADMAP.md) is the SOT for sequencing, ownership, and status; this section captures stable project context that doesn't belong in the roadmap.*

- Scratchpad at `ideas/peer-coordination.md` — canonical design log, multi-turn conversation between Zoe, Claude (Station), and Codex (Vigil).
- Archive at `archive/from-personal-agent-setup/specs/003-peer-coordination-constitution/` — prior speckit attempt scoped incorrectly to `personal-agent-setup`; preserved for reference, not active.
- Sequencing, ownership, and current-next work now live in [`ROADMAP.md`](ROADMAP.md). The older Transport MVP table that used to sit here was a 2026-04-17 snapshot and is no longer authoritative.
- Active transport implementation surface: contained `cc-connect/` workspace at
  repo root. Historical references to `~/github/cc-connect/` are now lineage,
  not the primary work surface.

- **Discord channel map**:
  - `#open-floor-work` (`1495074895615361186`) — Station-work-thread / operational working surface for peer-coordination implementation. Dalgos + Vigil both respond here. This channel was renamed from `#open-floor` on 2026-04-19; ID unchanged.
  - `#open-floor` (`1494836296336543774`) — earlier generic working channel, Station allowlisted.
  - `#open-floor-pilot` (`1495441240194289758`) — the actual Phase 3 pilot channel. No bots bound yet; dedicated pilot-scoped bots TBD when pilot starts.
  - `1488717251212476569` — main cross-repo orchestration channel (Station).
  - `1494847228655829073` — vault-keeper / "Dalgos work" channel. Post-swap Dalgos is OFF this channel; Station allowlisted for debug access.
- **cc-connect daemon**: runs from contained `~/github/peer-coordination/cc-connect/cc-connect` (not the earlier external `~/github/cc-connect/` path). launchd plist at `~/Library/LaunchAgents/com.cc-connect.service.plist` points at the contained binary. Web admin enabled on port 9820 (Tailscale-accessible). Management token in `~/.cc-connect/config.toml` under `[management]`.
- **Known limitations** affecting the pilot are tracked at [`docs/known-limitations.md`](docs/known-limitations.md). Read before running pilot sessions.

## Reference Material

- `ideas/peer-coordination.md` — live scratchpad. Read before proposing policy changes; append turns rather than rewriting history.
- `archive/from-personal-agent-setup/specs/003-peer-coordination-constitution/spec.md` — prior constitutional draft. Useful as input for the real constitution; scope was wrong (targeted `personal-agent-setup` instead of this standalone repo).
- `.specify/memory/constitution.md` — speckit constitution template, not yet filled in. First real spec work.

## Session Norms for Claude

- Before proposing state-changing transport or runtime config changes, verify the target (which bot, which config file) and request explicit approval (✅ react or text "go") — matches the approval policy in the scratchpad.
- Verify bot identity from the inbound Discord `chat_id` against the bot map before signing "via X" in any turn; do not infer from conversation topic.
- When editing the scratchpad, append a dated turn signature; do not rewrite prior turns.
