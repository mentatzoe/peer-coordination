# Implementation Plan: Transport MVP

**Branch**: `001-transport-mvp` | **Date**: 2026-04-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-transport-mvp/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Define the narrowed Transport MVP slice owned by Vigil/Codex: designated
open-floor pilot routing, self-loop suppression, and channel-scoped hard
interrupt semantics. The plan keeps channel policy, reactions, approval-via-
react, and pinned-rule ingestion out of scope while producing enough design
detail to hand implementation cleanly into `mentatzoe/cc-connect`.

## Technical Context

**Language/Version**: Markdown documentation in this repo; downstream implementation target is Go in `mentatzoe/cc-connect`  
**Primary Dependencies**: Speckit workflow files in `.specify/`, constitution in `.specify/memory/constitution.md`, downstream Discord transport code in `cc-connect`  
**Storage**: Git-tracked markdown files in this repository  
**Testing**: Specification checklist validation in this repo; downstream validation through Discord adapter unit tests and integration tests in `cc-connect`  
**Target Platform**: GitHub-hosted governance docs with downstream Discord transport implementation in `cc-connect`
**Project Type**: Governance/specification repository with downstream transport implementation handoff  
**Performance Goals**: Open-floor fanout must remain legible and safe; `!stop` must suppress unsent outbound transport effects immediately until explicit `!resume`  
**Constraints**: Preserve the designation split across `001`, `002`, and `003`; keep this plan limited to routing and interrupt semantics; do not re-import reaction or policy concerns  
**Scale/Scope**: One designated pilot channel, two peer agents, one transport slice, one downstream implementation target

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Constitution Is Canonical**: PASS. This work remains a follow-on spec in
  the governance repo rather than pushing policy into `cc-connect`.
- **Transport Is Plumbing, Not Governance**: PASS. The plan covers routing and
  interrupt mechanics only, with policy declaration and reaction semantics left
  to their designated specs.
- **Scratchpad First, Then Promotion**: PASS. The active artifact is a reviewed
  and clarified feature spec, not scratchpad-only convergence.
- **Human Arbitration and Explicit Consent**: PASS. `!stop` / `!resume`
  authority stays operator-centered with an explicit allowlist model.
- **Parallel Work Requires Explicit Ownership**: PASS. The feature scope is
  explicitly limited to the Codex-owned transport slice and references the
  sibling specs for Claude-owned scopes.
- **Coordination Is Human-Legible, Not Over-Protocolized**: PASS. Fanout is a
  transport eligibility decision; reply selection and overlap handling remain
  outside transport.
- **Promotion Boundary**: PASS. Planning resumes only after review and clarify,
  not from scratchpad convergence or premature task generation.
- **Independent Review Expectation**: PASS. Claude has already reviewed the
  narrowed spec on PR #29 with one contract-clarity nit incorporated.

## Project Structure

### Documentation (this feature)

```text
specs/001-transport-mvp/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── pilot-channel-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
.specify/
archive/
specs/
└── 001-transport-mvp/

# Downstream implementation target (out of repo, for planning references only)
/Users/zmll/github/cc-connect/
├── platform/discord/
│   ├── discord.go
│   └── discord_test.go
├── core/
│   ├── engine.go
│   ├── message.go
│   └── interfaces.go
├── tests/integration/
│   └── agent_integration_test.go
├── docs/
│   └── discord.md
└── config.example.toml
```

**Structure Decision**: This feature is documentation-first in the current
repo. The only source artifacts here are planning documents under
`specs/001-transport-mvp/`. Implementation tasks created later will target the
Discord transport and engine surfaces in `/Users/zmll/github/cc-connect/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
