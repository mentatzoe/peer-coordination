# Peer-Coordination Vision

**Content status**: ratified in [discussion #32](https://github.com/mentatzoe/peer-coordination/discussions/32) (north star alignment Q2, hypothesis reframing Q3, work distribution steers).
**Artifact status**: under review in [discussion #36](https://github.com/mentatzoe/peer-coordination/discussions/36).
**Last revised**: 2026-04-18.
**Owner of this doc**: Claude (per work distribution table on #32).
**Top-level reference**: this is the vision spine. Linked from the README. Everything else (design, POC, specs) should be consistent with this doc; when there's a conflict, this is the document that defines the target, not the implementation choice.

## Purpose

Capture — compactly and durably — the question this project exists to answer, and the specific falsifiable hypotheses the first POC is organized around. This is NOT a protocol definition, NOT a spec, and NOT an implementation blueprint. It's the thing every other artifact points back at when asked "why does this matter?"

## North Star

> A **human-readable, non-orchestrated, agentic peer-to-peer coordination framework.**
>
> Materialized in a given instance as a conversation in a channel, but independent of any specific goal — software development, debate, games, creative work, crisis response, whatever.
>
> The question it is designed to answer:
>
> **"Can agents organize themselves without the need for orchestration? What does it look like when agents (and their underlying models) have to infer a way of working in a 'natural' or 'organic' pattern?"**

### What this means concretely

- **Human-readable**: coordination traces MUST remain legible to an uninvolved human reader. If an agent's message only makes sense to another agent, something has gone wrong.
- **Non-orchestrated**: there is no central controller dictating turn-taking, task allocation, or conflict resolution. The operator is an arbiter of last resort, not a router.
- **Agentic**: each participant is a full agent with its own reasoning, not a specialized subroutine.
- **Peer-to-peer**: participants address each other directly, not through a mediator.
- **Framework, not product**: the output of this project is a way of thinking about peer coordination, tested via one or more POCs. It is not a specific app or deployment.
- **Instance-agnostic**: a working framework should produce coherent coordination logic across substrates (Discord, terminal, Slack, etc.) and across goals (software dev, conversation, debate, games). Surface conventions — how a pause is signaled, which emoji palette gets used, what command prefixes exist — may legitimately vary by substrate or activity; what transfers is the organizing principle.

### What the north star is NOT

- Not a claim that orchestration is bad in general. Orchestrated multi-agent systems work well for many problems. This project is asking a different question: what happens WITHOUT orchestration?
- Not a claim that protocols are unnecessary. Some protocols are constitutional (Principle II / VI work). The claim is narrower: coordination **policy** should emerge from shared context and local inference, not from a rigid protocol.
- Not a prediction of success. The hypotheses below may fail. Failure is data.

## Hypotheses

The north star, reframed as falsifiable claims the POC is organized around.

### H1 — Convergence

> **Given shared context (pinned rules, channel history, operator turns) and minimal transport scaffolding, peer agents will converge on a coherent coordination pattern without a mediator or handshake protocol.**

- **Testable in the initial POC.**
- **Fails if**: agents require operator redirection on most turns; agents need re-prompting to coordinate; coordination collapses into loops, deadlocks, or one-sided dominance.

### H2 — Legibility

> **The emerging coordination pattern remains legible to an uninvolved human reader throughout the session. No drift toward in-group shorthand.**

- **Testable in the initial POC.**
- **Fails if**: agents develop conventions (emoji combinations, abbreviations, shorthand) that require background context to decode; given the preserved episode record (channel history + pinned rules + operator turns), a fresh human reader still can't reconstruct why the exchange makes sense; the Facebook-2017 "i i i i i" failure mode appears.

### H3 — Generalizability

> **The core coordination logic that emerges — how peers infer turn-taking, resolve overlap, establish local norms — transfers across substrates (Discord, terminal, other platforms) and across goal domains (software development, creative work, debate, games), even if surface conventions vary by substrate or activity.**

- **Designed-for in the initial POC** (at the architecture level — no hard assumptions that wouldn't transfer).
- **Tested in follow-on** (actual substrate / goal transfer runs).
- **Fails if**: the underlying coordination logic doesn't survive substrate or goal transfer — e.g., agents can't organize without orchestration in substrate B even though they could in substrate A; we find hidden dependencies on one substrate's or one domain's features that aren't just surface conventions.

### Implicit across all three

- **Evaluation is unobtrusive.** Metrics are extracted post-hoc from transcripts. No instrumentation that changes agent behavior. The observer effect is real; we mitigate by observing after the fact, not during.

## How we stay honest

Hypotheses invite motivated reasoning. Guarding against it:

- **We do not optimize for confirming H1, H2, or H3.** If the POC fails a hypothesis, that's information, not a failure of the project.
- **We explicitly capture negative results.** A session where heuristics didn't work is as informative as one where they did.
- **We audit for drift, not just for success.** Active search for H2 failure modes (private shorthand, in-group conventions) is part of the evaluation, not an afterthought.
- **Independent review.** Per the constitution's Governance expectation (v1.3.0), material changes receive independent review from an agent or human other than the primary author. The same principle applies to interpretation of results — no single agent should be the only reader of the outcomes.

## Scope boundaries

### In scope

- Conversational peer coordination between agents (and the operator).
- Shared-context mechanisms (pinned rules, channel history, emoji palette) that let agents orient without an orchestrator.
- Evaluation mechanisms that distinguish real coordination from coordination theater.
- Substrate-neutral architectural thinking (even when specific specs are substrate-specific).

### Out of scope

- Task routing as the coordination problem (see AgentNet; different problem).
- Full federated learning or privacy-preserving multi-agent training (see KNEXA-FL; different problem).
- Building a general-purpose multi-agent framework to compete with AutoGen/CrewAI/LangGraph (those are orchestrated by design; we're exploring the non-orchestrated slice).
- The specific product that uses this coordination. The POC is a research probe; if something product-shaped falls out, that's separate scope.

## Relationship to other artifacts

| Artifact | Role |
|---|---|
| `.specify/memory/constitution.md` | Durable principles + governance. The north star is subordinate to the constitution; no conflict expected but constitution wins if one arises. |
| `design/architecture.md` *(Codex-owned, in progress)* | Three-layer mental model (transport / coordination / evaluation) with responsibilities, boundaries, architectural capability requirements, failure taxonomies, and validation signals per layer. |
| `design/poc.md` *(co-authored, Claude starts)* | Concrete POC scope, success/fail conditions rooted in H1/H2/H3, architecture-to-tech-stack mapping, development phases. |
| Specs (`specs/001-*` through `specs/005-*`) | Deliverable-bound artifacts for specific transport/coordination mechanisms. Subordinate to the architecture doc. |
| `observations/harness-behaviors.md` | Running field journal of cross-harness behavior observations. Feeds H2/H3 evaluation. |

## How to use this doc

- Read it before starting any significant design work in this repo.
- When you're not sure whether something is in scope, check the "Scope boundaries" section.
- When you're not sure whether a change is safe, check whether it's consistent with the hypotheses.
- When you want to change something in this doc: open a discussion; this doc is meant to be stable, and changes should be deliberate. It follows the same promotion boundary as the constitution.

## Changelog

- **2026-04-18 (first revision round)**: addressed Codex findings from [discussion #36](https://github.com/mentatzoe/peer-coordination/discussions/36#discussioncomment-16616190): softened H3 to distinguish core coordination logic from surface conventions; reframed H2 failure condition against the preserved episode record rather than context-freedom; split status line into content-ratified vs artifact-under-review; updated relationship table to match current architecture vocabulary.
- **2026-04-18**: first draft. Authored by Claude per work distribution on [discussion #32 comment 16614566](https://github.com/mentatzoe/peer-coordination/discussions/32#discussioncomment-16614566). North star framing ratified in #32 Q2. Hypothesis framing with test/design-for split ratified in #32 Q3.
