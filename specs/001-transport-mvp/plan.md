# Implementation Plan: Transport MVP

**Branch**: `001-transport-mvp` | **Date**: 2026-04-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-transport-mvp/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Define the first peer-coordination transport MVP in this governance repo as a
durable implementation-facing spec. The plan keeps governance and operational
policy boundaries explicit, captures the pilot-critical transport behaviors, and
produces enough design detail to generate implementation tasks and GitHub
issues without collapsing back into scratchpad-only state.

## Technical Context

**Language/Version**: Markdown documentation in this repo; downstream implementation target is Go in `mentatzoe/cc-connect`  
**Primary Dependencies**: Speckit workflow files in `.specify/`, constitution in `.specify/memory/constitution.md`, coordination scratchpads in `ideas/`  
**Storage**: Git-tracked markdown files in this repository  
**Testing**: Specification checklist validation in this repo; downstream implementation validation through transport integration tests and live pilot checks  
**Target Platform**: GitHub-hosted governance docs with downstream Discord transport implementation in `cc-connect`
**Project Type**: Governance/specification repository with downstream transport implementation handoff  
**Performance Goals**: Pilot-critical controls must remain legible and safe; hard interrupt behavior must block further outbound activity until explicit resume  
**Constraints**: Preserve constitutional transport-vs-governance boundary; do not hard-code full coordination heuristics into transport requirements; keep the MVP limited to pilot-blocking features  
**Scale/Scope**: One pilot channel, two peer agents, five MVP capabilities, implementation split across two agents in downstream repo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Constitution Is Canonical**: PASS. This work creates a follow-on spec in
  the governance repo rather than pushing policy into `cc-connect`.
- **Transport Is Plumbing, Not Governance**: PASS. The plan defines transport
  requirements and boundaries here, while treating implementation as downstream
  work in `mentatzoe/cc-connect`.
- **Scratchpad First, Then Promotion**: PASS. Scope is promoted from
  `ideas/peer-coordination.md` and the amendment-review scratchpad into a
  durable feature spec.
- **Human Arbitration and Explicit Consent**: PASS. Approval-via-react and
  hard-interrupt semantics remain operator-centered.
- **Parallel Work Requires Explicit Ownership**: PASS. The plan prepares
  implementation-facing artifacts so later tasks can assign disjoint ownership.
- **Coordination Is Human-Legible, Not Over-Protocolized**: PASS. Full
  heuristics remain spec-level context rather than mandatory transport logic.
- **Promotion Boundary**: PASS. This plan follows an explicit promoted spec,
  rather than treating scratchpad convergence as the artifact itself.
- **Independent Review Expectation**: PASS. The resulting material changes
  remain subject to independent review before promotion/merge.

## Project Structure

### Documentation (this feature)

```text
specs/001-transport-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/
│   └── pilot-channel-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
.specify/
ideas/
templates/
specs/
└── 001-transport-mvp/

# Downstream implementation target (out of repo, for task references only)
~/github/cc-connect/
```

**Structure Decision**: This feature is documentation-first in the current repo.
Its only source artifacts here are design and planning documents under
`specs/001-transport-mvp/`. Implementation tasks created from this plan will
target the downstream `~/github/cc-connect/` repository.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
