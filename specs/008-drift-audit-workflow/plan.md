# Implementation Plan: Drift-Audit Workflow

**Branch**: `008-drift-audit-workflow` | **Date**: 2026-04-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-drift-audit-workflow/spec.md`

## Summary

Operationalize the ratified drift-audit rubric (spec 005 / `observations/drift-audits/RUBRIC.md` v1) as a repeatable post-session workflow that produces a committed `drift-audit.json` inside every counted session bundle. This slice owns the **workflow wrapper** — trigger, responsibility, two-auditor reconciliation, rubric-version pinning lifecycle, re-audit policy, and git integration. It does NOT redefine the rubric, the output schema, the intervention-tag shape, or the LLM-assisted authoring path; those are owned by spec 005, spec 001, the Codex intervention-tagging slice, and a deferred follow-on respectively. Implementation is prose (procedure doc + workflow contracts) plus a short quickstart; no runtime code or CLI tooling in v1.

## Technical Context

**Language/Version**: N/A — workflow is procedure (markdown) + git commit conventions. No runtime code in this slice.
**Primary Dependencies**: `specs/001-session-bundle-skeleton/spec.md` (session bundle + `drift-audit.json` consumer contract), `specs/005-drift-audit-rubric/spec.md` + `data-model.md` + `contracts/drift-audit-output.md` (rubric, output schema, output guarantees), `observations/drift-audits/RUBRIC.md` (the live rubric; consumed by version SHA), `specs/006-discord-transcript-export/spec.md` (transcript input).
**Storage**: Git — `observations/sessions/<session-id>/drift-audit.json` is the committed artifact location (per spec 001 FR-008), landed via amend commit per spec 001 FR-014. Rubric version is pinned by git SHA.
**Testing**: Not required for this slice. Validation is by inspection + Phase 3 session trial (SC-001 time target, SC-002 cross-auditor agreement rate). Unit-test scope is empty because the workflow is human-executed on closed bundles. Optional: a walked-through mock audit in `quickstart.md`.
**Target Platform**: Repo-local documentation + procedure; no deployment surface.
**Project Type**: Documentation / specification slice within an existing repo.
**Performance Goals**: SC-001 target ≤15 operator-minutes per ≤200-turn bundle (aligns with RUBRIC.md §4 target). SC-002 target ≥90% within-tolerance agreement across counted sessions.
**Constraints**: No LLM runtime dependency in v1 (FR-013). Idempotent modulo timestamp (FR-010). No mid-session rubric changes (spec 005 §6.4, inherited). Halt-before-partial-audit on missing inputs (FR-018). Rubric version MUST resolve to a committed SHA (FR-002).
**Scale/Scope**: Small-N POC — ~3–5 Phase 3 baseline sessions, optional 1–2 Phase 4 Gemini sessions. Workflow is human-executed per session; no batch or continuous-scan infrastructure.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.specify/memory/constitution.md` v1.5.0 principles:

- **I. Constitution Is Canonical**: ✓ workflow subordinates to constitution by reference; defers rubric ownership to spec 005 (which also subordinates). No amendment or override of constitutional text.
- **II. Transport Is Plumbing, Not Governance**: ✓ workflow sits in Layer 3 (evaluation) per `design/architecture.md`. No transport-layer scope. No cc-connect tie-in.
- **III. Scratchpad First, Then Promotion**: ✓ slice is a speckit-promoted artifact chain (specify → plan → tasks → implement). No policy drift from scratchpad.
- **IV. Human Arbitration and Explicit Consent**: ✓ FR-008 makes the operator the explicit arbiter on above-tolerance divergence; FR-007 requires public surfacing of divergence so calibration triggers are not hidden.
- **V. Parallel Work Requires Explicit Ownership**: ✓ ACTIVE-SLICES.md row claimed for Claude; do-not-touch surfaces declared; cross-slice dependencies (005, 006, 007, intervention-tagging) named explicitly in spec Context.
- **VI. Coordination Is Human-Legible, Not Over-Protocolized**: ✓ arbitration signal is a grep-able commit token (`[arbitrated]`), not a machine handshake; re-audit trigger is operator-initiated + POC-exit sweep, not continuous daemon. Procedure remains operator-readable.

No constitution gates violated. No Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```text
specs/008-drift-audit-workflow/
├── spec.md              # /speckit.specify output
├── plan.md              # this file (/speckit.plan output)
├── research.md          # Phase 0 output — decisions + rationale
├── data-model.md        # Phase 1 output — workflow-level entities (defers JSON schema to spec 005)
├── quickstart.md        # Phase 1 output — operator walkthrough (single-auditor + two-auditor + re-audit)
├── contracts/
│   └── workflow-contracts.md  # Phase 1 output — workflow-level guarantees (trigger, idempotency, amend-commit format, arbitration signal, POC-exit sweep)
├── checklists/
│   └── requirements.md  # /speckit.specify validation checklist (landed)
└── tasks.md             # /speckit.tasks output (not created here)
```

### Source Code (repository root)

No source code is produced by this slice. Runtime-surface references:

```text
observations/drift-audits/
├── RUBRIC.md            # landed via spec 005 — rubric read by this workflow, not modified
├── README.md            # landed via spec 005 — authoring workflow, not modified
└── CHANGELOG.md         # landed via spec 005 — rubric version log, not modified

observations/sessions/<session-id>/
├── transcript.md        # produced by spec 006 — workflow input
├── meta.json            # produced by spec 001 — workflow input (pinned_rules_ref, session_id, closed_at)
├── interventions.json   # produced by the intervention-tagging slice (Codex) — workflow input (opaque shape)
└── drift-audit.json     # produced by THIS workflow — committed output, schema owned by spec 005
```

**Structure Decision**: Documentation/specification slice. The only new repo-content this slice produces is the 5 speckit artifacts under `specs/008-drift-audit-workflow/`. All runtime-surface references (`observations/sessions/*`, `observations/drift-audits/RUBRIC.md`) are read-from or written-to per existing spec 001 / spec 005 contracts; this slice does not create new directories or schemas.

## Complexity Tracking

No constitutional violations. No complexity entries required.
