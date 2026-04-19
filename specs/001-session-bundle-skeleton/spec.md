# Feature Specification: Session Bundle Skeleton

**Feature Branch**: `001-session-bundle-skeleton`
**Created**: 2026-04-19
**Status**: Draft
**Input**: Define the canonical per-session artifact bundle under `observations/sessions/<session-id>/` that Phase 2 + Phase 3 of the peer-coordination POC depend on. Preserve transcript, session metadata, tagged operator interventions, a human-readable summary, and a drift-audit output per `design/poc.md`'s Layer 3 artifact bundle. Include directory layout, session-ID naming, file stubs, a `README.md` explaining the bundle pattern, and commit discipline. Must be consistent with the intervention-type taxonomy (`safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other`) and the Layer 3 capability requirements in `design/architecture.md`. Out of scope: drift-audit rubric, intervention-tagging UX, KPI rollup script, operator-facing session ops.

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifact**: [`design/poc.md`](../../design/poc.md) §"Layer 3 artifact bundle" (the per-session bundle list) and §"Measurement model" (intervention taxonomy, timing rules).
- **Architecture reference**: [`design/architecture.md`](../../design/architecture.md) Layer 1 ("Layer 1 preserves the episode record") + Layer 3 capabilities.
- **Roadmap workstream**: `Evaluation surface build` (Phase 2 in [`ROADMAP.md`](../../ROADMAP.md)).
- **Staffing**: Claude lead; Codex cross-reviewer at spec-draft-complete + implementation-complete (per [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41) operating model).

## User Scenarios & Testing *(mandatory)*

The "users" of this artifact are (in priority order): the operator (Zoe), the cross-reviewing agents (Claude and Codex), a fresh human reviewer doing the H2 legibility test, and any automated tooling that consumes bundle content in Phase 2/3.

### User Story 1 — Operator commits a completed session's artifact bundle without ambiguity (Priority: P1)

As the operator, after a two-peer session completes, I need to place the preserved transcript, intervention log, pinned-rules snapshot, and summary into a single predictable location so the evidence is reviewable without reconstructing layout each time.

**Why this priority**: without a canonical bundle layout, every session produces ad-hoc evidence; cross-session review and KPI rollup become impossible. This is the MVP atom: one session in, one committed artifact bundle out.

**Independent Test**: hand the operator a dry-run transcript + intervention notes, ask them to produce a bundle following this spec's structure, and verify a cross-reviewer can locate each required artifact without operator guidance.

**Acceptance Scenarios**:

1. **Given** a completed session with operator intervention logs, peer transcript, and a pinned-rules snapshot, **When** the operator commits a session bundle per this spec, **Then** the bundle contains `transcript.md`, `meta.json`, `interventions.json`, `summary.md`, and `drift-audit.json` (placeholder acceptable pre-Phase-2) at `observations/sessions/<session-id>/`.
2. **Given** a bundle committed to the repo, **When** a cross-reviewer navigates to `observations/sessions/<session-id>/`, **Then** the `README.md` at `observations/sessions/` explains the bundle pattern sufficiently that the reviewer can interpret every file without asking the operator.

### User Story 2 — Cross-reviewer evaluates H1/H2 KPIs against a preserved session (Priority: P1)

As a cross-reviewing agent (or human reviewer), I need to read a session bundle and compute the H1 intervention-rate, H1 stability, and H2 fresh-reader KPIs against the POC's "Per-session clear definitions" without running the session again.

**Why this priority**: this is exactly the handover contract between Phase 1 (bundle exists) and Phase 2/3 (bundle is evaluated). Without a schema tight enough to support KPI computation, Phase 2's gate cannot be met.

**Independent Test**: hand a cross-reviewer one committed bundle and the "Per-session clear definitions" table from `design/poc.md`; verify the reviewer can answer clear/not-clear on each KPI row strictly from bundle content.

**Acceptance Scenarios**:

1. **Given** a committed bundle with `interventions.json` entries tagged per the intervention taxonomy, **When** the reviewer computes intervention-rate per session, **Then** the count is reproducible by re-running a deterministic counter on the JSON.
2. **Given** the `meta.json` and `transcript.md`, **When** a fresh uninvolved human reviewer reads the bundle, **Then** they can reconstruct session goal, peer contributions, and why the exchange resolved or failed (H2 fresh-reader KPI input).

### User Story 3 — Agent session pickup after turnover reads the latest bundle without operator help (Priority: P2)

As an agent (Claude or Codex) starting a fresh session mid-POC (after compaction, restart, or context loss), I need to read the most recent session bundle(s) and understand what happened without the operator restitching state.

**Why this priority**: direct implementation of the artifact-driven operating model ratified in [#41](https://github.com/mentatzoe/peer-coordination/discussions/41). Makes session turnover graceful.

**Independent Test**: spin up a fresh agent session with no conversation context, point at `observations/sessions/`, and verify the agent can summarize the prior session without operator input.

**Acceptance Scenarios**:

1. **Given** a fresh agent session and no prior conversation context, **When** the agent reads `observations/sessions/` + the most recent bundle's `summary.md` and `interventions.json`, **Then** the agent can produce a coherent next-step proposal.

### Edge Cases

- **Session cancels partway** (operator `!stop` without `!resume`): bundle is still committed with whatever artifacts exist; `meta.json` records the early-close reason. Partial bundles are valid evidence.
- **Two sessions in the same day**: session-ID collision is avoided by the naming convention (see FR-002).
- **Transcript unavailable** (e.g., Discord export failure, upstream plugin issue like `anthropics/claude-plugins-official#1477`): bundle still commits with a placeholder `transcript.md` explaining the gap; `meta.json` flags the gap. Avoids silently dropping a session.
- **Pinned rules change mid-POC**: each session's `meta.json` references a specific pinned-rules snapshot (commit hash or inline copy), so sessions remain auditable against the rules active *at that session*.
- **Large transcripts**: bundles may include >1 MB transcripts for long sessions; repo remains readable, but large-file practices (not checking raw audio, trimming metadata) should be implied, not enforced in this spec.

## Requirements *(mandatory)*

### Functional Requirements

**Directory layout:**

- **FR-001**: The repo MUST contain a top-level directory `observations/sessions/` that serves as the root for all session bundles.
- **FR-002**: Each session bundle MUST live at `observations/sessions/<session-id>/`, where `<session-id>` is `YYYY-MM-DD-<short-slug>` (ISO-date + hyphen + operator-chosen descriptive slug, lowercase kebab-case, ≤32 chars). Example: `2026-04-20-dry-run-one`.
- **FR-003**: If two sessions share a date and slug, the operator MUST disambiguate by appending `-NN` (two-digit counter). Example: `2026-04-20-dry-run-one-02`.

**Required artifacts per bundle:**

- **FR-004**: Every committed bundle MUST contain `transcript.md` (the preserved conversation text).
- **FR-005**: Every committed bundle MUST contain `meta.json` (session metadata — see FR-010).
- **FR-006**: Every committed bundle MUST contain `interventions.json` (tagged operator intervention log — see FR-011).
- **FR-007**: Every committed bundle MUST contain `summary.md` (human-readable qualitative account — see FR-012).
- **FR-008**: Every committed bundle MUST contain `drift-audit.json` — a placeholder stub file (with schema `{"status": "pending-phase-2"}` or equivalent) is acceptable until the drift-audit rubric spec lands. Presence of the file is the FR; content schema is deferred.

**Artifact schemas (minimal invariants; not full schemas):**

- **FR-009**: `transcript.md` MUST preserve the turn-by-turn exchange in chronological order, with at minimum timestamp + author per turn. [NEEDS CLARIFICATION: Discord export format vs re-authored — export is richer but lossier; re-authored is cleaner but slower. Operator-cost question.]
- **FR-010**: `meta.json` MUST contain: `session_id`, `opened_at` (ISO-8601), `closed_at` (ISO-8601 or `null` if session cancelled before close), `close_reason` (one of `operator_close`, `pinned_rules_change`, `stop_no_resume`, `idle_timeout`, `cancelled`), `participants` (list of peers + operator), `pinned_rules_ref` (commit hash of pinned rules active at session open, OR inline snapshot if rules not in a git artifact), `substrate` (default: `discord`), `channel_id` (when substrate is discord).
- **FR-011**: `interventions.json` MUST be an array of objects, each with: `at` (ISO-8601 timestamp), `type` (one of `safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other` per `design/poc.md` measurement model), `reason` (free-text operator note), `target_turn` (optional reference to a transcript turn). Empty array is valid if no interventions occurred.
- **FR-012**: `summary.md` MUST contain at minimum: session goal or seed, per-peer contribution summary, observed coordination patterns, notable drift (if any), operator verdict on whether the session cleared H1 stability / H1 complementarity / H2 fresh-reader (pending, per "Per-session clear definitions").

**Authoring discipline:**

- **FR-013**: Bundles SHOULD be committed as a single squashed commit per session (`session bundle: <session-id>`), not streaming commits during a live session. Rationale: a committed bundle is an evidence artifact, not a work-in-progress.
- **FR-014**: If an operator discovers a bundle needs correction after commit (e.g., intervention log typo, summary edit), the correction is a follow-up commit with message `session bundle amend: <session-id> — <reason>`. Never rewrite history on session bundles.
- **FR-015**: Bundle directories MUST NOT contain secrets (tokens, DMs, unrelated private content). If a transcript contains accidental private content, the operator redacts before commit.

**README and template:**

- **FR-016**: `observations/sessions/README.md` MUST exist and explain: the directory naming rule (FR-002), the file list (FR-004 through FR-008), a pointer to this spec, and a pointer to `design/poc.md` Layer 3 artifact bundle for context.
- **FR-017**: A template sub-directory MUST exist at `observations/sessions/_template/` containing empty-but-valid `transcript.md`, `meta.json`, `interventions.json`, `summary.md`, `drift-audit.json` with `[FILL IN]` placeholders and comment-level instructions. Operators copy-and-edit the template for each new session. The `_` prefix excludes it from being counted as a session by any downstream tooling.

### Key Entities

- **Session Bundle**: the directory `observations/sessions/<session-id>/` and all files within. A single session produces exactly one bundle. The bundle is a durable evidence artifact for H1/H2 evaluation.
- **Session ID**: the string `YYYY-MM-DD-<short-slug>` identifying a specific session. Used as directory name, referenced from `meta.json` and from KPI rollups.
- **Intervention Entry**: one tagged operator action within a session, stored as an object in `interventions.json`. Type taxonomy is fixed; free-text reason is per-entry.
- **Pinned-Rules Snapshot**: the content of the Discord-pinned rules active at session open, captured either by commit reference or inline in `meta.json` so the session remains auditable against the exact rules that governed it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator unfamiliar with the spec can produce a valid bundle for a completed session in under 15 minutes using the `_template/` directory, with no cross-reviewer rework needed on the bundle's structure (content quality is a separate concern).
- **SC-002**: Given a committed bundle, a deterministic script can count interventions by type and compute intervention-rate per turn without human intervention (required for the H1 intervention-rate observable).
- **SC-003**: A fresh agent session with no prior conversation context can read the most recent bundle and produce a 3-paragraph summary that the operator judges materially correct. Direct test of the artifact-driven operating-model claim.
- **SC-004**: 100% of Phase 2 and Phase 3 counted sessions produce committed bundles containing all five required files (FR-004 through FR-008), with no session missed. Bundle-completeness is part of the Phase 1 exit gate.
- **SC-005**: A fresh uninvolved human reviewer, given only a bundle and the "Per-session clear definitions" table, can answer clear/not-clear on H1 stability + H1 complementarity + H2 fresh-reader strictly from bundle content for ≥80% of test sessions.

## Assumptions

- The POC substrate is Discord; `substrate: discord` is the default and only substrate this spec explicitly supports. Non-Discord substrates (Phase 5+) may need schema additions; deferred.
- Discord transcript export is workable in the Phase 1 timeframe, whether via the `mcp__plugin_discord_discord__fetch_messages` tool or a manual export. If neither path works reliably, FR-009 escalates to blocked (see NEEDS CLARIFICATION on FR-009).
- Pinned-rules content is already git-tracked (in this repo or linked). If pinned rules live only on Discord and are never committed, FR-010 falls back to the inline-snapshot path, which is suboptimal but workable.
- The intervention-tagging UX is being specified separately by Codex (Phase 2). This spec defines the *storage shape* of `interventions.json`; how entries are actually captured in real-time is out of scope here.
- The drift-audit rubric is being specified separately (Phase 2). This spec requires the file to exist per FR-008 but defers schema.
- Session-ID choice is an operator concern; a conflict-resolution rule (FR-003) is provided but the operator picks the slug. Agents do not auto-generate session IDs.
- Small-N assumption: Phase 3 will produce 3–5 baseline sessions plus optional 1–2 Gemini stretch sessions. The bundle format is designed for this scale; unbounded scaling (hundreds of sessions) is not a design constraint here.

## Dependencies

- Depends on `design/poc.md` v1 (measurement model + Layer 3 artifact bundle list) being canonical and not in flux. Currently satisfied — POC doc ratified via #38.
- Depends on the intervention-type taxonomy being frozen. Currently satisfied — `safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other`.
- Depends on `design/architecture.md` Layer 3 capabilities being canonical. Currently satisfied — approved via #35.
- Depends on the POC-level session definition (see `design/poc.md` Session Definition table) for `opened_at`, `closed_at`, `close_reason` values.
- Does NOT depend on the drift-audit rubric being complete (FR-008 accepts a placeholder).
- Does NOT depend on the intervention-tagging UX being complete (FR-011 defines storage shape, not capture mechanism).

## Open questions for cross-review

1. **FR-009 transcript source**: Discord export vs re-authored markdown vs hybrid. Trade-off is fidelity (export is full but messy) vs readability (re-authored is clean but slower). Operator-cost question. Flagged as NEEDS CLARIFICATION.
2. **Commit discipline (FR-013 / FR-014)**: is squashed-per-session the right default? Alternative is "one commit per artifact file within the session directory," which gives finer git history but a noisier log. Proposed default is squash; flagging for Codex + Zoe.
3. **Pinned-rules snapshot (FR-010)**: commit-hash-reference is tidier if pinned rules live in git; inline snapshot is more self-contained. Proposed rule is "commit-hash if available, inline fallback." Flagging in case Codex has a cleaner shape.
4. **Redaction mechanics (FR-015)**: how does an operator redact a bundle that's already been committed? Git-filter-branch is heavy; simpler is "if redaction needed, the bundle is reauthored + amended-commit with the original excised." Flagging; not spec-critical for Phase 1.
5. **Template location (FR-017)**: `observations/sessions/_template/` with `_` prefix to sort first. Is there a better convention used elsewhere in the repo? The repo uses `templates/` at the top level for discussion review templates. This spec's template lives within `observations/sessions/` rather than in top-level `templates/` because it's scope-local. Flagging in case cross-review prefers top-level.
