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
  - Final output `observations/poc-exit.md` is operator-ratifiable: CLI produces the deterministic content; operator ratifies by committing.
  - Bundle shape from spec 001 is preserved where possible; any new bundle field is additive.

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

**Independent Test**: given a set of counted session bundles each with a committed `kpi.json` (from Story 1), run `peer-session rollup`; verify that `observations/poc-exit.md` is produced with the counted-session total, the H1 decision-rule application (3/3, 3/4, or 4/5 sessions clear), the H2 fresh-reader pass-rate, and episode-record completeness, in a format the operator can review and ratify by committing.

**Acceptance Scenarios**:

1. **Given** a set of counted session bundles (3 to 5) each with a committed `kpi.json`, **When** the operator runs `peer-session rollup`, **Then** the command writes `observations/poc-exit.md` with the counted-session total, the applied H1 decision-rule result, the H2 fresh-reader pass-rate, and episode-record completeness across the counted sessions.
2. **Given** a session bundle that exists under `observations/sessions/` but is missing its `kpi.json`, **When** the operator runs `peer-session rollup`, **Then** the command reports which bundles are not yet tallied and either refuses to roll up or clearly excludes them with an explicit notice in the output.
3. **Given** the template bundle under `observations/sessions/_template/`, **When** the operator runs `peer-session rollup`, **Then** the template is excluded from the counted-session aggregate (consistent with spec 001 FR-017 "directories starting with `_` or `.` are filtered").
4. **Given** a counted-session total outside the H1 decision-rule range (fewer than 3 or more than 5), **When** the operator runs `peer-session rollup`, **Then** the command surfaces the out-of-range condition in the output rather than silently mis-applying the 3/3, 3/4, or 4/5 threshold.

---

### User Story 3 — Operator uses the workflow recipe to capture human-judgment KPIs (Priority: P3)

As the operator, for the KPI fields that are human judgments rather than counts (H2 fresh-reader outcome, H3 complementarity narrative, "ambiguous" per-session-clear cases, the ratification gate), I need a written authoring recipe that tells me where and how to capture those judgments so that they flow into the cross-session rollup in a predictable place and format.

**Why this priority**: the CLI cannot automate human judgment. Without a workflow doc, operators will capture these fields in inconsistent places across sessions, breaking `peer-session rollup`'s ability to aggregate. Lower priority than the CLI because the workflow alone does not produce the rollup — but the rollup alone does not produce ratifiable H2/H3 stances without it.

**Independent Test**: given the `observations/kpi-rollup/WORKFLOW.md` authoring recipe, a fresh operator can read it and know (a) where H2 fresh-reader outcomes get captured, (b) where H3 complementarity narrative goes, (c) how to resolve an "ambiguous" per-session-clear flag, and (d) what ratification looks like — without asking the spec authors.

**Acceptance Scenarios**:

1. **Given** `observations/kpi-rollup/WORKFLOW.md` and a closed session with no H2 fresh-reader outcome captured yet, **When** a fresh operator reads the workflow, **Then** they can capture the H2 outcome in the location the workflow prescribes and the subsequent `peer-session tally` run reflects it without workflow ambiguity.
2. **Given** a cross-session `peer-session rollup` run that flagged one session as "ambiguous per-session-clear", **When** the operator follows the workflow's ambiguity-resolution step, **Then** the session's clear status is resolved to `cleared` / `not-cleared` via a recorded operator verdict that subsequent re-runs honor deterministically.
3. **Given** a produced `observations/poc-exit.md`, **When** the operator follows the workflow's ratification gate, **Then** the ratification is recorded as a commit message or a documented field in the artifact (per the workflow's chosen convention), making ratification auditable after the fact.

---

### Edge Cases

- A session bundle has `kpi.json` from a prior run but has since had `interventions.json` or `drift-audit.json` amended via a FR-014 amend commit (spec 001) — `peer-session tally` MUST recompute cleanly and produce updated `kpi.json`.
- A session bundle's `transcript.md` has zero turns (session opened and closed without exchange) — intervention-rate per turn is undefined; the tally MUST handle this without divide-by-zero and MUST surface the zero-turn condition in `kpi.json`.
- `drift-audit.json` is still the placeholder `{"status": "pending-phase-2"}` from spec 001 rather than a real rubric output — the tally MUST recognize the placeholder and either exclude drift-verdict from the per-session-clear judgment or fail with a clear error, not silently treat the placeholder as a "no drift" verdict.
- The counted-session set contains a session whose `kpi.json` was committed before a later `interventions.json` amendment and has not been re-tallied — the rollup MUST surface the staleness (e.g., a timestamp or hash-of-inputs field in `kpi.json` that rollup checks against current bundle state).
- A session bundle's `meta.json` has `closed_at: null` (session never explicitly closed per spec 001) — the tally MUST refuse to tally an unclosed session, since the counted-session set requires closed bundles.
- `peer-session rollup` is re-run after `poc-exit.md` has already been committed — the commit/history model defined in the Clarifications below governs whether this overwrites, appends, or errors.
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
- **FR-011**: `peer-session rollup` MUST aggregate `kpi.json` files from all session bundles under `observations/sessions/` **excluding** directories whose names start with `_` or `.` (consistent with spec 001 FR-017), and MUST produce `observations/poc-exit.md`.
- **FR-012**: `observations/poc-exit.md` MUST include at minimum: counted-session total, the applied H1 decision-rule result (3/3, 3/4, or 4/5 per `design/poc.md`), per-session-clear summary (one row per counted session), H2 fresh-reader pass-rate across counted sessions, episode-record completeness across counted sessions, and a ratification-gate section the operator fills on ratification.
- **FR-013**: `peer-session rollup` MUST surface (not silently exclude) any counted session where `kpi.json` is missing, stale relative to current bundle content (per FR-005), or flagged `ambiguous` for `per_session_clear`. The rollup MUST refuse to produce a ratifiable `poc-exit.md` when any of these conditions is unresolved, or MUST clearly mark the rollup as "draft, not ratifiable" in its output.
- **FR-014**: `peer-session rollup` MUST surface when the counted-session total is outside the H1 decision-rule range (fewer than 3 or more than 5) rather than silently mis-applying the 3/3, 3/4, 4/5 threshold.
- **FR-015**: `peer-session rollup` MUST detect and refuse to aggregate when two sessions share a `session_id` (spec 001 FR-002 collision).

#### Workflow authoring recipe (Story 3)

- **FR-016**: The system MUST provide a workflow document at `observations/kpi-rollup/WORKFLOW.md` that covers at minimum: (a) where and how to capture H2 fresh-reader outcome, (b) where and how to record H3 complementarity narrative, (c) how to resolve an `ambiguous` per-session-clear flag into a recorded operator verdict, and (d) the ratification gate for `poc-exit.md`.
- **FR-017**: The workflow MUST mirror the authoring pattern established by spec 008's drift-audit workflow — plain-language recipe with explicit sections per step, operator-facing examples, and a rationale section — rather than inventing a new authoring format.
- **FR-018**: The workflow MUST define the ambiguity-resolution record in a way that subsequent `peer-session tally` and `peer-session rollup` runs honor deterministically (e.g., a recorded verdict field the tally reads, or an amend-commit convention).

#### Bundle integration and scope preservation

- **FR-019**: This slice MUST NOT redefine the session-bundle shape from spec 001. Any new required bundle artifact (such as `kpi.json`) MUST be additive. Schema documentation placement is resolved by FR-023 below.
- **FR-020**: This slice MUST NOT introduce new runtime dependencies beyond Python stdlib (matches spec 007's posture of a repo-owned artifact-first utility).
- **FR-021**: This slice MUST NOT require a running `cc-connect` daemon or import-level coupling to the contained `cc-connect/` workspace (matches spec 007 SC-004).
- **FR-022**: This slice MUST NOT alter spec 008's `drift-audit.json` schema; it consumes the schema as-is.

#### Open design questions (to be resolved via `/speckit-clarify`)

- **FR-023**: The project MUST resolve whether `kpi.json` schema documentation lives in `observations/sessions/_template/README.md` (consistent with existing `meta.json` / `interventions.json` / `drift-audit.json` docs) or lives only in this spec's Key Entities section. [NEEDS CLARIFICATION: schema documentation location for `kpi.json` — A) add a schema section to `observations/sessions/_template/README.md` alongside existing entries, so the template is the single source of truth for bundle schemas; B) keep schema documentation only in spec 010 (this spec), so the template stays unchanged; C) both — template carries the schema, this spec carries the rationale.]
- **FR-024**: The project MUST resolve where the H2 fresh-reader outcome is captured per session, since it crosses spec 009 (session-summary) territory. [NEEDS CLARIFICATION: H2 fresh-reader outcome location — A) as a structured field inside `summary.md` (requires spec 009 coordination); B) as a separate `observations/sessions/<session-id>/fresh-reader-audit.json` bundle file added additively; C) inside `kpi.json` itself as an operator-filled field that `peer-session tally` seeds but the operator completes.]
- **FR-025**: The project MUST resolve the commit/history model for `observations/poc-exit.md` so re-runs of `peer-session rollup` are unambiguous. [NEEDS CLARIFICATION: `poc-exit.md` commit/history model — A) edit-in-place, commit history is the audit trail; B) per-run separate files `poc-exit-<iso-timestamp>.md` with a `poc-exit.md` symlink/pointer to the latest; C) append-only: each rollup appends a dated section to a single `poc-exit.md`.]

### Key Entities *(include if feature involves data)*

- **Tally Command**: the `peer-session tally <session-id>` entry point that computes per-session count-based KPIs from a closed bundle and writes `kpi.json`.
- **Rollup Command**: the `peer-session rollup` entry point that aggregates per-session `kpi.json` files into the cross-session `poc-exit.md`.
- **Per-session KPI File (`kpi.json`)**: the committed per-session artifact containing deterministic count-based KPI fields, the `per_session_clear` judgment, and an inputs-hash staleness marker. Additive to the spec 001 bundle shape.
- **Cross-session Rollup Artifact (`poc-exit.md`)**: the single operator-ratifiable document that applies the H1 decision rule, surfaces H2 pass-rate and episode-record completeness, and hosts the ratification gate.
- **KPI Workflow Document (`observations/kpi-rollup/WORKFLOW.md`)**: the authoring recipe for human-judgment KPI capture, ambiguity resolution, and ratification — the operator-facing complement to the CLI.
- **Intervention-Type Taxonomy**: the frozen set from `design/poc.md` measurement model and spec 001 FR-011 (`safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other`) used as the `intervention_type_tally` key set.
- **Counted-session Set**: the non-template, non-hidden session bundles under `observations/sessions/` that the rollup aggregates — the 3 to 5 bundles the H1 decision rule evaluates.
- **Inputs Hash / Staleness Marker**: the content-hash or equivalent field in `kpi.json` that lets `peer-session rollup` detect stale tallies relative to current bundle content.
- **Per-session-clear Judgment**: the `cleared | not-cleared | ambiguous` field in `kpi.json` that maps to `design/poc.md`'s "Per-session clear definitions".
- **Ratification Gate**: the operator-ratification step in the workflow/artifact that marks `poc-exit.md` as the final POC-exit record rather than a draft.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A trained operator can produce `kpi.json` for a complete closed session bundle in under 30 seconds end-to-end with `peer-session tally <session-id>`, without hand-computing counts.
- **SC-002**: 100% of re-runs of `peer-session tally` against an unchanged bundle produce byte-identical `kpi.json` (modulo documented timestamp/hash fields).
- **SC-003**: 100% of `peer-session tally` runs against bundles incomplete per spec 001 FR-001..FR-011 fail loudly with a specific error, with zero cases of silently produced partial KPIs.
- **SC-004**: A trained operator can produce a draft `observations/poc-exit.md` in under 1 minute end-to-end with `peer-session rollup`, given that all counted sessions already have committed `kpi.json`.
- **SC-005**: A fresh reviewer (not the author) can read `observations/kpi-rollup/WORKFLOW.md` and correctly complete the H2 fresh-reader capture step and the ratification step on their first try without asking clarifying questions to the spec authors.
- **SC-006**: The per-session-clear judgment in `kpi.json` is reproducible by a second reviewer running `peer-session tally` independently, matching the original byte-for-byte in at least 100% of non-ambiguous cases (modulo timestamp).
- **SC-007**: The cross-session rollup correctly applies the H1 decision rule (3/3, 3/4, 4/5 per `design/poc.md`) in 100% of in-range counted-session totals and surfaces the out-of-range condition explicitly in 100% of out-of-range cases.

## Assumptions

- The `peer-session` CLI surface from spec 007 is landed on `main` and its extensibility intent (FR-012, Story 3) is the authoritative design posture for adding new subcommands.
- The bundle shape from spec 001 is the authoritative session-bundle contract; this slice is additive.
- The drift-audit workflow from spec 008 produces `drift-audit.json` in a shape this slice can consume as-is.
- The counted-session set size is 3 to 5 per `design/poc.md`'s H1 decision rule; anything outside that range is an operational exception, not a common case.
- Python stdlib is sufficient for all deterministic computations in this slice — no new runtime dependencies.
- Operators commit results (both `kpi.json` and `poc-exit.md`) into git; ratification lives in git history (commit authorship + message), not in a separate ratification system.
- LLM-assisted KPI extraction follows the spec 008 FR-014 defer pattern: explicitly out of scope for v1, revisited only after v1 manual path is validated end-to-end.

## Dependencies

- Landed: spec 001 (bundle shape), spec 007 (CLI surface), spec 008 (drift-audit workflow / `drift-audit.json` schema).
- Coordinated: spec 009 (session-summary) — if Clarification FR-024 resolves toward option A (H2 outcome as a field in `summary.md`), that placement requires a corresponding field in spec 009's `summary.md` schema.
- Not a hard prerequisite but strongly motivating: a non-empty counted-session set. This slice can be specified, planned, implemented, and unit-tested against synthetic fixtures before any live counted sessions run. End-to-end validation requires at least one real closed bundle.

## Out of Scope

- **LLM-assisted KPI extraction** — deferred per the spec 008 FR-014 defer pattern; v1 is deterministic count + workflow-captured judgment.
- **Phase 4 Gemini-extension rollup** — different counted-session set and different hypothesis framing; handled in a later spec.
- **Re-running Phase 3 baseline sessions** — this slice consumes session output, it does not produce or schedule sessions.
- **Intervention tagging capture UX** — Codex-owned roadmap item; this slice reads `interventions.json` but does not define how entries get captured in real-time.
- **Changes to `cc-connect` transport** — transport-side work lives in the contained `cc-connect/` workspace and is out of scope here.
- **New runtime dependencies beyond Python stdlib** — matches spec 007's posture.
- **Bundle-shape redefinition** — spec 001 remains authoritative; this slice is additive only.
