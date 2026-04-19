# Tasks: Pinned-Rules Authoring and Exposure

**Input**: Design documents from `specs/003-pinned-rules-authoring/`
**Prerequisites**: [`spec.md`](spec.md), [`plan.md`](plan.md), and spec 001 (session-bundle-skeleton) for the consumer contract.
**Tests**: Not required for this slice (documentation + seed markdown only). Validation is by inspection + SC-001–SC-005 applied during Phase 3 sessions.
**Retrofit note**: Implementation for this spec landed on `main` via `2b740e2` before the branch-per-slice workflow was adopted. This file retrofits the speckit `tasks` stage to close the asymmetry with Codex's spec 002 and enable future `analyze` drift checks.

## Format: `[ID] [P?] [Story] Description [→ commit]`

- **[P]**: Parallelizable task.
- **[Story]**: User story (US1 / US2 / US3 from `spec.md`).
- **[→ commit]**: Commit where the task was completed.
- **[x]**: Task complete.

## Phase 1: Setup

- [x] **T001** [US1] Create top-level directory `pinned-rules/` per FR-001. → `2b740e2` (implicit via first file added).

## Phase 2: Foundational (workflow + consumer-contract documentation)

- [x] **T002** [US1/US2/US3] Author `pinned-rules/README.md` — authoring workflow (FR-005, FR-009, FR-010), commit-hash-ref contract with session bundles (FR-011), Discord exposure discipline (FR-007, FR-008), single-pin rule, why single `current.md` + git versioning, cross-references to `design/poc.md`, `design/architecture.md`, `.specify/memory/constitution.md`, and the `specs/001-session-bundle-skeleton/spec.md` consumer contract. → `2b740e2`.

## Phase 3: User Story 1 — Operator authors + exposes (Priority: P1)

**Goal**: enable session open against a git-tracked, Discord-exposed ruleset.

**Independent Test**: operator opens a session, reads `pinned-rules/current.md`, records commit hash in `meta.json.pinned_rules_ref`.

- [x] **T003** [P] [US1] Author `pinned-rules/current.md` — v1 seed content per FR-012: turn-taking heuristics (yielding / claiming / building), distinct-contribution norm (H1 complementarity), plain-language preference (H2 legibility), emoji palette (✅ 👀 🤔 🚫 ⏸️) with defined semantics, `!stop`/`!resume` interrupt semantics, escalation path, operator role (Constitution Principle IV). → `2b740e2`.
- [x] **T004** [P] [US1] Verify `current.md` stays under the FR-014 ~1500 rendered-char cap (the tighter spec-level constraint; Discord's own pin limit is 2000). Measured at 1475 rendered chars. → `2b740e2`.

## Phase 4: User Story 2 — Operator updates between sessions (Priority: P1)

**Goal**: rules evolve without breaking past-session auditability.

**Independent Test**: update rules in a discrete commit; past sessions still reference their own ruleset via `pinned_rules_ref` commit hash.

- [x] **T005** [US2] Document commit-discipline for rules changes in `pinned-rules/README.md` — `pinned-rules: <summary>` message format per FR-005; one logical change per commit; re-pin discipline (FR-010). → `2b740e2`.
- [x] **T006** [US2] Document the session-break rule in `pinned-rules/README.md` — rules change closes the current session per `design/poc.md` (close_reason `pinned_rules_change`); new session opens against new rules. → `2b740e2`.

## Phase 5: User Story 3 — Reviewer audits against active ruleset (Priority: P1)

**Goal**: reviewer resolves `pinned_rules_ref` to exact rules content for H2 audit.

**Independent Test**: `git checkout <commit> && cat pinned-rules/current.md`.

- [x] **T007** [US3] Consumer contract with spec 001 FR-010 — `meta.json.pinned_rules_ref` preferred is commit hash, inline snapshot is fallback. Documented cross-directionally in both specs' READMEs. → spec 001 change in `29980de`; spec 003 scaffolding in `2b740e2`.

## Phase 6: Polish + convenience artifacts

- [x] **T008** [P] Author `pinned-rules/CHANGELOG.md` stub — v1 seed entry per FR-004 (optional convenience; git log is authoritative). → `2b740e2`.
- [x] **T009** Self-resolve 5 open questions with inline rationale in `spec.md` "Clarifications applied" (directory location, single `current.md`, operator-only authoring, single-pin rule, optional CHANGELOG) per Zoe's 2026-04-19 autonomous-progression directive. → `2b740e2`.

## Dependencies

- T001 → T002, T003, T004, T008
- T002 → T005, T006
- T003, T004, T008 can run in parallel (different files)
- T007 cross-links to spec 001; no fresh work needed in 003 beyond documenting the reference

## Not in this task list (intentionally deferred)

- cc-connect automation for pin synchronization (Phase 2+).
- Agent-authored rule-change PRs (operator-only in Phase 1).
- Rules version history in filenames (`v1.md`, `v2.md` etc.) — rejected per T009 rationale.
- Runtime tooling to check Discord-pin ↔ git drift (optional Phase 2+; current FR-010 says manual check).

## Verification checklist

- [x] All FRs from `spec.md` mapped to at least one task
- [x] All user stories have ≥1 task tagged with their story ID
- [x] Content-constraint FRs (FR-012, FR-013, FR-014) verified against seed `current.md`
- [x] Consumer contract with spec 001 is cross-linked bidirectionally
