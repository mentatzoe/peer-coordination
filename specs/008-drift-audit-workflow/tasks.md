---

description: "Task list for drift-audit-workflow feature implementation"
---

# Tasks: Drift-Audit Workflow

**Input**: Design documents from `/specs/008-drift-audit-workflow/`
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/workflow-contracts.md, quickstart.md (all landed)

**Tests**: No test tasks — this slice produces procedural documentation + runtime-accessible workflow artifacts, not code. Validation is by inspection, cross-slice consistency checks, and Phase 3 session trial (SC-001 / SC-002 are operational, not test-suite, criteria).

**Organization**: Tasks are grouped by user story from spec.md (US1 single-auditor P1, US2 two-auditor reconciliation P1, US3 re-audit P2). Each user story phase is independently deliverable; US1 is the MVP atom.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This slice has **no source code**. Paths refer to:

- **Specs**: `specs/008-drift-audit-workflow/` (already landed for this slice)
- **Runtime-facing evaluation artifacts**: `observations/drift-audits/` — where auditors actually read the procedure, parallel to how `observations/drift-audits/RUBRIC.md` (spec 005) lives at runtime rather than buried in `specs/005-*`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify the prerequisite spec artifacts are in place so downstream tasks can reference them without guessing.

- [X] T001 Verify `specs/008-drift-audit-workflow/` contains spec.md, plan.md, research.md, data-model.md, contracts/workflow-contracts.md, quickstart.md, and checklists/requirements.md; confirm all committed on branch `008-drift-audit-workflow`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the runtime-accessible scaffolding that all three user story phases need. Every user-story phase below authors or extends these files, so they must exist first.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Create `observations/drift-audits/WORKFLOW.md` skeleton at runtime location — frontmatter (version, scope, spec cross-ref), section stubs for Paths A/B/C to be filled by US1/US2/US3, prerequisite list, halt-condition placeholder, and a "Cross-references" block linking to `specs/008-drift-audit-workflow/spec.md`, `specs/008-drift-audit-workflow/quickstart.md`, `contracts/workflow-contracts.md`, and `observations/drift-audits/RUBRIC.md`
- [X] T003 [P] Create `observations/drift-audits/COMMIT-TAXONOMY.md` documenting the amend-commit token vocabulary from research.md R1 + R6: the standard `session bundle amend: <id> — drift-audit [ <token>] @ <short-sha>` format, the four taxonomy tokens (absent / `[arbitrated]` / `two-auditor-upgrade` / `re-run, supersedes <old-sha>`), grep examples, and a pointer to spec 001 FR-014's bundle-amend convention
- [X] T004 Update `observations/drift-audits/README.md` — add a "Workflow" subsection near the top linking to the new `WORKFLOW.md` and `COMMIT-TAXONOMY.md`, plus a one-line note that the workflow is specified in `specs/008-drift-audit-workflow/`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Single-auditor audit on a closed session bundle (Priority: P1) 🎯 MVP

**Goal**: Deliver the minimum workflow atom so an operator can run a drift audit on a closed session bundle and land a committed `drift-audit.json` inside the bundle.

**Independent Test**: from a closed session bundle (transcript + meta + interventions + pinned_rules_ref), follow `observations/drift-audits/WORKFLOW.md` Path A and verify a valid `drift-audit.json` lands in `observations/sessions/<session-id>/drift-audit.json` via a session-bundle amend commit conforming to C4 (no taxonomy token for single-auditor within-tolerance).

### Implementation for User Story 1

- [X] T005 [US1] Author Path A (single-auditor procedure) in `observations/drift-audits/WORKFLOW.md` — step-by-step covering: rubric-version pinning, running RUBRIC.md §4 against the bundle, authoring `drift-audit.json` against spec 005's schema, committing as session-bundle amend per C4 with no taxonomy token. Draw from `specs/008-drift-audit-workflow/quickstart.md` Path A but trim spec-facing framing so auditors can use it directly without the spec-level context. Also include a one-paragraph note on **idempotency** per FR-010: re-running the workflow on the same inputs produces byte-identical `drift-audit.json` modulo the `audited_at` timestamp, inherited from spec 005's canonical-form serialization per `research.md` R3 — no new normalization rule needed here.
- [X] T006 [US1] Author "Halt conditions" section in `observations/drift-audits/WORKFLOW.md` — enumerate the C1 pre-conditions (bundle presence, `meta.json` fields, `interventions.json` presence, RUBRIC.md committed SHA) and what to do when each fails, referencing FR-018 for non-silent-failure discipline.
- [X] T007 [US1] Author "Post-commit sanity checks" section in `observations/drift-audits/WORKFLOW.md` — the 4-command block from quickstart.md (jq validity, rubric_version resolves, load_bearing_findings_count matches, commit discoverable via `git log -1`). Position as "run after every committed audit."
- [X] T008 [US1] Append entry to `observations/drift-audits/CHANGELOG.md` recording that workflow v1 (single-auditor path) is available, with a link to `WORKFLOW.md` and the spec 008 cross-reference.

**Checkpoint**: At this point, User Story 1 is fully functional — a single operator can run the workflow end-to-end on a closed bundle and produce a committed audit. This is a shippable Phase 2 artifact.

---

## Phase 4: User Story 2 - Two-auditor reconciliation against spec 005 FR-016 tolerance (Priority: P1)

**Goal**: Enable counted-session two-auditor reconciliation so sessions can carry independent-review evidence per constitution v1.5.0 Principle IV.

**Independent Test**: given a bundle with two draft audits from independent auditors against the same pinned rubric version, follow `observations/drift-audits/WORKFLOW.md` Path B and verify (a) within-tolerance drafts produce a reconciled `drift-audit.json` committed with no taxonomy token citing both auditor identities, and (b) above-tolerance drafts trigger operator arbitration and commit with the `[arbitrated]` token discoverable via `git log --grep`.

### Implementation for User Story 2

- [X] T009 [US2] Author Path B (two-auditor reconciliation procedure) in `observations/drift-audits/WORKFLOW.md` — cover: shared rubric-version pinning, independent draft production (primary + cross-reviewer), tolerance check against spec 005 FR-016, within-tolerance merge path (Step 5a in quickstart), above-tolerance operator-arbitration path (Step 5b), commit format for each branch per C5.
- [X] T010 [US2] Document the LLM-judge-as-cross-reviewer assumption in `observations/drift-audits/WORKFLOW.md` — one short section noting: in POC staffing (per spec 008 Assumptions), two-auditor mode commonly means one human operator + one LLM judge running RUBRIC.md §7's prompt template; independence is operator-attested per FR-005; enabled from Phase 3 session 3+ per spec 005 §7.
- [X] T011 [US2] Add an "Arbitration ledger" reference row in `observations/drift-audits/COMMIT-TAXONOMY.md` — example: `git log --all --grep='\[arbitrated\]' --format='%H %s'` with a one-line note that the ledger is the calibration-signal surface spec 005 §6.3 counts against.

**Checkpoint**: At this point, US1 and US2 both work independently — single-auditor and two-auditor paths each produce correctly-tokenized committed audits.

---

## Phase 5: User Story 3 - Re-audit after rubric evolution or single→two upgrade (Priority: P2)

**Goal**: Allow past session bundles to be re-audited against an evolved rubric, or upgraded from single-auditor to two-auditor, without losing the historical audit trail.

**Independent Test**: given a session bundle with a prior committed `drift-audit.json` pinning rubric version `A`, follow `observations/drift-audits/WORKFLOW.md` Path C with a new rubric version `B` and verify (a) a new `drift-audit.json` replaces the prior, (b) the amend commit carries `re-run, supersedes <A-short>` in the subject, (c) the prior `A`-pinned audit is reconstructible via `git show <prior-commit>:observations/sessions/<id>/drift-audit.json`, and (d) if combined with a mode upgrade, the `two-auditor-upgrade` token also appears.

### Implementation for User Story 3

- [X] T012 [US3] Author Path C (re-audit + upgrade procedure) in `observations/drift-audits/WORKFLOW.md` — cover: identifying the trigger (rubric evolution vs mode upgrade vs both), pinning the new rubric version, running Path A or Path B to produce the new artifact (full replacement, not delta, per C6), commit format with the `re-run, supersedes <old-sha>` and/or `two-auditor-upgrade` tokens, prior-audit retrieval via `git show`.
- [X] T013 [US3] Document the POC-exit rubric-version sweep cross-slice dependency in `observations/drift-audits/WORKFLOW.md` — a short "Triggers" subsection within Path C noting both (a) explicit operator request is always valid, and (b) the POC-exit synthesis slice (not yet specced) produces a sweep artifact identifying stale bundles; this workflow only guarantees the data is available per FR-012 + C6.
- [X] T014 [US3] Add the `re-run, supersedes <old-sha>` and `two-auditor-upgrade` token examples (including the combined case) to `observations/drift-audits/COMMIT-TAXONOMY.md` if T003 left them as placeholders.

**Checkpoint**: All three user stories are now independently functional. Path A is the MVP, Path B extends to counted-session independent review, Path C enables rubric evolution and upgrade without history loss.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Consistency checks and PR-readiness per `docs/ways-of-working/pull-requests.md`.

- [X] T015 Run `/speckit-analyze` on `specs/008-drift-audit-workflow/` and address any blocking findings; required before PR per `docs/ways-of-working/pull-requests.md` artifact-consistency gate
- [X] T016 [P] Cross-slice consistency check — diff the amend-commit format in `contracts/workflow-contracts.md` C4 against spec 001 FR-014 to confirm no accidental redefinition; if drift is found, log in analyze.md rather than silently patching
- [X] T017 [P] Cross-slice consistency check — confirm `drift-audit.json` field usage in this slice matches spec 005's data-model.md (no implicit schema extensions); if drift, log in analyze.md
- [ ] T018 Open PR for branch `008-drift-audit-workflow` per `docs/ways-of-working/pull-requests.md` once analyze completes, linking the governing discussion (TBD — may be opened at PR time if a fresh review thread is desired, or tied to existing discussion #41 staffing)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 verifies prerequisites — no dependencies, can run immediately
- **Foundational (Phase 2)**: T002/T003/T004 create the runtime scaffolding all user stories fill in; BLOCKS all user stories
- **User Story 1 (Phase 3)**: depends on Phase 2 (T002 provides WORKFLOW.md skeleton, T003 provides COMMIT-TAXONOMY.md), no dependencies on US2 or US3
- **User Story 2 (Phase 4)**: depends on Phase 2 + extends WORKFLOW.md authored by US1 (T005 provides Path A structure that Path B parallels); no runtime dependency on US1's output being shipped first, but file-edit ordering matters
- **User Story 3 (Phase 5)**: depends on Phase 2 + parallels Path A/B structure established by US1 and US2
- **Polish (Phase N)**: depends on all desired user stories being complete; T015 analyze is blocking for T018 PR

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories. Deliverable on its own as the MVP.
- **User Story 2 (P1)**: Can be written independently of US1, but T009 edits the same file (`WORKFLOW.md`) as T005. Serialize file edits between US1 and US2 to avoid conflicts.
- **User Story 3 (P2)**: Can be written independently of US1/US2, but T012/T014 edit shared files. Serialize file edits.

### Within Each User Story

- Foundational files (WORKFLOW.md skeleton, COMMIT-TAXONOMY.md) must exist before story-specific sections are authored
- Story sections (Paths A, B, C) are added in user-story-priority order
- CHANGELOG entry lands at end of US1 only (since Paths B and C are extensions of the same v1 workflow, not new versions)

### Parallel Opportunities

- T003 (COMMIT-TAXONOMY.md) can run in parallel with T002 (WORKFLOW.md skeleton) — different files
- T016 and T017 (cross-slice consistency checks) can run in parallel during Polish — different cross-ref surfaces
- No intra-story parallelism: within each user story phase, tasks edit the same `WORKFLOW.md` file so they serialize

---

## Parallel Example: Phase 2 (Foundational)

```text
# T002 and T003 can run as parallel file creations:
Task T002: "Create observations/drift-audits/WORKFLOW.md skeleton with frontmatter + section stubs + cross-references"
Task T003: "Create observations/drift-audits/COMMIT-TAXONOMY.md with amend-commit token vocabulary"

# T004 depends on both T002 and T003 (references them), so it serializes after them.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (T001)
2. Complete Phase 2 (T002–T004 — foundation ready)
3. Complete Phase 3 / US1 (T005–T008 — single-auditor path shippable)
4. **STOP and VALIDATE**: run Path A mentally against a hypothetical closed bundle to confirm the procedure is self-sufficient
5. Ship US1 as a Phase 2 evaluation-surface milestone. Phase 3 POC sessions can begin single-auditor audits immediately.

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → test independently → **MVP ships, counted-session path not yet live**
3. Add US2 → test independently → two-auditor reconciliation live; counted-session eligibility unlocked
4. Add US3 → test independently → re-audit + upgrade live; rubric evolution safe
5. Polish → analyze + PR → merge
6. Each story adds value without breaking previous stories

### Solo Operator Strategy (POC-realistic)

With one operator doing all authoring:

1. T001 → T002/T003 (parallel file creation) → T004
2. T005 → T006 → T007 → T008 (US1)
3. T009 → T010 → T011 (US2)
4. T012 → T013 → T014 (US3)
5. T015 (analyze) → T016/T017 (parallel checks) → T018 (PR)

Expected total effort: ≤1 operator-day of authoring (most content is distillation from already-landed `quickstart.md` into runtime-facing form).

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and shippable
- No test tasks — this slice produces procedural documentation + commit-format conventions, not code; Phase 3 session trial is the real validation surface
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
- Avoid: accidentally modifying `observations/drift-audits/RUBRIC.md` (owned by spec 005; this slice only cross-references it)
- Avoid: accidentally redefining `drift-audit.json` schema fields (owned by spec 005 data-model.md)
- Avoid: committing source code or CLI tooling in this slice (out of scope per spec FR-013 + plan Structure Decision)
