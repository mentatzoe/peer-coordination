# POC — Peer Coordination Proof of Concept

**Status**: initial draft in progress. Claude authoring scope + success/fail; Codex to follow with architecture-to-tech-stack mapping + development phases per work distribution on [discussion #32 comment 16614566](https://github.com/mentatzoe/peer-coordination/discussions/32#discussioncomment-16614566).

**Owners**: Claude (scope, success/fail conditions) + Codex (tech-stack mapping, development phases). Co-authored overall.

**Top-level reference**: [`VISION.md`](../VISION.md) for the hypotheses this POC is organized around.

---

## Purpose

Define the first concrete test harness for the peer-coordination framework. This is the experiment through which H1, H2, and H3 from the vision doc are evaluated (H1/H2 directly; H3 by design-time constraint).

This is a **probe, not the product**. The POC produces observations that inform whether the non-orchestrated peer-coordination framework is viable, and if so, what shape it takes. The POC is not the framework; the framework is whatever we learn from running this POC (and any follow-ons).

## Scope *(Claude-authored)*

### What the POC IS

The first POC is a **two-agent conversational pilot in a designated Discord channel**. Concretely:

- **Participants**: two peer agents (Dalgos via cc-connect + Claude Code; Vigil via cc-connect + Codex) and one human operator (Zoe, functioning as operator/arbiter per constitution Principle IV).
- **Substrate**: Discord, specifically one designated open-floor channel (current candidate: `#open-floor`, channel ID `1494836296336543774`).
- **Activity domain for the first POC run**: intentionally left open — agents may converse about any topic the operator seeds. The first run is not scoped to software development specifically; H3 asks for domain-agnosticism, and the first POC can test that by running on different seed topics across sessions.
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

- Emoji palette (✅👀🤔🚫⏸️) is convention for the POC; operators may adopt it differently on other substrates.
- `!stop`/`!resume` as channel-wide interrupt is a Discord-suitable mechanism; another substrate may need a different interrupt.
- Pinned messages as the rule-injection mechanism is Discord-native; another substrate would use whatever its equivalent is (Slack pinned, Telegram pinned, terminal's MOTD, etc.).

These pilot-local assumptions are expected and not violations of H3. H3 asks whether the patterns abstract; it does not ask whether the first implementation generalizes mechanically.

## Success / Failure Conditions *(Claude-authored, rooted in H1/H2/H3)*

The POC is **successful** if it produces enough signal to distinguish between the three hypothesis outcomes:

- H1 (convergence) holds / doesn't hold in the observed sessions.
- H2 (legibility) holds / doesn't hold in the observed sessions.
- H3 (generalizability) is left testable by follow-on runs on non-Discord substrates, i.e., no architectural decisions in the POC pre-fail H3.

Success is NOT defined as "the agents coordinated well." Success is defined as "we learned something credible about whether the hypotheses hold." A POC that concludes H1 is wrong is as successful as one that concludes H1 holds — both advance the research.

### Success observables per hypothesis

**H1 — Convergence observables** (Layer 2):

- **Operator intervention rate per session.** If trending upward over the POC, H1 is weakening. If trending downward or stable-low, H1 is holding.
- **Turn-to-coordination time.** How many turns until agents settle into a coordination pattern (not a specific pattern; any pattern that doesn't require operator redirection each turn)? Shorter is better; increasing across sessions would be a negative signal.
- **Absence of loops / deadlocks.** Sessions that break down into agents-talking-past-each-other or infinite acknowledgment loops are H1 failures.
- **Presence of explicit yielding / claiming / building (heuristics #1–#3).** Not required to be present in prescribed form, but some observable signal that agents are orienting toward each other.
- **Escalation path usage (heuristic #7).** When agents disagree, do they route to scratchpad/discussion or loop in-channel? Routing is H1 holding; looping is H1 failing.

**H2 — Legibility observables** (Layer 3):

- **Fresh-reader test.** A person who hasn't read the session history can read the last N turns and pinned rules and understand what's happening. Conducted by the operator or an uninvolved human post-session. Binary pass/fail per session.
- **Drift audit.** Active search for: new emoji uses not in the shared palette; abbreviations that require context to decode; message patterns that only make sense between the specific agents. Zero-tolerance for H2; any drift is a finding, not a failure of the session (data is valuable).
- **Transcript completeness.** Can the full coordination history be reconstructed from the logs alone, without any hidden channel (DMs, side-chats, model-internal state)? If hidden-channel usage is needed to understand the session, H2 is compromised.

**H3 — Generalizability observables** (meta):

- **Substrate-dependency audit.** Look at every architectural decision in the POC; flag ones that would not work on a different substrate. Count and qualify. Decreasing substrate-dependency over POC iterations is a positive signal.
- **Follow-on readiness.** At the end of the POC, could we credibly run a second pilot on a non-Discord substrate without rewriting the coordination layer? If yes, H3 is designed-for correctly. If no, we've baked in substrate assumptions.

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

## References

- [Peer-Coordination Vision](../VISION.md) — north star and hypotheses this POC tests.
- [Constitution](../.specify/memory/constitution.md) — governance spine.
- [discussion #32](https://github.com/mentatzoe/peer-coordination/discussions/32) — ratification trail.
- [discussion #33](https://github.com/mentatzoe/peer-coordination/discussions/33) — Codex's research spike.
- [discussion #34](https://github.com/mentatzoe/peer-coordination/discussions/34) — Claude's research spike.
- [`observations/harness-behaviors.md`](../observations/harness-behaviors.md) — running field journal for pilot observations.

## Changelog

- **2026-04-18**: initial draft by Claude covering Purpose / Scope / Success-Fail / Open Questions. Architecture-to-tech-stack mapping and Development Phases sections stubbed for Codex to complete per #32 work distribution.
