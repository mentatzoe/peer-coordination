# Harness Behavior Observations

> **Purpose.** Running field journal of observed behavior differences across
> agent harnesses (cc-connect codex adapter vs Claude Code `--channels` plugin
> vs others) operating in the same Discord channels with the same operator.
>
> **Not governance.** This is an observation log, not a policy artifact. It
> informs future specs (especially the Transport MVP Spec's peer-reply
> behavior section) without being one.
>
> **Scope.** Harness + tooling differences — same or similar underlying models,
> different rendering / routing / context surfaces. Model-to-model comparisons
> belong elsewhere.

## How to add an entry

Append a new `##` section at the bottom. Each entry has:

- **Date/time (UTC)** in the heading
- **Harnesses observed** — which two (or more) are being compared
- **Observation** — what was noticed, ideally with a specific example
- **Framing** — the tradeoff or hypothesis; call out what's tentative
- **Implication** — where this shows up in spec/design work, if anywhere

Keep entries short. A paragraph per field is usually enough. If an observation
grows into a pattern worth ratifying, promote it to the Transport MVP Spec or
a follow-on spec and leave a `→ promoted to [link]` note here.

---

## 2026-04-18 — Mention disambiguation across harnesses

**Harnesses observed:** Station (Claude Code `--channels` plugin) vs Vigil (cc-connect codex adapter).

**Observation:** When Zoe @-mentioned Station in a threaded Discord reply saying *"Codex made this amendment on my request, please emoji react as ack or reopen the scratchpad if you'd like to discuss,"* Station correctly inferred "mentioned as subject / addressed for action" and responded with an emoji react. When a similar pattern occurs in the cc-connect-mediated channel for Vigil — an @-mention where the agent is referenced rather than addressed — Vigil defaults to "this is for me to respond to" and tries to help (e.g., rewrote Zoe's message as if she were asking for a better draft). Vigil's own framing: *"in a threaded reply, Claude could infer the mention was informational rather than an addressed handoff; in the shared cc-connect channel, that inference is weaker or absent."*

**Framing:** Thread context + reply metadata preserves enough signal for subject-vs-addressee disambiguation; cc-connect's current routing appears to thin that out, leaving @-mentions as the strongest signal the agent keys on. Tentative — possibly narrower than "all cc-connect," could be specific to the codex adapter's context construction.

**Implication:** Explicitly in scope for the Transport MVP Spec's peer-reply behavior section. Candidate rule: peer-reply logic should consider (reply context, addressee vs subject, operator-to-agent vs operator-about-agent) rather than keying only on mention presence.

---

## 2026-04-18 — Register: coworker vs tool

**Harnesses observed:** Station vs Vigil.

**Observation:** Zoe's framing: *"speaking to Claude (via Station) feels more like a coworker, speaking with Codex via cc-connect feels more like a tool."* Concretely: Vigil renders every tool call visibly in Discord (`💭 thinking`, `🔧 Tool #N: Bash`, `🧾 Bash`, `🟢 Status: completed`, `🔢 Exit: 0`, partial output); Station posts distilled results with key code or diff snippets only. Vigil also appends a structured footer on every message (`*gpt-5.4 · high · N% left · ~/github/peer-coordination*`) — model, reasoning, context-remaining, pwd. Station does not.

**Framing:** Tradeoff, not ranking. Tool register makes agent state legible and debuggable; conversational register feels natural but is harder to inspect. Both valuable; best mode likely depends on task (debugging / pair-programming favors tool register; design / brainstorming favors conversational).

**Implication:** Not a governance concern. Possibly a knob on the cc-connect codex adapter — `progress_style = "compact"` is already set in the Vigil config, suggesting either the setting isn't honored, or "compact" still surfaces more than Station does. Worth checking the adapter's render logic if channel noise becomes a UX issue.

---

## 2026-04-18 — Pipe-liveness signal gap (and mitigation)

**Harnesses observed:** Station (mitigated going forward) vs Vigil.

**Observation:** Zoe reported triple-messaging Station when response latency was unclear — no visible ack meant it was hard to tell if the pipe had broken vs if Station was just working. cc-connect surfaces tool calls, which doubles as an implicit "I'm alive" signal; Station doesn't.

**Framing:** The coworker register loses out on pipe-liveness signals that the tool register gets for free. Doesn't mean we need to migrate to tool register — but an explicit "received, working" signal would cover the gap without collapsing the register.

**Implication:** Behavior change adopted by Station on 2026-04-18: react 👀 on inbound Discord messages before starting substantive work (search, edit, commit). Quick text-only replies don't need it; the reply is the ack. Maps to the emoji palette from the original Principle VI discussion — fitting that it becomes an actual behavior.

---

## 2026-04-18 — "Silent drop" failure mode when agent drafts text without invoking the Discord reply tool

**Harnesses observed:** Station (Claude Code `--channels` plugin).

**Observation:** Station twice in a 15-minute window produced a response to an inbound Discord message by rendering the reply text in its local/conversation output WITHOUT invoking `mcp__plugin_discord_discord__reply`. From the operator's perspective on Discord, Station appeared silent for 75+ minutes. First instance: response to "Is item 5 what defines the heuristic for cooperation behaviour" (10:31 UTC inbound → no Discord reply until operator pinged at 11:47 UTC). Second instance: response to "What happened to item 2?" (11:49 UTC inbound → no Discord reply until operator pinged at 11:53 UTC).

**Framing:** Station's harness conflates "speaking" (textual output in the conversation) with "sending" (actually transmitting to the inbound channel). Claude-Code-in-channels mode inherits the terminal-session habit of "type a response, done" — but in a Discord-mediated session, the textual output doesn't reach the channel unless the Discord reply tool is explicitly invoked. Not hypothetical: happened twice in this session. Codex's cc-connect harness wouldn't hit this because every outbound message in cc-connect is explicitly a `Send` tool call with no "text-only output" affordance.

**Implication:** Station should treat "responding to a Discord inbound" and "rendering text locally" as distinct operations. Heuristic to adopt: **if an inbound arrived through Discord, the response MUST go out via `mcp__plugin_discord_discord__reply`.** Textual output in the conversation is supplementary (mostly for the terminal operator watching the session live), not a substitute for the Discord reply.

Related to the earlier "pipe-liveness" observation — both stem from the coworker register lacking explicit send/receive surfaces. The earlier `👀`-on-inbound fix catches the "am I being worked on" case; this observation catches the "did the work actually ship" case. Both are symptoms of the same class of bug.

**Candidate mitigation:** add a pre-turn check that when the most recent inbound is a Discord channel message, at least one `mcp__plugin_discord_discord__reply` call must appear in the same turn before considering the response complete. Harness-level enforcement, not agent-level discipline — discipline already failed twice.

---

## 2026-04-18 — Reaction events completely invisible to the native Discord plugin

**Harnesses observed:** Station (Claude Code `--channels` plugin, specifically `claude-plugins-official/discord@0.0.4`).

**Observation:** When Zoe added emoji reactions to Station's messages in the designated open-floor channel, Station received **no signal at all** — neither an inbound event nor any metadata on the message when subsequently fetched. Verified both push and pull paths live during the session:

- **Push (inbound events)**: zero events between Zoe's text messages over several turns where Zoe was actively reacting. No empty-body events, no reaction-typed events, nothing.
- **Pull (`mcp__plugin_discord_discord__fetch_messages`)**: fetched the last 10 messages from the channel; the returned payload for each message contains only `author`, `text`, `timestamp`, `message_id` — no `reactions` array, no count, no emoji field.

This is a **stronger** claim than the prior SESSION-HANDOFF note ("empty-body events arrive"): the behavior is complete invisibility, not partial data. Either the prior observation was from a different harness (possibly Vigil via cc-connect) or the plugin behavior changed between sessions. Today's observation is the tested ground truth.

**Framing:** The plugin offers `mcp__plugin_discord_discord__react` for outbound reactions (agent-to-Discord) but no symmetric inbound path for user-to-agent reactions. This breaks symmetry and rules out any reaction-based UX primitive (✅ approve, 👀 seen, 🚫 reject, 🤔 pushback) as a human-in-the-loop signal until fixed.

**Implication:** Blocks the peer-coordination POC's planned approval-via-react MVP item (transport-layer capability #4) and the emoji-palette workflow more broadly. Upstream issue filed at [`anthropics/claude-plugins-official#1477`](https://github.com/anthropics/claude-plugins-official/issues/1477) with two proposed fix shapes (push-path inbound event or pull-path `reactions` array on `fetch_messages`).

**Workaround until resolved:** explicit text confirmation is the reliable channel for anything semantically meaningful. Continue to ignore any empty-body inbound that does manage to come through (currently none observed on Station).

---

## 2026-04-19 — Broadcast-created thread did not bind back to the existing working session

**Harnesses observed:** Vigil / Codex via the Discord-facing transport surface (`cc-connect`-mediated workflow).

**Observation:** Zoe created a broadcast thread intending to continue the existing working session through that thread. Instead, the new thread appeared to behave like a **new session surface** rather than a continuation of the existing one. From the operator's perspective, thread creation did not reliably route back into the already-running working context.

**Framing:** Tentative but important. This suggests thread identity is not yet a stable enough addressing primitive for session continuity. Current session binding may be keyed more strongly to the immediate invocation surface or routing path than to the operator's intended thread target. In practice, creating a new thread can fork context rather than preserve it.

**Implication:** Transport-spec relevant. This affects:

- channel/thread binding semantics
- session continuity and recovery behavior
- how safe it is to use thread creation as an operator control surface

At minimum, thread creation should not be assumed to preserve an active working session unless the transport layer makes that guarantee explicit.

---

## 2026-04-19 — cc-connect drops Discord reply-to context before reaching the agent

**Harnesses observed:** Dalgos (cc-connect + Claude Code CLI). Likely same on Vigil (cc-connect + Codex CLI) by construction.

**Observation:** Operator used Discord's reply-to UI (quoting a specific earlier message for context) when sending a new message to Dalgos. The agent received the new message's text + mentions, but NOT the quoted message's content or reference. From the agent's perspective, the message is freestanding; the operator's intent to pin context to a specific earlier message is lost.

Concrete instance: operator quoted Station's `"Done. Daemon restarted from contained cc-connect binary — both bots live."` and asked `@Dalgos can you reply to this message I'm quoting just saying hi?`. Dalgos responded `"I don't see a quoted message — can you paste it or share the channel/message ID?"`, confirming cc-connect did not forward the reply-to context.

**Framing:** Two plausible root causes that likely both contribute:

1. **Reply-to payload not included**: Discord's gateway delivers `MessageReferenceID` on message events, but cc-connect's `handleMessageCreate` in `platform/discord/discord.go` constructs the `core.Message` from `m.Content` + attachments + mentions only — no `message_reference` field is looked up, fetched, or forwarded.
2. **Bot-author filter drops reply-to content when the referenced message is bot-authored** (related to [`mentatzoe/cc-connect#4`](https://github.com/mentatzoe/cc-connect/issues/4)): even if (1) were fixed, messages referencing a bot-authored earlier message would be filtered at the `if m.Author.Bot { return }` boundary in whatever lookup path fetches the reference content.

These are separable: (1) is a missing-field gap on ALL reply-to, (2) is a bot-filter interaction specific to quoted bot content.

**Implication:** Affects Layer 1 transport fidelity. Operators commonly use reply-to for context-pinning ("I'm asking about THIS earlier point"). Currently that intent is invisible to the agent, so the agent has to infer from text alone. Workaround: paste the referenced text or message ID inline.

**Upstream fix:** cc-connect should:

- parse `MessageReferenceID` from the inbound event
- fetch the referenced message (cached where possible)
- include a `ReplyToMessage` field on `core.Message` (or equivalent) with the referenced author, timestamp, and content
- gate bot-authored reference content on the same `allow_from_bots` allowlist proposed in cc-connect issue #4

Issue to be filed at `mentatzoe/cc-connect` as a sibling of #4; operator has flagged as "concern for another time" — not blocking Phase 1 but worth tracking.

**Workaround until resolved:** when the operator uses Discord's reply-to UI for context, the operator also pastes the relevant reference text (or a `<message-id>` link) in the message body so the agent has it inline.
