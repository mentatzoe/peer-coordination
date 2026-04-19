# Tasks: Session Bundle Skeleton

**Input**: Design documents from `specs/001-session-bundle-skeleton/`
**Prerequisites**: [`spec.md`](spec.md), [`plan.md`](plan.md)
**Tests**: Not required for this slice (scaffolding only; no runtime code to test). Validation is by inspection + SC-001 / SC-004 applied to real Phase 3 sessions when they begin.
**Retrofit note**: Implementation for this spec landed on `main` via `cc62e16` + revisions in `29980de` before the branch-per-slice workflow was adopted. This file retrofits the speckit `tasks` stage to close the asymmetry with Codex's spec 002 and enable future `analyze` drift checks. Task IDs reference commits where applicable.

## Format: `[ID] [P?] [Story] Description [→ commit]`

- **[P]**: Parallelizable task (different files, no dependencies).
- **[Story]**: User story the task serves (US1 / US2 / US3 from `spec.md`).
- **[→ commit]**: The commit where the task was completed.
- **[x]**: Task complete (since this is a retrofit, all tasks below are complete unless otherwise noted).

## Phase 1: Setup (shared infrastructure)

- [x] **T001** [US1] Create top-level directory `observations/sessions/` so bundles have a canonical root per FR-001. → `cc62e16` (implicit via first file added).

## Phase 2: Foundational (blocking prerequisites for all user stories)

- [x] **T002** [US1/US2/US3] Write `observations/sessions/README.md` — naming rule (FR-002/003), required-files table (FR-004–008), authoring discipline (FR-013–015), creation/review instructions. → `cc62e16`.
- [x] **T003** [US1/US2/US3] Create `observations/sessions/_template/` sub-directory with `_` prefix for tooling exclusion (FR-017). → `cc62e16`.
- [x] **T004** [US1/US2/US3] Author `observations/sessions/_template/README.md` — per-file schema documentation (since JSON can't carry inline comments). → `cc62e16`, revised for schema updates in `29980de`.

## Phase 3: User Story 1 — Operator commits a completed bundle (Priority: P1)

**Goal**: make the minimal-per-session artifact set canonical and copyable.

**Independent Test**: an operator given a dry-run transcript can produce a bundle following this spec's structure, and a cross-reviewer can locate each required artifact without operator guidance.

- [x] **T005** [P] [US1] Author `observations/sessions/_template/transcript.md` — turn-format stub with timestamp + author format and transcript-source note (FR-009). → `cc62e16`.
- [x] **T006** [P] [US1] Author `observations/sessions/_template/meta.json` — all required keys from FR-010 with `[FILL IN]` placeholders. → `cc62e16`, schema updated per Codex #43 findings (narrower `close_reason` enum, `participants` as `[{handle, role}]`, `transcript_source` field) in `29980de`.
- [x] **T007** [P] [US1] Author `observations/sessions/_template/interventions.json` — empty array + schema documented via `_template/README.md` (FR-011). → `cc62e16`, `target_turn` reference scheme (timestamp-based) documented in `29980de`.
- [x] **T008** [P] [US1] Author `observations/sessions/_template/summary.md` — required section headings per FR-012, keyed to H1 stability / H1 complementarity / H2 fresh-reader KPIs in `design/poc.md`. → `cc62e16`, N-peer-safe repeatable pattern applied in `29980de`.
- [x] **T009** [P] [US1] Author `observations/sessions/_template/drift-audit.json` — placeholder `{"status": "pending-phase-2"}` (FR-008). → `cc62e16`.

## Phase 4: User Story 2 — Cross-reviewer computes KPIs (Priority: P1)

**Goal**: schemas tight enough for deterministic KPI computation + human-reviewable KPI judgments.

**Independent Test**: given a bundle, a reviewer answers clear/not-clear on each KPI row strictly from bundle content.

- [x] **T010** [US2] Apply Codex #43 finding F1 — narrow `close_reason` enum to `operator_close | pinned_rules_change | stop_no_resume` (matches POC session model; removes `idle_timeout` + `cancelled`). → `29980de`.
- [x] **T011** [US2] Apply Codex #43 finding F2 — upgrade `participants` from `[handle]` to `[{handle, role}]` with role ∈ `peer | operator` so Phase 2 / Phase 4 consumers don't guess by position. → `29980de`.
- [x] **T012** [US2] Apply Codex #43 finding F3 — define `target_turn` reference scheme via ISO-8601 second-precision timestamps unique within a session (FR-009 amended; `target_turn` in `interventions.json` is the timestamp string of the referenced turn). → `29980de`.

## Phase 5: User Story 3 — Agent session pickup after turnover (Priority: P2)

**Goal**: a fresh agent session reads the latest bundle and continues without operator restitching.

**Independent Test**: fresh agent, no prior context → produces a coherent next-step proposal strictly from `observations/sessions/<id>/summary.md` + `interventions.json`.

- [x] **T013** [US3] Confirmed by the operating model itself (discussion #41): session turnover is tolerable because artifacts are state; this spec's bundle layout is one of the durable surfaces the model points at. Not a code task; validated in-thread at [`#41:16618224`](https://github.com/mentatzoe/peer-coordination/discussions/41#discussioncomment-16618224).

## Phase 6: Polish

- [x] **T014** Self-resolve 5 spec open questions with inline rationale (transcript source, commit discipline, pinned-rules snapshot, redaction mechanics, template location) per Zoe's 2026-04-19 directive authorizing autonomous speckit progression. → `cc62e16` spec.md "Clarifications applied" section.
- [x] **T015** Apply non-blocking #43 finding F4 — rewrite `summary.md` per-peer contribution section as N-peer-safe repeatable pattern. → `29980de`.

## Dependencies

- T001 → T002, T003
- T003 → T004, T005–T009
- T005–T009 run in parallel (different files)
- T004 → revised alongside schema changes in T010–T012
- T010–T012 are schema amendments; T013 is validation; T014 and T015 are polish
- No external dependencies (no cc-connect, no runtime code, no test infrastructure)

## Not in this task list (intentionally deferred)

- Actual session bundles (will land in Phase 3 sessions; this slice only produces the scaffolding).
- Drift-audit rubric (Phase 2 spec; FR-008 allows placeholder).
- Intervention-tagging UX (Codex's Phase 2 slice; FR-011 defines storage shape only).
- KPI rollup script (Phase 2 spec).
- Transcript export tooling (Phase 1 Codex slice, transport side).

## Verification checklist

- [x] All FRs from `spec.md` mapped to at least one task
- [x] All user stories have ≥1 task tagged with their story ID
- [x] Codex #43 findings all addressed (F1 / F2 / F3 blocking; F4 non-blocking)
- [x] Implementation files exist on `main` and match the schema the spec describes post-revision
