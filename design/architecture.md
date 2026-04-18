# Peer Coordination Design / Architecture

**Status:** Draft  
**Owner:** Codex  
**Date:** 2026-04-18

## Purpose

This document captures the current design-level convergence for the peer-coordination framework.

It is not a transport spec, not a governance amendment, and not a POC implementation plan. Its job is to make the architecture explicit before follow-on specs are written.

## Scope

This document defines:

- the three-layer abstraction
- responsibilities and boundaries for each layer
- architectural capability requirements for each layer
- architectural validation signals for each layer
- cross-layer design constraints derived from the source materials listed below

This document does not define:

- the project north star or hypothesis
- the POC tech stack and development phases
- concrete substrate selection, implementation-specific detail, or pilot measurement thresholds
- detailed Discord behavior or command schemas
- constitutional amendments

## Source Basis

This document is based on the following inputs:

- [VISION.md](../VISION.md)
- [Discussion #32: roadmap separation and gap analysis](https://github.com/mentatzoe/peer-coordination/discussions/32)
- [non-orchestrated-peer-coordination-codex.md](../docs/research/non-orchestrated-peer-coordination-codex.md)
- [non-orchestrated-peer-coordination-claude.md](../docs/research/non-orchestrated-peer-coordination-claude.md)

## Design Position

The current working architecture separates peer coordination into three layers:

1. **Interop / transport substrate**
2. **Coordination model**
3. **Evaluation of emergence and success**

This document operationalizes the approved vision in [VISION.md](../VISION.md): Layer 2 provides the conditions for H1-style convergence, Layer 3 provides the conditions for H2-style legibility assessment, and the cross-layer incremental-validation posture is how the architecture designs for H3 before H3 is tested directly in follow-on work.

The separation matters because the framework is otherwise at risk of collapsing:

- transport behavior into social policy
- social policy into governance
- pilot measurements into permanent principles

## Layer 1: Interop / Transport Substrate

### Responsibility

Layer 1 provides the shared environment in which peers can interact. It owns transport mechanics and shared artifact availability, not the social meaning of those artifacts.

It owns:

- message delivery and shared visibility
- identity, addressing, admission, and session continuity
- ordering, replayability, and recoverability of shared conversation state
- interruption and recovery primitives
- channel- or workspace-level binding
- substrate-provided primitives, such as reactions, pins, or commands
- exposure of shared coordination artifacts to participants in the same environment

### Boundary

Layer 1 does **not** decide:

- who should speak next
- what counts as good peer behavior
- whether a coordination episode succeeded
- what shared rules or symbols mean socially once exposed

It enables interaction. It does not socially organize it.

### Architectural capability requirements

- A shared surface where all participating peers and the operator can see the same conversation state.
- A clear way to distinguish peers and operator-visible authorship.
- A clear distinction between identity, visibility, and admission to the shared surface.
- A hard interrupt / pause mechanism that lets the operator stop or redirect activity.
- Enough ordering and replayability for participants and reviewers to reconstruct what happened.
- Enough session continuity and recovery semantics to preserve context across an ongoing coordination episode.
- Enough substrate support to expose shared coordination artifacts to all peers in the same environment.

### Architectural validation signals

Layer 1 is behaving correctly if:

- peers can participate in a shared conversation without hidden routing authority
- the operator can interrupt or recover the session without ambiguity
- participants can distinguish who was present, who could see the exchange, and who was authorized to act in it
- a reviewer can reconstruct event order and failure handling from the preserved record
- the transcript remains inspectable by a fresh human reader
- substrate features support coordination without themselves becoming the coordination policy

Layer 1 preserves the episode record as part of shared conversation state. Layer 3 uses that preserved record for interpretation and review.

## Layer 2: Coordination Model

### Responsibility

Layer 2 defines how peers are expected to coordinate inside the shared substrate. It owns the meaning and use of coordination artifacts once Layer 1 has made them visible.

It owns:

- the visible norms that orient peer behavior
- the interpretation of shared coordination artifacts such as pinned rules, reactions, and other visible signals
- how initiative, deference, extension, and silence remain available as possible postures
- how ambiguity is handled without reintroducing a moderator
- the boundary between organic role emergence and hard-coded role prescription
- when operator arbitration is expected

### Boundary

Layer 2 does **not** require:

- rigid turn-taking protocol
- mandatory status packets
- a host or selector role that decides who speaks next
- a fixed mapping from agent identity to permanent conversational role
- substrate-specific mechanics to carry the norms themselves

Layer 2 should stay closer to norms and affordances than to finite-state workflow.

### Architectural capability requirements

- A thin visible norm set, supplied by a separate artifact or operator-managed shared content, and made visible in-channel so peers can infer how to collaborate.
- A clear handoff between artifact availability at Layer 1 and artifact meaning at Layer 2.
- Space for peers to contribute differently to the current shared activity, whether that activity is coding, planning, discussion, or play.
- Space for silence and non-response when nothing useful needs to be added.
- A way for ambiguity or conflict to escalate to the operator without pretending the peers can always self-resolve.
- No requirement that peers express coordination through rigid, explicit protocol acts.

### Architectural validation signals

Layer 2 is behaving correctly if:

- coordination emerges without a host or hidden selector
- the resulting interaction remains human-readable
- peers are able to make distinct useful contributions relative to the shared activity
- norms shape behavior without scripting every move
- observed role patterns remain descriptive tendencies rather than becoming mandatory assignments

## Layer 3: Evaluation of Emergence and Success

### Responsibility

Layer 3 determines how coordination episodes should be evaluated after the fact.

It owns:

- the canonical observation artifact for a coordination episode
- how convergence, legibility, drift, failure, and intervention are assessed
- the review / replay model for examining the episode record
- the failure taxonomy used to classify what went wrong
- how preserved evidence is interpreted after the session
- how the team distinguishes emergent coordination from polite coincidence

### Boundary

Layer 3 should be as unobtrusive as possible.

It does **not**:

- inject live scoring into the conversation
- require self-reporting from peers during the interaction
- optimize peer behavior toward a metric
- turn the pilot into a benchmark harness at the expense of natural behavior

Evaluation should primarily happen post hoc from transcripts and associated operator observations.

### Architectural capability requirements

- A canonical episode record that preserves at least the transcript, event ordering, and operator interventions.
- A way to assess legibility from the resulting transcript.
- A way to assess whether peers contributed differently to the shared activity, rather than merely duplicating each other.
- A way to track operator intervention frequency, type, and reason.
- A minimal failure taxonomy that distinguishes at least convergence failure, legibility failure, complementarity failure, and intervention dependence.
- Episode records that support repeatable review of the same preserved artifact by multiple reviewers without rerunning the session. This is repeatability of review, not determinism of live behavior.

### Architectural validation signals

Layer 3 is behaving correctly if:

- a concrete validation run is falsifiable rather than anecdotal
- failures and near-misses are captured, not only successes
- a fresh human reader can understand what happened and why
- the team can tell the difference between real coordination and parallel output with light mutual acknowledgment
- the resulting episode record supports later critique without relying on memory or unstated context

## Cross-Layer Design Constraints

### Human legibility is invariant

The system is aiming for human-readable peer coordination, not just successful outcomes. Any pattern that depends on opaque shorthand, hidden side channels, or machine-only signaling is a regression against the core direction.

### Norms should be visible, but light

The coordination layer should provide orientation, not choreography. A good Layer 2 helps peers infer how to act without demanding they express their behavior through ritualized protocol steps.

### The operator is an arbiter, not an orchestrator

The operator must retain the ability to interrupt, ratify, or redirect. That does not imply a standing moderator role in the peer conversation itself. The architecture should preserve this distinction.

### Evaluation should be passive or post-session

The team wants to observe emergent coordination, not distort it through intrusive instrumentation. Evaluation should therefore lean on transcript review, observations, and retrospective analysis.

### Validation should be incremental

The framework can be validated on one substrate before broader portability claims are made. Portability should remain a design consideration, but not a premature burden on every artifact. In other words: design for broader generalizability, but test it incrementally.

## References

- [VISION.md](../VISION.md)
- [Discussion #32: roadmap separation and gap analysis](https://github.com/mentatzoe/peer-coordination/discussions/32)
- [non-orchestrated-peer-coordination-codex.md](../docs/research/non-orchestrated-peer-coordination-codex.md)
- [non-orchestrated-peer-coordination-claude.md](../docs/research/non-orchestrated-peer-coordination-claude.md)
