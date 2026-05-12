# Feature Specification: KPI Rollup

**Feature Branch**: `010-kpi-rollup`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: User description: "Extend the repo-owned `peer-session` CLI (spec 007) with two new subcommands for Phase 2 evaluation-surface: `peer-session tally <session-id>` (per-session) and `peer-session rollup` (cross-session). Together with a `WORKFLOW.md` authoring recipe, these produce the H1/H2 KPI rollup required by the `design/poc.md` measurement model — deterministic count-based KPIs via CLI, human-judgment KPIs via workflow, combined into the final `observations/poc-exit.md` artifact that operators ratify at POC exit."

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent contract**: [`design/poc.md`](../../design/poc.md) §"Success / Failure / KPI Framework", §"Per-session clear definitions", §"Measurement model".
- **Upstream dependencies (all landed)**:
  - [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) — bundle shape, `interventions.json` schema (FR-011), bundle completeness requirements (FR-001..FR-011), template pattern at `observations/sessions/_template/` (FR-017).
  - [`specs/007-session-bundle-init-cli/spec.md`](../007-session-bundle-init-cli/spec.md) — the `peer-session` CLI surface this slice extends, explicit extensibility intent (FR-012, Story 3 "validate / judge-prep" examples).
  - [`specs/008-drift-audit-workflow/spec.md`](../008-drift-audit-workflow/spec.md) — the drift-audit workflow whose `drift-audit.json` output is a tally input.
- **Downstream consumers (not yet landed)**:
  - [`specs/009-session-summary-workflow`](../009-session-summary-workflow/) — produces `summary.md` which may be asked to carry H2 fresh-reader outcome (see Clarifications below).
- **Roadmap position**: Phase 2 "Evaluation surface build" — ownership row `Claude (evaluation pipeline)` per [`ROADMAP.md`](../../ROADMAP.md). Blocks Phase 5 "POC exit and handoff".
- **Design position already converged**:
  - This slice **extends `peer-session`**, not a new CLI — per spec 007's explicit extensibility intent.
  - Count-based KPIs go through the CLI (deterministic, re-runnable). Human-judgment KPIs go through a `WORKFLOW.md` authoring recipe (spec-008 pattern).
  - Final output is a family of per-run `observations/poc-exit-<timestamp>.md` files with `observations/poc-exit.md` as a pointer to the latest; each per-run file is independently operator-ratifiable (CLI produces the deterministic content; operator ratifies by committing).
  - Bundle shape from spec 001 is preserved where possible; any new bundle field is additive.

## Clarifications

### Session 2026-04-21

- Q: Where is the H2 fresh-reader outcome captured per session? → A: As a separate `observations/sessions/<session-id>/fresh-reader-audit.json` bundle file (additive; mirrors the spec-008 pattern of landing structured evaluation output as its own file rather than wedging it into `summary.md` prose or compromising `kpi.json` determinism).
- Q: How should `peer-session rollup` behave when blocking conditions exist? → A: Split by condition type. Hard data gaps (missing/stale `kpi.json`, missing `fresh-reader-audit.json`) MUST refuse and exit non-zero; operator-judgment gaps (`per_session_clear` flagged `ambiguous`) MUST produce a draft-marked `poc-exit.md` so the operator can use the workflow to resolve ambiguity before ratifying.
- Q: What is the commit/history model for `observations/poc-exit.md` when `peer-session rollup` is re-run? → A: Per-run files. Each successful rollup run writes a new `observations/poc-exit-<ISO-8601-timestamp>.md` file; prior per-run files are preserved unchanged. `observations/poc-exit.md` itself is a pointer (symlink or equivalent) that resolves to the most recent per-run file. Ratification is per-file, so each rollup artifact is independently ratifiable and the file set makes the rollup history self-evident without git-log archaeology.
- Q: Where do schemas for this slice's new bundle files (`kpi.json`, `fresh-reader-audit.json`) live? → A: In `observations/sessions/_template/README.md` alongside the existing `meta.json` / `interventions.json` / `drift-audit.json` schema sections (the established spec-001 pattern). Spec 010 describes the files' role and minimum requirements; full serialized schemas, enums, and fill-in guidance live outside the spec in the template README. Broader principle: specs describe concept + minimum requirements; schemas live in the template README as the single operator-facing lookup surface.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Operator computes per-session KPIs from a closed bundle (Priority: P1)

As the operator, after a counted session closes and its bundle is complete, I need a deterministic way to turn the bundle's existing artifacts (`interventions.json`, `drift-audit.json`, `summary.md`) into a per-session KPI tally I can audit, so that the "did this session clear?" question has a single reproducible answer rather than a recomputation each time someone asks.

**Why this priority**: without per-session tallies, every cross-session rollup has to re-derive counts from raw artifacts, every reviewer produces subtly different numbers, and there is no durable per-session record of which sessions counted toward H1. This is the foundation the cross-session rollup consumes.

**Independent Test**: run `peer-session tally <session-id>` against a complete closed bundle from `observations/sessions/`; verify that `observations/sessions/<session-id>/kpi.json` is created, contains the deterministic count-based fields (intervention count, type tally, intervention-rate per turn, drift-audit verdict snapshot, per-session-clear judgment for H1), and is re-runnable with identical output.

**Acceptance Scenarios**:

1. **Given** a complete closed session bundle with `interventions.json`, `drift-audit.json`, `summary.md`, `transcript.md`, and `meta.json`, **When** the operator runs `peer-session tally <session-id>`, **Then** the command writes `observations/sessions/<session-id>/kpi.json` with the deterministic count-based KPI fields and exits successfully.
2. **Given** a session bundle missing any file required by spec 001 FR-001..FR-011, **When** the operator runs `peer-session tally <session-id>`, **Then** the command fails loudly with a specific error identifying the missing file(s) and does **not** produce a partial `kpi.json`.
3. **Given** an existing `kpi.json` from a prior run, **When** the operator re-runs `peer-session tally <session-id>` without any bundle changes, **Then** the resulting `kpi.json` is byte-identical to the prior run (idempotent).

---

### User Story 2 — Operator produces the POC-exit rollup across counted sessions (Priority: P2)

As the operator, at POC exit time after the baseline session set is complete, I need a way to aggregate the per-session tallies into a single ratifiable artifact that applies the H1 decision rule from `design/poc.md` and surfaces H2 pass-rate and episode-record completeness across the counted sessions, so that I can ratify the POC's hypothesis stances without re-running the measurement math.

**Why this priority**: this is the artifact Phase 5 "POC exit and handoff" explicitly requires. Without it, the POC cannot cleanly exit with a defensible stance on H1/H2/H3. Depends on User Story 1 producing consistent per-session input.

**Independent Test**: given a set of counted session bundles each with a committed `kpi.json` (from Story 1), run `peer-session rollup`; verify that a new `observations/poc-exit-<timestamp>.md` file is produced and the `observations/poc-exit.md` pointer is updated to reference it, with the per-run file carrying the counted-session total, the H1 decision-rule application (3/3, 3/4, or 4/5 sessions clear), the H2 fresh-reader pass-rate, and episode-record completeness, in a format the operator can review and ratify by committing.

**Acceptance Scenarios**:

1. **Given** a set of counted session bundles (3 to 5) each with a committed `kpi.json` and `fresh-reader-audit.json`, **When** the operator runs `peer-session rollup`, **Then** the command writes a new `observations/poc-exit-<timestamp>.md` file carrying the counted-session total, the applied H1 decision-rule result, the H2 fresh-reader pass-rate, and episode-record completeness across the counted sessions, and updates the `observations/poc-exit.md` pointer to reference the new file.
2. **Given** a session bundle that exists under `observations/sessions/` but is missing its `kpi.json` or `fresh-reader-audit.json`, **When** the operator runs `peer-session rollup`, **Then** the command refuses to produce a new per-run file or update the pointer, exits with non-zero status, and enumerates the unresolved bundles in its error output.
3. **Given** all counted bundles have complete `kpi.json` and `fresh-reader-audit.json` but one or more sessions' `per_session_clear` is flagged `ambiguous`, **When** the operator runs `peer-session rollup`, **Then** the command writes a new per-run file marked "draft, not ratifiable" (enumerating the ambiguous sessions), updates the `poc-exit.md` pointer to reference it, and exits successfully so the operator can resolve ambiguity via the workflow before ratifying.
4. **Given** the template bundle under `observations/sessions/_template/`, **When** the operator runs `peer-session rollup`, **Then** the template is excluded from the counted-session aggregate (consistent with spec 001 FR-017 "directories starting with `_` or `.` are filtered").
5. **Given** a counted-session total outside the H1 decision-rule range (fewer than 3 or more than 5), **When** the operator runs `peer-session rollup`, **Then** the command surfaces the out-of-range condition in the output rather than silently mis-applying the 3/3, 3/4, or 4/5 threshold.

---

### User Story 3 — Operator uses the workflow recipe to capture human-judgment KPIs (Priority: P3)

As the operator, for the KPI fields that are human judgments rather than counts (H2 fresh-reader outcome, H3 complementarity narrative, "ambiguous" per-session-clear cases, the ratification gate), I need a written authoring recipe that tells me where and how to capture those judgments so that they flow into the cross-session rollup in a predictable place and format.

**Why this priority**: the CLI cannot automate human judgment. Without a workflow doc, operators will capture these fields in inconsistent places across sessions, breaking `peer-session rollup`'s ability to aggregate. Lower priority than the CLI because the workflow alone does not produce the rollup — but the rollup alone does not produce ratifiable H2/H3 stances without it.

**Independent Test**: given the `observations/kpi-rollup/WORKFLOW.md` authoring recipe, a fresh operator can read it and know (a) where H2 fresh-reader outcomes get captured, (b) where H3 complementarity narrative goes, (c) how to resolve an "ambiguous" per-session-clear flag, and (d) what ratification looks like — without asking the spec authors.

**Acceptance Scenarios**:

1. **Given** `observations/kpi-rollup/WORKFLOW.md` and a closed session with no H2 fresh-reader outcome captured yet, **When** a fresh operator reads the workflow, **Then** they can capture the H2 outcome in the location the workflow prescribes and the subsequent `peer-session tally` run reflects it without workflow ambiguity.
2. **Given** a cross-session `peer-session rollup` run that flagged one session as "ambiguous per-session-clear", **When** the operator follows the workflow's ambiguity-resolution step, **Then** the session's clear status is resolved to `cleared` / `not-cleared` via a recorded operator verdict that subsequent re-runs honor deterministically.
3. **Given** a `observations/poc-exit-<timestamp>.md` file marked `ratifiable` (not `draft, not ratifiable`), **When** the operator follows the workflow's ratification gate, **Then** the ratification is recorded in that specific per-run file's ratification-gate section per the workflow's chosen convention, making ratification per-file and auditable without affecting prior per-run files.

---

### Edge Cases

- A session bundle has `kpi.json` from a prior run but has since had `interventions.json` or `drift-audit.json` amended via a FR-014 amend commit (spec 001) — `peer-session tally` MUST recompute cleanly and produce updated `kpi.json`.
- A session bundle's `transcript.md` has zero turns (session opened and closed without exchange) — intervention-rate per turn is undefined; the tally MUST handle this without divide-by-zero and MUST surface the zero-turn condition in `kpi.json`.
- `drift-audit.json` is still the placeholder `{"status": "pending-phase-2"}` from spec 001 rather than a real rubric output — the tally MUST recognize the placeholder and either exclude drift-verdict from the per-session-clear judgment or fail with a clear error, not silently treat the placeholder as a "no drift" verdict.
- The counted-session set contains a session whose `kpi.json` was committed before a later `interventions.json` amendment and has not been re-tallied — the rollup MUST surface the staleness (e.g., a timestamp or hash-of-inputs field in `kpi.json` that rollup checks against current bundle state).
- A session bundle's `meta.json` has `closed_at: null` (session never explicitly closed per spec 001) — the tally MUST refuse to tally an unclosed session, since the counted-session set requires closed bundles.
- `peer-session rollup` is re-run after a prior per-run file has been committed — per FR-025 the command writes a new `poc-exit-<timestamp>.md` and updates the `poc-exit.md` pointer; prior per-run files remain unchanged and readers determine current state from the pointer's target.
- Two sessions in the bundle set have the same `session_id` (spec 001 FR-002 name collision) — the rollup MUST refuse to aggregate until the collision is resolved.

## Requirements *(mandatory)*

### Functional Requirements

#### Per-session tally (Story 1)

- **FR-001**: The system MUST extend the existing `peer-session` CLI (per spec 007 FR-001, FR-012) with a `tally` subcommand invoked as `peer-session tally <session-id>`.
- **FR-002**: `peer-session tally <session-id>` MUST read `observations/sessions/<session-id>/interventions.json`, `drift-audit.json`, `summary.md`, `transcript.md`, and `meta.json`, and MUST write `observations/sessions/<session-id>/kpi.json`.
- **FR-003**: `kpi.json` MUST contain at minimum: `session_id`, `tallied_at` (ISO-8601 timestamp with at least second precision), `intervention_count` (integer), `intervention_type_tally` (object mapping each type in the frozen taxonomy from `design/poc.md` measurement model and spec 001 FR-011 to a count, with zeros for absent types), `intervention_rate_per_turn` (decimal) or a documented null-equivalent for zero-turn sessions, `drift_audit_verdict` (snapshot copied from `drift-audit.json`), `per_session_clear` (one of `cleared`, `not-cleared`, `ambiguous`) per poc.md's "Per-session clear definitions".
- **FR-004**: `peer-session tally` MUST be idempotent: re-running against an unchanged bundle MUST produce byte-identical `kpi.json` (modulo the `tallied_at` timestamp, which MAY update, and a content-hash field documented in FR-005).
- **FR-005**: `kpi.json` MUST include an `inputs_hash` field (or equivalent staleness marker) computed over the input files so that `peer-session rollup` can detect when a committed `kpi.json` is stale relative to current bundle content.
- **FR-006**: `peer-session tally` MUST fail loudly with a specific error identifying missing or invalid input files when the bundle does not satisfy spec 001 FR-001..FR-011, rather than producing a partial `kpi.json`.
- **FR-007**: `peer-session tally` MUST refuse to tally a session whose `meta.json.closed_at` is `null` (unclosed session).
- **FR-008**: `peer-session tally` MUST recognize the `drift-audit.json` placeholder (`{"status": "pending-phase-2"}` per spec 001) and either exclude drift-verdict from `per_session_clear` with an explicit notice in `kpi.json`, or fail with a clear error — never silently treat the placeholder as a "no drift" pass.
- **FR-009**: `peer-session tally` MUST handle zero-turn transcripts without divide-by-zero; `intervention_rate_per_turn` in that case MUST be a documented null-equivalent value and `kpi.json` MUST include an explicit `zero_turn_session` indicator.

#### Cross-session rollup (Story 2)

- **FR-010**: The system MUST extend `peer-session` with a `rollup` subcommand invoked as `peer-session rollup` (no positional argument; rolls up the full counted-session set).
- **FR-011**: `peer-session rollup` MUST aggregate `kpi.json` and `fresh-reader-audit.json` files from all session bundles under `observations/sessions/` **excluding** directories whose names start with `_` or `.` (consistent with spec 001 FR-017), MUST produce a per-run `observations/poc-exit-<timestamp>.md` file per FR-025, and MUST update the `observations/poc-exit.md` pointer to reference that file.
- **FR-012**: Each per-run `observations/poc-exit-<timestamp>.md` file (per FR-025) MUST include at minimum: counted-session total, the applied H1 decision-rule result (3/3, 3/4, or 4/5 per `design/poc.md`), per-session-clear summary (one row per counted session), H2 fresh-reader pass-rate across counted sessions, episode-record completeness across counted sessions, the file's ratifiability state (`ratifiable` or `draft, not ratifiable`), and a ratification-gate section the operator fills on ratification.
- **FR-013**: `peer-session rollup` MUST surface (not silently exclude) any counted session where `kpi.json` is missing, stale relative to current bundle content (per FR-005), `fresh-reader-audit.json` is missing, or `per_session_clear` is flagged `ambiguous`. Behavior depends on the condition type:
  - **Hard data gaps** (missing or stale `kpi.json`, or missing `fresh-reader-audit.json`): `peer-session rollup` MUST refuse to produce a new per-run file, MUST NOT update the `poc-exit.md` pointer, MUST exit with a non-zero status, and MUST enumerate the unresolved bundles in its error output.
  - **Operator-judgment gaps** (`per_session_clear` flagged `ambiguous` on one or more sessions): `peer-session rollup` MUST write a new per-run file marked clearly as `draft, not ratifiable`, MUST update the `poc-exit.md` pointer to reference it, MUST enumerate the ambiguous sessions in the artifact, and MUST exit successfully so the operator can use `observations/kpi-rollup/WORKFLOW.md` (FR-016c) to resolve ambiguity before ratifying.
- **FR-014**: `peer-session rollup` MUST surface when the counted-session total is outside the H1 decision-rule range (fewer than 3 or more than 5) rather than silently mis-applying the 3/3, 3/4, 4/5 threshold.
- **FR-015**: `peer-session rollup` MUST detect and refuse to aggregate when two sessions share a `session_id` (spec 001 FR-002 collision).

#### Workflow authoring recipe (Story 3)

- **FR-016**: The system MUST provide a workflow document at `observations/kpi-rollup/WORKFLOW.md` that covers at minimum: (a) how to author `fresh-reader-audit.json` per session (referencing the schema in `observations/sessions/_template/README.md` rather than duplicating it), (b) where and how to record H3 complementarity narrative, (c) how to resolve an `ambiguous` per-session-clear flag into a recorded operator verdict, and (d) the ratification gate for a per-run `poc-exit-<timestamp>.md` file.
- **FR-017**: The workflow MUST mirror the authoring pattern established by spec 008's drift-audit workflow — plain-language recipe with explicit sections per step, operator-facing examples, and a rationale section — rather than inventing a new authoring format.
- **FR-018**: Ambiguity resolution MUST use the amend-commit convention — operators resolve an `ambiguous` sub-judgment by amending the underlying bundle input (most commonly `fresh-reader-audit.json`'s `verdict`, or by running and committing the real drift audit to replace the spec-001 placeholder in `drift-audit.json`) and re-running `peer-session tally`. The re-run recomputes `per_session_clear` deterministically from the amended inputs; no override field in `kpi.json` is introduced. The workflow (FR-016c) MUST document this convention and its pre-commit review expectations. `peer-session tally` and `peer-session rollup` MUST NOT introduce any override-specific code paths — the determinism guarantee rests on tally's existing input-reading behavior (FR-002 + FR-004) plus the amend-commit discipline already established by spec 001 FR-014 for bundle corrections.

#### Bundle integration and scope preservation

- **FR-019**: This slice MUST NOT redefine the session-bundle shape from spec 001. Any new required bundle artifact (such as `kpi.json`) MUST be additive. Schema documentation placement is resolved by FR-023 below.
- **FR-020**: This slice MUST NOT introduce new runtime dependencies beyond Python stdlib (matches spec 007's posture of a repo-owned artifact-first utility).
- **FR-021**: This slice MUST NOT require a running `cc-connect` daemon or import-level coupling to the contained `cc-connect/` workspace (matches spec 007 SC-004).
- **FR-022**: This slice MUST NOT alter spec 008's `drift-audit.json` schema; it consumes the schema as-is.

#### Open design questions (to be resolved via `/speckit-clarify`)

- **FR-023**: Schema documentation for this slice's new bundle files (`kpi.json` and `fresh-reader-audit.json`) MUST live in `observations/sessions/_template/README.md` alongside the existing `meta.json` / `interventions.json` / `drift-audit.json` schema sections, consistent with the spec-001 convention. Spec 010 carries the files' conceptual role and minimum requirements (see FR-003, FR-024, and Key Entities); full serialized schema details (field types, enums, fill-in guidance, examples) MUST NOT be duplicated in spec 010. The template's `_` prefix already excludes the template directory from downstream tooling per spec 001 FR-017, so adding schema stubs there is non-breaking.
- **FR-024**: The H2 fresh-reader outcome MUST be captured per session in a dedicated `observations/sessions/<session-id>/fresh-reader-audit.json` bundle file. The file is additive to the spec 001 bundle shape and MUST contain at minimum: `session_id`, `audited_at` (ISO-8601 with at least second precision), `auditor` (handle/identity of the fresh reader), `verdict` (one of `pass`, `fail`, or `inconclusive`), and `reasoning` (free-text operator note). Authoring is operator-driven per `observations/kpi-rollup/WORKFLOW.md` (FR-016a); `peer-session tally` and `peer-session rollup` MUST read this file as an input but MUST NOT modify it.
- **FR-025**: Each successful `peer-session rollup` run MUST produce a new `observations/poc-exit-<ISO-8601-timestamp>.md` file (timestamp with at least second precision) carrying the per-run content required by FR-012. Prior per-run files MUST be preserved unchanged — re-runs MUST NOT rewrite, redact, or delete them. `observations/poc-exit.md` MUST exist as a pointer (symlink or equivalent) resolving to the most recently written per-run file; the rollup command MUST update the pointer on each successful run. Ratification is per-file: each per-run file is independently ratifiable via its ratification-gate section. If `observations/` contains no prior per-run file, the first `peer-session rollup` run MUST create both the first `poc-exit-<timestamp>.md` and the `poc-exit.md` pointer.

### Key Entities *(include if feature involves data)*

- **Tally Command**: the `peer-session tally <session-id>` entry point that computes per-session count-based KPIs from a closed bundle and writes `kpi.json`.
- **Rollup Command**: the `peer-session rollup` entry point that aggregates per-session `kpi.json` and `fresh-reader-audit.json` files into a new per-run `poc-exit-<timestamp>.md` and updates the `poc-exit.md` pointer.
- **Per-session KPI File (`kpi.json`)**: the committed per-session artifact containing deterministic count-based KPI fields, the `per_session_clear` judgment, and an inputs-hash staleness marker. Additive to the spec 001 bundle shape.
- **Fresh-reader Audit Artifact (`fresh-reader-audit.json`)**: the committed per-session artifact containing the H2 fresh-reader verdict (`pass`, `fail`, or `inconclusive`), auditor identity, timestamp, and free-text reasoning. Operator-authored per the workflow; additive to the spec 001 bundle shape.
- **Cross-session Rollup Artifact Family**: the per-run `observations/poc-exit-<timestamp>.md` files (each independently operator-ratifiable) plus the `observations/poc-exit.md` pointer that resolves to the latest. Each per-run file applies the H1 decision rule, surfaces H2 pass-rate and episode-record completeness, and hosts its own ratification gate.
- **KPI Workflow Document (`observations/kpi-rollup/WORKFLOW.md`)**: the authoring recipe for human-judgment KPI capture, ambiguity resolution, and ratification — the operator-facing complement to the CLI.
- **Intervention-Type Taxonomy**: the frozen set from `design/poc.md` measurement model and spec 001 FR-011 (`safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other`) used as the `intervention_type_tally` key set.
- **Counted-session Set**: the non-template, non-hidden session bundles under `observations/sessions/` that the rollup aggregates — the 3 to 5 bundles the H1 decision rule evaluates.
- **Inputs Hash / Staleness Marker**: the content-hash or equivalent field in `kpi.json` that lets `peer-session rollup` detect stale tallies relative to current bundle content.
- **Per-session-clear Judgment**: the `cleared | not-cleared | ambiguous` field in `kpi.json` that maps to `design/poc.md`'s "Per-session clear definitions".
- **Ratification Gate**: the operator-ratification step in the workflow/artifact that marks a specific per-run `poc-exit-<timestamp>.md` as a ratified POC-exit record rather than a draft. Ratification is per-file: a ratified per-run file remains so even when a later rollup run adds a newer per-run file.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A trained operator can produce `kpi.json` for a complete closed session bundle in under 30 seconds end-to-end with `peer-session tally <session-id>`, without hand-computing counts.
- **SC-002**: 100% of re-runs of `peer-session tally` against an unchanged bundle produce byte-identical `kpi.json` (modulo documented timestamp/hash fields).
- **SC-003**: 100% of `peer-session tally` runs against bundles incomplete per spec 001 FR-001..FR-011 fail loudly with a specific error, with zero cases of silently produced partial KPIs.
- **SC-004**: A trained operator can produce a draft per-run `poc-exit-<timestamp>.md` (with the pointer updated) in under 1 minute end-to-end with `peer-session rollup`, given that all counted sessions already have committed `kpi.json` and `fresh-reader-audit.json`.
- **SC-005**: A fresh reviewer (not the author) can read `observations/kpi-rollup/WORKFLOW.md` and correctly complete the H2 fresh-reader capture step and the ratification step on their first try without asking clarifying questions to the spec authors.
- **SC-006**: The per-session-clear judgment in `kpi.json` is reproducible by a second reviewer running `peer-session tally` independently, matching the original byte-for-byte in at least 100% of non-ambiguous cases (modulo timestamp).
- **SC-007**: The cross-session rollup correctly applies the H1 decision rule (3/3, 3/4, 4/5 per `design/poc.md`) in 100% of in-range counted-session totals and surfaces the out-of-range condition explicitly in 100% of out-of-range cases.

## Assumptions

- The `peer-session` CLI surface from spec 007 is landed on `main` and its extensibility intent (FR-012, Story 3) is the authoritative design posture for adding new subcommands.
- The bundle shape from spec 001 is the authoritative session-bundle contract; this slice is additive.
- The drift-audit workflow from spec 008 produces `drift-audit.json` in a shape this slice can consume as-is.
- The counted-session set size is 3 to 5 per `design/poc.md`'s H1 decision rule; anything outside that range is an operational exception, not a common case.
- Python stdlib is sufficient for all deterministic computations in this slice — no new runtime dependencies.
- Operators commit results (per-session `kpi.json` and `fresh-reader-audit.json`; cross-session per-run `poc-exit-<timestamp>.md` files plus the `poc-exit.md` pointer) into git; ratification lives in the per-run file's ratification-gate section plus the corresponding commit authorship + message, not in a separate ratification system.
- LLM-assisted KPI extraction follows the spec 008 FR-014 defer pattern: explicitly out of scope for v1, revisited only after v1 manual path is validated end-to-end.

## Dependencies

- Landed: spec 001 (bundle shape), spec 007 (CLI surface), spec 008 (drift-audit workflow / `drift-audit.json` schema).
- Not coordinated with spec 009 (session-summary): the 2026-04-21 clarification resolved FR-024 toward a dedicated `fresh-reader-audit.json` file, so spec 009's `summary.md` shape is not on this slice's critical path.
- Not a hard prerequisite but strongly motivating: a non-empty counted-session set. This slice can be specified, planned, implemented, and unit-tested against synthetic fixtures before any live counted sessions run. End-to-end validation requires at least one real closed bundle.

## Out of Scope

- **LLM-assisted KPI extraction** — deferred per the spec 008 FR-014 defer pattern; v1 is deterministic count + workflow-captured judgment.
- **Phase 4 Gemini-extension rollup** — different counted-session set and different hypothesis framing; handled in a later spec.
- **Re-running Phase 3 baseline sessions** — this slice consumes session output, it does not produce or schedule sessions.
- **Intervention tagging capture UX** — Codex-owned roadmap item; this slice reads `interventions.json` but does not define how entries get captured in real-time.
- **Changes to `cc-connect` transport** — transport-side work lives in the contained `cc-connect/` workspace and is out of scope here.
- **New runtime dependencies beyond Python stdlib** — matches spec 007's posture.
- **Bundle-shape redefinition** — spec 001 remains authoritative; this slice is additive only.
