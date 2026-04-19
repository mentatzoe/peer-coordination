# Tasks: Session Bundle Init CLI

**Input**: Design documents from `/specs/007-session-bundle-init-cli/`
**Prerequisites**: `spec.md` (required), `plan.md` (required), `research.md`, `data-model.md`, `contracts/init-cli-behavior.md`, `quickstart.md`

**Tests**: Required for this slice. `peer-session init` is a contract-bearing repo-owned CLI that mutates bundle artifacts and pinned-rules provenance; targeted `unittest` coverage is required before implementation is considered stable.

**Organization**: Tasks are grouped by user story so bundle creation, initialized-bundle clarity, and future-extensible CLI behavior remain independently reviewable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: establish the repo-owned CLI surface and local-config touchpoints.

- [ ] T001 Create the repo-owned CLI/package/test scaffolding in `peer-session`, `tools/peer_session/`, and `tests/peer_session/`.
- [ ] T002 Update `.gitignore` for repo-root Python/runtime artifacts and the local defaults file at `observations/sessions/defaults.toml`.
- [ ] T003 Add the committed defaults template at `observations/sessions/defaults.example.toml` and reserve the local-defaults guidance touchpoints in `observations/sessions/README.md`.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: build the shared helpers that every user story depends on before any story-specific workflow can work.

- [ ] T004 Add the argparse-based CLI skeleton for `peer-session init` in `tools/peer_session/cli.py` and wire the repo-root `peer-session` wrapper to it.
- [ ] T005 [P] Implement defaults-file loading and CLI override resolution helpers in `tools/peer_session/defaults.py`.
- [ ] T006 [P] Implement pinned-rules provenance helpers in `tools/peer_session/git_refs.py`.
- [ ] T007 [P] Implement session-id validation, template file-set validation, and bundle-copy primitives in `tools/peer_session/bundle_init.py`.
- [ ] T008 [P] Add shared temp-repo / temp-bundle test helpers in `tests/peer_session/`.

**Checkpoint**: CLI scaffolding, defaults resolution, pinned-rules provenance helpers, and bundle-copy validation all exist; user-story behavior can now be implemented safely.

## Phase 3: User Story 1 — Operator initializes a bundle without hand-copying the template (Priority: P1) 🎯 MVP

**Goal**: create `observations/sessions/<session-id>/` from `_template/` and fill the mechanical metadata the tool owns.

**Independent Test**: run `./peer-session init <session-id>` from the repo root and verify a new bundle directory exists with the full template file set and a mechanically populated `meta.json`.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add library-level init-success tests in `tests/peer_session/test_bundle_init.py` covering bundle creation, copied file set, and mechanical `meta.json` population.
- [ ] T010 [P] [US1] Add CLI invocation tests in `tests/peer_session/test_cli.py` covering `peer-session init <session-id>` success and non-zero failure exit propagation.

### Implementation for User Story 1

- [ ] T011 [US1] Implement the init workflow in `tools/peer_session/bundle_init.py` to copy `_template/`, fill `session_id`, `opened_at`, `substrate`, `channel_id`, and `participants`, and remove `meta.json.transcript_source`.
- [ ] T012 [US1] Wire `peer-session init` argument parsing and command execution through `tools/peer_session/cli.py` and the repo-root `peer-session` wrapper.
- [ ] T013 [US1] Implement clear failure handling for invalid session IDs and pre-existing target bundle directories in `tools/peer_session/bundle_init.py` and `tools/peer_session/cli.py`.

**Checkpoint**: the operator can initialize a new pre-session bundle end-to-end without manually copying `_template/`.

## Phase 4: User Story 2 — Initialized bundle is immediately usable as a clean artifact surface (Priority: P2)

**Goal**: make the initialized bundle low-ambiguity for later humans and agents by applying defaults truthfully and leaving pending content visibly unfinished.

**Independent Test**: inspect a freshly initialized bundle created from defaults + optional overrides and verify that auto-filled values are present, pending values remain visibly pending, and `transcript_source` is absent.

### Tests for User Story 2

- [ ] T014 [P] [US2] Add defaults-overlay and CLI-override precedence tests in `tests/peer_session/test_bundle_init.py`.
- [ ] T015 [P] [US2] Add tests in `tests/peer_session/test_bundle_init.py` covering template required-file validation, pending-field preservation, and omission of `meta.json.transcript_source`.

### Implementation for User Story 2

- [ ] T016 [US2] Implement effective defaults resolution and participant construction in `tools/peer_session/defaults.py` and `tools/peer_session/bundle_init.py`.
- [ ] T017 [US2] Implement required-template-file checks and placeholder-preserving `meta.json` transformation in `tools/peer_session/bundle_init.py`.
- [ ] T018 [US2] Document local defaults setup and initialized-bundle expectations in `observations/sessions/README.md` and `specs/007-session-bundle-init-cli/quickstart.md`.

**Checkpoint**: a fresh bundle clearly shows what the tool filled automatically versus what still needs human/session-time authoring.

## Phase 5: User Story 3 — CLI surface can grow later without changing the bundle contract (Priority: P3)

**Goal**: keep `peer-session` extensible for later artifact-first commands while making pinned-rules provenance truthful in v1.

**Independent Test**: verify that the CLI remains `init`-only in v1, while `pinned_rules_ref` resolves to a commit hash when safe and an inline snapshot when the rules file is dirty or otherwise not faithfully representable by `HEAD`.

### Tests for User Story 3

- [ ] T019 [P] [US3] Add pinned-rules provenance tests in `tests/peer_session/test_bundle_init.py` covering clean commit-hash resolution and dirty-file inline-snapshot fallback.
- [ ] T020 [P] [US3] Add CLI-surface tests in `tests/peer_session/test_cli.py` confirming the v1 command set is `init` only and exposes future-extensible help text cleanly.

### Implementation for User Story 3

- [ ] T021 [US3] Implement truthful `pinned_rules_ref` resolution in `tools/peer_session/git_refs.py` and integrate it into `tools/peer_session/bundle_init.py`.
- [ ] T022 [US3] Keep the v1 CLI surface narrow-but-extensible in `tools/peer_session/cli.py` and `tools/peer_session/__init__.py`.
- [ ] T023 [US3] Document the init-only scope and future artifact-first extension boundary in `specs/007-session-bundle-init-cli/quickstart.md`.

**Checkpoint**: `peer-session` stays repo-owned and extensible, while the initialized bundle records pinned-rules provenance truthfully.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T024 [P] Run the targeted CLI test suite with `python3 -m unittest discover -s tests/peer_session` and record the verification command/results for review.
- [ ] T025 [P] Review the final implementation for contract alignment against `specs/001-session-bundle-skeleton/spec.md` and log any necessary fast-follow separately rather than silently mutating unrelated bundle rules.
- [ ] T026 Add or update `specs/007-session-bundle-init-cli/analyze.md` once tasks and implementation are complete.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup completion and blocks all user stories
- **User Stories (Phases 3–5)**: depend on Foundational completion
- **Polish (Phase 6)**: depends on the desired user stories being complete

### User Story Dependencies

- **US1** starts immediately after Foundational and is the MVP gate for the slice
- **US2** depends on the CLI/package skeleton and init flow from US1
- **US3** depends on the CLI/package skeleton plus bundle metadata work from US1/US2, but should remain independently testable once those prerequisites exist

### Parallel Opportunities

- T005, T006, T007, and T008 can run in parallel after T004
- T009 and T010 can run in parallel
- T014 and T015 can run in parallel
- T019 and T020 can run in parallel
- T024 and T025 can run in parallel once implementation stabilizes

## Implementation Strategy

### MVP First (US1 only)

1. Complete Setup and Foundational tasks
2. Implement and verify `peer-session init` for a successful new-bundle path (US1)
3. Stop and validate that the repo can now create a pre-session bundle without manual `_template/` copying
4. Then add initialized-bundle clarity/defaults behavior (US2) and pinned-rules / future-extension concerns (US3)

### Incremental Delivery

1. Land repo-root CLI/package scaffolding and shared helpers
2. Land US1 end-to-end init flow
3. Land defaults-overlay / pending-field behavior
4. Land pinned-rules provenance truth and future-extension boundary
