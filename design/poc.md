# POC — Peer Coordination Proof of Concept

**Status**: Claude-authored sections revised 2026-04-18 per [discussion #37](https://github.com/mentatzoe/peer-coordination/discussions/37) feedback and downstream of the VISION.md revision round. Codex's Architecture → Tech Stack Mapping and Development Phases sections remain stubbed pending Codex's contribution per work distribution on [#32 comment 16614566](https://github.com/mentatzoe/peer-coordination/discussions/32#discussioncomment-16614566).

**Owners**: Claude (scope, success/fail conditions) + Codex (tech-stack mapping, development phases). Co-authored overall.

**Top-level reference**: [`VISION.md`](../VISION.md) for the hypotheses this POC is organized around.

---

## Purpose

Define the first concrete test harness for the peer-coordination framework. This is the experiment through which H1, H2, and H3 from the vision doc are evaluated (H1/H2 directly; H3 by design-time constraint).

This is a **probe, not the product**. The POC produces observations that inform whether the non-orchestrated peer-coordination framework is viable, and if so, what shape it takes. The POC is not the framework; the framework is whatever we learn from running this POC (and any follow-ons).

## Scope *(Claude-authored)*

### What the POC IS

The first POC is a **two-agent conversational pilot in a designated Discord channel**, with a possible three-agent stretch session later. Concretely:

- **Primary participants**: two peer agents, each described by its **transport** and its **agent harness** (the CLI that actually runs the session loop, tool use, and context management):
  - **Dalgos** = Discord transport via cc-connect + Claude Code CLI harness.
  - **Vigil** = Discord transport via cc-connect + Codex CLI harness.
  - One human operator (Zoe, functioning as operator/arbiter per constitution Principle IV).
  - Note: cc-connect is a communications bridge (it mediates Discord ↔ an agent CLI and handles message chunking, reactions, mentions, session lifecycle); it is **not** itself the agent harness. Both primary peers share the same transport and differ at the harness layer.
- **Stretch participant (non-blocking, optional)**: a third peer — **Gemini via the Gemini CLI harness** — introduced only if two-agent convergence is holding in later POC sessions. The H3 interest is that Gemini CLI is a **meaningfully different agent harness** from both Claude Code CLI and Codex CLI, so a three-peer session doubles as an early probe of **H3 transfer across harnesses on the same substrate** (tests whether the coordination logic depends on specific agent-CLI semantics that Claude Code and Codex happen to share, independent of the transport). Not a required outcome per Zoe's steer on [#37](https://github.com/mentatzoe/peer-coordination/discussions/37#discussioncomment-16616215); only pursued if there's signal to pursue it. If two-agent coordination fails first, the three-agent extension is not attempted in this POC.
  - **Open transport question for the stretch**: cc-connect currently ships adapters for Claude Code and Codex, not Gemini CLI. To route Gemini into the Discord POC, the transport path is TBD and must be resolved before the stretch session can run — either (a) a new cc-connect adapter for Gemini CLI, or (b) an alternative bridge (Discord MCP from a local Gemini session, a custom bot, or another mechanism). Picking between (a) and (b) has implications for how much of the three-peer comparison is apples-to-apples at the transport layer. This is a phase-planning question, not an observable; flagged here and re-raised in Open Questions.
- **Substrate**: Discord, specifically one designated open-floor channel (current candidate: `#open-floor`, channel ID `1494836296336543774`).
- **Activity domain for the first POC run**: intentionally left open — agents may converse about any topic the operator seeds. The first run is not scoped to software development specifically; H3 asks whether the **core coordination logic** transfers across goal domains, and the first POC can probe that by running different seed topics across sessions.
- **Duration per session**: operator-bounded. No fixed length. Sessions end when the operator signals, when convergence feels clear, or when a failure mode is observed.
- **Number of sessions before POC verdict**: TBD with Codex during phases section; early estimate is a handful (3–10), enough to see patterns beyond session-one noise but not so many that we're optimizing for the harness rather than learning from it.

### What the POC is NOT

- NOT a product rollout. No onboarding flow, no scaling to N agents, no multi-tenancy.
- NOT a benchmark against other multi-agent frameworks. We're not racing AutoGen/CrewAI/LangGraph; we're testing a distinct hypothesis.
- NOT a demonstration of capability. Agents are capable; the question is whether they coordinate, not whether they individually work.
- NOT Discord-specific framework claims. Discord is the first substrate. The framework-level claims (in `VISION.md`) are substrate-neutral; only the POC instantiation is Discord-specific.
- NOT a spec. This document describes the experiment; specs in `specs/` describe deliverables the experiment depends on.

### Explicit pilot-local assumptions

Per Zoe's steer on #32: the POC may freely assume Discord-specifics **in its own implementation**. Portability is a design-time concern at the architecture level, not a per-spec constraint for the POC phase.

These are the specific substrate-coupled choices the POC bakes in:

- Emoji palette (✅👀🤔🚫⏸️) is convention for the POC; operators may adopt it differently on other substrates.
- `!stop`/`!resume` as channel-wide interrupt is a Discord-suitable mechanism; another substrate may need a different interrupt.
- Pinned messages as the rule-injection mechanism is Discord-native; another substrate would use whatever its equivalent is (Slack pinned, Telegram pinned, terminal's MOTD, etc.).

These pilot-local assumptions are **surface conventions** in the H3 sense (see `VISION.md` H3 and "Instance-agnostic" bullet). They are expected and explicitly allowed to differ on different substrates. What H3 asks is whether the **core coordination logic** — how peers infer turn-taking, resolve overlap, establish local norms — survives without these specific surface conventions, not whether the specific conventions themselves transfer mechanically.

## Success / Failure Conditions *(Claude-authored, rooted in H1/H2/H3)*

The POC is **successful** if it produces enough signal to distinguish between the three hypothesis outcomes:

- H1 (convergence) holds / doesn't hold in the observed sessions.
- H2 (legibility) holds / doesn't hold in the observed sessions.
- H3 (generalizability) is left testable by follow-on runs on non-Discord substrates, i.e., no architectural decisions in the POC pre-fail H3.

Success is NOT defined as "the agents coordinated well." Success is defined as "we learned something credible about whether the hypotheses hold." A POC that concludes H1 is wrong is as successful as one that concludes H1 holds — both advance the research.

### Success observables per hypothesis

**H1 — Convergence observables** (Layer 2):

- **Operator intervention rate per session.** If trending upward over the POC, H1 is weakening. If trending downward or stable-low, H1 is holding. Maps to the architecture's **intervention-dependence** failure mode (`design/architecture.md` Layer 3 taxonomy).
- **Turn-to-coordination time.** How many turns until agents settle into a coordination pattern (not a specific pattern; any pattern that doesn't require operator redirection each turn)? Shorter is better; increasing across sessions would be a negative signal.
- **Absence of loops / deadlocks.** Sessions that break down into agents-talking-past-each-other or infinite acknowledgment loops are H1 failures. Maps to the architecture's **convergence failure** mode.
- **Presence of explicit yielding / claiming / building (heuristics #1–#3).** Not required to be present in prescribed form, but some observable signal that agents are orienting toward each other.
- **Complementarity.** Are peers making distinct useful contributions relative to the shared activity, or parallel output with light mutual acknowledgment? Maps to the architecture's **complementarity failure** mode — a session where agents appear coordinated but are each just producing their own thread independently is H1 failing even if operator-intervention rate is low.
- **Escalation path usage (heuristic #7).** When agents disagree, do they route to scratchpad/discussion or loop in-channel? Routing is H1 holding; looping is H1 failing.

**H2 — Legibility observables** (Layer 3):

- **Fresh-reader test.** A person who wasn't in the session can read the **preserved episode record** (channel history + pinned rules + operator turns) and reconstruct why the exchange makes sense. Binary pass/fail per session. Conducted by the operator or an uninvolved human post-session. Note: legibility tests whether the record is sufficient, **not** whether the last N turns are context-free — see `VISION.md` H2.
- **Drift audit.** Active search for: new emoji uses not in the shared palette; abbreviations that require context to decode; message patterns that only make sense between the specific agents. Zero-tolerance for H2; any drift is a finding, not a failure of the session (data is valuable).
- **Transcript completeness.** Can the full coordination history be reconstructed from the logs alone, without any hidden channel (DMs, side-chats, model-internal state)? If hidden-channel usage is needed to understand the session, H2 is compromised. Aligns with `design/architecture.md` Layer 1 capability: "Layer 1 preserves the episode record as part of shared conversation state."

**H3 — Generalizability observables** (meta / cross-layer):

- **Substrate-dependency audit.** Look at every architectural decision in the POC; for each one, classify it as either a **surface convention** (allowed to differ per substrate — emoji palette, interrupt syntax, pinning mechanism) or a **core coordination-logic assumption** (should survive substrate transfer — how peers infer turn-taking, resolve overlap, yield initiative). H3 holds iff the core-logic assumptions are substrate-neutral; surface-convention count is not the metric.
- **Follow-on readiness.** At the end of the POC, could we credibly run a second pilot on a non-Discord substrate with **new surface conventions** but the **same coordination logic**, without rewriting the coordination layer? If yes, H3 is designed-for correctly. If no, we've baked in substrate assumptions at the wrong layer.
- **Harness-dependency probe (stretch).** If the Gemini-CLI three-agent stretch session runs: does the coordination logic hold when one peer runs a meaningfully different **agent harness** (Gemini CLI) on the same substrate? A positive signal here is partial evidence for H3 even before a second-substrate run. Interpretation must account for the transport path chosen for Gemini (cc-connect adapter vs alternative bridge) — if Gemini rides a different transport, findings blend transport-dependency and harness-dependency and should be reported as such rather than as clean harness-independence.

### Failure conditions

The POC **fails** in the research sense if:

- We cannot distinguish between hypothesis outcomes. All observables ambiguous. The harness itself isn't informative.
- The POC instrumentation (evaluation, logging, audit) interferes with agent behavior enough to invalidate results. Observer-effect failure.
- The pilot cannot be safely interrupted — `!stop` doesn't work, operator loses arbiter capability — which means we have no way to halt a failure mode when we see one.

Any of these makes the POC not credible and requires a rebuild of the harness.

### What counts as a signed-off POC exit

- All three hypotheses have a documented stance (holds / doesn't hold / uncertain with reason).
- Observations file has enough entries to support the stances (lower bound: N sessions worth of observations, where N is TBD in the phases section).
- A decision has been made on whether to proceed to H3 test runs on a second substrate.
- Operator (Zoe) explicitly ratifies the POC conclusions.

---

## Architecture → Tech Stack Mapping *(Codex to author)*

*Per work distribution on #32, Codex owns the architecture-to-tech-stack mapping. Stub placeholder here; Codex to fill in with detail consistent with their `design/architecture.md` draft.*

**Expected content:**

- How each of the three layers (transport / coordination / evaluation) maps onto concrete pieces of the POC:
  - Layer 1 (transport) → cc-connect Discord platform adapter + `!stop`/`!resume` + open-floor mode + reactions + pinned-rules. Specs 001, 002, 003, 004, 005.
  - Layer 2 (coordination) → pinned channel rules + emoji palette + internalized heuristics. Gap-fill content TBD.
  - Layer 3 (evaluation) → observations file + session summaries + drift audit mechanism. Gap-fill content TBD.
- Which existing specs map onto Layer 1 vs Layer 2 vs Layer 3.
- Which Layer 2 and Layer 3 content is under-specified (per the layer-gap analysis) and needs new specs.
- Concrete submodule structure if the POC lives as a submodule of this repo (per Zoe's tactical note on #32).

*Codex: please append your content below this placeholder and remove the placeholder text. Leave the heading structure as-is for consistency.*

---

## Development Phases *(Codex to author)*

*Per work distribution, Codex owns the phases. Stub placeholder; Codex fills in.*

**Expected content:**

- What phases the POC goes through from current state → signed-off exit.
- Which existing specs need to land in which phase (e.g., 001 and 003 enable Phase 1; 004 enables Phase 2; etc.).
- Which gap-fill Layer 2 / Layer 3 specs need to exist for each phase.
- How many sessions per phase before moving to the next (guard against premature exit; guard against over-iteration).
- What operator inputs are needed per phase.
- Explicit gates between phases (when does each phase hand off to the next?).

*Codex: please append your content below this placeholder.*

---

## Open Questions (cross-cutting)

1. **How many total POC sessions before calling the experiment done?** Not a hard number, but range. TBD with phases.
2. **Does the fresh-reader H2 test need to be an uninvolved human specifically, or can it be an agent that wasn't in the session?** Operator call. Using an agent is faster but risks shared training biases; a human is slower but cleaner.
3. **At what point do we spin up the H3 substrate-transfer test?** Likely after POC signals H1 + H2 hold; but if H3 is designed-for at the architecture level, the test could run in parallel with later POC sessions rather than after.
4. **How is drift-audit tooling built without violating the "unobtrusive evaluation" steer?** Post-hoc transcript analysis is fine; anything that runs during a session risks observer effect.
5. **Gemini stretch transport path.** If the three-agent stretch session is attempted, what's the transport path for Gemini — a new cc-connect adapter for Gemini CLI, or an alternative bridge (Discord MCP from a local Gemini session, custom bot, etc.)? Affects whether findings isolate harness-dependency cleanly or blend it with transport-dependency. To be resolved before the stretch session runs; scoping the adapter effort (and whether it's in this POC or a follow-on) is a phase-planning question for Codex's Development Phases section.

## References

- [Peer-Coordination Vision](../VISION.md) — north star and hypotheses this POC tests.
- [Architecture](architecture.md) — three-layer model (transport / coordination / evaluation) with capability requirements and validation signals per layer. POC observables are aligned to this layering and to Layer 3's failure taxonomy.
- [Constitution](../.specify/memory/constitution.md) — governance spine.
- [discussion #32](https://github.com/mentatzoe/peer-coordination/discussions/32) — ratification trail.
- [discussion #33](https://github.com/mentatzoe/peer-coordination/discussions/33) — Codex's research spike.
- [discussion #34](https://github.com/mentatzoe/peer-coordination/discussions/34) — Claude's research spike.
- [discussion #35](https://github.com/mentatzoe/peer-coordination/discussions/35) — architecture review (Codex-owned artifact, Claude review applied).
- [discussion #36](https://github.com/mentatzoe/peer-coordination/discussions/36) — VISION.md review (closed as resolved on 2026-04-18).
- [discussion #37](https://github.com/mentatzoe/peer-coordination/discussions/37) — this document's review.
- [`observations/harness-behaviors.md`](../observations/harness-behaviors.md) — running field journal for pilot observations.

## Changelog

- **2026-04-18 (transport/harness clarification)**: corrected a conflation flagged by Zoe on Discord — cc-connect is the transport/communications bridge, not the agent harness. Distinguished transport (cc-connect) from agent harness (the underlying CLI: Claude Code CLI, Codex CLI, Gemini CLI) in the Primary / Stretch participants descriptions. Reframed the H3-via-harness probe as testing agent-CLI semantics, not "cc-connect-shaped semantics." Added an open question for the Gemini stretch transport path (cc-connect adapter vs alternative bridge), since it blends with the harness-dependency finding if not called out.
- **2026-04-18 (second revision round)**: revised in response to [#37](https://github.com/mentatzoe/peer-coordination/discussions/37) + downstream of VISION.md revisions (commits [`3ec72dc`](https://github.com/mentatzoe/peer-coordination/commit/3ec72dc), [`358af56`](https://github.com/mentatzoe/peer-coordination/commit/358af56)) + alignment to the latest `design/architecture.md` draft. Changes: added optional Gemini-CLI three-agent stretch participant per Zoe's [#37 comment](https://github.com/mentatzoe/peer-coordination/discussions/37#discussioncomment-16616215); reframed pilot-local assumptions explicitly as H3 "surface conventions" vs "core coordination logic"; updated H2 fresh-reader test to evaluate against the preserved episode record rather than a trailing turn window; updated H3 substrate-dependency audit to classify decisions as surface vs core rather than count substrate-coupling; added H3 harness-dependency probe tied to the stretch session; added complementarity observable to H1 tracking the architecture's Layer 3 failure taxonomy; added cross-references to `design/architecture.md` throughout. Codex-owned sections (Architecture → Tech Stack Mapping, Development Phases) remain stubbed pending Codex's contribution.
- **2026-04-18**: initial draft by Claude covering Purpose / Scope / Success-Fail / Open Questions. Architecture-to-tech-stack mapping and Development Phases sections stubbed for Codex to complete per #32 work distribution.
