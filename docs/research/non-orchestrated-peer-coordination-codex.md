# Research Spike: Non-Orchestrated Peer Coordination

**Author:** Codex  
**Date:** 2026-04-18  
**Prompt context:** Independent research spike requested in Discussion #32 after alignment on the north star: a human-readable, non-orchestrated, agentic p2p coordination framework.

## Scope

This memo looks for adjacent systems and papers that help answer:

1. What already exists for multi-agent coordination without a central orchestrator?
2. Which patterns transfer to `peer-coordination`?
3. Which patterns are solving a different problem and should not be imported directly?

This is not a literature survey of all multi-agent work. It is a targeted comparison of systems that are adjacent to the current north star.

## Executive View

My current read is:

- The exact thing we are trying to build is still thinly represented in the current art.
- Most existing systems fall into one of three buckets:
  - **orchestrated collaboration frameworks**
  - **interoperability / communication protocols**
  - **decentralized consensus or federation research**
- The closest adjacent practical substrate I found is **Campfire**: peer groups, recursive composition, no central authority, explicit fulfillment semantics, multi-transport support.
- The closest adjacent standards work is **A2A**: strong on interoperability and task exchange, weak on peer-group coordination as such.
- The closest adjacent decentralized research work is **AgentNet** and **DecentLLMs**: both remove a central orchestrator, but they do so through explicit graph structure or consensus roles rather than organic conversation.
- The most useful evaluation work for this repo is **LLM-Coordination** and **Emergent Coordination in Multi-Agent Language Models**. These do not provide a deployable framework, but they do provide language for what to measure.

The strongest conclusion from the spike is that the repo should treat **interoperability**, **coordination**, and **evaluation of emergence** as separate layers. Current art often conflates at least two of the three.

## Layer Definitions

The three layers I think should stay separate are:

### 1. Interop / transport substrate

This layer answers:

- how agents discover each other
- how they exchange messages, tasks, artifacts, and state
- how identity, addressing, and receipts work
- what the transport guarantees or does not guarantee
- how interruption, delivery, recovery, and multi-transport operation are handled

Examples from the research:

- **A2A** is primarily this layer: capability discovery, task lifecycle, message exchange, modality negotiation.
- **Campfire** is also strongly this layer, though it reaches upward into coordination via explicit fulfillment semantics and group composition.

Examples in this repo's current pilot:

- Discord as the shared surface
- open-floor routing
- reactions as a transport primitive
- pinned-rules ingestion
- `!stop` / `!resume`

This layer should answer **how agents can talk and stay in sync**, not **how they ought to organize socially**.

### 2. Coordination model

This layer answers:

- how agents decide who should act
- how initiative, yielding, interruption, and cooperation are handled
- whether norms are prescribed, inferred, or negotiated
- where human arbitration enters
- what counts as acceptable peer behavior

Examples from the research:

- **agentUniverse Discussion Group** hard-codes a host-led coordination model.
- **AgentNet** encodes coordination via dynamic topology and specialization.
- **DecentLLMs** encodes coordination via worker/evaluator roles and consensus.

Examples in this repo's current pilot:

- the idea of open-floor peer participation as a social mode, not just a routing mode
- coordination heuristics
- emoji conventions
- operator approval expectations
- any future policy around when a peer should respond, defer, build, or stay silent

This layer should answer **how peers work together legibly**, not just **how messages move**.

### 3. Evaluation of emergence and success

This layer answers:

- how we know coordination is actually working
- whether complementary behavior is emerging
- whether the system is only producing parallel output, or real peer organization
- what to measure during the pilot
- which findings are substrate-local and which seem general

Examples from the research:

- **LLM-Coordination** gives language for where coordination fails, especially around partner modeling.
- **Emergent Coordination in Multi-Agent Language Models** gives language for differentiation, complementarity, and collective structure.

Examples in this repo's current pilot:

- observations in `observations/harness-behaviors.md`
- future pilot success criteria
- any explicit comparison between 2-agent and N-agent behavior
- analysis of coordination failures, recovery, and drift

This layer should answer **whether the chosen substrate and coordination model are actually producing the thing we want**.

### Why the separation matters

If these layers are collapsed together, the repo risks importing the wrong answers from adjacent work:

- a transport standard starts pretending to be a social model
- a coordination policy gets mistaken for transport plumbing
- a pilot metric gets mistaken for a governance principle

The current art often does exactly that. Keeping the layers distinct is my main structural takeaway from the spike.

## Comparison Matrix

| Source | What it is | Coordination model | Human role | Transferable | Why it is not the target |
|---|---|---|---|---|---|
| Campfire | Peer coordination protocol | Many-to-many groups, recursive composition, explicit fulfillment | Human can be outside the loop; protocol carries coordination | Strong substrate ideas for p2p grouping, identity, receipt, recursion | More protocolized than the north star may want |
| A2A | Agent interoperability standard | Client-agent to remote-agent task exchange | Human typically initiates or supervises tasks | Good separation of interop from coordination | Not a peer-coordination model; still basically invocation-oriented |
| agentUniverse Discussion Group | Multi-agent discussion app | Host-organized rounds with participants | Human gives topic; host controls flow | Clear example of the default orchestrated pattern | Explicit moderator/host; not p2p |
| KNEXA-FL | Orchestrated-decentralized federation | Central profiler/matchmaker chooses p2p pairings | Human is outside the inner loop | Useful negative case for "thin orchestration" | Still requires a coordinating matcher |
| AgentNet | Decentralized agent network | Dynamic DAG routing by local expertise and RAG memory | Human mostly absent | Strong evidence that decentralized specialization is viable | Solves expertise routing, not legible conversation |
| DecentLLMs | Decentralized consensus for answer selection | Worker/evaluator roles with Byzantine-robust aggregation | Human mostly absent | Useful for fault tolerance and consensus language | Consensus layer, not coworker-style collaboration |
| LLM-Coordination | Evaluation benchmark | Coordination games, zero-shot partner matching | Human sets tasks / benchmark | Gives a way to measure coordination ability | Benchmark, not framework |
| Emergent Coordination in Multi-Agent Language Models | Evaluation / theory paper | Minimal feedback, no direct communication, prompt-induced collective structure | Human defines prompts / interventions | Useful language for emergence, differentiation, complementarity | Measurement lens, not an operational coordination design |

## Source Notes

### 1. Campfire

Source: https://getcampfire.dev/

What matters:

- Campfire positions itself explicitly as coordination "without a central server."
- A campfire is a group with its own cryptographic identity, and a campfire can join another campfire.
- The protocol supports:
  - no central authority
  - recursive composition
  - explicit `future` / `fulfills` semantics
  - reception requirements
  - multiple transports, including filesystem, HTTP, GitHub, and hosted MCP

Why it matters here:

- This is the strongest practical example I found of a real attempt to move coordination out of "the human as message bus."
- The recursive composition model is especially relevant. It lets sub-groups stay opaque while still participating as peers in a larger group.
- The protocol treats transport as negotiable, which matches the repo's instinct to separate governance from substrate.

What does not transfer cleanly:

- Campfire is more explicit and protocol-heavy than the current north star may want.
- `future` / `fulfills`, enforced reception, and eviction are powerful, but they are also exactly the sort of mechanism that can become orchestration-by-protocol if imported too early.

My read:

- Campfire is probably the most useful **positive** adjacent system.
- It is not a blueprint to copy, but it is the clearest evidence that peer coordination can be given a substrate without falling back to a central coordinator.

### 2. A2A

Source: https://developers.googleblog.com/a2a-a-new-era-of-agent-interoperability/

What matters:

- Google presents A2A as an open protocol for agents to communicate, securely exchange information, and coordinate actions across platforms.
- The model is client-agent to remote-agent.
- The protocol emphasizes:
  - capability discovery via agent cards
  - task lifecycle management
  - message exchange
  - modality negotiation
  - long-running task support

Why it matters here:

- A2A is useful precisely because it is **not** a full peer-coordination model.
- It cleanly separates inter-agent communication from higher-order governance and group behavior.
- That makes it a good example of how to keep interoperability distinct from coordination policy.

What does not transfer cleanly:

- A2A is still fundamentally invocation-oriented.
- It helps agents call, delegate to, and exchange artifacts with each other; it does not answer how a peer group should organically self-organize in a shared conversational environment.

My read:

- A2A is a strong candidate for a future transport/interoperability layer if the project ever generalizes beyond Discord.
- It should not be mistaken for the answer to the coordination question.

### 3. agentUniverse Discussion Group

Source: https://raw.githubusercontent.com/agentuniverse-ai/agentUniverse/master/docs/guidebook/en/Examples/Discussion_Group.md

What matters:

- The example uses two roles:
  - one discussion group host
  - multiple participants
- The host organizes the participants.
- Participants take turns by round.
- After several rounds, the host summarizes the result back to the user.

Why it matters here:

- This is a clean example of the default multi-agent discussion pattern in current frameworks.
- It is easy to reason about because control is centralized in a host role.

What does not transfer cleanly:

- It is explicitly not p2p.
- The moderator/host role is doing the exact work the project is trying not to hard-code into a central coordinator.

My read:

- Very useful as a **negative baseline**.
- It shows what the ecosystem reaches for when it wants "multi-agent discussion," and why that is not yet the same thing as peer coordination.

### 4. KNEXA-FL

Source: https://arxiv.org/abs/2601.17133

What matters:

- KNEXA-FL frames itself as "orchestrated decentralization."
- It removes central aggregation but keeps a central profiler/matchmaker.
- The central component does not exchange model weights directly, but it does decide who should collaborate with whom.

Why it matters here:

- This is a useful example of a design that recognizes pure random p2p is often not enough.
- It also shows one of the main temptations in decentralized systems: reintroduce a thin control layer because it works better.

What does not transfer cleanly:

- Even a non-aggregating matchmaker is still orchestration.
- This is optimizing model collaboration and knowledge transfer, not human-readable conversational coordination.

My read:

- KNEXA-FL is best read as a warning sign: decentralization often drifts back toward orchestration under performance pressure.

### 5. AgentNet

Source: https://arxiv.org/abs/2504.00587

What matters:

- AgentNet proposes decentralized coordination with dynamic DAG structure.
- Agents specialize, evolve, and route tasks based on local expertise and context.
- It removes central control and uses retrieval-based memory for continued specialization.

Why it matters here:

- This is one of the clearest research examples of decentralized specialization without a central orchestrator.
- It strengthens the claim that decentralized multi-agent systems do not need to collapse into fixed roles or a manager pattern.

What does not transfer cleanly:

- AgentNet is optimized around expertise routing and graph adaptation, not a human-readable shared conversation.
- It does not directly answer how human operators understand or arbitrate the group's behavior in real time.

My read:

- Useful proof that non-centralized specialization is viable.
- Less useful as a direct pattern for the repo's current conversational pilot.

### 6. DecentLLMs

Source: https://arxiv.org/abs/2507.14928

What matters:

- DecentLLMs proposes decentralized consensus with worker agents and evaluator agents.
- The design targets Byzantine robustness and answer quality under adversarial conditions.

Why it matters here:

- It introduces useful concepts for fault tolerance, answer selection, and robust aggregation.
- It also surfaces a core tradeoff: decentralized does not necessarily mean unconstrained; it can still rely on strong role structure.

What does not transfer cleanly:

- Evaluator/worker stratification is closer to consensus machinery than to coworker-style collaboration.
- It optimizes "pick the best answer" rather than "let a group work together legibly."

My read:

- Valuable as a resilience pattern.
- Not a fit for the primary interaction model unless the project later needs explicit adversarial or fault-tolerant answer selection.

### 7. LLM-Coordination

Source: https://arxiv.org/abs/2310.03903

What matters:

- The paper introduces a benchmark for coordination settings rather than a framework.
- It finds LLM agents perform better when coordination depends on environmental variables and worse when active consideration of partners' beliefs and intentions is required.
- It also suggests robustness to unseen partners in zero-shot coordination settings.

Why it matters here:

- This is directly relevant to the repo's north star because it gives language for where coordination breaks.
- The key signal is that coordination is not one thing. Simple shared-environment alignment is easier than reasoning about another agent's beliefs.

My read:

- Strong input for future evaluation design.
- If the pilot is meant to test organic coordination, it should include cases that genuinely require partner modeling, not just shared context reading.

### 8. Emergent Coordination in Multi-Agent Language Models

Source: https://arxiv.org/abs/2510.05174

What matters:

- The paper asks when a collection of LLM agents becomes a higher-order collective rather than a bundle of individual actors.
- It finds stronger collective structure when agents have identity-linked differentiation and prompts that ask them to consider what other agents might do.
- It distinguishes simple temporal coupling from performance-relevant synergy.

Why it matters here:

- This is the most directly useful source for thinking about what to measure in the pilot.
- It supports the idea that prompt-level framing can move a group from aggregate behavior to complementary behavior without hard-coding a protocol.

My read:

- This paper is important because it backs a middle position:
  - not full orchestration
  - not pure laissez-faire
  - but prompt and context structures that make complementarity more likely

That is close to the repo's actual design tension.

## Synthesis

### 1. Interoperability is not coordination

A2A is the clearest example. It solves agent discovery, task exchange, and communication format. It does not tell a peer group how to self-organize.

Implication:

- The repo should avoid conflating transport/interoperability work with coordination policy.

### 2. Decentralized does not mean unstructured

Campfire, AgentNet, and DecentLLMs all remove a central orchestrator, but they still impose structure:

- Campfire: explicit group and fulfillment semantics
- AgentNet: graph topology and retrieval-driven specialization
- DecentLLMs: worker/evaluator roles and consensus

Implication:

- The real design question is not `orchestrated vs free-form`.
- It is `what is the thinnest structure that still preserves legibility, recovery, and useful specialization?`

### 3. The closest gap in current art is human-readable peer collaboration

There are many systems for:

- centralized multi-agent orchestration
- agent invocation across frameworks
- decentralized consensus or federation

There are far fewer for:

- human-readable, peer-to-peer, multi-agent collaboration
- in a shared conversational surface
- with a human arbiter still visibly in the loop

Implication:

- The repo is not merely selecting among existing patterns.
- It is likely combining pieces that are usually studied separately.

### 4. The pilot should be treated as an experiment, not only a feature rollout

The evaluation papers matter because they suggest the right success signal is not just "did the agents produce something useful."

The stronger question is:

- Did complementary behavior emerge?
- Did agents model each other at all?
- Did shared context reduce or increase coordination failures?
- What failed at 2 agents, and what failure modes would likely amplify at N?

Implication:

- Pilot measurement should include emergence and interaction quality, not only task completion.

## Transferable Patterns

These feel worth carrying forward:

1. **Separate transport from coordination policy.**
   A2A is useful precisely because it does not try to be the whole system.

2. **Use a shared substrate that supports identity, history, and recoverability.**
   Campfire's cryptographic identity, recursive groups, and transport flexibility are strong cues.

3. **Expect decentralized systems to need explicit recovery semantics.**
   Reception, interruption, fulfillment, and state visibility do not disappear just because the system is p2p.

4. **Preserve agent differentiation without rigid role assignment.**
   Emergent Coordination suggests identity-linked differentiation and mutual modeling improve collective behavior.

5. **Measure coordination quality directly.**
   LLM-Coordination and Emergent Coordination are more useful here than another workflow framework because they help define what success even means.

## Non-Transferable or High-Risk Imports

These look risky to import wholesale:

1. **Host/moderator control as the default discussion pattern.**
   Useful baseline, wrong shape.

2. **Thin orchestration that quietly becomes a central planner.**
   KNEXA-FL is valuable, but its matchmaker is still orchestration.

3. **Consensus machinery as the main interaction model.**
   DecentLLMs is good for robust selection, not for organic coworker-style collaboration.

4. **Over-protocolizing too early.**
   Campfire's strongest ideas are also a warning: protocols become governance if imported without care.

## Open Questions for `peer-coordination`

1. What is the thinnest coordination layer that still gives:
   - identity
   - recoverability
   - interruption
   - group formation
   - human legibility

2. Which pilot mechanics are substrate-local and which are durable framework ideas?

3. How much explicit signaling should be designed versus allowed to emerge?

4. Is the right long-term model:
   - direct peer conversation
   - indirect coordination through shared artifacts
   - or a hybrid of both

5. What evaluation signals would show the pilot is surfacing real peer coordination rather than just polite parallel output?

## Working Conclusion

The most important thing I learned from the spike is that the repo should not ask one artifact to do too much.

There are at least three different problems in play:

1. **Interop / transport substrate**
2. **Coordination model**
3. **Evaluation of emergence and success**

Current art usually specializes in one of those three. The repo's distinctive move is that it is trying to keep all three visible at once while preserving a human-readable, non-orchestrated interaction style.

That makes the project unusual, but not ungrounded. There is enough adjacent work to justify the direction. There is not enough exact precedent to assume the current Discord pilot architecture is already the correct general form.

## References

- Campfire: https://getcampfire.dev/
- A2A announcement: https://developers.googleblog.com/a2a-a-new-era-of-agent-interoperability/
- agentUniverse Discussion Group example: https://raw.githubusercontent.com/agentuniverse-ai/agentUniverse/master/docs/guidebook/en/Examples/Discussion_Group.md
- AgentNet: https://arxiv.org/abs/2504.00587
- DecentLLMs: https://arxiv.org/abs/2507.14928
- KNEXA-FL: https://arxiv.org/abs/2601.17133
- LLM-Coordination: https://arxiv.org/abs/2310.03903
- Emergent Coordination in Multi-Agent Language Models: https://arxiv.org/abs/2510.05174
