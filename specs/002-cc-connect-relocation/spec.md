# Feature Specification: cc-connect Relocation

**Feature Branch**: `[002-cc-connect-relocation]`  
**Created**: 2026-04-19  
**Status**: Draft  
**Input**: User description: "Bring the implementation-facing `cc-connect` repo fully under this repo so the Phase 1 transport work is contained here."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start transport work from one place (Priority: P1)

As a Phase 1 transport owner, I need the implementation-facing `cc-connect`
workspace to live inside this repository so I can move from roadmap/spec work
to transport implementation without depending on a separate local clone or
hidden setup knowledge.

**Why this priority**: This unblocks the first transport-facing Phase 1 work and
reduces the current split between governance decisions here and transport work
elsewhere.

**Independent Test**: A collaborator starting from this repo alone can identify
the contained `cc-connect` workspace, the current transport spec, and the
active review thread without consulting prior chat history.

**Acceptance Scenarios**:

1. **Given** a collaborator opens this repository at the root, **When** they
   follow the active roadmap/spec references, **Then** they can locate the
   contained `cc-connect` workspace without needing a separate checkout.
2. **Given** Phase 1 transport work is about to begin, **When** the owner reads
   the relocation spec and current roadmap state, **Then** they can tell which
   work belongs in the contained transport workspace versus governance docs.

---

### User Story 2 - Review transport work in context (Priority: P2)

As a peer reviewer, I need transport changes to be traceable from the planning
artifacts to the contained implementation workspace so I can audit the change
without reconstructing context manually.

**Why this priority**: The autonomous loop depends on durable handoff. Review
becomes fragile if the implementation surface sits outside the artifact trail.

**Independent Test**: A reviewer can start from the spec/review discussion,
trace into the contained transport workspace, and understand the intended
boundary without relying on ephemeral session context.

**Acceptance Scenarios**:

1. **Given** a transport-side implementation commit exists, **When** a reviewer
   follows the linked spec and discussion references, **Then** they can trace
   the change into the contained workspace and back to its governing artifact.
2. **Given** a reviewer is assessing whether a change belongs in governance or
   transport, **When** they inspect the relocation guidance, **Then** the
   boundary is explicit enough to route the change correctly.

---

### User Story 3 - Preserve repo boundaries after relocation (Priority: P3)

As a maintainer, I need the full move of `cc-connect` into this repo to avoid
collapsing transport implementation into project policy, so the contained code
can evolve without silently redefining the standard.

**Why this priority**: The relocation only helps if it improves operational
containment without breaking the governance/transport split this repo exists to
protect.

**Independent Test**: A maintainer can inspect the resulting repo shape and
determine that governance artifacts remain authoritative while the contained
transport workspace is treated as an implementation surface.

**Acceptance Scenarios**:

1. **Given** the transport workspace now lives in this repo, **When** a
   maintainer reviews the active docs, **Then** they can still tell that
   `VISION.md`, `design/`, the constitution, and follow-on specs remain the
   source of policy.
2. **Given** future transport work is proposed, **When** the change is planned,
   **Then** the relocation guidance makes clear that implementation detail does
   not by itself amend governance artifacts.

### Edge Cases

- How should active docs behave while historical references still point to the
  old standalone local clone path?
- What happens if the contained transport workspace is present but its lineage
  to the prior fork/upstream is not legible to reviewers?
- How should maintainers handle governance-only changes so the presence of the
  contained transport workspace does not imply every repo edit belongs there?
- What happens if transport implementation needs to move faster than the
  planning docs, but cannot modify canonical governance artifacts autonomously?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain the full implementation-facing
  `cc-connect` workspace within this repository rather than requiring a separate
  external clone for active Phase 1 work.
- **FR-002**: The repo MUST keep the governance/policy surface and the contained
  transport workspace explicitly separated, even after the full move.
- **FR-003**: Active planning artifacts for Phase 1 MUST point transport work to
  the contained workspace and MUST no longer depend on a user-specific external
  clone path as the primary implementation surface.
- **FR-004**: The contained transport workspace MUST preserve legible provenance
  to its prior fork/upstream lineage so reviewers can understand where it came
  from and how it should be maintained.
- **FR-005**: A collaborator entering through this repo MUST be able to discover
  the contained transport workspace, the active spec/review thread, and the
  current owner/handover state without reading prior chat logs.
- **FR-006**: The relocation MUST support the Phase 1 autonomous loop by making
  transport work reviewable through durable artifacts rather than session memory
  alone.
- **FR-007**: The relocation MUST NOT by itself amend `VISION.md`,
  `design/architecture.md`, `design/poc.md`, or the constitution; any required
  changes to those artifacts remain separate governance actions.
- **FR-008**: The resulting repo shape MUST make it possible to route a proposed
  change to either the contained transport workspace or the governance surface
  without ambiguity in normal Phase 1 work.
- **FR-009**: Any active documentation updated as part of the relocation MUST
  describe the contained workspace as an implementation surface, not as the
  source of policy.

### Key Entities *(include if feature involves data)*

- **Contained transport workspace**: The full `cc-connect` implementation
  surface brought under this repository for Phase 1 transport work.
- **Governance surface**: Canonical project artifacts such as `VISION.md`,
  `design/`, the constitution, and follow-on specs that remain authoritative for
  policy and framework shape.
- **Handover trail**: The linked roadmap entries, spec discussions, and commits
  that let a collaborator re-enter the work without relying on a preserved live
  session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A collaborator starting from this repository can identify the
  contained `cc-connect` workspace and its governing transport spec/review
  thread within 5 minutes, using repo artifacts alone.
- **SC-002**: All active Phase 1 planning references that govern transport work
  point to the contained workspace rather than a user-specific external clone.
- **SC-003**: A peer reviewer can trace at least one transport work item from
  roadmap/spec discussion to the contained workspace and back without requiring
  additional operator explanation.
- **SC-004**: After relocation, active docs still distinguish implementation
  surfaces from governance/policy surfaces with no blocking ambiguity raised in
  review.

## Assumptions

- The operator decision is settled: the intended outcome is a **full move** of
  the implementation-facing `cc-connect` repo into this repository.
- Exact git mechanics for performing the move are implementation/planning work,
  not part of this specification's decision surface.
- The contained workspace will live in a clearly named top-level location so it
  is easy to find from the repo root.
- Historical references to the old standalone clone may remain in archival
  material, but active planning artifacts should be updated to the new source of
  implementation truth.
- The goal of this relocation is to support the POC transport build, not to
  collapse governance and implementation into one undifferentiated surface.
