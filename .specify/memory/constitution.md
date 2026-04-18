<!--
Sync Impact Report
- Version change: 1.2.0 → 1.3.0 (MINOR — adds an explicit independent-review expectation for material changes before promotion)
- Amendment rationale: Zoe approved the generalized constitutional form of a review-separation rule: material changes should receive independent review from an agent or human other than the primary author. The intent is independence of review, not PR-specific workflow. This strengthens governance review expectations without hard-coding tool-specific process. Scratchpad: `ideas/constitution-amendment-review.md`.
- Modified principles: none
- Modified sections:
  - Governance — compliance review expectations expanded to include independent review by someone other than the primary author for material changes
- Added principles: none
- Removed principles: none
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no changes needed
  - .specify/templates/spec-template.md ✅ no changes needed
  - .specify/templates/tasks-template.md ✅ no changes needed
  - templates/scratchpad.md ✅ no changes needed
  - AGENTS.md ✅ no changes needed
  - CLAUDE.md ✅ no changes needed
- Follow-up TODOs:
  - When the Transport MVP Spec is written, it MUST incorporate the 7 coordination heuristics, the react-driven loop-prevention choice, and the "transport MUST NOT block inter-agent replies" rule.
- Prior history:
  - 1.2.0 (ratified 2026-04-18) — added the explicit promotion-boundary rule to Principle III and Governance; updated the scratchpad template to match.
  - 1.1.1 (ratified 2026-04-18) — trimmed Principle VI to governance-only language; moved heuristics and mechanism language back to follow-on spec territory.
  - 1.1.0 (ratified 2026-04-18) — added Principle VI (since trimmed), expanded Principle III scratchpad definition, added P1–P4 roadmap priorities, MVP scope clarification (since trimmed).
  - 1.0.0 (ratified 2026-04-18) — initial constitution with principles I–V, Scope and Deliverables, Specification Workflow and Roadmap, Governance.
-->

# peer-coordination Constitution

## Core Principles

### I. Constitution Is Canonical
This repository MUST be the canonical home of the peer-coordination standard.
Governance for multi-agent collaboration MUST live here, not inside downstream
implementation repos or ephemeral chat history. When a scratchpad, Discord
thread, or implementation detail conflicts with this constitution, the
constitution wins once amended and ratified. The purpose of this repo is to
separate the standard from any one consuming project so the standard can remain
coherent even as implementations change.

### II. Transport Is Plumbing, Not Governance
Transport systems such as `cc-connect` MUST be treated as session and delivery
plumbing, not as the source of coordination policy. Transport may enforce
selected mechanics such as routing, interruption, reactions, or channel-scoped
controls, but it MUST NOT become the only place where the collaboration model is
defined. Governance belongs in this repository; transport repos implement the
parts that need code. This keeps the standard understandable even when multiple
transports or runtime setups exist.

### III. Scratchpad First, Then Promotion
Live coordination MAY begin in a scratchpad such as `ideas/peer-coordination.md`
when ideas are still moving quickly, but settled decisions MUST be promoted into
constitutional or spec artifacts here. Scratchpads capture a **Policy Body**
(evolving canonical thinking, edited in place as consensus forms), **Resolved
and Open Questions**, **Next Actions**, and a turn-based **Discussion Log**
(append-only). The Policy Body reflects current thinking; the Discussion Log
preserves history of how the thinking evolved. The canonical scratchpad
structure is defined in `templates/scratchpad.md`. Scratchpads are not the
final authority — constitutions and specs capture ratified decisions.
Scratchpad convergence alone MUST NOT amend durable artifacts. Promotion from a
scratchpad into a constitution, spec, or other governance artifact requires an
explicit operator-directed promotion step. This preserves context without
letting policy drift across half-finished notes or discussion alone be mistaken
for ratification.

### IV. Human Arbitration and Explicit Consent
The human operator MUST remain the final arbiter of coordination policy,
ownership disputes, and state-changing actions in shared channels. Agents MAY
propose actions, negotiate boundaries, and suggest workflow changes, but they
MUST leave final approval and policy arbitration to the human when outcomes are
ambiguous or have side effects. Interrupt semantics such as `!stop` and
`!resume`, and approval policies layered above native tool approvals, exist to
keep experimentation safe without collapsing into hidden autonomy.

### V. Parallel Work Requires Explicit Ownership
When multiple agents work in parallel, they MUST record ownership boundaries,
expected touched files or surfaces, and acceptance criteria before overlapping
implementation begins. Parallelism is encouraged, but silent overlap is not.
Routing work, reaction work, and governance work SHOULD be split into clear
slices with documented ownership, then reconverged through shared specs and
scratchpads. Organic differences in tone or style MAY emerge, but they MUST NOT
be turned into artificial governance rules unless the operator explicitly wants
that.

### VI. Coordination Is Human-Legible, Not Over-Protocolized
Multi-agent collaboration MUST remain legible to the human operator and SHOULD
prefer heuristic, operator-centered coordination over brittle handshake
protocols. Specific coordination heuristics, acknowledgment behaviors, and
loop-management rules are operational and belong in follow-on specs.

## Scope and Deliverables

This repository defines the peer-coordination standard itself.

- It MUST contain constitutions, specifications, scratchpads, and decision
  records for multi-agent collaboration.
- It MUST NOT become the implementation home for transport features that belong
  in downstream repos such as `cc-connect`.
- It MAY reference downstream repos as implementation targets, pilot venues, or
  adopters of the standard.
- It MUST preserve the distinction between governance, specification, and
  implementation so that downstream repos are consumers of the standard rather
  than parents of it.

The minimum durable outputs of this repo are:

- a ratified constitution
- feature specs for important slices of the standard
- a live coordination scratchpad while work is active
- explicit records of confirmed decisions, open questions, and next actions

## Specification Workflow and Roadmap

Work in this repository MUST follow a simple promotion path:

1. Explore and converge in the scratchpad.
2. Ratify durable rules in the constitution.
3. Create follow-on specs for scoped concerns that are too detailed for the
   constitution.
4. Implement code changes in the downstream repo that owns them.
5. Feed results, lessons, and unresolved tensions back into this repository.

The current roadmap of follow-on specs is, in priority order:

1. **Transport MVP Spec (P1)** — blocking the first open-floor pilot.
   Defines the first open-floor pilot capabilities, including open-floor mode,
   hard interrupt behavior, reactions, approval-via-react, and pinned-rules
   ingestion. This spec belongs here; implementation belongs in `cc-connect`.

   The Transport MVP Spec MUST preserve Principle VI. Loop prevention,
   acknowledgment behavior, and interrupt semantics are defined in the spec,
   consistent with that principle.

2. **Channel Policy and Presence Spec (P2)**
   Defines channel activation modes, per-channel allowlists, verbosity levels,
   ambient behavior, and how bots are intentionally present in a guild.

3. **Workspace and Session Binding Spec (P3)**
   Defines multi-workspace behavior, channel-to-repo binding, workspace init
   prompts, and recovery behavior when agents enter new channels.

4. **Operations and Rollout Spec (P4)**
   Defines pilot rollout, safety checks, migration expectations, and how the
   standard graduates from experimental use to broader adoption.

These follow-on specs MUST stay subordinate to the constitution and MUST NOT
silently redefine its principles.

## Governance

This constitution governs the peer-coordination standard and supersedes any
conflicting informal practice in this repository.

Amendments require:

1. A documented rationale explaining why the current constitutional text is
   insufficient or misleading.
2. An updated constitutional draft in this repository.
3. A semantic version bump applied deliberately:
   - MAJOR for principle removal or incompatible redefinition
   - MINOR for new principles or materially expanded sections
   - PATCH for clarifications, wording improvements, and non-semantic cleanup
4. An explicit operator-directed promotion step. Agent alignment or scratchpad
   convergence alone is insufficient to amend the constitution.
5. A consistency check across active specs and project guidance files so they do
   not drift away from the amended constitution.

Compliance review expectations:

- New specs MUST state how they comply with the constitution.
- Material changes to constitutions, specs, or project guidance SHOULD receive
  independent review from an agent or human other than the primary author
  before promotion.
- Downstream implementation work MUST preserve the transport-versus-governance
  boundary.
- Scratchpad conclusions that become durable policy MUST be promoted here
  promptly.

**Version**: 1.3.0 | **Ratified**: 2026-04-18 | **Last Amended**: 2026-04-18
