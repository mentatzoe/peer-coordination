# Implementation Plan: KPI Rollup

**Branch**: `010-kpi-rollup` | **Date**: 2026-04-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-kpi-rollup/spec.md`

## Summary

Extend the existing `peer-session` CLI (spec 007) with two Phase 2 evaluation-surface subcommands — `peer-session tally <session-id>` (per-session KPI extraction) and `peer-session rollup` (cross-session aggregation into a per-run `poc-exit-<timestamp>.md` plus `poc-exit.md` pointer) — and add a companion `observations/kpi-rollup/WORKFLOW.md` for the human-judgment KPIs the CLI cannot automate (H2 fresh-reader authoring, H3 complementarity narrative, ambiguity resolution, ratification gate). Schema documentation for the two new bundle files (`kpi.json`, `fresh-reader-audit.json`) lands in `observations/sessions/_template/README.md` alongside the existing spec-001 schema sections. No new runtime dependencies beyond Python stdlib; no `cc-connect` coupling.

## Technical Context

**Language/Version**: Python 3.14.x, standard-library only (matches spec 007's posture)  
**Primary Dependencies**: `argparse`, `datetime`, `hashlib`, `json`, `pathlib`, `unittest` (all stdlib)  
**Storage**: Repo filesystem artifacts under `observations/sessions/<session-id>/` (per-session `kpi.json`, `fresh-reader-audit.json`) and `observations/` (per-run `poc-exit-<timestamp>.md` + `poc-exit.md` symlink pointer)  
**Testing**: `python3 -m unittest` targeted to new modules; synthetic session-bundle fixtures under `tests/peer_session/fixtures/` covering the six spec-010 edge cases  
**Target Platform**: Local operator / agent workstations (macOS and Linux) running from the repository root; Windows not supported (symlink assumption in FR-025)  
**Project Type**: Repo-owned filesystem-first CLI utility — extension of the spec-007 `peer-session` package, not a new CLI  
**Performance Goals**: `peer-session tally` produces `kpi.json` in under 30 seconds (SC-001); `peer-session rollup` produces a per-run `poc-exit-<timestamp>.md` in under 1 minute (SC-004); both commands have zero network and zero daemon dependency  
**Constraints**: Must be idempotent (byte-identical output modulo documented timestamp/hash fields, FR-004, SC-002); must not import `cc-connect` or the contained workspace (FR-021); must not redefine the spec-001 bundle shape (FR-019); must not add runtime dependencies beyond stdlib (FR-020); must fail loudly on bundles incomplete per spec 001 FR-001..FR-011 (FR-006, SC-003); must recognize and refuse silent-pass on the spec-001 `drift-audit.json` placeholder (FR-008)  
**Scale/Scope**: 3–5 counted sessions at POC exit (H1 decision-rule range); two new CLI subcommands; two new bundle-file schemas; one workflow doc; one per-run rollup-artifact family; bounded repo-root test surface with synthetic fixtures

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I — Constitution Is Canonical**: Pass. The slice adds evaluation tooling around the canonical `design/poc.md` KPI framework and `specs/001-session-bundle-skeleton` bundle shape; it does not relocate governance into transport code and does not redefine canonical design artifacts.
- **Principle II — Transport Is Plumbing, Not Governance**: Pass. This slice is squarely Layer 3 (evaluation) per the three-layer model in `design/architecture.md`. It consumes the bundle artifacts Layer 1 transport produces, but has no import of, dependency on, or interaction with `cc-connect`. FR-021 encodes this.
- **Principle III — Scratchpad First, Then Promotion**: Pass. The work is proceeding through the spec/plan artifact chain under `specs/010-*`; decisions from brainstorm and clarify are promoted into spec 010 rather than left in conversation.
- **Principle IV — Human Arbitration and Explicit Consent**: Pass. The CLI produces deterministic count-based output; all human judgment (H2 fresh-reader verdict, H3 complementarity, ambiguous per-session-clear resolution, ratification of each per-run rollup file) stays with the operator via the workflow doc (FR-016, FR-024, FR-025). The CLI never ratifies on behalf of the operator.
- **Principle V — Parallel Work Requires Explicit Ownership**: Pass. The slice is claimed in `ACTIVE-SLICES.md` as Claude-owned; its do-not-touch surface is scoped to `specs/010-kpi-rollup/**` plus the new `observations/kpi-rollup/` directory and the additive `kpi.json` / `fresh-reader-audit.json` files. It deliberately avoids spec 009's (session-summary, Claude-owned in a separate session) `summary.md` shape — the clarify session resolved FR-024 away from that coupling.
- **Principle VI — Coordination Is Human-Legible, Not Over-Protocolized**: Pass. The split between deterministic CLI (count-based KPIs) and plain-prose workflow doc (human-judgment KPIs) keeps evaluation human-legible. No new handshake protocol is introduced. The `poc-exit.md` pointer + per-run files preserves a readable rollup history without relying on git-log archaeology.

**Post-design check (after Phase 1)**: Still passes. The chosen module layout extends spec 007's package without redefining any of its existing public entry points, adds no runtime dependencies, and keeps the bundle contract with spec 001 additive. See the re-check note at the end of Phase 1 design outputs.

## Project Structure

### Documentation (this feature)

```text
specs/010-kpi-rollup/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── tally-cli-behavior.md
│   └── rollup-cli-behavior.md
├── checklists/
│   └── requirements.md
└── tasks.md                         # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
peer-session                         # spec-007 wrapper; unchanged
tools/
└── peer_session/
    ├── __init__.py                  # unchanged
    ├── cli.py                       # EXTENDED — add `tally` and `rollup` subparsers
    ├── defaults.py                  # unchanged
    ├── bundle_init.py               # unchanged
    ├── git_refs.py                  # unchanged
    ├── tally.py                     # NEW — per-session KPI computation
    ├── rollup.py                    # NEW — cross-session aggregation
    ├── bundle_io.py                 # NEW — shared bundle-file readers + inputs-hash helper
    └── per_session_clear.py         # NEW — composite per-session-clear judgment per poc.md

tests/
└── peer_session/
    ├── __init__.py                  # unchanged
    ├── test_cli.py                  # EXTENDED — tally + rollup dispatch tests
    ├── test_bundle_init.py          # unchanged
    ├── test_support.py              # EXTENDED — fixture helpers for synthetic bundles
    ├── test_tally.py                # NEW
    ├── test_rollup.py               # NEW
    ├── test_per_session_clear.py    # NEW
    └── fixtures/                    # NEW
        ├── session_minimal/         # complete minimal bundle (passes tally)
        ├── session_missing_fra/     # missing fresh-reader-audit.json
        ├── session_placeholder_drift/ # drift-audit.json is the spec-001 placeholder
        ├── session_zero_turns/      # transcript.md has no turns
        ├── session_unclosed/        # meta.json.closed_at is null
        ├── session_ambiguous/       # per_session_clear resolves to ambiguous
        └── rollup_counted_set/      # full set of 3 bundles for rollup test

observations/
├── sessions/
│   └── _template/
│       ├── README.md                # EXTENDED — add schema sections for kpi.json + fresh-reader-audit.json
│       ├── kpi.json                 # NEW — placeholder with [FILL IN] markers
│       └── fresh-reader-audit.json  # NEW — placeholder with [FILL IN] markers
└── kpi-rollup/
    └── WORKFLOW.md                  # NEW — operator-facing authoring recipe
```

**Structure Decision**: Extend spec 007's `tools/peer_session/` package rather than introducing a second CLI package. This honors spec 007's FR-012 + Story 3 extensibility intent and reuses the existing test harness (`tests/peer_session/test_support.py`). New logic is split into four modules — `tally`, `rollup`, `bundle_io` (shared helpers), `per_session_clear` (composite judgment) — so each file stays focused and each has isolated unit tests. Fixture bundles under `tests/peer_session/fixtures/` exercise the six edge cases in the spec plus the happy path. Template additions live in `observations/sessions/_template/` per the FR-023 clarification.

## Phase 0: Research Decisions

See [research.md](./research.md) for the decisions that harden this plan:

1. Inputs-hash algorithm: SHA-256 over canonicalized-JSON dumps (sorted keys, no whitespace) of `interventions.json`, `drift-audit.json`, `fresh-reader-audit.json`, plus the raw bytes of `summary.md`, `transcript.md`, `meta.json` — stored in `kpi.json.inputs_hash` as a hex digest. Stale detection: rollup recomputes and compares.
2. Per-run file timestamp format: UTC ISO-8601 basic (no colons) — `YYYYMMDDTHHMMSSZ`. Safe for macOS/Linux filesystems; sortable lexically.
3. `poc-exit.md` pointer: POSIX symlink via `os.symlink` — chosen over a pointer-markdown file because the spec explicitly names "symlink or equivalent". Windows is not a target per Technical Context; a fallback pointer file is deferred until Windows support becomes a requirement.
4. `per_session_clear` judgment: composite over six sub-criteria derived from `design/poc.md`'s "Per-session clear definitions" — three H1 (stable coordination, complementarity, intervention load) and three H2 (fresh-reader, drift, completeness). Tally emits each sub-judgment and rolls them up; the top-level `per_session_clear` is `cleared` iff all applicable sub-judgments are `cleared`, `not-cleared` if any are `not-cleared`, else `ambiguous` (any required operator-authored input is missing or inconclusive).
5. Intervention-rate: `directive_redirect`-typed intervention count divided by turn count; null + explicit `zero_turn_session` indicator when transcript has no turns (FR-009).
6. Drift-audit placeholder detection: exact string match on `{"status": "pending-phase-2"}` (post-`json.loads` `{"status": "pending-phase-2"}` equality); when detected, `per_session_clear_h2_drift` is `ambiguous` with reason, not `cleared`.
7. Tally vs. missing fresh-reader-audit.json: tally does NOT refuse — it runs, but marks `per_session_clear_h2_fresh_reader` (and thus the top-level `per_session_clear`) as `ambiguous`. Rollup DOES refuse on missing fresh-reader-audit.json per FR-013 hard-gap branch. This split separates "bundle complete per spec 001" (tally's gate) from "counted-session-ready per spec 010" (rollup's gate).

## Phase 1: Design Outputs

- [data-model.md](./data-model.md) — entity definitions for `kpi.json`, `fresh-reader-audit.json`, `poc-exit-<timestamp>.md`, the rollup snapshot, inputs-hash, and per-session-clear sub-judgments.
- [contracts/tally-cli-behavior.md](./contracts/tally-cli-behavior.md) — operator-visible contract for `peer-session tally <session-id>` (inputs, outputs, exit codes, idempotence, failure modes).
- [contracts/rollup-cli-behavior.md](./contracts/rollup-cli-behavior.md) — operator-visible contract for `peer-session rollup` (counted-session discovery, H1 decision-rule application, hard-gap refuse vs. judgment-gap draft, pointer update, per-run file format).
- [quickstart.md](./quickstart.md) — end-to-end operator flow from closed bundle → tally → fresh-reader-audit authoring → re-tally → rollup → ratification.

**Agent context update**: the `CLAUDE.md` SPECKIT plan pointer has been updated from `specs/008-drift-audit-workflow/plan.md` to `specs/010-kpi-rollup/plan.md` between the `<!-- SPECKIT START -->` and `<!-- SPECKIT END -->` markers.

**Post-design constitution re-check**: The module split (`tally`, `rollup`, `bundle_io`, `per_session_clear`) and fixture set do not introduce constitutional concerns. No new runtime dependencies. No transport coupling. No redefinition of spec-001 bundle shape. Still passes.

## Implementation Strategy

1. Add the two new CLI subparsers in `tools/peer_session/cli.py`, dispatching to `tally.run_tally()` and `rollup.run_rollup()`. Preserve the existing `init` subparser untouched.
2. Build `bundle_io` first as the shared read-only layer (bundle-completeness validation, canonicalized-JSON hashing for the inputs-hash field, ISO-8601 timestamp handling). Unit-test before anything downstream consumes it.
3. Build `per_session_clear` as a pure function over already-parsed bundle inputs, returning sub-judgments and the top-level rollup. Unit-test against the six sub-criteria from `design/poc.md` and the fixture matrix.
4. Build `tally.run_tally()` layered on `bundle_io` + `per_session_clear`. Hard-fail on spec-001 bundle incompleteness; soft-mark on missing fresh-reader-audit.json. Emit `kpi.json` with the documented fields and inputs-hash. Verify idempotence by re-running against the happy-path fixture and diffing byte-for-byte.
5. Build `rollup.run_rollup()` over the committed per-session `kpi.json` + `fresh-reader-audit.json` set. Apply FR-013 split: refuse on hard data gaps; produce draft-marked per-run file on judgment gaps. Apply the H1 decision rule (3/3, 3/4, 4/5). Write the per-run `poc-exit-<timestamp>.md` and update the `poc-exit.md` symlink via `os.symlink` (remove and recreate atomically).
6. Add the template schema sections (`observations/sessions/_template/README.md`) for `kpi.json` and `fresh-reader-audit.json`, plus placeholder JSON files in `_template/` with `[FILL IN]` markers per the spec-001 convention.
7. Author `observations/kpi-rollup/WORKFLOW.md` following the spec-008 authoring pattern: operator-facing recipe with explicit sections for (a) authoring `fresh-reader-audit.json`, (b) recording H3 complementarity narrative, (c) resolving ambiguous per-session-clear, (d) ratifying a per-run `poc-exit-<timestamp>.md`.
8. Add `tests/peer_session/test_tally.py`, `test_rollup.py`, `test_per_session_clear.py` exercising the six edge cases from the spec. Reuse `test_support.py` for temp-dir fixture setup; mirror spec 007's unittest style.
9. Update `ROADMAP.md`'s Evaluation-surface row to note spec 010 landed when the PR merges. (Out of scope for the plan artifact itself; noted for the tasks/implementation cycle.)

## Complexity Tracking

No constitutional violations or exceptional-complexity justifications are required for this slice.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
