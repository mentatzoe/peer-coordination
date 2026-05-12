---

description: "Implementation task list for KPI Rollup"
---

# Tasks: KPI Rollup

**Input**: Design documents from `specs/010-kpi-rollup/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: INCLUDED. The `contracts/tally-cli-behavior.md` and `contracts/rollup-cli-behavior.md` documents enumerate contract tests explicitly (9 and 10 respectively). `research.md` §10 also commits the slice to synthetic-fixture-backed unit tests with no skip-on-missing-infra shortcuts. Tests are therefore first-class deliverables, not optional additions.

**Organization**: Tasks are grouped by user story (P1 per-session tally, P2 cross-session rollup, P3 workflow recipe) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Repository-root single-project layout per plan.md:

- CLI package: `tools/peer_session/`
- CLI tests: `tests/peer_session/`
- CLI wrapper: `peer-session` (repo root; unchanged from spec 007)
- Bundle template: `observations/sessions/_template/`
- New workflow surface: `observations/kpi-rollup/`

All paths below are repository-relative from the worktree root `/Users/zmll/github/peer-coordination/.worktrees/kpi-rollup/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Stub out new directories and empty placeholders so downstream tasks have stable paths to write to.

- [ ] T001 Create `observations/kpi-rollup/` directory (empty for now; holds `WORKFLOW.md` authored in US3) via `mkdir -p observations/kpi-rollup` from worktree root.
- [ ] T002 Create `tests/peer_session/fixtures/` directory via `mkdir -p tests/peer_session/fixtures` to host synthetic session bundles for all downstream tests.

**Checkpoint**: Empty directories exist; foundational work can proceed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared infrastructure that MUST be complete before any user story can be implemented — template schema additions (used by both tally and rollup via operators/agents), shared `bundle_io` helpers (used by both tally and rollup), composite `per_session_clear` logic (used by tally, consumed by rollup), and fixture bundles (used by all tests).

**⚠️ CRITICAL**: No user-story work begins until this phase is complete.

### Template schema and placeholders

- [ ] T003 [P] Add `kpi.json` schema section to `observations/sessions/_template/README.md` documenting the full serialized shape (fields from data-model.md's `KPIFile` entity), field types, enum values (`per_session_clear`, breakdown sub-states), and example. Match the style of the existing `meta.json` / `interventions.json` / `drift-audit.json` sections. Per FR-023 clarification.
- [ ] T004 [P] Add `fresh-reader-audit.json` schema section to `observations/sessions/_template/README.md` documenting fields from data-model.md's `FreshReaderAudit` entity (`session_id`, `audited_at`, `auditor`, `verdict` enum, `reasoning`), with example. Per FR-024.
- [ ] T005 [P] Create `observations/sessions/_template/kpi.json` with all fields present but populated with `[FILL IN]` markers (consistent with spec 001 FR-017's `_template/` placeholder convention).
- [ ] T006 [P] Create `observations/sessions/_template/fresh-reader-audit.json` with all fields present but populated with `[FILL IN]` markers.

### Shared Python modules

- [ ] T007 Implement `tools/peer_session/bundle_io.py` — stdlib-only shared helpers: (a) `read_bundle(session_dir: Path) -> BundleInputs` that loads and validates all spec-001 required files, failing with specific errors on incompleteness per FR-006; (b) `compute_inputs_hash(inputs: BundleInputs) -> str` implementing the SHA-256 canonical-JSON hash per research §1; (c) `format_iso8601_utc(dt: datetime) -> str` returning timestamps matching research §2 (`YYYYMMDDTHHMMSSZ` for filenames, seconds-precision ISO for fields). Type-hinted, stdlib-only (`hashlib`, `json`, `datetime`, `pathlib`).
- [ ] T008 Implement `tools/peer_session/per_session_clear.py` — pure function `compute_per_session_clear(inputs: BundleInputs, fresh_reader_audit: Optional[dict]) -> dict` returning the six sub-judgments plus top-level composite per research §4. Each sub-judgment is one of `cleared | not-cleared | ambiguous` with an optional `reason`. No I/O; consumes already-parsed inputs. Depends on T007.

### Unit tests for foundational modules

- [ ] T009 [P] Add `tests/peer_session/test_bundle_io.py` — unit tests for `read_bundle` (missing-file failure, valid-bundle happy path), `compute_inputs_hash` (determinism: same inputs → same hash; change in any input → different hash), and `format_iso8601_utc` (exact format match). Depends on T007.
- [ ] T010 [P] Add `tests/peer_session/test_per_session_clear.py` — unit tests for `compute_per_session_clear` covering the 6 sub-judgments individually (each reaching `cleared`, `not-cleared`, and `ambiguous` where applicable) plus the top-level composite rule (cleared-only, any not-cleared, any ambiguous without not-cleared). Depends on T008.

### Fixture bundles

- [ ] T011 [P] Create `tests/peer_session/fixtures/session_minimal/` — complete bundle that passes tally cleanly with `per_session_clear == "cleared"`. Includes real `interventions.json`, `drift-audit.json` (non-placeholder), `summary.md`, `transcript.md` with ≥1 peer turn, `meta.json` with `closed_at` set, and `fresh-reader-audit.json` with `verdict: "pass"`.
- [ ] T012 [P] Create `tests/peer_session/fixtures/session_missing_fra/` — identical to `session_minimal` but without `fresh-reader-audit.json`. Exercises the tally-tolerates-rollup-refuses split (research §7).
- [ ] T013 [P] Create `tests/peer_session/fixtures/session_placeholder_drift/` — identical to `session_minimal` but `drift-audit.json` is the spec-001 placeholder `{"status": "pending-phase-2"}`. Exercises FR-008 branch.
- [ ] T014 [P] Create `tests/peer_session/fixtures/session_zero_turns/` — bundle whose `transcript.md` has no peer turns. Exercises FR-009 null-rate branch.
- [ ] T015 [P] Create `tests/peer_session/fixtures/session_unclosed/` — bundle whose `meta.json.closed_at` is `null`. Exercises FR-007 refuse branch.
- [ ] T016 [P] Create `tests/peer_session/fixtures/session_ambiguous/` — bundle where operator-judgment-dependent sub-judgments resolve to `ambiguous` (e.g., `fresh-reader-audit.json` has `verdict: "inconclusive"`). Exercises composite ambiguity rule.
- [ ] T017 [P] Create `tests/peer_session/fixtures/rollup_counted_set/` — a full set of three complete bundles (each with `kpi.json` and `fresh-reader-audit.json` pre-populated) for end-to-end rollup testing, including at least one session that clears and one that does not, to exercise the H1 decision-rule logic.
- [ ] T018 [P] Extend `tests/peer_session/test_support.py` with fixture-handling helpers — e.g., `load_fixture(name) -> Path`, `copy_fixture_to_tempdir(name) -> Path`, and a pytest-style context manager for temp-directory isolation. Mirrors spec 007's existing test_support patterns.

**Checkpoint**: Shared infrastructure ready; US1/US2/US3 can begin in parallel.

---

## Phase 3: User Story 1 — Operator computes per-session KPIs from a closed bundle (Priority: P1) 🎯 MVP

**Goal**: `peer-session tally <session-id>` produces a deterministic, re-runnable, byte-idempotent `kpi.json` from a closed session bundle. This is the foundation the cross-session rollup consumes.

**Independent Test**: Run `peer-session tally session_minimal` against the happy-path fixture in a temp-directory; verify `kpi.json` is created with the expected fields, exit code 0, and re-running produces byte-identical output modulo `tallied_at`. Additionally, verify each of the 9 contract tests in `contracts/tally-cli-behavior.md` passes.

### Implementation

- [ ] T019 [US1] Implement `tools/peer_session/tally.py` — module exposing `run_tally(session_id: str, sessions_root: Path) -> int` that: reads inputs via `bundle_io.read_bundle`, refuses on unclosed session (FR-007, exit 3), computes `intervention_count`, `intervention_type_tally` (seeded with all 6 taxonomy keys per FR-003), `intervention_rate_per_turn` per research §5, reads `fresh-reader-audit.json` when present (tolerates absence per research §7), invokes `per_session_clear.compute_per_session_clear`, detects drift-audit placeholder per research §6, computes `inputs_hash` via `bundle_io.compute_inputs_hash`, writes `kpi.json` atomically to `sessions_root / session_id / "kpi.json"`, and returns 0 on success or a documented non-zero exit code per `contracts/tally-cli-behavior.md`. Depends on T007, T008.
- [ ] T020 [US1] Wire the `tally` subparser into `tools/peer_session/cli.py` — add a new subparser named `tally` with positional argument `session_id`, dispatch to `tally.run_tally`, return its exit code. Preserve the existing `init` subparser behavior unchanged (regression-proof).

### Tests

- [ ] T021 [P] [US1] Add `tests/peer_session/test_tally.py` — implement the 9 contract tests from `contracts/tally-cli-behavior.md` §"Contract tests": happy path, idempotence (byte-identical modulo `tallied_at` — this scenario also satisfies SC-006's second-reviewer reproducibility since the function is pure over its inputs), staleness (input change → hash change), missing fresh-reader-audit (soft), drift placeholder (soft), zero turns, bundle incomplete (refuse exit 2), unclosed session (refuse exit 3), invalid intervention type (refuse exit 4). Uses fixtures from T011–T016. Depends on T018, T019.
- [ ] T022 [US1] Extend `tests/peer_session/test_cli.py` with a `test_cli_tally_dispatch` case — verifies `peer-session tally <session-id>` from the CLI entry point reaches `tally.run_tally` with the expected arguments and propagates its exit code. Depends on T020, T021.

**Checkpoint**: `peer-session tally` works end-to-end; operator can tally any closed bundle deterministically. US1 is independently deliverable as the MVP for this slice.

---

## Phase 4: User Story 2 — Operator produces the POC-exit rollup across counted sessions (Priority: P2)

**Goal**: `peer-session rollup` aggregates committed per-session `kpi.json` + `fresh-reader-audit.json` across the counted-session set, applies the H1 decision rule per `design/poc.md`, writes a new `observations/poc-exit-<timestamp>.md` per-run file, and updates the `observations/poc-exit.md` symlink pointer. Refuses on hard data gaps; produces draft-marked output on operator-judgment gaps.

**Independent Test**: Run `peer-session rollup` against `tests/peer_session/fixtures/rollup_counted_set/` (3 bundles, each with committed `kpi.json` + `fresh-reader-audit.json`); verify a new `poc-exit-<timestamp>.md` is written with the H1 `3/3` decision rule applied, `poc-exit.md` symlink resolves to it, and exit code 0. Additionally, verify each of the 10 contract tests in `contracts/rollup-cli-behavior.md` passes.

**Depends on**: US1 complete (needs `tally` working to generate fixture `kpi.json` files) OR fixtures with pre-populated `kpi.json` (T017 does the latter, so US2 can proceed in parallel with US1 tests).

### Implementation

- [ ] T023 [US2] Implement `tools/peer_session/rollup.py` — module exposing `run_rollup(observations_root: Path) -> int` that: discovers counted-session bundles per research §8 (skip `_`-prefix and hidden dirs), verifies each has `kpi.json` + `fresh-reader-audit.json`, recomputes inputs-hash and detects staleness per FR-005, detects session-id collisions per FR-015, aggregates into an in-memory `IntersessionRollupSnapshot` per data-model.md, applies the FR-013 split (refuse on hard data gaps → exit 2; draft-mark on judgment gaps → exit 0), applies the H1 decision rule against `counted_session_total` per research §9 (FR-014 keys the in-range check on the counted-session set; do NOT subtract ambiguous sessions before applying the threshold), computes `h2_fresh_reader_pass_rate` over `counted_session_total` per FR-012 ("across counted sessions"), surfaces out-of-range conditions per FR-014, renders the per-run `poc-exit-<timestamp>.md` per `contracts/rollup-cli-behavior.md` §"Per-run file structure", writes it atomically to `observations_root / f"poc-exit-{timestamp}.md"`, and updates the `poc-exit.md` symlink via `os.unlink` + `os.symlink` per research §3. Depends on T007, T019 (rollup reads `kpi.json` files whose format is defined by tally).
- [ ] T024 [US2] Wire the `rollup` subparser into `tools/peer_session/cli.py` — add a subparser named `rollup` (no positional args), dispatch to `rollup.run_rollup`, return its exit code. Preserve existing `init` and `tally` subparsers unchanged.

### Tests

- [ ] T025 [P] [US2] Add `tests/peer_session/test_rollup.py` — implement the contract tests from `contracts/rollup-cli-behavior.md` §"Contract tests": happy path 3/3, happy path 3/4 with 1 not-cleared, 1 ambiguous session → draft (3-session in-range case — asserts NOT out-of-range; this is the FR-014 "counted-session total" range-key regression test), missing kpi.json → refuse, missing fresh-reader-audit.json → refuse, stale kpi.json → refuse, session-id collision → refuse, 2-session out-of-range → draft with surface, template excluded, symlink update on second run. Also asserts `h2_fresh_reader_pass_rate` denominator equals `counted_session_total` (FR-012 regression: 2 passes + 1 ambiguous reports 2/3, not 2/2). Uses fixtures from T017. Depends on T018, T023.
- [ ] T026 [US2] Extend `tests/peer_session/test_cli.py` with a `test_cli_rollup_dispatch` case — verifies `peer-session rollup` from the CLI entry point reaches `rollup.run_rollup` and propagates its exit code. Depends on T024, T025.

**Checkpoint**: `peer-session rollup` works end-to-end; operator can produce a POC-exit rollup from the counted-session set. US2 delivered.

---

## Phase 5: User Story 3 — Operator uses the workflow recipe to capture human-judgment KPIs (Priority: P3)

**Goal**: Operators have an authored recipe at `observations/kpi-rollup/WORKFLOW.md` covering fresh-reader audit authoring, H3 complementarity narrative, ambiguity resolution, and the per-file ratification gate — so those human-judgment inputs flow into the rollup predictably.

**Independent Test**: A fresh operator (not the workflow author) reads `observations/kpi-rollup/WORKFLOW.md` and without additional explanation can correctly (a) author a `fresh-reader-audit.json`, (b) locate where to record H3 complementarity narrative, (c) resolve an ambiguous per-session-clear flag, (d) follow the ratification gate for a per-run `poc-exit-<timestamp>.md`. Meets spec SC-005.

**Depends on**: Phase 1 (needs the `observations/kpi-rollup/` directory) and understanding of US1/US2 behavior (the workflow references both commands). Can be drafted in parallel with US1/US2 implementation but cross-checked after they land.

### Implementation

- [ ] T027 [US3] Author `observations/kpi-rollup/WORKFLOW.md` with the four required sections per FR-016, using the spec-008 drift-audit-workflow authoring pattern (plain prose, operator-facing, explicit section per step, rationale subsection):
  - **§A Authoring `fresh-reader-audit.json`** — who the fresh reader is (per `design/poc.md` H2 definition), what they read, how the operator ratifies the reconstruction, how to write the file referencing the schema in `observations/sessions/_template/README.md` (no schema duplication per FR-023).
  - **§B Recording H3 complementarity narrative** — where in the bundle this goes (likely in `summary.md` — note coordination with spec 009 is not tight because spec 010 does not read the complementarity narrative from any structured field; H3 at the per-session level is consumed via `per_session_clear_breakdown.h1_complementarity`'s `reason` field when ambiguous).
  - **§C Resolving `ambiguous` per-session-clear via amend-commit** — per FR-018, the resolution mechanism is the amend-commit convention (not an override field in `kpi.json`). Operators resolve ambiguity by amending the underlying bundle input (e.g., `fresh-reader-audit.json`'s `verdict`, or running a real drift audit that replaces the spec-001 placeholder in `drift-audit.json`) with an amend commit following spec 001 FR-014's discipline, then re-running `peer-session tally` to recompute `per_session_clear` deterministically from the amended inputs. The workflow MUST document this convention explicitly, name the permissible amend targets per sub-judgment, and describe the pre-commit review expectations so amend commits remain auditable.
  - **§D Ratification gate for a per-run `poc-exit-<timestamp>.md`** — how the operator reviews the per-run file, what to fill in the ratification-gate subsection, the convention for recording ratification (text in the section + commit metadata), and what it means for a per-run file to be ratified vs. superseded by a later per-run file.

**Checkpoint**: Human-judgment KPI capture is operator-legible without asking the spec authors; US3 delivered.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full slice works end-to-end, run manual smoke tests, and prepare PR-landing artifacts.

- [ ] T028 Run the full `python3 -m unittest discover tests/peer_session` test suite from the worktree root and confirm all new and existing tests pass. No skipped tests. Depends on T019–T026.
- [ ] T029 Run the 11-item manual smoke-test checklist from [`quickstart.md`](./quickstart.md) §"Manual smoke-test checklist" against a real operator-style invocation of the CLI from the worktree root. Document any deviations. Per the user memory "Interactive CLIs require manual testing". Depends on T028.
- [ ] T030 Verify `readlink observations/poc-exit.md` (after a successful rollup) resolves to the expected `poc-exit-<timestamp>.md` filename. Confirms research §3 symlink implementation is working. Part of T029 but called out explicitly because it's easy to miss.
- [ ] T031 [P] Update the `010-kpi-rollup` row in `ACTIVE-SLICES.md` from phase `brainstorm` → `review` (and subsequently → `implement` once PR review begins). **Note**: `ACTIVE-SLICES.md` lives on `main`, not on this branch — land the row update as a separate direct-to-`main` commit following the project's slice-claim convention (see the `2f49e85` claim commit for spec 009 as reference). Do NOT commit the row change on `010-kpi-rollup`. Ensure the `Last confirmed` date and `Notes` column are current.
- [ ] T032 [P] Author a PR description for this slice summarizing: spec/clarify/plan/tasks landing, 3 user stories implemented, all contract tests passing, manual smoke-test completed, deferrals (LLM-assisted KPI extraction per spec 008 FR-014 pattern, Phase 4 Gemini-extension rollup), and any known limitations discovered during implementation. This becomes the `gh pr create --body` input.
- [ ] T033 Validate `observations/kpi-rollup/WORKFLOW.md` usability against SC-005 — hand the workflow to a fresh reviewer (Codex or Zoe, whoever has not co-authored the doc) and ask them to walk through §A (authoring `fresh-reader-audit.json`) and §D (ratification gate) without author assistance. Document clarifications they had to ask for; revise the workflow inline before PR finalization so the "first-try without asking" threshold is met. Depends on T027.

**Checkpoint**: Slice is implementation-complete, verified end-to-end, and ready for peer review.

---

## Dependencies

```text
Phase 1 (Setup: T001, T002)
   │
   ▼
Phase 2 (Foundational: T003–T018)
   │     ├── Template: T003, T004, T005, T006 (all [P] among themselves)
   │     ├── Core modules: T007 (bundle_io) → T008 (per_session_clear)
   │     ├── Foundational tests: T009, T010 (after T007, T008)
   │     └── Fixtures: T011–T018 (all [P] among themselves)
   │
   ▼ (Foundational checkpoint)
   │
   ├── Phase 3 (US1 P1, MVP): T019 → T020, T021 → T022
   │
   ├── Phase 4 (US2 P2): T023 → T024, T025 → T026
   │   (T023 can start once T019 lands kpi.json shape; parallel with US1 tests)
   │
   └── Phase 5 (US3 P3): T027
       (Can be drafted in parallel with US1/US2 once plan.md clarifies
        the cross-command references.)
   │
   ▼ (All user stories complete)
   │
Phase 6 (Polish: T028 → T029, T030; T031 [P], T032 [P]; T033 after T027)
```

### Story-level dependency summary

- **US1 (P1, MVP)** depends only on Phase 1 + 2. Independently deliverable.
- **US2 (P2)** depends on Phase 1 + 2 + the `kpi.json` shape from US1's T019 (the `rollup.py` module consumes files `tally.py` produces). In practice, T023 (rollup impl) can start as soon as T019's `kpi.json` format is committed; US1 and US2 tests can run in parallel.
- **US3 (P3)** depends on Phase 1's directory creation (T001) and on the CLI contract shapes established by US1/US2 (the workflow doc references `peer-session tally` and `peer-session rollup`). Can be drafted early and polished once US1/US2 behavior is finalized.

---

## Parallel Execution Opportunities

Within each phase, tasks marked `[P]` are parallelizable because they touch independent files with no cross-dependencies.

- **Phase 2 Template additions**: T003, T004, T005, T006 — four operators can edit four independent files simultaneously.
- **Phase 2 Fixtures**: T011, T012, T013, T014, T015, T016, T017 — each creates an independent fixture directory; run concurrently.
- **Phase 2 Foundational tests**: T009 and T010 depend only on their respective modules (T007, T008) and not on each other.
- **Phase 3 and Phase 4**: once T019 lands, T023 can start in parallel with T021 (US1 tests).
- **Phase 6 Polish**: T031 (ACTIVE-SLICES row) and T032 (PR description) are parallelizable and touch different files.

---

## Implementation Strategy

**MVP scope** — US1 alone. Ship `peer-session tally` first. It produces valuable per-session `kpi.json` artifacts even before any cross-session rollup exists. Operators can use it immediately after each session close to see intervention load, drift verdict, and per-session-clear breakdown. This matches the spec 007 extensibility pattern of landing incremental CLI subcommands.

**Incremental delivery**:

1. **Increment 1 (US1 MVP)**: Ship `peer-session tally` end-to-end (T001–T022 + partial T028/T029). Operators can start tallying closed sessions immediately. Deliverable as its own PR if Phase 4 work is delayed.
2. **Increment 2 (US2)**: Ship `peer-session rollup` (T023–T026). Operators can now produce draft POC-exit artifacts.
3. **Increment 3 (US3)**: Ship `observations/kpi-rollup/WORKFLOW.md` (T027). Operators can complete the human-judgment path.
4. **Finalize**: full test suite + manual smoke + polish + PR (T028–T032).

**Current session plan**: this slice ships all three increments in a single PR because the commands are tightly coupled (rollup consumes tally's output, and the workflow references both). The MVP-first ordering survives as the task-execution order, not as separate PRs.

**Pitfalls to avoid** (from user memory):

- **"A partial solution is not done"** — all six edge cases from the spec MUST have explicit test coverage before declaring done; don't ship with one or two untested.
- **"Test-driven quality validation — tests must verify real behavior"** — fixtures MUST be real filesystem bundles, not dict mocks. Do not shortcut fixtures into in-memory dicts "because it's faster" — the IO path is where bugs live.
- **"Interactive CLIs require manual testing"** — unit tests are necessary but not sufficient; T029's 11-item manual smoke-test is mandatory, not optional polish.
- **"Framework primitives over reimplementation"** — use `argparse` subparsers (already in `cli.py`) rather than rolling a bespoke dispatch. Use `hashlib.sha256` rather than a custom hash. Use `os.symlink` rather than a pointer-file workaround.
