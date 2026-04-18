# Feature Specification: Peer Coordination Constitution

**Feature Branch**: `003-peer-coordination-constitution`  
**Created**: 2026-04-18  
**Status**: Draft  
**Input**: User description: "With two agents working, I'd rather have a solid spec. It's just a matter of whether it belongs on personal setup agent, whether it should go on its own repo, or whethr these are changes to cc-connect. Perfect, let's spec it here - add a small roadmap for the differnt specs. The constitution is the most importnat"

## User Scenarios & Testing

### User Story 1 - Establish a canonical constitution (Priority: P1)

As the operator coordinating multiple agents, I want one canonical constitution in this repository that explains the governing rules for collaboration, so that future sessions do not have to reconstruct the standard from Discord history or competing notes.

**Why this priority**: Without a constitutional spine, every later transport or workflow decision becomes easier to misread, duplicate, or silently reinterpret.

**Independent Test**: A new session can read this spec and identify the canonical governance surface, what belongs in this repo, and what remains implementation work elsewhere.

**Acceptance Scenarios**:

1. **Given** a future agent session starts with only repository context, **When** it reads the constitutional spec, **Then** it can identify the governing document for multi-agent collaboration without referring to prior chat logs.
2. **Given** an unresolved design question about collaboration behavior, **When** the operator checks the constitutional spec, **Then** they can determine whether the question is governance, transport, or operational policy.

---

### User Story 2 - Separate governance from transport implementation (Priority: P2)

As an agent making changes across multiple repos, I want the spec to state clearly which decisions belong in `personal-agent-setup` and which changes belong in `cc-connect`, so that we do not confuse the standard with a specific implementation.

**Why this priority**: The current work spans both durable policy and real transport code changes. Mixing them would create avoidable confusion and ownership drift.

**Independent Test**: For each currently known MVP item, a reader can tell whether it belongs in the constitutional spec, a follow-on spec in this repo, or implementation work in `cc-connect`.

**Acceptance Scenarios**:

1. **Given** an item like open-floor mode or reaction approvals, **When** a reader consults the spec, **Then** they can tell that the behavior is governed here but implemented in `cc-connect`.
2. **Given** a question about tone, decision records, or collaboration norms, **When** a reader consults the spec, **Then** they can tell that it belongs to the constitutional layer rather than transport code.

---

### User Story 3 - Give future work a clear roadmap (Priority: P3)

As the operator planning follow-on work, I want a small roadmap of the next related specs, so that the constitution can stay central while later specs remain scoped and understandable.

**Why this priority**: The work is already evolving. A short roadmap keeps the constitution from bloating while still giving future sessions a coherent place to continue.

**Independent Test**: A future contributor can name the next few specs to create and explain why each exists without inventing a new structure.

**Acceptance Scenarios**:

1. **Given** the constitutional spec is approved, **When** future work begins, **Then** the next specs are already named and ordered by purpose.
2. **Given** a later decision is too detailed for the constitution, **When** the operator reviews the roadmap, **Then** they can place that work into the appropriate follow-on spec.

---

### Edge Cases

- What happens when the scratchpad and constitution disagree? The constitution wins once updated; the scratchpad remains useful as design history and live discussion context.
- What happens when a transport implementation must temporarily diverge during a pilot? The exception must be recorded explicitly as a pilot constraint or open question rather than silently redefining the standard.
- What happens when one agent is unavailable? The governance model remains valid; ownership and handoff expectations should still be recoverable from the written docs.
- What happens when a future transport other than `cc-connect` is introduced? The constitution remains applicable as long as it continues to treat transport as plumbing rather than governance.

## Requirements

### Functional Requirements

- **FR-001**: The repository MUST contain a canonical constitutional spec for multi-agent collaboration that is readable without prior Discord or terminal history.
- **FR-002**: The constitutional spec MUST define `personal-agent-setup` as the home for governance, collaboration norms, decision framing, and durable documentation of the multi-agent standard.
- **FR-003**: The constitutional spec MUST define transport systems such as `cc-connect` as session and delivery plumbing, not as the source of governance.
- **FR-004**: The constitutional spec MUST define how live scratchpads and coordination notes relate to the canonical spec, including that scratchpads may capture active discussion but do not supersede ratified constitutional text.
- **FR-005**: The constitutional spec MUST define how decisions, open questions, handoffs, and manual steps should be documented so future sessions can recover state reliably.
- **FR-006**: The constitutional spec MUST preserve room for organic behavioral drift between agents and MUST NOT require an artificial personality split as part of the standard.
- **FR-007**: The constitutional spec MUST include a short roadmap of follow-on specs, with the constitution explicitly positioned as the highest-priority document.
- **FR-008**: The constitutional spec MUST state that transport MVP work may be specified here but implemented in `cc-connect`, with expected ownership and file-boundary clarity before parallel coding begins.
- **FR-009**: The constitutional spec MUST support the current personal setup context without requiring immediate extraction into a separate repository.
- **FR-010**: The constitutional spec MUST make it clear when a new concern should become a follow-on spec rather than being absorbed into the constitution.

### Key Entities

- **Constitution**: The highest-priority document defining the durable rules, boundaries, and collaboration principles for the multi-agent standard.
- **Coordination Scratchpad**: A live working document used for discussion, convergence, and handoff, subordinate to the constitution once constitutional decisions are ratified.
- **Transport MVP**: The initial set of transport-facing capabilities needed to support the pilot behavior, governed by the constitution but implemented in `cc-connect`.
- **Decision Record**: A durable record of confirmed choices, open questions, manual steps, and next actions that lets later sessions recover the current state.
- **Follow-on Spec**: A narrower specification created when a topic is important but too detailed or implementation-shaped to live in the constitution.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A new agent session can identify the canonical governance document, the live coordination surface, and the implementation repo for transport work in under 10 minutes using repository docs alone.
- **SC-002**: For the current open-floor pilot scope, every known work item can be placed unambiguously into one of three buckets: constitutional governance, follow-on spec work in this repo, or implementation work in `cc-connect`.
- **SC-003**: The constitution includes a roadmap with at least three clearly differentiated follow-on specs, ordered by priority and purpose.
- **SC-004**: The constitution can be used to explain the standard to a future collaborator without requiring any artificial prompt-level tone split between agents.

## Specification Roadmap

The constitution is the highest-priority document. Everything else should either refine it or implement it.

1. **Constitution**
   Purpose: define principles, governance boundaries, source-of-truth rules, decision-recording norms, and the relationship between scratchpads, specs, and implementation repos.
   Priority: highest. This is the spine for every later spec.

2. **Transport MVP Spec**
   Purpose: describe the first pilot capabilities needed for open-floor collaboration, including interruption, routing, reactions, approvals, and rules ingestion.
   Scope note: specified here for shared understanding, implemented in `cc-connect`.

3. **Channel Policy and Presence Spec**
   Purpose: define how channel allowlists, channel verbosity, ambient participation, and per-channel operating modes should work once the MVP exists.
   Scope note: this should absorb later work such as channel allowlists paired with verbosity.

4. **Workspace and Session Binding Spec**
   Purpose: define workspace binding expectations, multi-workspace behavior, channel-to-repo mapping, and recovery behavior when agents enter a new channel.
   Scope note: this keeps runtime ergonomics separate from governance and transport control flow.

5. **Operations and Rollout Spec**
   Purpose: define pilot rollout steps, safety checks, migration expectations, and how the standard graduates from personal setup experimentation into something broader if needed.
   Scope note: only promote this beyond the personal setup context if reuse pressure is real.

## Assumptions

- The current work remains centered on a personal setup, even if parts of the standard may become reusable later.
- `cc-connect` is the current transport implementation target for the pilot, and no competing transport needs to be standardized immediately.
- The existing scratchpad in `ideas/peer-coordination.md` remains useful as a live coordination surface while the constitution becomes the durable policy spine.
- Follow-on specs should stay small and purposeful rather than recreating the constitution in multiple places.
