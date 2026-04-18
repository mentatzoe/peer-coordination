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
