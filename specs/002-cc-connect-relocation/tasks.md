# Tasks: cc-connect Relocation

**Input**: Design documents from `/specs/002-cc-connect-relocation/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No new test files are required for this feature. Verification is
done by running the existing `cc-connect` build/test surfaces plus root-doc
traceability checks.

**Organization**: Tasks are grouped by user story so each outcome can be
implemented and verified independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Freeze the import inputs and destination conventions before moving
repo history.

- [ ] T001 Capture the source fork commit and chosen import method in `specs/002-cc-connect-relocation/research.md`
- [ ] T002 [P] Add the final verification/handoff checklist scaffold to `specs/002-cc-connect-relocation/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Perform the contained import and align the active guidance surface.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Import the current `mentatzoe/cc-connect` fork history into `cc-connect/`
- [ ] T004 [P] Update root discovery guidance to point at `cc-connect/` in `README.md`
- [ ] T005 [P] Update collaborator/runtime guidance to point at `cc-connect/` in `CLAUDE.md`
- [ ] T006 [P] Update implementation-surface references to `cc-connect/` in `ROADMAP.md`
- [ ] T007 Add the provenance and boundary note in `cc-connect/README.peer-coordination.md`

**Checkpoint**: `cc-connect/` exists as a contained workspace and active docs no
longer depend on a standalone local clone as the primary implementation surface

---

## Phase 3: User Story 1 - Start transport work from one place (Priority: P1) 🎯 MVP

**Goal**: A collaborator can enter through this repo and begin Phase 1 transport
work without relying on an external checkout.

**Independent Test**: Starting from repo-root docs alone, a collaborator can
find `cc-connect/`, identify the relevant transport surfaces, and build the main
entrypoint.

- [ ] T008 [US1] Verify the required Phase 1 transport surfaces exist in `cc-connect/agent/`, `cc-connect/platform/discord/`, and `cc-connect/cmd/cc-connect/`
- [ ] T009 [US1] Remove or rewrite any remaining active standalone-clone instructions in `README.md`, `CLAUDE.md`, and `ROADMAP.md`
- [ ] T010 [US1] Run `go build ./cmd/cc-connect` from `cc-connect/cmd/cc-connect/` and fix any relocation fallout in `cc-connect/`

**Checkpoint**: User Story 1 is complete when the contained workspace is
discoverable from root docs and the primary `cc-connect` entrypoint builds.

---

## Phase 4: User Story 2 - Review transport work in context (Priority: P2)

**Goal**: A reviewer can audit the contained workspace with legible provenance
and a durable handoff trail.

**Independent Test**: Starting from the spec/review trail, a reviewer can trace
into `cc-connect/`, understand where it came from, and verify the relevant
transport checks.

- [ ] T011 [US2] Finalize source fork / upstream / maintenance-boundary wording in `cc-connect/README.peer-coordination.md`
- [ ] T012 [US2] Record the canonical re-entry path and implementation audit path in `specs/002-cc-connect-relocation/quickstart.md`
- [ ] T013 [US2] Run targeted checks in `cc-connect/platform/discord/`, `cc-connect/agent/claudecode/`, `cc-connect/agent/codex/`, and `cc-connect/agent/gemini/`

**Checkpoint**: User Story 2 is complete when provenance is explicit and the
POC-relevant transport surfaces have been verified from the contained workspace.

---

## Phase 5: User Story 3 - Preserve repo boundaries after relocation (Priority: P3)

**Goal**: The move improves containment without blurring policy and
implementation.

**Independent Test**: A maintainer can inspect the active docs and see that
`cc-connect/` is implementation-only while the root artifacts remain
authoritative for governance/design.

- [ ] T014 [US3] Add or tighten implementation-not-policy wording in `README.md` and `cc-connect/README.peer-coordination.md`
- [ ] T015 [US3] Audit active docs for remaining governance/transport ambiguity in `AGENTS.md`, `README.md`, `CLAUDE.md`, `ROADMAP.md`, and `specs/002-cc-connect-relocation/spec.md`
- [ ] T016 [US3] Update `specs/002-cc-connect-relocation/plan.md` and `specs/002-cc-connect-relocation/research.md` if implementation changed the chosen mechanics or boundary assumptions

**Checkpoint**: User Story 3 is complete when the active repo surface makes the
boundary legible without requiring operator clarification.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency and audit readiness

- [ ] T017 [P] Re-run root-doc traceability checks across `AGENTS.md`, `README.md`, `CLAUDE.md`, and `ROADMAP.md`
- [ ] T018 [P] Refresh the final verification/handoff notes in `specs/002-cc-connect-relocation/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and benefits from User Story 1 build verification
- **User Story 3 (Phase 5)**: Depends on Foundational completion and should run after the main provenance/doc updates land
- **Polish (Phase 6)**: Depends on all selected user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start as soon as the import and active-doc updates are in place
- **User Story 2 (P2)**: Depends on the contained workspace existing; otherwise independent of User Story 3
- **User Story 3 (P3)**: Depends on the contained workspace and provenance note existing so the boundary can be audited accurately

### Parallel Opportunities

- `T004`, `T005`, and `T006` can run in parallel after the import target is known
- `T017` and `T018` can run in parallel during the final polish pass

---

## Parallel Example: Foundational Phase

```bash
Task: "Update root discovery guidance to point at cc-connect/ in README.md"
Task: "Update collaborator/runtime guidance to point at cc-connect/ in CLAUDE.md"
Task: "Update implementation-surface references to cc-connect/ in ROADMAP.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate that the contained workspace is discoverable and builds

### Incremental Delivery

1. Import `cc-connect/` and update active docs
2. Prove discovery/buildability (US1)
3. Harden provenance and audit trail (US2)
4. Audit and tighten boundary language (US3)
5. Finish with cross-cutting traceability cleanup

### Parallel Team Strategy

With multiple contributors available after the import lands:

1. One contributor updates root guidance (`README.md`, `CLAUDE.md`, `ROADMAP.md`)
2. One contributor finalizes provenance/boundary notes in `cc-connect/README.peer-coordination.md`
3. One contributor runs build/test verification in the contained workspace

---

## Notes

- This task list assumes the outcome-level decision is already settled: the full
  `cc-connect` repo moves under this repository.
- The exact import command sequence is implementation detail; the task list
  cares about the durable outputs and validation.
- The canonical coordination index for this slice remains `ROADMAP.md` ->
  discussion `#41` -> discussion `#42` -> commit history.
