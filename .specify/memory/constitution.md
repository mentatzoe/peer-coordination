<!--
Sync Impact Report
- Version change: 1.4.0 → 1.5.0 (MINOR — aligns the constitution with the newly-landed canonical design artifacts: VISION.md, design/architecture.md, design/poc.md; expands Scope and Deliverables to name them; adds a pointer to ROADMAP.md in the Specification Workflow section; enriches Principle II to reference the three-layer architectural model)
- Amendment rationale: Zoe feedback on [discussion #40 comment 16617623](https://github.com/mentatzoe/peer-coordination/discussions/40#discussioncomment-16617623) asked for the constitution to be aligned with the now-landed design artifacts (VISION / architecture / POC), not just the P1–P4 roadmap removal. This amendment names those artifacts as canonical-and-subordinate, updates the minimum durable outputs list, points the roadmap reference at ROADMAP.md + design/poc.md, and enriches Principle II with the three-layer model that now formalizes the transport-vs-governance boundary. No principles are added or removed; alignment is reference-level, not content duplication.
- Modified principles:
  - II. Transport Is Plumbing, Not Governance — added one sentence referencing the canonical three-layer model in design/architecture.md as the definition of the transport/non-transport boundary
  - VI. Coordination Is Human-Legible, Not Over-Protocolized — broadened "follow-on specs" to "follow-on specs or POC-level design artifacts such as design/poc.md"
- Modified sections:
  - Scope and Deliverables — added Canonical Design Artifacts subsection naming VISION.md, design/architecture.md, design/poc.md; expanded the minimum-durable-outputs list to include them and the observations/ surface
  - Specification Workflow — the roadmap pointer now names ROADMAP.md and design/poc.md Development Phases explicitly
- Added principles: none
- Removed principles: none
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no changes needed
  - .specify/templates/spec-template.md ✅ no changes needed
  - .specify/templates/tasks-template.md ✅ no changes needed
  - templates/scratchpad.md ✅ no changes needed
  - templates/document-review-discussion.md ✅ no changes needed
  - AGENTS.md ✅ no changes needed
  - CLAUDE.md ✅ verified 2026-04-19 — already references VISION/architecture/POC in its "Current State" and "Reference Material" sections
  - README.md ✅ verified 2026-04-19 — already links to VISION, architecture, POC, and ROADMAP
- Follow-up TODOs:
  - Piece 2 from [discussion #32 comment 16617193](https://github.com/mentatzoe/peer-coordination/discussions/32#discussioncomment-16617193): Codex-led roadmap adjustment — ROADMAP.md draft already landed; review cycle remains.
- Prior history:
  - 1.4.0 (ratified 2026-04-19) — removed the P1–P4 follow-on-spec roadmap from the Specification Workflow section; kept the 5-step promotion path.
  - 1.3.0 (ratified 2026-04-18) — added independent-review expectation for material changes before promotion.
  - 1.2.0 (ratified 2026-04-18) — added the explicit promotion-boundary rule to Principle III and Governance; updated the scratchpad template to match.
  - 1.1.1 (ratified 2026-04-18) — trimmed Principle VI to governance-only language; moved heuristics and mechanism language back to follow-on spec territory.
  - 1.1.0 (ratified 2026-04-18) — added Principle VI (since trimmed), expanded Principle III scratchpad definition, added P1–P4 roadmap priorities (removed in 1.4.0), MVP scope clarification (since trimmed).
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
parts that need code. The canonical three-layer model in
[`design/architecture.md`](../../design/architecture.md) (Layer 1 transport,
Layer 2 coordination, Layer 3 evaluation) defines the boundary between what
transport owns and what it does not; transport is Layer 1 only. This keeps the
standard understandable even when multiple transports or runtime setups exist.

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
loop-management rules are operational and belong in follow-on specs or
POC-level design artifacts such as [`design/poc.md`](../../design/poc.md).

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

### Canonical Design Artifacts

Alongside this constitution, the following design artifacts are canonical and
subordinate to it:

- **[`VISION.md`](../../VISION.md)** — north-star statement and the falsifiable
  hypotheses (H1 convergence, H2 legibility, H3 generalizability) that the
  first POC is organized around.
- **[`design/architecture.md`](../../design/architecture.md)** — three-layer
  architectural model (transport / coordination / evaluation) with capability
  requirements, failure taxonomies, and validation signals per layer.
- **[`design/poc.md`](../../design/poc.md)** — proof-of-concept scope,
  participants, KPIs, and development phases for the first Discord-based
  peer-coordination probe.

Amendments to these artifacts follow the same independent-review and
operator-directed-promotion expectations as constitutional amendments. When a
design artifact conflicts with this constitution, the constitution wins once
amended and ratified; conversely, the constitution is expected to reflect
canonical framing established in these artifacts via amendment rather than
drift.

### Minimum durable outputs

The minimum durable outputs of this repo are:

- a ratified constitution
- the canonical design artifacts named above: `VISION.md`,
  `design/architecture.md`, `design/poc.md`
- feature specs for important slices of the standard
- a live coordination scratchpad or equivalent review-discussion surface while
  work is active
- a field-journal / observations surface (`observations/`) capturing
  cross-session learnings that feed back into design and governance
- explicit records of confirmed decisions, open questions, and next actions

## Specification Workflow

Work in this repository MUST follow a simple promotion path:

1. Explore and converge in the scratchpad.
2. Ratify durable rules in the constitution.
3. Create follow-on specs for scoped concerns that are too detailed for the
   constitution.
4. Implement code changes in the downstream repo that owns them.
5. Feed results, lessons, and unresolved tensions back into this repository.

Follow-on specs MUST stay subordinate to the constitution and MUST NOT silently
redefine its principles. The current roadmap — which follow-on specs to cut,
in what order, and who owns what — is maintained in
[`ROADMAP.md`](../../ROADMAP.md) and tracks the development phases defined in
[`design/poc.md`](../../design/poc.md). The roadmap can change at project speed
without requiring a constitutional amendment every time priorities shift.

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

**Version**: 1.5.0 | **Ratified**: 2026-04-18 | **Last Amended**: 2026-04-19
