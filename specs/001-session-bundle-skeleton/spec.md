# Feature Specification: Session Bundle Skeleton

**Feature Branch**: `001-session-bundle-skeleton`
**Created**: 2026-04-19
**Status**: Clarified (self-resolved per operator directive on 2026-04-19 authorizing autonomous speckit progression)
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

- **FR-009**: `transcript.md` MUST preserve the turn-by-turn exchange in chronological order, with at minimum **timestamp + author per turn**. **Timestamps MUST be ISO-8601 with at least second precision and unique within a session** — this uniqueness is the anchor that `interventions.json.target_turn` references. **Preferred source**: Discord export via `mcp__plugin_discord_discord__fetch_messages` rendered into markdown (richer fidelity, reproducible, operator-light). **Fallback**: operator-re-authored markdown when export is unavailable (e.g., upstream plugin breakage). The source used MUST be recorded in `meta.json` under `transcript_source` (`export` or `reauthored` or `hybrid`).
- **FR-010**: `meta.json` MUST contain: `session_id`, `opened_at` (ISO-8601), `closed_at` (ISO-8601 or `null` if session ended without explicit close), `close_reason` (one of `operator_close`, `pinned_rules_change`, `stop_no_resume` — matching the three close triggers in `design/poc.md` session definition; no separate `idle_timeout` close because idle is not a close trigger in the POC model, it gates operator-re-open only), `participants` (array of objects, each with `handle` and `role` where role is one of `peer`, `operator`; see Key Entities for the rationale), `pinned_rules_ref` (**preferred**: commit hash of pinned rules active at session open; **fallback**: inline snapshot object `{inline: "<content>"}` when rules are not git-tracked), `substrate` (default: `discord`), `channel_id` (when substrate is discord), `transcript_source` (per FR-009).
- **FR-011**: `interventions.json` MUST be an array of objects, each with: `at` (ISO-8601 timestamp with at least second precision), `type` (one of `safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other` per `design/poc.md` measurement model), `reason` (free-text operator note), `target_turn` (optional; when present, the value is the ISO-8601 timestamp string of the referenced turn in `transcript.md`, which is the canonical turn key per FR-009's uniqueness constraint). Empty array is valid if no interventions occurred.
- **FR-012**: `summary.md` MUST contain at minimum: session goal or seed, per-peer contribution summary, observed coordination patterns, notable drift (if any), operator verdict on whether the session cleared H1 stability / H1 complementarity / H2 fresh-reader (pending, per "Per-session clear definitions").

**Authoring discipline:**

- **FR-013**: Bundles MUST be committed as a single commit per session (`session bundle: <session-id>`) when possible — all five required files in one commit. Streaming commits during a live session are discouraged because a committed bundle is an evidence artifact, not a work-in-progress. If a live session is multi-hour and partial commits are operationally useful, they are allowed but SHOULD be squashed before the session is considered closed.
- **FR-014**: If a bundle needs correction after commit (intervention log typo, summary edit, late operator verdict), the correction MUST be a follow-up commit with message `session bundle amend: <session-id> — <reason>`. Never rewrite history on session bundles; the amend commit is the durable record of the correction.
- **FR-015**: Bundle directories MUST NOT contain secrets (tokens, DMs, unrelated private content). Redaction mechanic: if a committed bundle is found to contain content that should not have been committed, the operator (1) authors a corrected version in the same directory, (2) commits with message `session bundle amend: <session-id> — redaction: <reason>`, and (3) the original content remains in git history but is marked superseded by the amend commit. For sensitive content requiring hard removal from history, escalate to operator (`git-filter-branch` / BFG is out of normal bundle workflow).

**README and template:**

- **FR-016**: `observations/sessions/README.md` MUST exist and explain: the directory naming rule (FR-002), the file list (FR-004 through FR-008), a pointer to this spec, and a pointer to `design/poc.md` Layer 3 artifact bundle for context.
- **FR-017**: A template sub-directory MUST exist at `observations/sessions/_template/` containing empty-but-valid `transcript.md`, `meta.json`, `interventions.json`, `summary.md`, `drift-audit.json` with `[FILL IN]` placeholders and comment-level instructions. Operators copy-and-edit the template for each new session. The `_` prefix both sorts the template first in directory listings and excludes it from being counted as a session by any downstream tooling (e.g., KPI rollup scripts should filter directories starting with `_` or `.`). The template lives scope-locally under `observations/sessions/` rather than the top-level `templates/` directory because it is a bundle-shape artifact tied to this spec, not a generic repo-wide template.

### Key Entities

- **Session Bundle**: the directory `observations/sessions/<session-id>/` and all files within. A single session produces exactly one bundle. The bundle is a durable evidence artifact for H1/H2 evaluation.
- **Session ID**: the string `YYYY-MM-DD-<short-slug>` identifying a specific session. Used as directory name, referenced from `meta.json` and from KPI rollups.
- **Participant**: an object `{handle, role}` where `role ∈ {peer, operator}`. Role semantics are kept at the schema boundary because Phase 2 rollups and Phase 4 (Gemini extension, variable peer count) need to distinguish peers from the operator without guessing by list position. The POC allows N peers (2 baseline, 3 with Gemini stretch) plus exactly one operator.
- **Intervention Entry**: one tagged operator action within a session, stored as an object in `interventions.json`. Type taxonomy is fixed; free-text reason is per-entry. `target_turn`, when used, references a transcript turn by its ISO-8601 timestamp (canonical turn key per FR-009).
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

## Clarifications applied (self-resolved 2026-04-19)

Per [Zoe's operator directive on Discord](https://discord.com/channels/1484970897893752902) authorizing autonomous speckit progression in the absence of peer-to-peer comms, the five original open questions are resolved here with best-judgment defaults. Codex (cross-reviewer) may push back retroactively on any of these; resolution lands as a follow-up commit.

1. **FR-009 transcript source**: **Resolved** — Discord export via `mcp__plugin_discord_discord__fetch_messages` (rendered to markdown) is the preferred source; operator re-authored markdown is the fallback when export fails. Source recorded in `meta.json.transcript_source`. Rationale: fidelity preferred, with an explicit operator escape hatch; `transcript_source` field makes the choice auditable per session.
2. **FR-013/FR-014 commit discipline**: **Resolved** — one commit per session (all five required files) is the rule when operationally feasible. Streaming commits during a live session are allowed for long sessions but MUST be squashed before session close. Corrections are follow-up commits (`session bundle amend: <id> — <reason>`), never history rewrites. Rationale: bundles are evidence artifacts; git history for each session reads as one record per session.
3. **FR-010 pinned-rules snapshot**: **Resolved** — commit-hash reference is preferred; inline snapshot `{inline: "<content>"}` is the fallback. Rationale: if pinned rules are git-tracked (which is the intended path in this repo), commit-hash is tighter and diff-able; inline is only needed for out-of-band rules captured during a session.
4. **FR-015 redaction mechanics**: **Resolved** — normal redaction is an amend commit with `session bundle amend: <id> — redaction: <reason>`; the original stays in git history but is marked superseded. Hard removal from history (sensitive content requiring BFG / filter-branch) is an explicit operator escalation outside the normal bundle workflow. Rationale: keeps redaction in the normal evidence trail for operational transparency; reserves destructive history rewrites for genuine security incidents with operator judgment.
5. **FR-017 template location**: **Resolved** — `observations/sessions/_template/` scope-local, keeping bundle-shape templates next to the bundles they template. Top-level `templates/` is reserved for repo-wide templates (discussion-review, scratchpad). Rationale: scope-locality avoids a long round-trip when operators need to reference the template, and the `_` prefix handles sorting + tooling exclusion cleanly.

All five resolutions are defaults, not immutable. If cross-review disagrees, amend commits can revise any of them.

## Amendments from Codex cross-review (2026-04-19, discussion #43)

Cross-review findings from [Codex on #43](https://github.com/mentatzoe/peer-coordination/discussions/43) addressed:

- **Finding 1 (blocking)**: `close_reason` enum narrowed to match `design/poc.md` session model. Removed `idle_timeout` (idle is not a close trigger in the POC; it gates operator-re-open only) and `cancelled` (subsumed by `operator_close` or `stop_no_resume`). Final enum: `operator_close`, `pinned_rules_change`, `stop_no_resume`.
- **Finding 2 (blocking)**: `participants` upgraded from `[handle, ...]` to `[{handle, role}, ...]` where `role ∈ {peer, operator}`. Preserves role semantics at the schema boundary for Phase 2 rollups and Phase 4 (N-peer sessions).
- **Finding 3 (blocking)**: `target_turn` reference scheme defined. Transcript timestamps MUST be ISO-8601 with at least second precision and unique within a session (FR-009); `interventions.json.target_turn` uses that timestamp string as the canonical turn key.
- **Finding 4 (non-blocking)**: `summary.md` template updated to N-peer-safe repeatable bullets (applied in the template, not the spec text itself).
