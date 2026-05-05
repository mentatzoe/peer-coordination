# Implementation Plan: Intervention-Tagging Workflow

**Branch**: `011-intervention-tagging` | **Date**: 2026-05-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-intervention-tagging/spec.md`

## Summary

Operationalize the intervention log required by `design/poc.md` and spec 001 as a repeatable post-session tagging workflow. This slice owns the schema for each `interventions.json` record, the fixed POC taxonomy, citation keys for downstream artifacts, append-only commit discipline, and a repo-owned CLI path for add/validate operations. Implementation updates the session-bundle runtime docs/templates, extends `tools/peer_session/` with intervention add/validate support, and lands a synthetic dry-run under `observations/sessions/_synthetic/011-intervention-tagging-dry-run/`.

## Technical Context

**Language/Version**: Python 3.11+ for existing `tools/peer_session/` CLI; Markdown + JSON for runtime artifacts.
**Primary Dependencies**: Python standard library only (`argparse`, `json`, `datetime`, `pathlib`, `re`); existing `tools.peer_session` package; spec 001 / 006 / 007 bundle contracts; spec 008 / 009 consumer discipline.
**Storage**: Git-tracked files. Runtime log location is `observations/sessions/<session-id>/interventions.json`; synthetic dry-run lives under a `_`-prefixed non-counted directory.
**Testing**: Existing `unittest` suite under `tests/peer_session/`; add tests for intervention add/validate, CLI surface, validation failures, and synthetic dry-run JSON conformance.
**Target Platform**: Repo-local operator tooling on macOS/Linux shell; no deployment surface.
**Project Type**: Documentation/specification slice plus small CLI extension inside existing repo tooling.
**Performance Goals**: SC-001 <=5 minutes for two tags on a synthetic bundle; CLI operations complete in interactive time for small-N POC bundles.
**Constraints**: No live Discord slash-command dependency; no bridge or cc-connect changes; no KPI rollup; top-level `interventions.json` remains an array; append-only bundle history; CLI must halt before partial writes on invalid input.
**Scale/Scope**: Small-N POC: 3-5 Phase 3 sessions plus optional Gemini extension. Expected intervention records per session are low double digits at most.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.specify/memory/constitution.md` v1.5.0:

- **I. Constitution Is Canonical**: Pass. The workflow is a spec artifact subordinate to constitution/design artifacts and does not redefine product direction or hypothesis outcomes.
- **II. Transport Is Plumbing, Not Governance**: Pass. The slice is Layer 3 evaluation and does not alter cc-connect, Discord routing, or transport policy.
- **III. Scratchpad First, Then Promotion**: Pass. PC-66 is a speckit-seed promoted into a spec chain and runtime artifacts.
- **IV. Human Arbitration and Explicit Consent**: Pass. The operator ratifies all committed intervention records; agent self-flags are not evidence until operator recorded.
- **V. Parallel Work Requires Explicit Ownership**: Pass. `ACTIVE-SLICES.md` claims `011-intervention-tagging` for Codex and declares touched surfaces.
- **VI. Coordination Is Human-Legible, Not Over-Protocolized**: Pass. Records are simple JSON with free-text reasons and stable citation ids; live instrumentation is deferred to avoid observer-effect pressure.

No constitution gates violated. No Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```text
specs/011-intervention-tagging/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── intervention-log-contract.md
├── checklists/
│   └── requirements.md
├── tasks.md
└── analyze.md
```

### Source Code / Runtime Artifacts (repository root)

```text
tools/peer_session/
├── cli.py                  # add `intervention add` and `intervention validate`
└── interventions.py        # new schema/validation/add helpers

tests/peer_session/
├── test_cli.py             # CLI surface and failure behavior
└── test_interventions.py   # new validation/add tests

observations/sessions/
├── README.md               # point at intervention workflow/taxonomy
├── INTERVENTIONS-WORKFLOW.md
├── INTERVENTIONS-TAXONOMY.md
├── _template/
│   ├── README.md           # schema docs updated
│   └── interventions.json  # remains `[]`
└── _synthetic/
    └── 011-intervention-tagging-dry-run/
        ├── README.md
        ├── meta.json
        ├── transcript.md
        └── interventions.json
```

**Structure Decision**: Documentation/specification plus a small repo-owned CLI extension. The CLI lives in the existing `tools/peer_session/` surface from spec 007 because intervention tagging is a session-bundle operation, not a transport operation. Runtime docs live under `observations/sessions/` alongside the summary workflow because operators author intervention logs inside session bundles.

## Complexity Tracking

No constitutional violations. No complexity entries required.
