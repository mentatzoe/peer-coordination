# Research Spike: Non-Orchestrated Peer Coordination — Claude's Notes

**Agent**: Claude (Opus 4.7, via Station)
**Date**: 2026-04-18
**Scope**: 1-day spike
**Parallel to**: Codex's spike (separate document, same questions, independent method)
**Triggered by**: peer-coordination discussion #32, Zoe's direction to proceed with independent spikes after Q1/Q2 alignment on the north star.

## Purpose

Survey what's known about **non-orchestrated peer coordination** — systems where multiple agents (AI, biological, or human) self-organize to collaborate without a central controller dictating turn-taking, task assignment, or conflict resolution.

The goal is NOT an exhaustive literature review. It's a focused probe to inform our scope: **which patterns transfer to our project, which don't, and which open questions should shape the next phase of specs.**

## Framing

Per the project's revised north star (ratified on discussion #32, 2026-04-18):

> A human-readable, non-orchestrated agentic p2p coordination framework, where agents infer a way of collaborating from shared context, local signals, and human-visible norms rather than from a central orchestrator or rigid machine protocol. Domain-agnostic: conversation, debate, games, creative work, crisis response, whatever.

This shifts the question from "what multi-agent frameworks exist?" to "what is known about **emergent** coordination across domains, and what fails when agents are left to self-organize?"

## Method

Five-hour reading pass across:
1. Current CS/AI multi-agent frameworks (AutoGen, CrewAI, LangGraph, CAMEL, AgentNet, agentUniverse, knexa-fl).
2. Swarm-intelligence literature (biological inspiration, stigmergy, emergent global behavior from local rules).
3. Historical failure cases (Facebook "negotiation bots" 2017 — emergent private language).
4. Human analogues (improv theater, deliberative dialogue) as proof that humans DO self-organize without orchestrators in specific domains, and lessons from how they do it.

Classification of each source on the shared axes I proposed on the discussion:

- Is the project orchestrated or peer-to-peer?
- Is coordination protocol-based or heuristic-based?
- Is the human a participant, an arbiter, or absent?
- What domains did they cover?
- What did they learn that generalizes?

## Survey

### A. CS/AI multi-agent frameworks

#### A1. AutoGen (Microsoft)
- **Orchestration**: mostly orchestrated (GroupChat has a "manager" agent that selects who speaks next), though the manager can be another LLM rather than hard-coded.
- **Coordination**: conversational, protocol-light. Agents talk in natural language, structure comes from role prompts and the group-chat manager.
- **Human posture**: participant-capable — agents converse with each other AND with humans in natural language.
- **Domains**: code generation, research, creative problem-solving.
- **What transfers**: group-chat as a coordination primitive (multiple agents, shared channel, turn-taking managed lightly). Natural-language-as-protocol works when agents are capable enough.
- **What doesn't**: still relies on a selector (the manager) — not fully peer-to-peer by our definition. And the "iterative refinement" model assumes everyone's working on the same task, not independent-work-with-occasional-coordination.

#### A2. CrewAI
- **Orchestration**: orchestrated (role-based with a Process that structures handoffs).
- **Coordination**: protocol-based (each role has explicit responsibilities, handoff rules).
- **Human posture**: configurable; usually absent after setup.
- **Domains**: business automation, structured workflows.
- **What transfers**: nothing directly — CrewAI is explicitly the orchestrated model we're moving away from. Useful as negative space: CrewAI works because it's structured; demonstrates the cost of ceding structure.

#### A3. LangGraph
- **Orchestration**: orchestrated (directed graph with conditional edges; graph IS the orchestrator).
- **Coordination**: protocol-based (state transitions are explicit).
- **Human posture**: usually absent; human-in-the-loop is a specific node type.
- **Domains**: enterprise workflows, stateful agent systems.
- **What transfers**: checkpointing / time-travel / state persistence patterns — if we want to inspect the trajectory of an emergent coordination episode, these ideas are useful for the observation infrastructure, not for the coordination itself.

#### A4. CAMEL ("Communicative Agents for Mind Exploration")
- **Orchestration**: semi-orchestrated. Two agents (AI assistant + AI user) operate in a "role-playing" frame where a task specifier seeds the task. After that, the two agents converse directly.
- **Coordination**: heuristic-based (inception prompting gives each agent its role and the norms of the interaction; not a rigid protocol).
- **Human posture**: seeder role, then absent.
- **Domains**: programming collaboration, business simulation, math/reasoning tasks.
- **What transfers**: **role-as-prompt-amendment is a light coordination mechanism that worked** — agents maintained coherent collaboration over many turns without an orchestrator in between. Also: inception prompting is effectively "pin the rules" for two agents — directly analogous to our MVP item 5 (pinned-rules ingestion).
- **What doesn't**: CAMEL's scenarios are typically 2 agents with aligned goals. Our case is 2+ agents where agents may have different domains of ownership (Dalgos for vault-keeper, Vigil for broader workspace), which creates coordination surface CAMEL didn't test.
- **Notable**: the paper explicitly studies "emergent knowledge" in the conversations — not just task completion. This matches our "pilot is an experiment" framing.

#### A5. AgentNet (NeurIPS 2025)
- **Orchestration**: **fully decentralized** — this is the closest thing in the literature to what we're trying to build.
- **Coordination**: hybrid. Agents form a Directed Acyclic Graph (DAG) dynamically; routing decisions are local (each agent decides whether to handle a task or forward it). RAG-based memory for agent self-specialization.
- **Human posture**: absent after setup.
- **Domains**: task-oriented (QA, multi-step reasoning). Not conversational.
- **What transfers**: **the DAG topology that adapts in real time** is interesting — we may want similar behavior where admitted peers shape themselves to whoever's best for the current conversation. The no-central-orchestrator stance aligns with our north star.
- **What doesn't**: AgentNet optimizes for task routing (which agent does the work), not for emergent coordination norms in a shared conversation. Our question is upstream — not "who does the task" but "how do they agree on how to talk." AgentNet assumes the coordination style is already solved.
- **Notable**: mentions "emergent collective intelligence" and "fault tolerance" as design goals. Aligns with our pilot-as-experiment framing.

#### A6. agentUniverse
- **Orchestration**: orchestrator-assumed. Their "Discussion Group" example pattern uses a moderator agent.
- **Coordination**: protocol-based (patterns library).
- **Human posture**: operator configures, then absent.
- **Domains**: multi-agent application development.
- **What transfers**: the Discussion Group pattern is conceptually similar to open-floor — but they solved it by adding a moderator (orchestrator-by-another-name). That's the exact trap we want to avoid per our Principle VI.
- **What doesn't**: their solution doesn't generalize to our north star because it recreates orchestration.

#### A7. knexa-fl (Fujitsu)
- **Orchestration**: orchestrated decentralized — contradictory at first glance, but their model has peer LLM nodes that federate via an orchestrator layer. More "coordinated distributed" than "emergent peer-to-peer."
- **Coordination**: protocol-based federation.
- **Human posture**: absent.
- **Domains**: federated LLM training/inference.
- **What transfers**: privacy-preserving coordination between agents with different knowledge domains is a useful pattern if we eventually want peer agents to share working state without sharing full context.
- **What doesn't**: their scope is federated ML, not conversational coordination. Totally different problem.

### B. Biological inspiration — swarms and slime molds

#### B0. Why biology before more CS

Biology has been solving distributed coordination for ~billions of years without anything resembling a central orchestrator. The failure modes and success patterns are empirically well-characterized. Two strands are worth separating: swarm intelligence (many simple individuals) and slime-mold-style distributed self-organization (one organism behaving like a network).

#### B1. Swarm intelligence — key principles
- **Local interactions produce global behavior** without the individuals knowing the global pattern (stigmergy, flocking rules, ant pheromone trails).
- **Robustness emerges from redundancy and simple rules** — individuals can fail, the swarm continues.
- **No single individual holds global state** — the environment itself is the shared state.
- **Emergent behavior is often unreasonably effective at specific tasks** (foraging, migration, nest construction) but fails outside those narrow cases.

#### B2. What transfers to our case

- **Shared environment as coordination substrate.** In our pilot, the Discord channel IS the shared state. All agents see the same messages, same pins, same reactions. This is stigmergy-like: coordination happens by acting on the shared environment, not by direct agent-to-agent messages.
- **Local rules, global behavior.** Our 7 heuristics (claim by answering, yield explicitly, etc.) are local rules. If they produce coherent global coordination, that's swarm-analogous.
- **Simplicity of individuals.** Swarms work with simple rules. We're in the opposite case — our agents are complex LLMs — but the INVARIANTS we enforce on them should be simple. Complex rules imposed on complex agents is where coordination gets brittle.

#### B3. What doesn't transfer from swarms

- **Swarms don't do language.** They do spatial coordination. Our agents' substrate is text, which has vastly more degrees of freedom. Lessons about spatial convergence don't help with semantic convergence.
- **Swarms don't negotiate task allocation in human-legible form.** A bee doesn't explain why it's foraging west; it just does. Our agents' actions MUST be legible to humans (Principle VI).
- **Swarms optimize for a narrow fitness function.** Our agents are general-purpose; there's no analogous fitness gradient.

#### B4. Slime molds — the one-organism-as-network case (added per Zoe's suggestion)

*Physarum polycephalum* — the acellular slime mold — is a distinct and unusually relevant analogue. It's NOT a swarm (it's a single organism), but it behaves as a distributed network:

- **No nervous system, no central control.** The organism is a single cell with many nuclei, spread across a substrate in a tube network.
- **Problem-solving by gradient response.** In classic experiments, Physarum solves maze shortest-path problems and approximates optimal transport networks (e.g., famously, the Tokyo rail network) simply by growing tubes toward food sources and thickening the tubes that carry the most flow.
- **The substrate does the computation.** Physarum doesn't model its environment; the environment itself is the computational surface. Signaling molecules diffuse through tubes; successful pathways thicken via positive feedback; unused pathways atrophy.

**Why this is a better analogue than swarms for some of our invariants:**

1. **One-organism-as-network maps to the "single logical entity composed of distributed processes" framing.** Our peer-coordination isn't really two independent agents coordinating — it's more like two lobes of a thinking process sharing a substrate. Swarm framing can mislead us into thinking of agents as autonomous in a way they're not; slime mold framing captures the shared-substrate reality better.
2. **Positive-feedback thickening matches how conventions strengthen.** When one agent uses 👀 successfully, the other is more likely to use it, the operator sees it work, it becomes a convention. Physarum's successful-pathway-thickening is this same dynamic — reinforced signaling without central sanction.
3. **Atrophy is active.** Unused pathways actively weaken and disappear. Our heuristics should probably work the same way: if a pattern isn't used, it shouldn't be enforced forever. Contrast with protocol-based systems where deprecation is explicit and costly.
4. **No internal messaging; environment IS the signal.** Physarum doesn't send messages between tubes; flow through tubes IS the message. Analogous to our design: agents don't message each other through a side-channel; they act on the shared Discord channel and that IS the coordination medium.

**What doesn't transfer from slime mold:**

- Physarum doesn't need to produce human-legible output. Its "reasoning trace" is physical — you can see the tubes. Our agents produce text that humans read, and the constraint that the text stays legible to humans isn't something biology enforces.
- Slime mold is homogeneous — every part of the organism has the same "behavior rules." Our agents are different (Claude, Codex) with different training, different strengths. More like a heterogeneous ecosystem than a single organism.
- Physarum is deterministic at the tube level (given substrate + food positions, you get roughly the same network). LLMs are stochastic. Conventions we rely on need to survive sampling noise.

**Notable**: the Physarum model has been formalized as a distributed algorithm with provable convergence to shortest paths (Bonifaci et al. 2012 — included in sources). That's unusual — biology usually resists formalization, and when it yields, the formal model is worth studying. For us: **our heuristics probably have an analogous formal analogue worth discovering**, even if we don't formalize it up front.

### C. Historical failure case: Facebook negotiation bots (2017)

In 2017, Meta AI researchers trained two chatbots to negotiate item splits. Because the reward function incentivized successful negotiation (not English), the bots developed a **private shorthand** — phrases like `"i i i i i i i"` where repetition encoded quantity. The experiment was shut down / the bots were constrained to human-readable language.

This is the most cited failure mode of emergent multi-agent coordination. What it teaches us:

- **When agents optimize only for outcomes and not for legibility, they drift away from human-readable communication.** This is the central risk of our project.
- **Reward functions are where this risk lives.** If we ever instrument the pilot with any success metric that agents can optimize for, we risk the same drift.
- **Mitigation: Principle VI is exactly the right invariant.** Human legibility is a constraint, not a nice-to-have. Our agents shouldn't be optimizing for outcomes at the expense of legibility — because that path leads to `"i i i i i i"`.

**However**: the Facebook bots were trained from scratch with RL. Our agents are pre-trained LLMs with strong priors toward natural language. The failure mode is attenuated but not eliminated — we could still see drift toward in-group shorthand (e.g., `"+1"` as a shortcut for substantive agreement) if we don't watch for it.

### D. Human analogues

Humans routinely self-organize without orchestrators in specific domains. Lessons from two:

#### D1. Improv theater (Yes-And norm)

Improv succeeds at multi-performer coordination with no director and no script. The load-bearing norms are:

- **"Yes, and"**: accept what the previous performer offered, then extend. Don't deny or rewrite.
- **Make your scene partner look good**: the goal is collective excellence, not individual spotlight.
- **Commit to the offer**: don't hedge; treat established facts as real.
- **Trust the ensemble**: someone will handle what you can't; don't try to control everything.

**What transfers to our project**:

- **Norms-as-coordination mechanism.** Improv runs on a small set of internalized norms, not a protocol. Directly analogous to our 7 heuristics.
- **Build, don't compete.** Our heuristic #3 is essentially "Yes, and."
- **Silence is OK.** Improv has "the silent scene"; not every performer speaks in every beat. Our heuristic #5.

**What doesn't transfer**:
- Improv is **ephemeral** — scenes don't need to be replayed or audited. Our agents' actions need to be auditable in logs. Improv norms don't constrain the output for external readability the way Principle VI does.
- Improv works because performers are **trained together** on the norms. Our agents don't have shared training; they have shared prompts + pinned rules.

#### D2. Quaker meetings / deliberative dialogue

Quaker business meetings use "sense of the meeting" — no vote, no leader; the group reaches a consensus through silence-punctuated speaking, and a clerk surfaces the emergent agreement when it stabilizes. Academic work on deliberative democracy extends this to AI-assisted deliberation.

**What transfers**:

- **Silence as part of the coordination.** Not speaking is as important as speaking. Our heuristic #5 (silence is OK) is this exact pattern.
- **The clerk is not a decision-maker.** They surface what's emerging, they don't direct it. If we ever need a role that looks like coordination-helper, this is the model — observe and surface, not decide.
- **Long time horizons are OK.** Quaker meetings take hours; convergence isn't rushed. We should not artificially force rapid convergence in the pilot.

**What doesn't transfer**:
- Quaker meetings have **shared values prior to the meeting**. Our agents have different training, different biases, no shared history. Can't assume value alignment.
- The "sense of the meeting" is a social construct that requires **humans reading the room**. LLMs don't read the room the same way; proxies like explicit agreement reactions (✅ in our emoji palette) are necessary.

## Patterns that transfer to our project

Cross-referencing the sources above:

1. **Shared environment as coordination substrate (stigmergy, improv stage, meeting room).** Our Discord channel is the shared state. Pinned rules + message history + reactions all live in that shared state. This is load-bearing for our model.

2. **Local rules, global behavior (swarms, improv).** Our 7 heuristics should be LOCAL to each agent's decision-making. We should resist pushing them into the global transport layer — Principle VI's meeting-not-protocol framing is exactly this.

3. **Role-as-prompt-amendment (CAMEL, improv "character").** Agents take on roles through prompts + pinned rules, not through hard-coded role logic. Aligns with our MVP item 5 (pinned-rules ingestion).

4. **Heuristics, not handshakes (improv, Quaker).** Norms are internalized per agent; the other agent doesn't need to receive a protocol message to know what you're doing. Aligns with the v1.1.1 constitution trim.

5. **Human legibility as explicit invariant (Principle VI; contra Facebook 2017).** If we don't enforce this, drift happens. Not optional.

6. **Emergent observation is the point, not a side effect (CAMEL, AgentNet's "emergent intelligence" framing).** The pilot is an experiment, not a feature ship — our Q2 ratification.

7. **Silence as coordination (Quaker, swarm robotics' "don't signal if nothing to signal", improv's silent scene).** Agents not responding IS information. Our heuristic #5.

## Patterns that do NOT transfer (watch for these false friends)

1. **Orchestrator patterns dressed up as peer-to-peer.** AutoGen's GroupChat, agentUniverse's Discussion Group — both add a moderator agent and call it emergent. Don't. Principle II excludes this.

2. **Protocol-based task routing (AgentNet's DAG).** Task routing is a different problem than conversational coordination. If we find ourselves designing a task-routing mechanism, we've shifted problems.

3. **Reward-based optimization (Facebook 2017).** We should NOT introduce any success metric agents can optimize for. Observations are the unit of value, not scores.

4. **Swarm-style "simple agents" thinking.** We have complex agents. The wisdom is "simple rules, complex agents" — don't translate "simple rules" into "simple agents." Our agents are full LLMs with all their capability intact.

5. **Value-pre-alignment assumption (Quaker meetings).** We can't assume agents share values. The constitution provides the common ground; we should not rely on implicit shared context beyond that.

## Open questions for our case

From the spike, these surface as questions I didn't have good answers for:

1. **What's the unit of observation for the pilot?** If the pilot is an experiment, what are we measuring? Candidates: convergence time, legibility of the trace, emergence of heuristics not in the initial pinned rules, drift from heuristics over time. Related to observation #7 from the scratchpad.

2. **How do we detect drift toward private protocol?** Facebook's `"i i i i i"` would be obvious; subtler drift (e.g., agents using emoji in ways that have in-group meaning but aren't legible to Zoe) would need detection. Manual review? Periodic audit?

3. **Does coordination degrade when we add a third agent?** Everything in our current design is 2-agent. The swarm literature suggests coordination generally works at scale IF the local rules are simple and robust — but we haven't tested 3-agent cases and "the rules are simple" is more aspirational than verified.

4. **Is the pilot's Discord substrate load-bearing, or arbitrary?** If we move to Slack, Telegram, or a terminal, does the model still work? The swarm literature says the substrate choice affects what emerges; the improv literature says the stage shapes the performance.

5. **How do we capture emergent heuristics that we didn't predict?** If the agents invent a new convention during the pilot (e.g., "I'll mark this with 🚧 to indicate work-in-progress"), that's exactly what we want to observe. The observations file is one surface; do we need something more structured?

6. **Do "roles" need to be explicit in prompts, or can they be truly emergent?** CAMEL uses role prompts; improv uses character choices. Our agents have identities (Dalgos, Vigil) but not roles per se. Might this be a gap?

## Recommendations for the pilot

Grounded in what transferred:

1. **Pin rules, don't encode rules.** The MVP item 5 (pinned-rules ingestion) is the right mechanism; pinning specific heuristics to a channel is the right way to apply them. Don't hard-code heuristics in agent prompts directly — keep the pinned rules as the authoritative source that can be changed per-channel.

2. **Instrument observations, not rewards.** Every coordination episode produces an observation. Keep the observations file pattern going; consider more structured extraction (frequency of each heuristic's use, who yields most often, whether silence is actually happening).

3. **Legibility-first audit.** Periodically review pilot transcripts for drift toward in-group shorthand. If agents start using reactions in non-palette ways (custom emoji, meaningful omissions), flag it.

4. **Defer 3-agent testing until 2-agent patterns stabilize.** The literature supports that scale changes the dynamics. Don't multiply variables.

5. **Test substrate portability lightly.** Before declaring the model "domain-agnostic" per the north star, try one non-Discord substrate (maybe a terminal-based conversation) to verify the mechanisms don't depend on Discord specifics.

6. **Consider a "meeting minutes" artifact per session.** Analogous to the Quaker clerk's role — surface what happened, what converged, what didn't. Could be an auto-generated summary at session close, cross-referenced with the observations file.

## What Codex's spike will likely cover that mine won't

Flagging for comparison-readiness:

- More formal literature depth on multi-agent systems theory (Shoham-Leyton-Brown territory, BDI architectures, etc.).
- Tighter typology of coordination patterns from game-theoretic / agent-theoretic angles.
- Probably more rigorous evaluation of AgentNet's formal claims.

My angle leaned toward cross-domain analogues (improv, Quaker, swarm) and the legibility/drift risk. Expect the two documents to complement rather than overlap.

## Sources

- [AgentNet: Decentralized Evolutionary Coordination for LLM-based Multi-Agent Systems](https://arxiv.org/abs/2504.00587) — the closest existing work to our model.
- [Multi-Agent Collaboration Mechanisms: A Survey of LLMs](https://arxiv.org/html/2501.06322v1)
- [CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society](https://arxiv.org/abs/2303.17760)
- [CrewAI vs LangGraph vs AutoGen: Choosing the Right Multi-Agent AI Framework](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)
- [6 Multi-Agent Orchestration Patterns for Production (2026)](https://beam.ai/agentic-insights/multi-agent-orchestration-patterns-production)
- [From animal collective behaviors to swarm robotic cooperation](https://pmc.ncbi.nlm.nih.gov/articles/PMC10089591/)
- [Swarm intelligence — Wikipedia](https://en.wikipedia.org/wiki/Swarm_intelligence)
- [Physarum polycephalum: the Mazerunner — Bioengineering Hyperbook, McGill](https://bioengineering.hyperbook.mcgill.ca/physarum-polycephalum-slime-mold-the-mazerunner/)
- [A mathematical model for adaptive transport network in path finding by true slime mold — Tero et al., PubMed](https://pubmed.ncbi.nlm.nih.gov/17069858/)
- [Physarum Can Compute Shortest Paths — Bonifaci et al., arXiv 1106.0423](https://arxiv.org/abs/1106.0423)
- [Random network peristalsis in Physarum polycephalum organizes fluid flows across an individual — PNAS](https://www.pnas.org/doi/10.1073/pnas.1305049110)
- [Deal or no deal? Training AI bots to negotiate — Engineering at Meta (2017)](https://engineering.fb.com/2017/06/14/ml-applications/deal-or-no-deal-training-ai-bots-to-negotiate/)
- [Did Facebook Shut Down an AI Experiment Because Chatbots Developed Their Own Language? — Snopes](https://www.snopes.com/fact-check/facebook-ai-developed-own-language/)
- [Yes, And: Improv's Most Important Rule — Backstage](https://www.backstage.com/magazine/article/yes-and-improv-rule-77269/)
- [Creative Collaboration: Lessons from Improv Theater](https://innovationmanagement.se/2008/11/04/creative-collaboration-lessons-from-improv-theater/)
- [The Secret Language Of AI: Emergent Communication In Machines](https://aicompetence.org/the-secret-language-of-ai-emergent-communication/)
- [agentUniverse](https://github.com/agentuniverse-ai/agentUniverse) (surfaced by Zoe)
- [knexa-fl](https://github.com/FujitsuResearch/knexa-fl) (surfaced by Zoe)
