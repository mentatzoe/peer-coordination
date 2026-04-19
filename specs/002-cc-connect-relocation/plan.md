# Implementation Plan: cc-connect Relocation

**Branch**: `[002-cc-connect-relocation]` | **Date**: 2026-04-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-cc-connect-relocation/spec.md`

**Note**: This plan is being executed inside the ratified autonomous Phase 1
loop. It is intentionally artifact-driven so the slice can be re-entered from
repo state and discussions rather than a preserved live session.

## Summary

Bring the existing `mentatzoe/cc-connect` fork under this repository as a
contained top-level `cc-connect/` workspace, preserving provenance and active
reviewability while keeping governance artifacts authoritative at the repo root.
The plan chooses a subtree-style import so the implementation surface is truly
contained here without recreating an external-repo dependency.

## Technical Context

**Language/Version**: Go 1.25.0 in the contained `cc-connect` workspace; Markdown for planning/governance artifacts  
**Primary Dependencies**: existing `cc-connect` Go module and build/test tooling, git with subtree-capable history import, active repo docs/discussions  
**Storage**: Git history + repository files  
**Testing**: Markdown/path sanity checks in this repo; `go build ./cmd/cc-connect`; targeted `go test` packages in the contained workspace  
**Target Platform**: Local developer workstations using this repo as the Phase 1 control surface, with Discord as the initial transport substrate  
**Project Type**: Governance/spec repository containing a subordinate Go CLI/service workspace for transport implementation  
**Performance Goals**: Preserve existing `cc-connect` buildability and Phase 1 dry-run readiness; no material relocation-induced regression in operator discoverability or review traceability  
**Constraints**: Must preserve governance/transport separation, avoid nested-git ambiguity for day-to-day work, keep provenance legible, and avoid amending canonical design artifacts as part of the move  
**Scale/Scope**: One contained repo import, active-doc updates, provenance/boundary scaffolding, and verification sufficient to unblock later Phase 1 transport implementation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I — Constitution Is Canonical**: Pass. The move keeps policy at
  the repo root and treats the contained workspace as subordinate
  implementation, not as a new source of governance.
- **Principle II — Transport Is Plumbing, Not Governance**: Pass. The import is
  explicitly a Layer 1 implementation surface; planning includes provenance and
  boundary docs so transport does not silently redefine policy.
- **Principle III — Scratchpad First, Then Promotion**: Pass. This slice is
  being run through a spec/plan artifact chain with discussion-backed review,
  not through chat-only convergence.
- **Principle IV — Human Arbitration and Explicit Consent**: Pass. The
  outcome-level decision (`full move under this repo`) was operator-set in
  discussion #41; this plan only operationalizes it.
- **Principle V — Parallel Work Requires Explicit Ownership**: Pass. Codex owns
  this slice; Claude is the cross-reviewer; status is indexed through
  `ROADMAP.md` and discussion #41.
- **Principle VI — Coordination Is Human-Legible, Not Over-Protocolized**:
  Pass. The move adds explicit provenance and handoff surfaces rather than
  hidden repo-state assumptions.

**Post-design check**: Still passes. The chosen structure keeps governance and
contained transport distinct, makes the handoff trail explicit, and does not
require constitutional or canonical-design edits to execute the move itself.

## Project Structure

### Documentation (this feature)

```text
specs/002-cc-connect-relocation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── workspace-boundary.md
└── tasks.md
```

### Source Code (repository root)

```text
AGENTS.md
CLAUDE.md
README.md
ROADMAP.md
VISION.md
design/
observations/
specs/
cc-connect/              # contained implementation-facing transport workspace
├── agent/
├── cmd/cc-connect/
├── core/
├── daemon/
├── platform/discord/
├── tests/
└── web/
```

**Structure Decision**: Keep this repository as the governance/spec root and add
the imported `cc-connect/` workspace as a clearly bounded top-level subordinate
implementation surface. Do not spread transport code into the root-level docs
tree, and do not rely on a separate local clone once the move lands.

## Phase 0: Research Decisions

See [research.md](./research.md) for the decisions that harden this plan:

1. Use a subtree-style import into `cc-connect/` to preserve history without
   keeping a separate repo boundary in day-to-day work.
2. Add a peer-coordination-owned provenance/boundary note alongside the
   contained workspace so lineage and ownership remain legible after import.
3. Update active docs that currently point at a standalone local clone so the
   artifact trail stays consistent with the new implementation surface.

## Phase 1: Design Outputs

- [data-model.md](./data-model.md) defines the core repo-level entities this
  move introduces or updates.
- [contracts/workspace-boundary.md](./contracts/workspace-boundary.md) defines
  the collaborator-facing contract for where transport work lives and how it
  stays separate from governance.
- [quickstart.md](./quickstart.md) captures the operator-free re-entry and
  implementation sequence for executing the move.

## Implementation Strategy

1. Import the current `mentatzoe/cc-connect` fork under a top-level
   `cc-connect/` prefix using a history-preserving approach.
2. Add a provenance/boundary note in or adjacent to the contained workspace so
   reviewers can see source fork, upstream lineage, and maintenance intent.
3. Update active docs in this repo that still treat `~/github/cc-connect` as the
   primary implementation surface.
4. Verify the contained workspace still builds/tests at the targeted entry
   points and that active docs point to the new implementation surface.
5. Report the implementation-complete checkpoint back through discussion #41 and
   request peer audit.

## Complexity Tracking

No constitutional violations or exceptional complexity justifications are
currently required. The feature is a bounded repo-shape change plus doc
realignment.
