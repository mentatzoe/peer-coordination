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

- Keep constitutions, specs, coordination docs, and decision records here.
- Treat repos like `cc-connect` and `personal-agent-setup` as downstream
  implementation or adoption targets.
- Do not let implementation details silently redefine the governance layer.

## Working Norms

- Use `ideas/peer-coordination.md` as the current live scratchpad until its
  stable decisions are promoted into the constitution or follow-on specs.
- Prefer explicit documentation of decisions, open questions, manual steps,
  and ownership boundaries.
- Keep governance separate from transport plumbing.
- Let agent style differences drift organically unless the operator asks for a
  formal rule.

## Speckit Flow

- Start with `/speckit-constitution`.
- Use `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, and
  `/speckit-tasks` for scoped follow-on work.
- Keep specification work here and code changes in the implementation repo
  where they belong.

## Collaborators & Harnesses

- **Zoe Lopez-Latorre** — operator. Uses **they/them** pronouns (hard rule; never she/her or he/him). Expressive, often reaches out via Discord voice messages — transcripts flatten affect, ask when tone is ambiguous.
- **Claude** (this agent) — reachable via three surfaces:
  - **Station** — Claude Code `--channels` / personal agent (default for cross-repo orchestration including this repo).
  - **Dalgos** — cc-connect bot scoped to vault-keeper only (renamed from Legion on 2026-04-17, Umbra Bibliothecam lore). Gated to mention-only as of 2026-04-17.
  - **Direct terminal sessions**.
- **Codex** — runs in the standalone Codex app (not CLI). Peer collaborator, not ambient.
  - **Vigil** — cc-connect bot, Codex-powered, peer-coordination scope. Live since 2026-04-17 via launchd daemon.
- Treat Claude and Codex as **co-primary peers**, not primary/secondary. Different access surfaces, peer authority.

## Related Repos

- **`mentatzoe/cc-connect`** (private fork of `chenhg5/cc-connect`) — transport layer. All transport MVP code changes for peer coordination land here, not in this repo. Local clone at `~/github/cc-connect/` with `origin=mentatzoe`, `upstream=chenhg5`.
- **`personal-agent-setup`** — agent configuration hub. The scratchpad originated there and was archived to `archive/from-personal-agent-setup/` when this repo was created.
- **`vault-keeper`** — Dalgos's target project; reference for file-level multi-agent conventions (`docs/multi-agent-parallel-work.md`).

## Current State (as of 2026-04-17)

- Scratchpad at `ideas/peer-coordination.md` — canonical design log, multi-turn conversation between Zoe, Claude (Station), and Codex (Vigil).
- Archive at `archive/from-personal-agent-setup/specs/003-peer-coordination-constitution/` — prior speckit attempt scoped incorrectly to `personal-agent-setup`; preserved for reference, not active.
- Transport MVP (in `mentatzoe/cc-connect`):

  | # | Item | Owner |
  |---|------|-------|
  | 1 | `!stop` / `!resume` transport detection | Vigil (Codex) |
  | 2 | Open-floor mode + no-self-loop guard | Vigil (Codex) |
  | 3 | Agent-initiated emoji reacts | Dalgos (Claude) |
  | 4 | Approval-via-react workflow | Dalgos (Claude) |
  | 5 | Pinned-rules ingestion at session start | Dalgos (Claude), second pass |

- Pilot channel: Discord `#open-floor` (`1494836296336543774`), mention-only until MVP #1/#2 land, then flips to open-floor mode.
- Dalgos cc-connect config: mention-only, `guild_id` set, `respond_to_at_everyone_and_here = false`, `work_dir=/Users/zmll/github/vault-keeper`.

## Reference Material

- `ideas/peer-coordination.md` — live scratchpad. Read before proposing policy changes; append turns rather than rewriting history.
- `archive/from-personal-agent-setup/specs/003-peer-coordination-constitution/spec.md` — prior constitutional draft. Useful as input for the real constitution; scope was wrong (targeted `personal-agent-setup` instead of this standalone repo).
- `.specify/memory/constitution.md` — speckit constitution template, not yet filled in. First real spec work.

## Session Norms for Claude

- Before proposing state-changing transport or runtime config changes, verify the target (which bot, which config file) and request explicit approval (✅ react or text "go") — matches the approval policy in the scratchpad.
- Verify bot identity from the inbound Discord `chat_id` against the bot map before signing "via X" in any turn; do not infer from conversation topic.
- When editing the scratchpad, append a dated turn signature; do not rewrite prior turns.
