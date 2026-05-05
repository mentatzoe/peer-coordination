# Tasks: Intervention-Tagging Workflow

**Input**: Design documents from `/specs/011-intervention-tagging/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included for the repo-owned CLI implementation because this slice adds executable session-bundle tooling.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Speckit artifacts and active-slice ownership.

- [X] T001 Record active ownership for `011-intervention-tagging` in `ACTIVE-SLICES.md`
- [X] T002 Create `specs/011-intervention-tagging/` spec chain and `.specify/feature.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schema, validation logic, and runtime docs used by all stories.

- [X] T003 [P] Author intervention record schema and workflow contracts in `specs/011-intervention-tagging/data-model.md` and `specs/011-intervention-tagging/contracts/intervention-log-contract.md`
- [X] T004 [P] Author runtime intervention docs in `observations/sessions/INTERVENTIONS-WORKFLOW.md` and `observations/sessions/INTERVENTIONS-TAXONOMY.md`
- [X] T005 [P] Update bundle docs/template schema references in `observations/sessions/README.md` and `observations/sessions/_template/README.md`
- [X] T006 Implement intervention validation/add helpers in `tools/peer_session/interventions.py`
- [X] T007 Wire CLI subcommands in `tools/peer_session/cli.py`

**Checkpoint**: Schema, docs, and CLI primitives are available for story implementation.

---

## Phase 3: User Story 1 - Operator Tags a Closed Session (Priority: P1) MVP

**Goal**: Operator can append valid post-session intervention records.

**Independent Test**: Use a temp bundle with empty `interventions.json`, add a turn-targeted clarification and span-targeted directive redirect, then validate the output.

- [X] T008 [P] [US1] Add unit tests for valid add/validate flows in `tests/peer_session/test_interventions.py`
- [X] T009 [P] [US1] Add CLI tests for `intervention add` and `intervention validate` in `tests/peer_session/test_cli.py`
- [X] T010 [US1] Ensure invalid type, missing reason, duplicate id, and malformed span halt before writes in `tools/peer_session/interventions.py`

**Checkpoint**: US1 works independently through the CLI path.

---

## Phase 4: User Story 2 - Consumers Cite Interventions (Priority: P1)

**Goal**: Downstream artifacts can resolve stable citation keys and compute directive signal without transcript re-derivation.

**Independent Test**: Validate a synthetic log with `iv-001` and `iv-002`; resolve `interventions.json#iv-002`; count directive signal as 1.

- [X] T011 [P] [US2] Add citation helper/tests in `tests/peer_session/test_interventions.py`
- [X] T012 [US2] Document citation key and directive-signal contract in `observations/sessions/INTERVENTIONS-TAXONOMY.md`
- [X] T013 [US2] Add synthetic dry-run bundle under `observations/sessions/_synthetic/011-intervention-tagging-dry-run/`

**Checkpoint**: US2 has executable validation plus committed dry-run evidence.

---

## Phase 5: User Story 3 - History-Preserving Corrections (Priority: P2)

**Goal**: Operators can revise intervention logs via follow-up amend commits and documented taxonomy tokens.

**Independent Test**: Runtime docs provide the revision commit recipe and the quickstart cites git-history retrieval.

- [X] T014 [US3] Document revision tokens and no-`--amend` discipline in `observations/sessions/INTERVENTIONS-WORKFLOW.md`
- [X] T015 [US3] Add revision examples to `specs/011-intervention-tagging/quickstart.md`

**Checkpoint**: US3 is covered by runtime docs and commit taxonomy.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T016 Run the Python test suite for `tests/peer_session`
- [X] T017 Run `/speckit-analyze` equivalent on `specs/011-intervention-tagging/` and record results in `analyze.md`
- [X] T018 Update `ROADMAP.md` to mark intervention tagging landed and clear the open row

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Phase 1; blocks all user stories.
- **US1 and US2 (Phases 3-4)**: depend on Phase 2; may proceed in parallel after helpers/docs exist.
- **US3 (Phase 5)**: depends on Phase 2; can proceed after commit taxonomy is drafted.
- **Polish (Phase 6)**: depends on desired user stories complete.

### Parallel Opportunities

- T003, T004, T005 can run in parallel after directory setup.
- T008 and T009 can run in parallel once helper API shape is known.
- T011 and T012 can run in parallel after citation key is stable.

## Implementation Strategy

1. Deliver schema/docs plus CLI add/validate as the MVP (US1).
2. Add citation and directive-count validation (US2).
3. Document revision discipline (US3).
4. Run tests and analysis before PR.
