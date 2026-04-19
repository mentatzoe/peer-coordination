# Known Limitations

Curated list of transport / harness / tooling limitations that **affect the peer-coordination pilot**. Read before running Phase 3 sessions or interpreting observed behavior.

Each entry includes: what the limitation is, where it bites in the pilot, the workaround, and the tracking issue if filed.

**Full observation journal** with more detail (including non-pilot-critical observations, harness comparisons, etc.) lives at [`observations/harness-behaviors.md`](../observations/harness-behaviors.md). This doc is a curated subset focused on pilot impact.

---

## 1. Reaction events invisible to the native Discord plugin

**Summary**: Emoji reactions on bot-authored messages are NOT forwarded to the agent via the Claude Code `--channels` Discord plugin (`claude-plugins-official/discord@0.0.4`). Neither inbound events nor metadata on `fetch_messages` payloads carry reaction data.

**Pilot impact**: Blocks any reaction-based UX primitive — approval-via-react, "seen" heuristic, emoji coordination palette signals from operator to agent.

**Affects**: Station only (native plugin). Dalgos + Vigil (cc-connect-based) may have different semantics here — unverified; worth testing as part of pilot prep.

**Workaround**: Explicit text confirmation from operator. Pinned rules' emoji palette remains informational-only from the agent's perspective; agents can emit reactions outbound but can't observe inbound reactions.

**Upstream issue**: [`anthropics/claude-plugins-official#1477`](https://github.com/anthropics/claude-plugins-official/issues/1477) with two proposed fix shapes (push-path reaction event or pull-path `reactions` array).

**Observation entry**: [`observations/harness-behaviors.md` — 2026-04-18 "Reaction events completely invisible to the native Discord plugin"](../observations/harness-behaviors.md).

---

## 2. Bot-to-bot message visibility blocked by cc-connect filter

**Summary**: cc-connect's Discord platform unconditionally drops all bot-authored messages via `if m.Author.Bot { return }`. This prevents peer agents from seeing each other's outputs.

**Pilot impact**: **Blocker for emergent peer coordination**, which is the whole point of the POC per `VISION.md` H1. Without a fix, every exchange has to go through the operator as a relay — violates the non-orchestrated-coordination hypothesis directly.

**Affects**: Dalgos ↔ Vigil visibility (and any future Gemini agent) on Discord via cc-connect.

**Workaround**: Operator relays messages manually between bots. Not scalable; defeats the POC intent but unblocks immediate pairings.

**Upstream issue**: [`mentatzoe/cc-connect#4`](https://github.com/mentatzoe/cc-connect/issues/4) — proposes adding a per-project `allow_from_bots` allowlist so specific peer-bot IDs are exempt from the filter.

**Severity for pilot**: Priority to fix before Phase 3 baseline runs. Without it, H1 (convergence without mediator) can't be tested.

---

## 3. Discord reply-to context not forwarded

**Summary**: When the operator uses Discord's reply-to UI (quoting a specific earlier message), cc-connect doesn't parse `MessageReferenceID` or fetch the referenced message. The agent receives the current message text only; the operator's intent to pin context to a specific earlier message is lost.

**Pilot impact**: Operator's common habit of "reply-to the specific point I'm responding to" is invisible to agents. Agents have to infer context from text alone. Compounds with #2 when the referenced message is bot-authored.

**Affects**: Dalgos + Vigil (cc-connect-mediated). Station may or may not have the same issue via the native plugin — unverified.

**Workaround**: When reply-to context matters, paste the referenced text (or message ID) inline in the new message so the agent has it.

**Upstream issue**: [`mentatzoe/cc-connect#5`](https://github.com/mentatzoe/cc-connect/issues/5) — proposes a `ReplyTo` field on `core.Message` with bot-content gating on the same `allow_from_bots` allowlist from #4.

**Observation entry**: [`observations/harness-behaviors.md` — 2026-04-19 "cc-connect drops Discord reply-to context before reaching the agent"](../observations/harness-behaviors.md).

---

## 4. Permission-prompt session freeze (MITIGATED)

**Summary**: In `mode = "default"`, Claude Code's permission prompts travel via cc-connect's slash-command UI. If the prompt fails to render or round-trip, the session stalls indefinitely waiting for an unanswered prompt — eventually killed by the 2h idle-timeout safety.

**Pilot impact**: Would block any Dalgos session that triggers a Bash/Edit permission prompt if the slash-command UI isn't round-tripping. Observed live on 2026-04-19 before mitigation.

**Mitigation (applied 2026-04-19)**: Dalgos runs in `mode = "yolo"` (Claude Code's `--permission-mode bypassPermissions`) — permission prompts are skipped entirely at the child level. Vigil already runs in `yolo`. Same for any future agents; yolo mode is the pilot default.

**Tradeoff**: Yolo mode means unrestricted tool access per project. Acceptable for the peer-coordination scope (mostly docs + scaffolding); risk is low. Operator retains ceiling via Discord `!stop`, branch protection, and config-level project scoping.

**Tracking**: [`mentatzoe/cc-connect#3`](https://github.com/mentatzoe/cc-connect/issues/3) (filed earlier for the session-stuck pattern; mitigation via yolo avoids triggering it; structural fix may still be useful for the `mode=default` case).

**Observation entry**: [`observations/harness-behaviors.md` — 2026-04-18 "Silent drop" + later 2026-04-19 discussion](../observations/harness-behaviors.md).

---

## 5. Silent-drop: Station rendering Discord reply as text (PARTIALLY MITIGATED)

**Summary**: Station (Claude Code `--channels`) sometimes produces a response to an inbound Discord message as local text output WITHOUT invoking `mcp__plugin_discord_discord__reply`. From Discord's perspective, Station appears silent.

**Pilot impact**: Would be blocking if Station were the primary pilot agent. Post-2026-04-19 swap, Dalgos (cc-connect) is the peer-coord agent and doesn't hit this — cc-connect has no "text-only output" affordance; every outbound is an explicit send tool call. Station retains the channel for debug/relay; silent-drops there are recoverable via operator re-ping.

**Affects**: Station only. Dalgos + Vigil (cc-connect) are not affected by construction.

**Workaround**: Station enforces a pre-turn check (candidate mitigation): if the most recent inbound came from Discord, the turn must include at least one Discord reply tool call before completing.

**Observation entry**: [`observations/harness-behaviors.md` — 2026-04-18 "Silent drop"](../observations/harness-behaviors.md).

---

## 6. Channel-binding + thread-isolation tradeoff (no "shared channel+threads" mode)

**Summary**: cc-connect's `thread_isolation` flag is binary. With `channel_id` bound, `thread_isolation=true` gives per-thread sessions (threads in scope but isolated from the parent channel's session); `thread_isolation=false` drops thread messages entirely. No mode currently provides "threads in scope with session shared across parent + threads."

**Pilot impact**: If the pilot wants functional-topic threads with unified session context, it's not available. For now Dalgos + Vigil are configured with `thread_isolation=true` + no `channel_id` (responds anywhere allowlisted, per-thread sessions).

**Workaround**: Operator discipline — keep main conversation in the channel; use threads for genuinely side-branched topics where per-thread context reset is acceptable.

**Tracking**: Not yet filed upstream. Could be a feature ask (`thread_mode` enum: `isolated | inherit_parent | ignore`). Medium priority; will revisit if pilot surfaces a concrete need.

**Observation entry**: discussion trail in Discord + config-swap rationale (2026-04-19).

---

## 7. Operator-facing idle threshold is mental-model only (not runtime-enforced)

**Summary**: `design/poc.md`'s session definition uses a "1h idle" threshold as a gate for session-open semantics, but the cc-connect runtime does NOT enforce any idle-timeout detection. Sessions only close on explicit `!stop` / pin change / operator close.

**Pilot impact**: Operator has to mentally track idle time if they want session-bundle boundaries to reflect intended breaks. If the operator forgets to `!stop` before a long pause, the runtime keeps the session "open" indefinitely — when they return, the next exchange is treated as the same session unless they explicitly `!stop` + `!resume`.

**Workaround**: Operator discipline. Use `!stop` before stepping away when session boundaries matter. When authoring the session bundle post-hoc, split by intended session breaks via `meta.json.session_id` rather than relying on runtime state.

**Tracking**: No upstream issue; this is a deliberate design choice per [`specs/004-discord-session-controls/`](../specs/004-discord-session-controls/) FR-011 (operator-facing idle semantics, not runtime-enforced).

**Future option**: Could add a runtime `idle_ping` feature (notify operator after N minutes silence) without changing the close semantics. Deferred until pilot experience shows the need.

---

## Adding a new entry

When a new pilot-affecting limitation surfaces:

1. Log the detailed observation in [`observations/harness-behaviors.md`](../observations/harness-behaviors.md).
2. File an upstream issue if applicable (usually `mentatzoe/cc-connect` for cc-connect issues, `anthropics/claude-plugins-official` for Claude Code plugin issues).
3. Add a curated summary here with the workaround + issue link, so operators running pilots have a single digest to check.

Keep entries here tight — the journal is the source of truth for detail; this is the pilot-prep cheat sheet.
