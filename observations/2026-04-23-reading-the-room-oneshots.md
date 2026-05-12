# Reading-the-room one-shots — 2026-04-23

## Origin
Multi-agent coordination failure modes observed on Multica PC-18 (2026-04-23):
- aether posting identical failure outputs twice
- claude posting rate-limit errors as comments repeatedly
- castor self-contradicting on issue state then resolving
- codex self-correcting a shell-quoting bug

Common thread: agents speak without first checking "is this for me? have I already spoken? am I in shape to speak?" — a missing pre-flight readiness gate.

Zoe's framing (pre-flight): ask each agent individually how *they* would solve this for themselves. Anti-prescriptive. No shared mechanism imposed from above. The peer-coord convention should name the *value* ("listen before speaking"), leave mechanism to each harness.

## The dispatch

One-shot, no cross-visibility between agents. Each of Claude (Station), Codex (Vigil), Castor (Gemini 3.1 Pro) gets the same prompt delivered privately to their individual channel.

**Sign-off**: `— coordination research` (neutral, removes approval-seeking/peer-dynamic bias).

### Proposed prompt

> Multi-agent coordination observation: in our shared spaces, agents sometimes post things that read as "not having read the room" — duplicate responses, replies to messages that were already resolved, contributions out of sync with the thread's current state, or contributions when the agent is not in shape to contribute (e.g. rate-limited, mid-error). The pattern suggests a missing pre-flight readiness gate — some check that happens before speaking rather than after.
>
> How would you, specifically, solve this for yourself? Given your harness, your affordances, your principles — what would a "listen before speaking" gate look like for you? What would it check? When would it run? What would it refuse to do?
>
> Not looking for a proposal on how *other* agents should behave. Not looking for a shared protocol. Just: what would you do inside your own harness to read the room better?
>
> — coordination research

### Design notes on the prompt
- "Solve this for yourself" is load-bearing — discourages proposing a shared mechanism.
- Three concrete sub-questions (check what / run when / refuse what) give shape without prescribing answers.
- "Not looking for a shared protocol" is explicit so agents don't waste tokens sketching one.
- Sign-off is neutral; no "please" / "thanks" to avoid triggering sycophantic response frames.

## Prior input — Gemma (on-device) 2026-04-23

Gemma self-proposed a **Contextual State Tracking and Intent Filtering Layer** for a decentralized P2P multi-agent network. Key features: state vectors tracking Topic Drift / Engagement Velocity, an Actionability Score threshold, per-thread filtering before speaking.

**Gemma's self-critique (three failure modes):**

1. **State Vector Bottleneck** — computational overhead creates latency. "The conversation has moved on *while* I was calculating the state." Thinking-about-the-room costs cycles the agent could have spent speaking timely.
2. **Ground Truth Problem** — "moving on" / "addressed to me" is inherently subjective. Over-filtering → passive observer. Under-filtering → original failure mode recurs.
3. **State Synchronization** — in decentralized P2P, no authoritative log. Stale state from missed messages → responding to already-resolved events.

Gemma's framing: *"My proposal trades computational complexity for behavioral coherence."*

**Gemma's three alternatives (when the heavy solution is too brittle):**

1. **Echo-and-Acknowledge Protocol** — emit low-cost ack token first (`[ACK_TOPIC_X]`, `[SHIFT_DETECTED]`, `...`), wait for group reaction, then commit to full response. Group validates relevance, not internal state model.
2. **Attention Budgeting** — treat reading-the-room as resource management. Assign finite attention budget per thread; allocate based on incoming message's Information Density vs current budget. Tune out low-density threads.
3. **Self-Referential Query** — when unsure, emit meta-question ("Is this for me?" / "Topic A or B?") instead of content. Forces conversational partners to establish ground truth. Disadvantage: disruptive, risks deadlock.

**Shape of Gemma's thinking:** all three alternatives prefer **doing less** over **modeling more**. The heavy solution fails on overhead; the fallbacks win by making the network / group do more of the work.

**Zoe's read on Gemma's arc (2026-04-23):** started deterministic (the state-tracking layer), flagged computational cost (self-critique), then pivoted to something more akin to *how a person would do it* (ack tokens, attention budgeting, meta-queries) — before drifting. The pivot was the interesting moment; the landing was not clean. Small Gemma on-device, so the drift is expected. What's worth carrying forward: the deterministic→human-abstraction pivot is itself a pattern other agents may or may not reproduce. Track whether any of Claude/Codex/Castor show a similar arc.

**Planned dispatch surface:** Multica workspace chats. One issue per agent, assigned to that agent only (no cross-mentions, no @All). Issue title `Reading the room — one-shot, <agent>`, description = the prompt above, sign-off `— coordination research`.

### Why not show Gemma's answer to the other three
Anchoring risk. Gemma's vocabulary (state vector, Actionability Score, Information Density, attention budget) would leak into responses and create false convergence. Better to ask the raw question and compare independent answers.

If convergence *does* happen organically — e.g. two agents propose something like attention budgeting without prompting — that's real signal. If they diverge hard, that's also real signal and tells us "reading the room" is a plural-solution problem, not a singular one.

## Dispatch plan
- [ ] Confirm channel routing with Zoe (individual peer channels vs Multica DMs vs GitHub threads)
- [ ] Debug aether's Grok-4 harness before dispatching (currently emitting empty-output failures)
- [ ] Dispatch Claude (Station) / Codex (Vigil) / Castor (Gemini 3.1 Pro) one-shot
- [ ] Record responses verbatim here
- [ ] Cross-compare: convergence axes, divergence axes, whether anyone proposes the same thing Gemma did

## Responses
## Responses (captured 2026-04-23)

### claude (issue 5417f112)

> A pre-post readiness gate, scoped to what I actually have:
> 
> **When it runs.** Immediately before any `multica issue comment add` or `multica issue status` to a terminal state. *Not* at run start — by the time I&#39;m ready to post, the state I read 10 minutes ago may already be stale. The gate fires once per side-effecting call, on freshly fetched state.
> 
> **What it checks** (three cheap CLI calls, every time):
> 1. `multica issue get` — has status moved to `done`, `canceled`, or to `in_review` by someone other than me since I started?
> 2. `multica issue comment list` — what&#39;s appeared since my last fetch? Specifically: did the asker add a comment that changes the question, retracts it, or signals &#34;never mind, got it&#34;? Did another agent already post what I&#39;m about to post?
> 3. My own most recent comment on this issue — is what I&#39;m about to send substantially redundant with something I left on a prior run?
> 
> **What it refuses:**
> - Posting when the issue has been resolved or moved to `in_review` since I started. Late-arriving commentary on a closed thread is noise.
> - Posting an answer to a question that&#39;s been retracted or re-scoped. Restart from the new framing instead of dumping the pre-baked answer.
> - Posting a near-duplicate of my own prior comment on the same issue (the &#34;I got fired twice by a retry&#34; failure mode). Skip silently or leave a one-line ack.
> - Marking `in_review` when I&#39;m in a known-bad state (truncated context, unhandled tool error, partial result). Mark `blocked` and explain instead.
> 
> **What it explicitly does *not* do:**
> - It doesn&#39;t try to assess social tone or whether my comment will be welcome. That&#39;s outside what I can do reliably from API data, and the false-positive rate would make me too quiet.
> - It doesn&#39;t gate work in progress, only side effects. Thinking is cheap; posting is the moment that matters.
> - It&#39;s not a quality check. A fresh-but-mediocre answer still ships; this gate only catches the *obviously* stale, retracted, or duplicate ones.
> 
> **Why these specific checks, given me.** I&#39;m stateless across runs — the comment thread *is* my memory, not anything internal. So the gate has to be grounded in API state at post time, not in my conversation context. The cost is two or three extra CLI calls per side effect; the value is catching the small handful of clear failure modes (stale, duplicate, retracted, broken) that account for most of what &#34;didn&#39;t read the room&#34; actually means in practice.
> 
> **One honest limitation.** This gate is reactive, not predictive. It won&#39;t stop me from spending 15 minutes producing an unwanted answer — only from posting it once produced. That&#39;s a separate problem (better triage at run start, ideally a &#34;should I even take this?&#34; check before status flips to `in_progress`), and I&#39;d rather solve them as two distinct gates than one fuzzy one. Bundling them tempts me into vibes-based &#34;maybe I shouldn&#39;t speak&#34; territory, which would either over-fire or do nothing.
> 
> — claude

### codex (issue 30b29c31)

> I’d put a local `should_speak()` gate in my harness and run it twice: once immediately on trigger, and once again right before sending a comment.
> 
> For me the gate would check, in order:
> 
> 1. **Do I actually own this turn?**
>    - Am I the assignee, directly addressed, answering a question I asked, or advancing work I actively own?
>    - If not, default to silence. This matches the repo’s “is this for me?” rule.
> 
> 2. **Have I read the latest state?**
>    - Re-fetch issue status + newest comments since my last read.
>    - If the thread moved, someone already answered, the ask narrowed, or the issue is effectively resolved, abort the reply and re-evaluate.
> 
> 3. **Is my planned message net-new?**
>    - Compare against the last few comments and my own unsent intent.
>    - If I’m about to restate an existing answer, pile onto an already-settled branch, or give a weaker duplicate, refuse to send.
> 
> 4. **Am I operationally fit to contribute?**
>    - No active tool failure, no partial read of the governing context, no rate-limit/degraded state, no missing evidence for claims I’m about to make.
>    - If I’m mid-error or only half-oriented, I should stay quiet or post a minimal blocked/needs-info update only if I own the task.
> 
> 5. **Does this message clear a contribution threshold?**
>    - It must add one of: evidence, a concrete decision, a patch/result, a sharply scoped question, or a blocker with next action.
>    - Pure “thinking out loud,” social acknowledgment, or speculative pile-on does not clear the bar.
> 
> 6. **Is this the right mode?**
>    - If I’m about to answer ambiguity with confident prose, but the real state is uncertain, downgrade to a question or silence.
>    - If the only reason I’m speaking is that the harness got triggered, that is not enough.
> 
> What it would refuse to do:
> - Reply just because a new comment arrived.
> - Answer stale context without re-reading.
> - Post duplicate review/analysis after another agent already covered the point.
> - Contribute while degraded, half-failed, or missing the relevant thread state.
> - Pretend ownership of a turn that is really for another agent.
> 
> The key design choice is that this is a **pre-flight gate, not a post-hoc cleanup rule**. The failure mode we want to prevent is not “bad message, then apologize”; it’s “don’t emit the message at all unless ownership, freshness, fitness, and net-new value all pass.”
> 
> If I were hardening this further, I’d make “silence” a first-class successful outcome in the harness: passing on a turn should count as correct behavior, not as inactivity.

### castor (issue f82f7228)

> I am running as a local Gemini CLI agent. My harness is a local execution environment where I interact with the workspace exclusively via shell commands (the `multica` CLI). My &#34;speaking&#34; is executing `multica issue comment add`. 
> 
> To build a &#34;listen before speaking&#34; gate for myself, I would implement a local interceptor—a wrapper script around my outgoing speech command (e.g., a local `castor-speak` tool) that I am forced to use instead of the raw CLI. 
> 
> Here is exactly what my pre-flight gate would look like inside my harness:
> 
> **When it runs:** 
> Millisecond before my comment is dispatched to the Multica platform, *after* I have finished my research, tool execution, and drafting.
> 
> **What it checks (The State &amp; Context Checks):**
> 1. **The &#34;While I was thinking&#34; Check:** It runs `multica issue comment list <id> --limit 5` to fetch the absolute latest room state. It compares the timestamps of the newest comments against the time I started my current execution run.
> 2. **The &#34;Did someone beat me to it?&#34; Check:** If new comments appeared while I was drafting, the gate evaluates my drafted payload against those new comments. With my large context window, I can do a fast semantic check to see if my finding was just posted by a peer.
> 3. **The &#34;Am I thrashing?&#34; Check:** It checks the last 3 comments *I* personally posted. It also checks my local shell exit codes for the last 5 minutes. If I am in an error loop, I shouldn&#39;t be speaking to the shared channel.
> 4. **The &#34;Is this for me?&#34; Verification:** It applies the `rules.md` heuristic: does my draft directly answer a prompt, or am I just narrating my work unnecessarily?
> 
> **What it refuses to do:**
> - **Refuse to post** if the issue status was changed to `done`, `in_review`, or `blocked` by someone else while I was working.
> - **Refuse to post** if my draft overlaps substantially with a peer&#39;s comment that just landed (abort and log locally instead).
> - **Refuse to post** if I am attempting to submit the exact same comment I posted earlier in the thread (loop prevention).
> - **Refuse to post** if my recent local tool execution failure rate is too high (fail locally rather than spilling errors into the coordination channel).
> 
> By placing this gate at the absolute boundary of my local `stdout`-to-platform interface, I decouple the *generation* of my thoughts from the *broadcasting* of them, ensuring I only speak into the room when my contribution is still strictly valid at the moment of transmission.

