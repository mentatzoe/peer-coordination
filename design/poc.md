# POC — Peer Coordination Proof of Concept

**Status**: Co-authored draft revised 2026-04-18 per [discussion #37](https://github.com/mentatzoe/peer-coordination/discussions/37) feedback and downstream of the VISION.md / architecture revision rounds. Claude-authored scope + success/fail sections and Codex-authored Architecture → Tech Stack Mapping + Development Phases sections are now both present; the next step is integrated review on the full document.

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
- **Number of sessions before POC verdict**: phase-bounded rather than fixed up front. Current planning assumption: **3–5 two-peer sessions** as the baseline evidence set, with an **optional 1–2 stretch sessions** if the Gemini extension is attempted. Enough to see patterns beyond session-one noise, but not so many that we optimize for the harness instead of learning from it.

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
- Observations file has enough entries to support the stances (current planning range: 3–5 baseline sessions, plus optional 1–2 stretch sessions if Phase 4 is entered).
- A decision has been made on whether to proceed to H3 test runs on a second substrate.
- Operator (Zoe) explicitly ratifies the POC conclusions.

---

## Architecture → Tech Stack Mapping *(Codex-authored)*

The architecture doc defines the POC in three layers. This section maps those layers to the actual moving parts of the first Discord-based probe.

### Layer map

| Architecture layer | POC responsibility | Concrete components in this POC | Current state | Main gaps / follow-on needs |
|---|---|---|---|---|
| **Layer 1 — Interop / transport substrate** | Put all participants into the same inspectable shared surface; preserve episode record; provide interruption and recovery | Discord channel; `cc-connect` as the Discord ↔ CLI bridge; Claude Code CLI harness; Codex CLI harness; operator account; channel history; pinned message support; reactions; `!stop` / `!resume`; designated open-floor channel binding | Partly available conceptually; implementation work still required downstream | concrete transport specs / implementation in the transport repo; channel binding and recovery behavior; Gemini bridge if stretch phase runs |
| **Layer 2 — Coordination model** | Make shared norms visible and interpretable without hard-coding a moderator protocol | operator-managed pinned rules; emoji palette; channel-local norms; harness-side inference from shared context; escalation to operator when ambiguity persists | Partly defined in `VISION.md` and `design/architecture.md`; not yet fully materialized as a dedicated artifact | a clearer norms artifact if pinned rules become too ad hoc; possible future Layer 2 spec stream if the norm set hardens |
| **Layer 3 — Evaluation of emergence and success** | Preserve evidence and judge whether coordination is real, legible, and informative | Discord transcript / preserved episode record; operator notes; [`observations/harness-behaviors.md`](../observations/harness-behaviors.md); post-session drift audit; post-session discussion review; hypothesis stances recorded against H1/H2/H3 | Structurally defined, but still mostly manual | stronger evaluation routine if manual review becomes too loose; possible Layer 3 spec stream for episode-record shape / audit procedure |

### Concrete stack by component

#### Shared substrate

- **Discord** is the first substrate, not the framework.
- The POC assumes one designated open-floor channel as the shared conversational surface.
- Channel history plus pinned rules form the minimum shared context for both peers and the operator.

#### Bridge / transport layer

- **`cc-connect`** is the communications bridge between Discord and the local agent harnesses.
- It is responsible for delivery, mention handling, session lifecycle, and substrate-local primitives.
- It is **not** the agent harness and should stay policy-light.

#### Agent harness layer

- **Claude Code CLI** and **Codex CLI** are the initial harnesses for the two-peer baseline.
- If attempted, **Gemini CLI** is a harness-diversity stretch, not part of the minimum viable POC.
- A Gemini stretch run only counts as clean harness-diversity evidence if the transport story is called out honestly; if Gemini uses a different bridge path, the result blends harness and transport effects.

#### Coordination surface

- The coordination layer in this POC is intentionally thin:
  - pinned rules
  - emoji palette
  - operator-visible conversation history
  - local inference by each harness
- This is enough to test whether peers can organize without introducing a host or explicit workflow protocol.

#### Evaluation surface

- The canonical episode evidence for the POC is:
  - the preserved Discord transcript / channel history
  - the pinned rules active for that run
  - the operator's interventions
  - post-session observations in [`observations/harness-behaviors.md`](../observations/harness-behaviors.md)
  - review comments and conclusions in GitHub Discussions
- This keeps evaluation post hoc and inspectable, consistent with `VISION.md` and `design/architecture.md`.

### Spec / artifact mapping

This repo does **not** currently have all POC-relevant specs landed on `main`, so the safest way to think about mapping is by capability stream, not just by spec number.

- **Transport-facing capability streams** map to Layer 1:
  - open-floor routing and interruption
  - reaction / mention handling
  - pinned-rules exposure
  - session binding / recovery
- **Coordination-facing capability streams** map to Layer 2:
  - shared rule content
  - emoji / signal conventions
  - escalation expectations
- **Evaluation-facing capability streams** map to Layer 3:
  - episode-record preservation
  - observation logging
  - drift / legibility audit routine
  - hypothesis verdict write-up

If future spec work is created from this POC, it should be cut along those capability lines rather than forcing everything back into a single monolithic POC spec.

### Recommended submodule shape

Per Zoe's repo-sovereignty steer, the implementation-facing POC should live as a submodule under this repo once there is actual runnable code or config to isolate. Recommended shape:

- `poc/discord-peer-coordination/` as the submodule root for the first runnable Discord probe

Rationale:

- keeps governance/design docs in this repo
- keeps transport/harness implementation isolated
- gives the POC a stable path for references from `design/poc.md`, review threads, and later observations

Until that submodule exists, this document should treat the POC as a planned implementation surface rather than pretending the repo already contains the runnable harness.

---

## Development Phases *(Codex-authored)*

The POC should progress by **capability gates**, not by raw implementation volume. The point is to learn something credible about H1/H2/H3, not to build out an ever larger Discord bot surface.

### Phase 0 — Artifact alignment and planning

**Goal:** ensure the vision, architecture, and POC shape agree before implementation begins.

**Outputs:**

- approved `VISION.md`
- converged `design/architecture.md`
- converged `design/poc.md`
- named review threads for each artifact

**Operator input needed:**

- document arbitration where Claude and Codex materially disagree

**Gate to next phase:**

- vision and architecture are approved
- this POC doc is strong enough to guide implementation without obvious scope ambiguity

### Phase 1 — Two-peer substrate baseline

**Goal:** get the minimum two-peer Discord harness running safely enough to observe real sessions.

**Required capabilities:**

- both primary peers can participate in the designated Discord channel
- shared context is visible to both peers
- `!stop` / `!resume` or equivalent operator interrupt works
- episode record is preservable and reviewable after the session
- pinned rules or equivalent shared coordination artifact is exposed in-channel
- **operator interventions are distinguishable by type/reason in the preserved record** (safety stop, clarification, redirect, drift-catch, etc.), per `design/architecture.md` Layer 3 capability ("a way to track operator intervention frequency, type, and reason"). Without this, the Phase 2 intervention-rate observable is hard to interpret — three safety stops read very differently from three directive redirects.

**Likely dependency streams:**

- Layer 1 transport work
- channel binding / recovery behavior
- baseline open-floor behavior

**Operator input needed:**

- channel selection / channel access
- confirmation that the interrupt mechanism is acceptable
- initial pinned-rule set for the first run

**Gate to next phase:**

- at least one dry run completes without transport ambiguity
- operator can interrupt safely
- post-session evidence is inspectable from preserved artifacts

### Phase 2 — Two-peer baseline observation run

**Goal:** gather the first real evidence for H1 and H2 on the minimum viable harness.

**Planned session count:**

- **3–5 two-peer sessions** across more than one seeded topic

**What happens in this phase:**

- run the two-peer probe
- record operator interventions (with type/reason tagging per the capability added above)
- log observations after each session
- evaluate H1 convergence and H2 legibility against the preserved episode record
- classify visible Discord couplings as surface conventions vs core coordination-logic dependencies **session by session**, in the observations file — running capture here makes the Phase 5 follow-on-readiness assessment tractable instead of retrospective guesswork

**Operator input needed:**

- seed prompts / topics
- post-session review participation
- intervention when required by safety or ambiguity

**Gate to next phase:**

- at least 3 two-peer sessions completed, each with intervention log + observation notes committed to the repo
- if convergence remains inconclusive after 5 sessions, exit to Phase 3 for credibility review rather than extending the baseline indefinitely (guards against optimizing for the harness instead of learning from it)
- failures, if any, are understood as either harness-credibility failures or genuine hypothesis pressure

### Phase 3 — Credibility repair or confirmation

**Goal:** decide whether the harness is credible enough to continue, and repair only what is necessary for credibility.

**What happens in this phase:**

- fix harness-breaking problems only:
  - unsafe interrupt behavior
  - missing or corrupted episode record
  - evaluation method interfering with the session
  - transport ambiguity that prevents interpretation of results
- avoid tuning the system merely to make H1/H2 "pass"

**Operator input needed:**

- approval on whether a change is a credibility repair or a hypothesis-distorting optimization

**Gate to next phase:**

- either:
  - the two-peer POC is judged credible enough to continue, or
  - the harness is judged uninformative and the POC exits early as a failed probe

### Phase 4 — Optional harness-diversity stretch

**Goal:** run the optional Gemini-including stretch only if the two-peer baseline is already holding together.

**Entry conditions:**

- two-peer baseline is not collapsing
- a transport path for Gemini is explicitly chosen and documented
- the team accepts that findings may mix harness and transport effects if Gemini does not ride the same bridge path

**Planned session count:**

- **1–2 stretch sessions max**

**Operator input needed:**

- explicit go / no-go on attempting the stretch
- confirmation that the added complexity is worth the signal

**Gate to next phase:**

- stretch findings are recorded as either:
  - useful early H3-adjacent evidence, or
  - too confounded to interpret cleanly

### Phase 5 — POC exit and handoff

**Goal:** end the POC with explicit conclusions rather than an indefinite pilot.

**Required outputs:**

- documented stance for each hypothesis:
  - H1 holds / does not hold / uncertain
  - H2 holds / does not hold / uncertain
  - H3 is or is not still credibly testable in follow-on
- sufficient observations to support those stances
- decision on whether to proceed to a non-Discord H3 test
- identified Layer 2 / Layer 3 gaps that should become follow-on artifacts or specs

**Operator input needed:**

- explicit ratification of the POC conclusions

**Exit condition:**

- the operator signs off on the hypothesis verdicts and the next-step decision

---

## Open Questions (cross-cutting)

Each question is annotated with the phase in which it is expected to be resolved, so the phase plan and the open-question list stay in sync.

1. **How many total POC sessions before calling the experiment done?** Current planning range: 3–5 two-peer baseline sessions (Phase 2), plus optional 1–2 Gemini stretch sessions if Phase 4 is entered. Exact exit still depends on hypothesis clarity, not on hitting the top of the range mechanically. *Resolves: superseded by the Phase 2 / Phase 4 gates.*
2. **Does the fresh-reader H2 test need to be an uninvolved human specifically, or can it be an agent that wasn't in the session?** Operator call. Using an agent is faster but risks shared training biases; a human is slower but cleaner. *Resolves: Phase 2 (operator picks the reviewer type for the first observation run; may change across sessions).*
3. **At what point do we spin up the H3 substrate-transfer test?** Likely after POC signals H1 + H2 hold; but if H3 is designed-for at the architecture level, the test could run in parallel with later POC sessions rather than after. *Resolves: Phase 5 (POC exit decision on whether to proceed to a non-Discord H3 test).*
4. **How is drift-audit tooling built without violating the "unobtrusive evaluation" steer?** Post-hoc transcript analysis is fine; anything that runs during a session risks observer effect. *Resolves: Phase 3 (credibility repair explicitly covers "evaluation method interfering with the session").*
5. **Gemini stretch transport path.** If the three-agent stretch session is attempted, what's the transport path for Gemini — a new cc-connect adapter for Gemini CLI, or an alternative bridge (Discord MCP from a local Gemini session, custom bot, etc.)? Affects whether findings isolate harness-dependency cleanly or blend it with transport-dependency. *Resolves: before Phase 4 entry (Phase 4's entry conditions explicitly require the Gemini transport path to be chosen and documented, and the team to accept any blended-signal consequences honestly).*

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

- **2026-04-18 (Claude integration pass on Codex sections)**: iterated on Codex's handoff pass per Zoe's direction on Discord. Added Phase 1 capability requirement: operator interventions must be tagged by type/reason in the preserved record (connects to architecture.md Layer 3 capability + the H1 intervention-rate observable, which otherwise can't distinguish safety stops from directive redirects). Made Phase 2 substrate-coupling classification a **session-by-session running capture** so Phase 5 follow-on-readiness isn't reconstructed retrospectively. Tightened Phase 2 → Phase 3 gate with concrete session-count thresholds (≥3 completed, force-exit at 5 if inconclusive). Fixed escaped quotes in Phase 3. Annotated each Open Question with the phase where it resolves, keeping the phase plan and the OQ list in sync. Endorsed Codex's capability-stream framing (vs spec-number framing) as the honest choice given current repo state; no revisions to that section.
- **2026-04-18 (Codex handoff pass)**: filled the previously stubbed **Architecture → Tech Stack Mapping** and **Development Phases** sections. Added a three-layer → concrete-stack mapping, capability-stream framing instead of overcommitting to spec numbers not yet landed on `main`, recommended submodule shape (`poc/discord-peer-coordination/`), and a phase plan from artifact alignment through optional Gemini stretch and POC exit. Also updated the scope's session-count sentence and the signed-off exit criterion to align with the newly-added phases section, and updated the top status line to reflect that the document is now a full co-authored draft rather than a partial handoff.
- **2026-04-18 (transport/harness clarification)**: corrected a conflation flagged by Zoe on Discord — cc-connect is the transport/communications bridge, not the agent harness. Distinguished transport (cc-connect) from agent harness (the underlying CLI: Claude Code CLI, Codex CLI, Gemini CLI) in the Primary / Stretch participants descriptions. Reframed the H3-via-harness probe as testing agent-CLI semantics, not "cc-connect-shaped semantics." Added an open question for the Gemini stretch transport path (cc-connect adapter vs alternative bridge), since it blends with the harness-dependency finding if not called out.
- **2026-04-18 (second revision round)**: revised in response to [#37](https://github.com/mentatzoe/peer-coordination/discussions/37) + downstream of VISION.md revisions (commits [`3ec72dc`](https://github.com/mentatzoe/peer-coordination/commit/3ec72dc), [`358af56`](https://github.com/mentatzoe/peer-coordination/commit/358af56)) + alignment to the latest `design/architecture.md` draft. Changes: added optional Gemini-CLI three-agent stretch participant per Zoe's [#37 comment](https://github.com/mentatzoe/peer-coordination/discussions/37#discussioncomment-16616215); reframed pilot-local assumptions explicitly as H3 "surface conventions" vs "core coordination logic"; updated H2 fresh-reader test to evaluate against the preserved episode record rather than a trailing turn window; updated H3 substrate-dependency audit to classify decisions as surface vs core rather than count substrate-coupling; added H3 harness-dependency probe tied to the stretch session; added complementarity observable to H1 tracking the architecture's Layer 3 failure taxonomy; added cross-references to `design/architecture.md` throughout. Codex-owned sections (Architecture → Tech Stack Mapping, Development Phases) remain stubbed pending Codex's contribution.
- **2026-04-18**: initial draft by Claude covering Purpose / Scope / Success-Fail / Open Questions. Architecture-to-tech-stack mapping and Development Phases sections stubbed for Codex to complete per #32 work distribution.
