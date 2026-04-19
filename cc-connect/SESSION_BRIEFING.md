# Session briefing — cc-connect evaluation

I just cloned cc-connect (https://github.com/chenhg5/cc-connect) into this directory
to evaluate whether it fits my workflow, and if so, stand up a minimal prototype
before committing to it. Don't install or run anything destructive until I approve.

## My setup

- macOS, Claude Code v2.1.80+, shell is zsh.
- I run multiple concurrent Claude Code sessions, one per project. Current active projects:
  - `~/github/vault-keeper`
  - `~/github/shani`
  - `~/github/verbose-eureka`

  Plus one "overarching" personal-agent session.
- I already have a Discord bot and server configured. Token + access policy live at
  `~/.claude/channels/discord/` (with `dmPolicy=allowlist` and guild channel
  `1494411823389085727` opted in). A second test channel `1494734138060701857`
  also exists for vault-keeper.
- **I want Codex bound alongside Claude Code from the start.** Codex tokens are
  now available again. The existing Station bot is my Claude identity;
  I'll create a second Discord app for a Codex bot. The point of going with
  cc-connect was specifically to have Claude + Codex coexist in shared
  project channels. So the prototype target is now:
  - Claude Code on vault-keeper (existing Station bot)
  - Codex on vault-keeper (new Discord bot, to be created)
  - Both in the same project channel/thread, each addressable by @-mention

## Preferences / constraints

- I want chat-native UX, NOT Remote Control (already tried, didn't like — it's
  "CLI-under-glass"; I use Termius+Tailscale+tmux for raw CLI from mobile).
- Prefer: bot-per-agent-identity (one `@zoe_claude_bot` shared across projects),
  project channels where multiple agent-bots can eventually coexist.
- Happy to run a persistent daemon if needed (already run an RNS one).
- I dislike Telegram enough to avoid it if Discord works.

## Task for this session

1. Read the cc-connect README, `docs/`, and any quickstart material. Summarise the
   architecture in ≤5 bullets. Specifically answer:

   a. Does it support one bot across multiple projects, or does each project need
      its own bot?

   b. Does it support shared channels where multiple agent-bots coexist (for the
      "@claude and @codex both in #vault-keeper" future)?

   c. How does it map "a Discord message" to "a specific Claude Code session
      in the right project directory"? Thread-per-session? Channel-per-project?

   d. Does it handle worktrees, or expect me to manage those separately?

   e. Is there a reliable path to reuse my existing Discord bot token and
      `access.json`, or does cc-connect want its own Discord app?

2. Draft a minimal `config.toml` for TWO agents (Claude Code via the existing
   Station Discord bot, and Codex via a new Discord bot I'll need to create)
   bound to ONE project (vault-keeper). Show me the config before writing to
   disk. Cover:
   - `[[providers]]` entries for both Anthropic (Claude) and whatever Codex
     needs
   - Two `[[projects]]` entries, same `dir`, different `agent.type`, each with
     its Discord bot token
   - How `thread_isolation` should be set so both bots can live in the same
     channel cleanly
   - Whether `/bind claudecode` + `/bind codex` slash-commands are needed at
     runtime, or if static config is enough

3. List every step needed to run the prototype end-to-end, flagging anything
   that requires my intervention (permission grants, Discord channel setup,
   new tokens, etc.).

4. Identify risks or gotchas specific to my setup (existing bot conflict,
   macOS-specific issues, permission mode implications — cc-connect may run
   Claude in `-p` / non-interactive mode, which affects permission prompts).

5. Report back. Wait for approval before any destructive action (installing
   deps, starting the bridge, modifying `~/.claude/channels/discord/`).

## Out of scope

- Other projects beyond vault-keeper until vault-keeper is proven working
  with both Claude + Codex.
- Any contributions to cc-connect itself.
- Any attempt to modify my existing Discord (Station) bot in ways that break
  its current access.json / allowlist.
- Building a custom orchestrator for autonomous agent-to-agent conversation.
  For now, "both bots in the same channel, I address each by @-mention, with
  `cc-connect relay send` as an explicit CLI primitive for cross-agent
  delegation" is the target UX. If that's insufficient after real use, we'll
  revisit.
- **`run_as_user` / multi-Unix-user isolation.** I know cc-connect supports
  this (per-project, `sudo -n -iu <user>`, with doctor preflight checks). It's
  the right tool for truly unattended autonomous agents like OpenClaw, but
  overkill for Claude + Codex running under my supervision. Isolation target
  for this prototype is git worktrees + branch discipline — NOT separate
  Unix users. Do not suggest or configure `run_as_user` unless I raise it
  again.

## Prior-session context (for your reference)

This briefing came out of a long brainstorming session in `~/github/vault-keeper`
where we compared: official Discord/Telegram channels plugins, a custom relay
daemon, Remote Control, and existing community bridges. We settled on "try
cc-connect" because it's the only one that matches the full brief
(multi-agent + multi-platform + project-based routing + shared-channel
multi-agent coexistence) — 5.4k stars, actively maintained, much cheaper than
reinventing.

**Calibration on cc-connect's multi-agent story (confirmed from docs/usage.md
and docs/discord.md):**

- **What works**: two bots (Claude + Codex) coexist in one Discord channel,
  each as its own Discord app. `thread_isolation` keeps their replies clean.
  User addresses whichever by @-mention. `/bind claudecode` and `/bind codex`
  bind multiple agent types from within chat.
- **What's a CLI primitive**: inter-agent relay via
  `cc-connect relay send --to codex "..."` — works, but it's explicit
  delegation, not autonomous conversation.
- **What isn't there**: autonomous "hey Claude, ask Codex" agent-to-agent
  conversation. If we want that later, we build a thin orchestrator on top.

Key rejection reasons for alternatives:

- **Remote Control**: CLI-under-glass, not chat-native.
- **Official --channels Discord plugin**: single-session-per-bot-token; can't
  handle multiple concurrent Claude sessions on one bot.
- **Custom relay daemon we were about to design**: cc-connect already does
  most of this (multi-project routing + multi-platform + multi-agent binding).
- **claude-mpm**, **ruflo**, **ComposioHQ/agent-orchestrator**, **overstory**,
  **metaswarm** — checked; none has a richer Discord multi-agent story than
  cc-connect, and most skip Discord entirely.
