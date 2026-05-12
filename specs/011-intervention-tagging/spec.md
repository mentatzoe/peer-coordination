# Feature Specification: Intervention-Tagging Workflow

**Feature Branch**: `011-intervention-tagging`
**Created**: 2026-05-05
**Status**: Draft
**Input**: PC-66 eng-seed: define and implement the Codex-owned intervention-tagging schema/workflow that produces `observations/sessions/<session-id>/interventions.json`, unblocks Phase 2 exit, composes with spec 009 `summary.md`, and supplies H1 directive-intervention evidence without KPI rollup logic.

## Clarifications

### Session 2026-05-05

- Q: Live vs post-session tagging - which path is required for v1? -> A: Post-session annotation is the required v1 path, completed before summary authoring and before the next counted session or within 24 hours of close, whichever comes first. Live capture is allowed only as scratch input and does not become bundle evidence until post-session review writes the committed `interventions.json`.
- Q: Attribution granularity - what is mandatory? -> A: Every record MUST carry `attribution` with one of `operator_directed` or `agent_self_flagged`, plus an `actor` string. Operator-directed entries are mandatory for operator interventions; agent-self-flagged entries are supported when a peer explicitly identifies its own need for intervention, but operator ratification is still required before commit.
- Q: Per-turn vs per-span - how should multi-turn redirects be represented? -> A: One intervention record may target a single turn, a turn span, or the whole session. Multi-turn redirects SHOULD be one span-targeted record rather than repeated per-turn records unless the operator made distinct interventions with distinct reasons.
- Q: Schema versioning - does tagging need a version field? -> A: Yes. Because `interventions.json` remains a top-level array for spec 001 compatibility, each record carries `taxonomy_version: "poc-v1"`. Taxonomy changes create a new version string and do not silently mutate prior records.

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifacts**:
  - [`design/poc.md`](../../design/poc.md) - Layer 3 artifact bundle, measurement model, minimum intervention taxonomy, and Phase 2 exit gate.
  - [`design/architecture.md`](../../design/architecture.md) - Layer 3 requirement to track operator intervention frequency, type, and reason.
  - [`VISION.md`](../../VISION.md) - H1 convergence and H2 legibility hypotheses; intervention load is evidence, not live scoring.
- **Upstream dependencies (landed)**:
  - [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) - requires `interventions.json` in the bundle and FR-014 amend-commit discipline.
  - [`specs/006-discord-transcript-export/spec.md`](../006-discord-transcript-export/spec.md) - produces transcript turns cited by intervention targets.
  - [`specs/007-session-bundle-init-cli/spec.md`](../007-session-bundle-init-cli/spec.md) - creates the initial bundle and empty intervention log.
- **Adjacent evaluation dependencies (landed / in review)**:
  - [`specs/008-drift-audit-workflow/spec.md`](../008-drift-audit-workflow/spec.md) - reads `interventions.json` as context and must cite intervention ids rather than re-derive operator actions.
  - [`specs/009-session-summary-workflow/spec.md`](../009-session-summary-workflow/spec.md) - cites intervention types/reasons in `summary.md` and treats this schema as the source of truth.
- **Downstream consumers (out of scope here)**:
  - KPI rollup / spec 010 consumes `interventions.json` but owns cross-session aggregation, thresholds, and hypothesis verdict computation.
- **Roadmap workstream**: `Evaluation surface build` (Phase 2), Codex-owned schema / tagging slice.
- **Scope boundary**:
  - In scope: record schema, taxonomy, authoring workflow, citation key, commit discipline, CLI-assisted post-session add/validate path, runtime docs, template update, and synthetic dry-run.
  - Out of scope: live Discord slash-command UI, KPI rollup logic, drift-audit rubric scoring, summary verdict logic, transcript export, and session lifecycle controls.

## User Scenarios & Testing *(mandatory)*

The users of this workflow are the **operator** (tags interventions after a session), a **peer agent** (may self-flag an intervention candidate), a **reviewing auditor** (checks the log against the transcript), and **downstream consumers** (summary, drift-audit, KPI rollup).

### User Story 1 - Operator tags a closed session's interventions (Priority: P1)

As the operator, after a session closes and the transcript is available, I record every operator intervention in `observations/sessions/<session-id>/interventions.json` using a fixed taxonomy, clear reason, attribution, timestamp, and target turn or span, so H1 intervention-load evidence is captured without relying on memory or ad-hoc prose.

**Why this priority**: Phase 2 cannot exit until intervention tagging works end-to-end. The operator needs a low-friction, post-session path before summary, drift-audit, and KPI rollup can consume consistent evidence.

**Independent Test**: given a closed synthetic bundle with `transcript.md` and `meta.json`, run the post-session add workflow twice, verify `interventions.json` is a valid array with unique `iv-###` ids, fixed taxonomy values, required attribution/version fields, and target references that match transcript timestamps or spans.

**Acceptance Scenarios**:

1. **Given** a closed session bundle and no interventions yet, **When** the operator records a clarification at one transcript turn, **Then** `interventions.json` contains one record with `id: "iv-001"`, `type: "clarification"`, `attribution: "operator_directed"`, an operator `actor`, a non-empty `reason`, `target.kind: "turn"`, and `taxonomy_version: "poc-v1"`.
2. **Given** a redirect spans multiple turns, **When** the operator records the redirect with start/end turn references, **Then** the workflow creates one `directive_redirect` record with `target.kind: "span"` and both span bounds, not repeated per-turn duplicates.
3. **Given** the operator attempts to record a tag with an unknown type or missing reason, **When** validation runs, **Then** the workflow halts before writing a partial record and reports the specific invalid field.

---

### User Story 2 - Downstream artifacts cite interventions without re-deriving them (Priority: P1)

As a summary author, drift auditor, or KPI rollup consumer, I cite intervention records by stable ids from `interventions.json` and read their type/reason/attribution directly, so downstream artifacts do not reinterpret transcript turns into competing intervention accounts.

**Why this priority**: the same operator action feeds H1 directive-load evidence, summary context, and drift-audit context. If each consumer re-derives interventions from transcript text, the session bundle can contradict itself.

**Independent Test**: given an `interventions.json` with `iv-001` and `iv-002`, write a summary/drift-audit note that cites `interventions.json#iv-001`; verify the cited id resolves within the bundle, the consumer can read `type` and `reason` directly, and no consumer invents a new intervention type outside the taxonomy.

**Acceptance Scenarios**:

1. **Given** a `directive_redirect` record `iv-002`, **When** the drift-audit or summary references it, **Then** the citation key is `interventions.json#iv-002` inside the same session bundle, or `observations/sessions/<session-id>/interventions.json#iv-002` across bundles.
2. **Given** a downstream KPI rollup counts directive interventions, **When** it reads `interventions.json`, **Then** it counts records whose `type` is `directive_redirect` and MUST NOT infer additional directive interventions from transcript prose.
3. **Given** a consumer sees an `agent_self_flagged` attribution, **When** it reports operator load, **Then** it distinguishes the self-flag from operator-directed intervention rather than adding both to the same operator-directed numerator.

---

### User Story 3 - Operator corrects or extends intervention tags without rewriting history (Priority: P2)

As the operator, when an intervention is missed, mis-targeted, or needs a reason correction, I land a follow-up session-bundle amend commit that replaces the current `interventions.json` while preserving the prior version in git history.

**Why this priority**: Phase 3 sessions will be reviewed under time pressure. Corrections are expected, but the evidence trail must stay reconstructible per spec 001 FR-014.

**Independent Test**: commit an initial `interventions.json`, make a follow-up correction using the revision workflow, and verify the current file is valid while the prior version is retrievable via `git show <prior-commit>:observations/sessions/<session-id>/interventions.json`.

**Acceptance Scenarios**:

1. **Given** an initial log is committed, **When** the operator adds a missed intervention after review, **Then** the follow-up commit subject includes `interventions revision: missed-tag` and the new record receives the next unused `iv-###` id.
2. **Given** a record target was wrong, **When** the operator corrects it, **Then** the correction edits the existing record id rather than creating a second contradictory record, and the commit body names the correction reason.
3. **Given** a prior schema version exists, **When** a new taxonomy version is introduced later, **Then** old records keep their original `taxonomy_version`; migration, if ever needed, is an explicit follow-up slice.

### Edge Cases

- **No interventions occurred**: `interventions.json` MUST be `[]`; empty is a valid, committed evidence state.
- **Near-empty transcript**: intervention tagging still runs; records may target the session as a whole if no specific turn exists.
- **Unknown target turn**: validation MUST fail for a turn or span target whose timestamp is not present in `transcript.md`, unless the target kind is `session`.
- **Multiple interventions at one turn**: allowed when type or reason differs; each record gets its own id.
- **Agent self-flag without operator ratification**: not committed as evidence. The operator may record it as `agent_self_flagged` only after post-session review.
- **Live scratch note differs from post-session record**: the committed post-session record wins. Live notes are not evidence unless incorporated into `interventions.json`.
- **Typo correction**: follow-up amend commit, never `git commit --amend` on a prior bundle commit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The intervention log artifact MUST live at `observations/sessions/<session-id>/interventions.json` and MUST remain a top-level JSON array for compatibility with spec 001 and existing session-bundle templates.
- **FR-002**: Each intervention record MUST include `id`, `taxonomy_version`, `at`, `type`, `reason`, `attribution`, `actor`, and `target`.
- **FR-003**: `id` MUST be unique within the session, stable across revisions, and follow `iv-###` using chronological insertion order unless the operator supplies a stable id for a historical correction.
- **FR-004**: `taxonomy_version` MUST be `poc-v1` for this POC taxonomy. A future taxonomy change MUST use a new version string and MUST NOT silently rewrite old records.
- **FR-005**: `type` MUST be one of the POC taxonomy values from `design/poc.md`: `safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, or `other`.
- **FR-006**: `reason` MUST be a non-empty operator-readable explanation of why the intervention occurred. `other` records MUST include enough detail to explain why no fixed type fit.
- **FR-007**: `at` MUST be an RFC3339 UTC timestamp representing when the intervention was made or, for post-session-only reconstruction, the best transcript-aligned timestamp the operator can cite.
- **FR-008**: `attribution` MUST be one of `operator_directed` or `agent_self_flagged`. Operator-directed entries count toward operator intervention load; agent-self-flagged entries do not unless downstream KPI logic explicitly decides otherwise.
- **FR-009**: `actor` MUST identify the human or peer that made or requested the intervention (e.g. `Zoe`, `Vigil`). It is a string in v1 to preserve operator speed; structured identities are deferred.
- **FR-010**: `target` MUST be exactly one of: a single turn (`{"kind":"turn","turn_ref":"<timestamp>"}`), a turn span (`{"kind":"span","start_turn_ref":"<timestamp>","end_turn_ref":"<timestamp>"}`), or the full session (`{"kind":"session"}`).
- **FR-011**: The workflow MUST validate that turn and span target timestamps exist in `transcript.md` before committing, except for historical bundles where the operator explicitly records an unresolved target as a session-level intervention.
- **FR-012**: Citation keys MUST be `interventions.json#<id>` within the same bundle and `observations/sessions/<session-id>/interventions.json#<id>` when cited cross-bundle or from POC-level artifacts.
- **FR-013**: Downstream artifacts MUST cite intervention ids and read `type`/`reason` from `interventions.json`; they MUST NOT re-derive operator interventions from transcript prose when the log is present.
- **FR-014**: `directive_redirect` records are the authoritative per-session signal for H1 directive-intervention load. Drift-audit and KPI rollup consumers MAY reference the record id but MUST NOT create a separate directive-intervention classification.
- **FR-015**: The required authoring path is post-session annotation after transcript availability and before summary authoring; the operator SHOULD complete it before the next counted session or within 24 hours of session close, whichever comes first.
- **FR-016**: Live tagging notes are allowed only as scratch input in v1. This slice MUST NOT require Discord slash commands, live UI, or bridge changes for Phase 2 exit.
- **FR-017**: The workflow MUST support both add and validate operations through repo-owned tooling or documented manual steps; implementation v1 provides the `peer-session intervention add` and `peer-session intervention validate` CLI path.
- **FR-018**: The workflow MUST commit initial and revised `interventions.json` changes via session-bundle amend commits per spec 001 FR-014. Commit subject format: `session bundle amend: <session-id> — interventions[ <taxonomy-token>] @ <transcript-short-sha>`.
- **FR-019**: Revision commits MUST be follow-up commits, never history rewrites. The prior log version MUST remain retrievable via git history.
- **FR-020**: The workflow MUST provide a synthetic-transcript dry-run proving that the schema, CLI add/validate path, citation key, and directive-count signal work end-to-end without a real Phase 3 session.

### Key Entities

- **Session bundle** *(owned by spec 001)*: directory under `observations/sessions/<session-id>/` containing transcript, meta, intervention log, drift-audit, and summary.
- **Intervention log** *(owned by this slice)*: top-level JSON array in `interventions.json`; empty array is valid.
- **Intervention record** *(owned by this slice)*: one tagged intervention object with stable id, taxonomy version, type, reason, attribution, actor, timestamp, and target.
- **Intervention taxonomy** *(owned by this slice for POC v1)*: fixed values `safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other`, sourced from `design/poc.md`.
- **Target reference** *(owned by this slice, transcript-dependent)*: single-turn, span, or session target object used to cite where the intervention applies.
- **Citation key** *(owned by this slice)*: `interventions.json#iv-###` for within-bundle references.
- **Attribution** *(owned by this slice)*: `operator_directed` or `agent_self_flagged`; separates operator load from peer self-awareness signals.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a synthetic closed bundle, the operator can create two valid intervention records and validate the log in <=5 minutes using the documented CLI path.
- **SC-002**: 100% of intervention records in counted session bundles validate against the v1 required fields and taxonomy before summary authoring begins.
- **SC-003**: A downstream consumer can resolve a same-bundle citation key such as `interventions.json#iv-001` to exactly one record in 100% of valid bundles.
- **SC-004**: The directive-intervention load numerator for a session can be computed by counting `type == "directive_redirect"` records with `attribution == "operator_directed"` without reading transcript prose.
- **SC-005**: Corrections preserve prior versions through git history in 100% of revision cases; no intervention-log workflow uses `git commit --amend` on a previously committed bundle.
- **SC-006**: The Phase 2 dry-run leaves committed or staged evidence under `observations/sessions/_synthetic/011-intervention-tagging-dry-run/` showing the schema and citation contract end-to-end.

## Assumptions

- The session bundle has already been initialized by spec 001 / spec 007 and has a transcript exported by spec 006 before post-session tagging begins.
- `interventions.json` already exists as `[]` in newly initialized bundles; this slice fills or validates it rather than changing the top-level bundle shape.
- POC sessions are small-N and short enough for manual post-session annotation. No batch importer or live bridge integration is required for Phase 2.
- The operator remains authoritative on what counts as an intervention. Peer self-flags are evidence only after operator ratification into the log.
- KPI rollup decides how intervention counts compose across sessions; this slice only supplies per-session records and the directive signal.

## Dependencies

- **Upstream (landed)**: spec 001 (bundle shape and amend commits), spec 006 (transcript), spec 007 (bundle init CLI/template).
- **Adjacent (landed/in review)**: spec 008 (drift-audit consumes intervention context), spec 009 (summary cites intervention types/reasons).
- **Downstream (out of scope)**: KPI rollup / spec 010, POC exit synthesis.
- **Constitutional**: aligns with constitution v1.5.0: Layer 3 evaluation artifact, human arbitration, append-only session-bundle history, and human-legible records rather than hidden live instrumentation.
