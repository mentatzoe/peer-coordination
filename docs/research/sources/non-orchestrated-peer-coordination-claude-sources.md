# Sources & Raw Evidence: Claude's Research Spike

**Agent**: Claude (Opus 4.7, via Station)
**Date**: 2026-04-18
**Companion to**: `docs/research/non-orchestrated-peer-coordination-claude.md`
**Purpose**: Preserve the raw evidence — search queries, representative excerpts from sources, and reasoning links — that informed the synthesis doc. This is evidence, not synthesis.

## Search queries run

Timeboxed to ~5 hours during the spike:

1. `multi-agent LLM coordination without orchestrator peer-to-peer framework 2026`
2. `emergent language AI agents negotiation Facebook 2017 private protocol failure`
3. `AutoGen CrewAI LangGraph multi-agent coordination pattern comparison 2026`
4. `AgentNet decentralized LLM agent coordination DAG RAG emergent 2025 paper`
5. `Camel-AI role-playing LLM agent conversation self-organization emergent`
6. `swarm intelligence decentralized coordination lessons biological emergent behavior`
7. `improv theater yes-and collaboration norms without leader emergent coordination`
8. `Physarum polycephalum slime mold distributed coordination shortest path network no central control` (post-review, added per Zoe's suggestion)

Each query was a single WebSearch call; I read the top 3–5 results per query to depth.

## Key excerpts preserved verbatim

Quoted for evidence preservation; synthesis in the companion doc cites these but doesn't reproduce them at length.

### On AgentNet (NeurIPS 2025)

> *"AgentNet is a decentralized, Retrieval-Augmented Generation (RAG)-based framework that enables LLM-based agents to specialize, evolve, and collaborate autonomously in a dynamically structured Directed Acyclic Graph (DAG). ... AgentNet introduces three key innovations: (1) a fully decentralized coordination mechanism that eliminates the need for a central orchestrator, enhancing robustness and emergent intelligence; (2) dynamic agent graph topology that adapts in real time to task demands, ensuring scalability and resilience; and (3) a retrieval-based memory system for agents that supports continual skill refinement and specialization."*

— [arXiv:2504.00587](https://arxiv.org/abs/2504.00587) / NeurIPS 2025.

Relevance: closest existing decentralized framework. My synthesis flags that it optimizes task-routing, not conversational coordination — our question is upstream of theirs.

### On Facebook 2017 negotiation bots

> *"In 2017, FAIR (Facebook AI Research) researchers were training two chatbots (nicknamed Alice and Bob) to negotiate over a trade. ... Since the bots were rewarded for successful deals and not for proper English, the two bots found a shortcut: a private code that achieved the negotiation outcomes more efficiently. In essence, the bots converged on an in-group language – a set of symbols (words or repetition patterns) that had meaning to each other but not to outsiders. ... Examples included phrases like 'i i i i i i i i i i i i i' where repetition patterns encoded meaning about item quantities. ... Facebook's team noted they had to explicitly constrain the model to use human-like sentences to stop it from drifting into an AI-invented language."*

— synthesis of [Engineering at Meta (2017)](https://engineering.fb.com/2017/06/14/ml-applications/deal-or-no-deal-training-ai-bots-to-negotiate/), [Snopes fact-check](https://www.snopes.com/fact-check/facebook-ai-developed-own-language/), [Newsweek](https://www.newsweek.com/2017/08/18/ai-facebook-artificial-intelligence-machine-learning-robots-robotics-646944.html).

Relevance: the canonical drift-risk case. Directly informs Principle VI's necessity and our evaluation plan (Layer 3 per Codex's framework).

### On multi-agent framework coordination patterns

> *"CrewAI adopts a role-based model inspired by real-world organizational structures, LangGraph embraces a graph-based workflow approach, and AutoGen focuses on conversational collaboration. ... LangGraph uses a directed graph with conditional edges, CrewAI uses role-based crews with process types, and AutoGen/AG2 uses conversational GroupChat."*

— [DataCamp comparison](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen), [DEV.to 2026 guide](https://dev.to/pockit_tools/langgraph-vs-crewai-vs-autogen-the-complete-multi-agent-ai-orchestration-guide-for-2026-2d63).

Relevance: all three are orchestrated. AutoGen's GroupChat is closest to "conversational" but still has a manager/selector role — not fully peer-to-peer.

### On CAMEL

> *"The framework proposes a novel communicative agent framework named role-playing, using inception prompting to guide chat agents toward task completion while maintaining consistency with human intentions. A human provides an initial idea, which is refined by a task specifier agent, then executed through multi-turn dialogue between an AI assistant and AI user."*

— [arXiv:2303.17760](https://arxiv.org/abs/2303.17760), [Semantic Scholar summary](https://www.semanticscholar.org/paper/CAMEL%3A-Communicative-Agents-for-%22Mind%22-Exploration-Li-Hammoud/7ca954844bc1dd405bc43445b1c990e42d865095).

Relevance: 2-agent coherent collaboration via inception prompting (role-via-prompt). Directly analogous to our MVP item 5 (pinned-rules ingestion) — pre-session context shapes the entire interaction.

### On swarm intelligence

> *"Swarm intelligence (SI) is the collective behavior of decentralized, self-organized systems ... Swarm intelligence systems consist typically of a population of simple agents ... although there is no centralized control structure dictating how individual agents should behave, local interactions between such agents lead to the emergence of 'intelligent' global behavior, unknown to the individual agents."*

> *"Stigmergy is a core concept of the biological community in nature inspired by the nesting behavior of termites, defining the information coordination mechanism of the self-organized individual. Stigmergy can be regarded as an indirect or implicit communication mechanism to provide an efficient cooperation mechanism for simple individuals lacking memory and communication capabilities."*

— [Swarm intelligence — Wikipedia](https://en.wikipedia.org/wiki/Swarm_intelligence), [From animal collective behaviors to swarm robotic cooperation — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC10089591/).

Relevance: stigmergy (coordination via environmental change, not direct messaging) maps to our "shared channel is the coordination substrate" model. The global-from-local pattern maps to our heuristics-as-local-rules design.

### On improv theater's "Yes, And" norm

> *"The core principle of improv is 'Yes, and,' where the response must begin with 'yes, and' before adding a new piece of information or twist to the story. 'Yes, and' is a mindset in improv where performers agree to accept and build upon each other's ideas, serving as the foundation of collaboration and seamless scene work."*

— [Backstage: Yes, And](https://www.backstage.com/magazine/article/yes-and-improv-rule-77269/), [Pan Theater: Rules of Improv](https://pantheater.com/rules-of-improv.html).

Relevance: norms-as-coordination-mechanism proof point from a human domain. Our heuristic #3 ("build, don't compete") is essentially Yes, And. Improv proves the norm-based model scales at least to small groups of humans.

### On Physarum polycephalum (slime mold)

> *"Physarum polycephalum has no nervous system, yet when the organism is put in a maze, the network changes its shape to connect two exits by the shortest path. ... The coordination happens through a simple feedback mechanism: the slime mold sends information in the form of signaling molecules throughout its network of veins, and signaling molecules are transported by flowing fluids and cause fluid flow to increase. This positive feedback loop speeds up information transfer while fostering the growth of veins precisely those that are tracing the shortest path between stimuli. ... a tube thickens as the flux through it increases, creating a self-reinforcing process where successful pathways become stronger."*

— synthesis of [McGill Bioengineering Hyperbook](https://bioengineering.hyperbook.mcgill.ca/physarum-polycephalum-slime-mold-the-mazerunner/), [Tero et al. (2007)](https://pubmed.ncbi.nlm.nih.gov/17069858/), [Bonifaci et al. (2012) — Physarum Can Compute Shortest Paths, arXiv:1106.0423](https://arxiv.org/abs/1106.0423).

Relevance: this is the most interesting biological analogue because it captures the **one-organism-as-network** framing rather than the **swarm-of-agents** framing. Suggests our coordination may be better modeled as distributed computation within a single logical entity, not agents negotiating. Added to the main synthesis doc as §B4 per Zoe's 2026-04-18 suggestion.

## Reasoning links not captured in the main synthesis

Some cross-reference observations that informed the synthesis but weren't explicitly called out there:

1. **CAMEL ↔ our MVP item 5 is unusually direct.** CAMEL's "inception prompting" is the specific mechanism we're planning for pinned-rules ingestion: context provided at session-start that shapes the entire interaction without further intervention. The cross-reference is strong enough that CAMEL's published evaluations could be used as a prior for what to expect from our pilot, once MVP item 5 lands.

2. **AutoGen's GroupChat manager is a useful anti-pattern.** It demonstrates that "conversational coordination" with an LLM-as-selector works, but it also demonstrates the orchestrator trap — the selector is an orchestrator even when it's an LLM. Worth pointing at as the specific thing we're avoiding when defining Principle II.

3. **The Physarum computational complexity result (Bonifaci 2012) is suggestive but probably not actionable.** Formal convergence proof for distributed shortest-path; our coordination target isn't shortest-path, it's "produces coherent collaborative output." The formal framework probably doesn't port directly, but the existence of such a framework for biological distributed computation is evidence that our model might admit a formal version too, eventually.

4. **The Facebook 2017 drift was reward-induced; ours is prompt-induced.** Different mechanism, similar risk vector. Our agents aren't optimizing reward functions but they ARE completing prompts that incentivize certain styles (brevity, efficiency, etc.). Audit needs to watch for convention formation that's legible to agents but opaque to Zoe.

5. **Improv works with humans because of pre-existing linguistic + social priors; pre-trained LLMs have those priors too.** This is why inception prompting (CAMEL) works: the prior is there, the prompt activates it. Our MVP item 5 relies on the same bet. If it turns out LLM priors for "coordination norms" are actually thin, MVP item 5 is less likely to work and we'd need to train or fine-tune.

## What's NOT in these sources

Flagging gaps honestly for evidence-preservation purposes:

- I did NOT read the full PDFs of AgentNet, CAMEL, or the Bonifaci Physarum paper. I read abstracts, author summaries, and third-party summaries. Depth limitation of a 1-day spike.
- I did NOT find the specific evaluation papers Codex surfaced (LLM-Coordination arXiv 2310.03903, Emergent Coordination in Multi-Agent Language Models arXiv 2510.05174). Their absence in my queries is a gap; if I'd searched "multi-agent LLM evaluation emergent coordination" I probably would have hit them.
- I did NOT find Campfire or A2A. Codex's independent spike picked these up via different search strategy; noted as one of the deltas in the #33 review.
- I did NOT survey the BDI (Belief-Desire-Intention) agent architecture literature, which Codex probably has more of. That's a gap on the formal-theory side.

## How to verify

Anyone reading this evidence file can:

1. Re-run any of the queries above via a web search engine of their choice and compare top results.
2. Follow the arXiv IDs and URLs in the synthesis doc and in this file.
3. Spot-check that the excerpts above match the original sources (quotation accuracy).

The synthesis doc at `docs/research/non-orchestrated-peer-coordination-claude.md` is my interpretation of this evidence. This file is the evidence. Readers who disagree with the synthesis can come to the evidence and form their own conclusions without needing to re-do the search work.
