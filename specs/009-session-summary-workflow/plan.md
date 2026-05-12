# Implementation Plan: Session-Summary Workflow

**Branch**: `009-session-summary-workflow` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-session-summary-workflow/spec.md`

## Summary

Operationalize the post-session procedure that produces `observations/sessions/<session-id>/summary.md` — the human-readable qualitative account required by spec 001 FR-012 — as a repeatable workflow complementing the drift-audit workflow (spec 008). The output is a structured markdown document conforming to hybrid inverted-pyramid ordering: Seed → Verdicts (strict labeled lines) → Drift (cross-referencing `drift-audit.json`) → What happened (free-form prose). The workflow supports two author-discipline modes the operator picks per-session (single-author OR agent-drafted + operator-ratified), a revision path preserving bundle history per spec 001 FR-014, and an optional peer-audit ledger via a `[peer-audited by <id>]` commit token. Implementation is prose (procedure doc + workflow contracts + runtime-facing doc under `observations/`) plus a quickstart; no runtime code, no CLI, no tests in this slice.

## Technical Context

**Language/Version**: N/A — workflow is procedure (markdown) + git commit conventions. No runtime code in this slice.
**Primary Dependencies**: `specs/001-session-bundle-skeleton/spec.md` (FR-007 `summary.md` required presence, FR-012 required sections, FR-014 bundle-amend-commit convention), `specs/005-drift-audit-rubric/spec.md` + `data-model.md` (drift-audit schema the summary cites), `specs/008-drift-audit-workflow/spec.md` + `contracts/workflow-contracts.md` C8 (consumer discipline: cite `drift-audit.json.verdict`, don't re-derive findings), `observations/drift-audits/RUBRIC.md` (rubric content), `specs/006-discord-transcript-export/spec.md` (transcript input), `design/poc.md` (per-session clear-definition criteria for H1 stability / H1 complementarity / H2 fresh-reader-pass).
**Storage**: Git — `observations/sessions/<session-id>/summary.md` is the committed artifact location, landed via session-bundle amend commit per spec 001 FR-014. Drift-audit version is pinned on the commit subject via short SHA.
**Testing**: Not required for this slice. Validation is by inspection + Phase 3 session trial (SC-001 time target, SC-003 fresh-reader rate). Unit-test scope is empty because the workflow is human-executed on closed bundles. An illustrative mock summary in `quickstart.md` doubles as dry-run verification material.
**Target Platform**: Repo-local documentation + procedure; no deployment surface.
**Project Type**: Documentation / specification slice within an existing repo.
**Performance Goals**: SC-001 target ≤20 operator-minutes per ≤200-turn bundle (allowance for drafting + drift-citation verification + verdict-rationale writing). SC-002 target 100% coverage of closed counted bundles within 48 operator-hours.
**Constraints**: No LLM runtime dependency in v1 (FR-014). Hybrid inverted-pyramid ordering with grep-stable verdict-line format (FR-010). Drift-section cites `drift-audit.json.verdict` only — no re-derivation (FR-008). Operator is authoritative on H1/H2 verdicts regardless of who drafted the prose (FR-005). Halt-before-partial-summary on missing inputs (FR-002). Per spec 001 FR-014 the revision path is ALWAYS a follow-up commit — NEVER `git commit --amend` on an existing summary.
**Scale/Scope**: Small-N POC — ~3–5 Phase 3 counted sessions, optional 1–2 Phase 4 Gemini sessions. Workflow is human-executed per session; no batch or continuous-scan infrastructure.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.specify/memory/constitution.md` v1.5.0 principles:

- **I. Constitution Is Canonical**: ✓ workflow subordinates to constitution by reference; defers rubric + drift-audit + bundle ownership to specs 005 / 008 / 001 (all subordinate to constitution). No amendment or override.
- **II. Transport Is Plumbing, Not Governance**: ✓ workflow sits in Layer 3 (evaluation) per `design/architecture.md`. No transport-layer scope. No cc-connect tie-in.
- **III. Scratchpad First, Then Promotion**: ✓ slice is a speckit-promoted artifact chain (specify → clarify → plan → tasks → analyze → implement).
- **IV. Human Arbitration and Explicit Consent**: ✓ FR-005 makes the operator authoritative on H1/H2 verdicts regardless of drafter identity; FR-018's optional peer-audit ledger is discovery mechanism, not verdict override.
- **V. Parallel Work Requires Explicit Ownership**: ✓ ACTIVE-SLICES.md row claimed for Claude; do-not-touch surfaces declared; cross-slice dependencies (001, 005, 006, 008, intervention-tagging) named explicitly in spec Context.
- **VI. Coordination Is Human-Legible, Not Over-Protocolized**: ✓ summary is plain markdown prose (the hybrid structure constrains only 4 section headings + verdict-line format; prose body is free-form). Peer-audit token is grep-able commit convention, not a machine handshake. Revision is plain git follow-up, not a protocol.

No constitution gates violated. No Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```text
specs/009-session-summary-workflow/
├── spec.md              # /speckit.specify output (updated with /speckit.clarify Q/As)
├── plan.md              # this file (/speckit.plan output)
├── research.md          # Phase 0 output — decisions + rationale
├── data-model.md        # Phase 1 output — workflow-level entities (prose, not JSON)
├── quickstart.md        # Phase 1 output — operator walkthrough (single-author + agent-drafted + revision + peer-audit paths)
├── contracts/
│   └── workflow-contracts.md  # Phase 1 output — workflow-level guarantees C1–C8
├── checklists/
│   └── requirements.md  # /speckit.specify validation checklist (all items pass)
└── tasks.md             # /speckit.tasks output (not created here)
```

### Source Code (repository root)

No source code is produced by this slice. Runtime-surface references:

```text
observations/sessions/<session-id>/
├── transcript.md        # produced by spec 006 — workflow input (cited by turn timestamp)
├── meta.json            # produced by spec 001 — workflow input (session_id, pinned_rules_ref, closed_at)
├── interventions.json   # produced by the intervention-tagging slice (Codex) — workflow input (opaque shape)
├── drift-audit.json     # produced by spec 008 workflow — workflow input (verdict + findings cited)
└── summary.md           # produced by THIS workflow — committed output

observations/sessions/
├── SUMMARY-WORKFLOW.md      # NEW (/speckit.implement) — runtime-facing operator walkthrough
├── SUMMARY-TAXONOMY.md      # NEW (/speckit.implement) — grep-able commit-taxonomy reference
└── _template/summary.md     # UPDATED (/speckit.implement) — template reflecting the hybrid inverted-pyramid shape

observations/sessions/README.md  # UPDATED (/speckit.implement) — point at SUMMARY-WORKFLOW.md alongside existing bundle-workflow docs
```

**Structure Decision**: Documentation/specification slice, parallel to spec 008. The only new repo content this slice produces during `/speckit.implement` is runtime-facing docs under `observations/sessions/` (SUMMARY-WORKFLOW.md + SUMMARY-TAXONOMY.md + template update) and the speckit artifacts under `specs/009-session-summary-workflow/`. Runtime docs live alongside `observations/sessions/README.md` to mirror how spec 008's drift workflow lives alongside `observations/drift-audits/RUBRIC.md`. All runtime-surface references (bundle inputs + committed output path) are read-from or written-to per existing spec 001 contracts; this slice does not create new directories or schemas.

## Complexity Tracking

No constitutional violations. No complexity entries required.
