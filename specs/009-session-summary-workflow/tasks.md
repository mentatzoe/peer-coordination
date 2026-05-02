---

description: "Task list for session-summary-workflow feature implementation"
---

# Tasks: Session-Summary Workflow

**Input**: Design documents from `/specs/009-session-summary-workflow/`
**Prerequisites**: spec.md (with clarify resolutions), plan.md, research.md, data-model.md, contracts/workflow-contracts.md, quickstart.md (all landed)

**Tests**: No test tasks — this slice produces procedural documentation + runtime-accessible workflow artifacts, not code. Validation is by inspection, cross-slice consistency checks, and Phase 3 session trial (SC-001 / SC-002 / SC-003 are operational criteria, not test-suite).

**Organization**: Tasks are grouped by user story from spec.md (US1 single-author + agent-drafted P1 MVP, US2 drift-audit citation discipline P1, US3 follow-up-commit lifecycle — revision + peer-audit — P2). Each user story phase is independently deliverable; US1 is the MVP atom.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This slice has **no source code**. Paths refer to:

- **Specs**: `specs/009-session-summary-workflow/` (already landed for this slice)
- **Runtime-facing evaluation artifacts**: `observations/sessions/` — where auditors actually read the procedure, parallel to how `observations/drift-audits/WORKFLOW.md` (spec 008) lives at runtime rather than buried in `specs/008-*`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify the prerequisite spec artifacts are in place so downstream tasks can reference them without guessing.

- [X] T001 Verify `specs/009-session-summary-workflow/` contains spec.md, plan.md, research.md, data-model.md, contracts/workflow-contracts.md, quickstart.md, and checklists/requirements.md; confirm all committed on branch `009-session-summary-workflow`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the runtime-accessible scaffolding that all three user story phases need. Every user-story phase below authors or extends these files, so they must exist first.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Create `observations/sessions/SUMMARY-WORKFLOW.md` skeleton at runtime location — frontmatter (version, scope, spec cross-ref), section stubs for Paths A/B/C/D to be filled by US1/US2/US3, common prerequisite list per C1, halt-condition placeholder, post-commit sanity-check placeholder, and a "Cross-references" block linking to `specs/009-session-summary-workflow/spec.md`, `specs/009-session-summary-workflow/quickstart.md`, `contracts/workflow-contracts.md`, `observations/drift-audits/WORKFLOW.md` (spec 008), and `observations/sessions/README.md` (bundle-level README)
- [X] T003 [P] Create `observations/sessions/SUMMARY-TAXONOMY.md` documenting the amend-commit token vocabulary per research.md R1: the standard `session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>` format, the four taxonomy tokens (absent / `[peer-audited by <id>]` / `revision: <reason>` / `revision: drift-refresh, supersedes <old-drift-short-sha>`), combined-token examples, grep recipes per C7, and a pointer to spec 001 FR-014's bundle-amend convention + spec 008's COMMIT-TAXONOMY.md as the prior-art pattern being reused
- [X] T004 [P] Update `observations/sessions/_template/summary.md` to reflect the FR-010 hybrid inverted-pyramid shape — replace any prior template content with the four-section skeleton (`## Seed`, `## Verdicts`, `## Drift`, `## What happened`) including `[FILL IN]` placeholders that show the R2 grep-stable verdict-line format and a placeholder drift citation; include an operator comment at the top referencing `observations/sessions/SUMMARY-WORKFLOW.md` for the full procedure
- [X] T005 Update `observations/sessions/README.md` — add a "Summary authoring" subsection linking to the new `SUMMARY-WORKFLOW.md` and `SUMMARY-TAXONOMY.md`, plus a one-line note that the workflow is specified in `specs/009-session-summary-workflow/` and that the template at `_template/summary.md` now reflects the hybrid inverted-pyramid shape

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Operator produces a committed `summary.md` for a closed session (Priority: P1) 🎯 MVP

**Goal**: Deliver the minimum workflow atom so an operator can produce a `summary.md` for any closed session bundle — via either single-author (Path A) or agent-drafted + operator-ratified (Path B) per the clarify Q1 tiered decision — and land it via a conforming amend commit.

**Independent Test**: given a closed session bundle (transcript + meta + interventions + drift-audit.json committed), follow `observations/sessions/SUMMARY-WORKFLOW.md` Path A OR Path B and verify (a) `summary.md` lands at `observations/sessions/<session-id>/summary.md` via a session-bundle amend commit, (b) the file contains the four required sections in inverted-pyramid order, (c) three verdict lines appear in the R2 grep-stable format, (d) the commit body carries the `Mode:` line, and (e) the amend-commit subject conforms to the C4 format with `@ <drift-audit-short-sha>`.

### Implementation for User Story 1

- [X] T006 [US1] Author Path A (single-author procedure) in `observations/sessions/SUMMARY-WORKFLOW.md` — step-by-step covering: drift-audit-version pinning, composing the four-section summary with the R2 grep-stable verdict-line format, committing as session-bundle amend per C4 with no taxonomy token + `Mode: single-author` commit body. Draw from `specs/009-session-summary-workflow/quickstart.md` Path A but trim spec-facing framing so operators can use the runtime doc directly without the spec-level context. Implements FR-001, FR-002, FR-003, FR-005, FR-006, FR-007, FR-009, FR-010, FR-013, FR-014 (manual-only v1), FR-017 (verdict-line format).
- [X] T007 [US1] Author Path B (agent-drafted + operator-ratified procedure) in `observations/sessions/SUMMARY-WORKFLOW.md` — cover: drafter produces summary (or scratch `summary.draft.md`); operator reviews, edits, writes verdicts themselves per FR-005; operator commits with `Mode: agent-drafted, drafted-by: <id>, ratified-by: <id>` body. Include explicit guidance that scratch drafts MUST be removed before commit (no `summary.draft.md` in the bundle). Implements FR-004 tiered author discipline, FR-005, C5 two-author lifecycle.
- [X] T008 [US1] Author "Halt conditions" section in `observations/sessions/SUMMARY-WORKFLOW.md` — enumerate the C1 pre-conditions (bundle presence, `meta.json` fields, `interventions.json` presence, `drift-audit.json` committed, working tree clean) and what to do when each fails, referencing FR-002 + FR-018 for non-silent-failure discipline. Mirrors the spec 008 WORKFLOW.md "Halt conditions" section structure.
- [X] T009 [US1] Author "Post-commit sanity checks" section in `observations/sessions/SUMMARY-WORKFLOW.md` — the six-check bash block from quickstart.md (four required sections present in order, three verdict lines in R2 format, drift citation present, valid commit subject, `Mode:` body line present, drift-audit short SHA resolves). Position as "run after every committed summary (Path A or B)." Explicitly state that sanity-check failures are fixed via Path C revision — NEVER `git commit --amend` per spec 001 FR-014 + C6.
- [X] T010 [US1] Create `observations/sessions/CHANGELOG.md` with a 2026-04-21 seed entry recording that summary-workflow v1 (Paths A + B) is now available, with a link to `SUMMARY-WORKFLOW.md` and the spec 009 cross-reference. Mirrors the `observations/drift-audits/CHANGELOG.md` pattern established by spec 005 so both Phase 2 runtime directories have parallel structure.
- [X] T010b [US1] Document the **FR-015 LLM-assisted authoring entry criteria** in a dedicated section of `observations/sessions/SUMMARY-WORKFLOW.md` — mirrors spec 008's LLM-judge cross-reviewer block. Short section stating: LLM-assisted summary authoring is a deferred follow-on slice; entry criteria are (a) ≥2 counted sessions have landed with manual summaries (Path A or Path B), (b) operator has defined an LLM prompt template suitable for the hybrid inverted-pyramid structure + R2 verdict-line format, (c) manual operator ratification remains the gate. This slice does NOT operationalize the automation.
- [X] T010c [US1] Add a **Downstream consumption** section to `observations/sessions/SUMMARY-WORKFLOW.md` (mirrors spec 008 WORKFLOW.md's Downstream consumption pointer per FR-017 + C8) — one short section directing KPI rollup + H1/H2 reviewers to read verdict lines via the R2 grep recipe and to cite `drift-audit.json.verdict` from the Drift section rather than re-deriving; includes the grep recipe `grep -E '^- \*\*H[12] '` as a quickstart reference.

**Checkpoint**: US1 is fully functional — an operator can produce and commit a single-author OR agent-drafted summary end-to-end using only `SUMMARY-WORKFLOW.md` + `SUMMARY-TAXONOMY.md` + the updated template. This is the shippable Phase 2 evaluation-surface MVP for summaries.

---

## Phase 4: User Story 2 - Summary cites drift-audit, does not re-derive drift findings (Priority: P1)

**Goal**: Enforce the drift-citation discipline at the summary-authoring boundary — the Drift section of every committed summary cites `drift-audit.json.verdict` verbatim and references specific load-bearing findings, without re-deriving findings from transcript.

**Independent Test**: given a bundle whose `drift-audit.json.verdict` is `load_bearing_drift` with 2 specific findings, follow the Drift-section guidance in `observations/sessions/SUMMARY-WORKFLOW.md` and verify the authored summary (a) names the verdict verbatim, (b) references the findings by `turn_ref` or `category`, (c) does not introduce any drift category absent from `drift-audit.json.findings[]`, and (d) cites the drift-audit short SHA matching the amend-commit subject.

### Implementation for User Story 2

- [X] T011 [US2] Author the "Drift section guidance" subsection in `observations/sessions/SUMMARY-WORKFLOW.md` (shared across Path A + Path B) — explain FR-008 citation discipline with a concrete worked example (e.g. `drift-audit.json.verdict: minor_drift` with one `warn`-severity finding → example Drift section text citing verdict verbatim + referencing the finding by `turn_ref`). Explicitly state: if the operator disagrees with the committed `drift-audit.json`, they re-audit via spec 008 Path C (the summary never carries a disagreement — it cites whatever the current drift-audit says). Implements FR-008, C2, C8 consumer discipline at the authoring boundary.
- [X] T012 [US2] Add a "Drift-audit version pinning" reference row to `observations/sessions/SUMMARY-TAXONOMY.md` — document the `@ <drift-audit-short-sha>` convention in the commit subject, the grep pattern for finding which summaries were authored against a specific drift-audit SHA (`git log --grep='@ <short-sha>'`), and how re-audit triggers the `revision: drift-refresh, supersedes <old-short-sha>` taxonomy token. Cross-references E3 + E6 in data-model.md.

**Checkpoint**: US1 + US2 both work — summaries can be authored end-to-end with drift-citation discipline enforced at the authoring surface.

---

## Phase 5: User Story 3 - Summary revision + peer-audit preserve bundle history (Priority: P2)

**Goal**: Deliver the follow-up-commit lifecycle — both revision (typo, late-arriving verdicts, drift-refresh) and peer-audit (optional post-commit review with `[peer-audited by <id>]` token) — without rewriting git history.

**Independent Test**: commit an initial `summary.md`, then (a) revise via follow-up commit per `observations/sessions/SUMMARY-WORKFLOW.md` Path C and verify the prior version is retrievable via `git show <prior-commit>:...`, (b) add a peer-audit follow-up commit per Path D and verify `git log --all --grep='peer-audited'` returns the ledger entry, (c) confirm no `git commit --amend` was used on any prior summary commit.

### Implementation for User Story 3

- [X] T013 [US3] Author Path C (revision procedure) in `observations/sessions/SUMMARY-WORKFLOW.md` — cover: identifying the reason (typo / late H1 or H2 verdict / drift-refresh), editing `summary.md`, committing as a follow-up amend with the `revision: <reason>` taxonomy token (or `revision: drift-refresh, supersedes <old-drift-short-sha>` for the upstream-triggered case), and verifying prior-version preservation via `git show`. Explicitly forbid `git commit --amend` with a reference to spec 001 FR-014 + PR #66's I1 lesson. Implements FR-011, FR-012, C6 append-only.
- [X] T014 [US3] Author Path D (peer-audit procedure) in `observations/sessions/SUMMARY-WORKFLOW.md` — cover: reading the committed summary, deciding audit outcome (no material findings / wording suggestions / material disagreement), committing the peer-audit event via follow-up amend with `[peer-audited by <id>]` token. For audits with no rendered-prose changes, append a non-rendered HTML audit marker so the commit still touches `summary.md` and appears in the path-limited ledger; for audits that incorporate wording suggestions, use the combined form (`[peer-audited by <id>] revision: <reason>`). Document the ledger grep recipe per C7. Implements FR-018, E5, C7 peer-audit ledger.
- [X] T015 [US3] Add combined-token examples for peer-audit + revision to `observations/sessions/SUMMARY-TAXONOMY.md` — `[peer-audited by <id>] revision: wording-cleanup` and `[peer-audited by <id>] revision: H2-verdict-resolved`. Verify the token-ordering convention (bracket first, revision second) is consistent with spec 008's COMMIT-TAXONOMY.md combined-token examples.

**Checkpoint**: All three user stories + the full four-path workflow (single-author / agent-drafted / revision / peer-audit) are independently functional. US1 ships MVP on its own; US2 + US3 layer additional discipline on top.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Consistency checks and PR-readiness per `docs/ways-of-working/pull-requests.md`.

- [X] T016 Run `/speckit-analyze` on `specs/009-session-summary-workflow/` and address any blocking findings; required before PR per `docs/ways-of-working/pull-requests.md` artifact-consistency gate
- [X] T017 [P] Cross-slice consistency check — diff the amend-commit format in `contracts/workflow-contracts.md` C4 against spec 001 FR-014 to confirm no accidental redefinition of the bundle-amend-commit base convention; also confirm no instruction anywhere in `observations/sessions/SUMMARY-WORKFLOW.md` suggests `git commit --amend` (lesson from spec 008 PR #66). If drift is found, log in analyze.md rather than silently patching.
- [X] T018 [P] Cross-slice consistency check — confirm the summary's drift-citation references in `observations/sessions/SUMMARY-WORKFLOW.md` match spec 005 data-model.md's `drift-audit.json` schema (verdict enum values, finding fields used) and spec 008's commit-taxonomy pattern (bracket-token convention, `@ <short-sha>` anchor). If drift, log in analyze.md.
- [ ] T019 Open PR for branch `009-session-summary-workflow` per `docs/ways-of-working/pull-requests.md` once analyze completes; link to discussion #41 for staffing context and flag the PR body with the cross-review ask (agent-drafted mode's `Mode:` body convention, hybrid inverted-pyramid verdict-line format, peer-audit ledger token syntax — all new patterns this slice introduces that merit cross-agent review).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 verifies prerequisites — no dependencies, can run immediately
- **Foundational (Phase 2)**: T002/T003/T004 are parallelizable (different files); T005 depends on T002 + T003 being present (references them); BLOCKS all user stories
- **User Story 1 (Phase 3)**: depends on Phase 2 (T002 provides SUMMARY-WORKFLOW.md skeleton, T003 provides SUMMARY-TAXONOMY.md, T004 provides updated template), no dependencies on US2 or US3
- **User Story 2 (Phase 4)**: depends on Phase 2 + T006 (Path A established in US1 provides the Drift-section-shaped framework T011 extends); T012 depends on T003 (SUMMARY-TAXONOMY.md skeleton present)
- **User Story 3 (Phase 5)**: depends on Phase 2 + T006 (Path A + its amend-commit primitive is what Path C/D build follow-up commits upon); T013/T014 edit shared `SUMMARY-WORKFLOW.md`, serialize file edits between T013 → T014
- **Polish (Phase N)**: T016 depends on all user stories being complete; T017/T018 can run in parallel; T019 depends on T016 (analyze must land first per pull-requests.md gate)

### User Story Dependencies

- **User Story 1 (P1 MVP)**: No dependencies on other stories. Deliverable on its own as the MVP.
- **User Story 2 (P1)**: Extends Path A/B's Drift section with citation-discipline guidance. T011 edits the same file as T006/T007, so serialize file edits.
- **User Story 3 (P2)**: Extends SUMMARY-WORKFLOW.md with Path C + Path D. Shares SUMMARY-WORKFLOW.md with US1/US2, so serialize file edits.

### Within Each User Story

- Foundational files (SUMMARY-WORKFLOW.md skeleton, SUMMARY-TAXONOMY.md, template update) must exist before story-specific sections are authored
- Story sections added in user-story-priority order (US1 → US2 → US3)

### Parallel Opportunities

- T002 + T003 + T004 (Foundational): independent file creations, full parallel
- T017 + T018 (Polish): independent cross-slice consistency checks, full parallel
- No intra-story parallelism: within each user story phase, tasks edit the shared `SUMMARY-WORKFLOW.md` file and serialize

---

## Parallel Example: Phase 2 (Foundational)

```text
# T002, T003, T004 all parallelizable — different files, no dependencies on each other:
Task T002: "Create observations/sessions/SUMMARY-WORKFLOW.md skeleton with frontmatter + section stubs + cross-references"
Task T003: "Create observations/sessions/SUMMARY-TAXONOMY.md with amend-commit token vocabulary"
Task T004: "Update observations/sessions/_template/summary.md to the hybrid inverted-pyramid shape"

# T005 depends on T002 + T003 (references them), so serializes after.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (T001)
2. Complete Phase 2 (T002–T005 — foundation ready)
3. Complete Phase 3 / US1 (T006–T010 — single-author + agent-drafted paths shippable)
4. **STOP and VALIDATE**: walk Path A and Path B mentally against a hypothetical closed bundle to confirm the procedure is self-sufficient
5. Ship US1 as a Phase 2 evaluation-surface milestone. Phase 3 POC sessions can begin producing summaries (single-author OR agent-drafted) immediately.

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → test independently → **MVP ships, summary lifecycle covers initial commit only**
3. Add US2 → test independently → drift-citation discipline enforced; prevents summary↔drift-audit divergence
4. Add US3 → test independently → revision + peer-audit paths live; counted-session lifecycle complete
5. Polish → analyze + cross-slice checks + PR
6. Each story adds value without breaking previous stories

### Solo Operator Strategy (POC-realistic)

With one operator doing all authoring:

1. T001 → T002/T003/T004 (parallel file creation) → T005
2. T006 → T007 → T008 → T009 → T010 (US1 — single `SUMMARY-WORKFLOW.md` edit session)
3. T011 → T012 (US2)
4. T013 → T014 → T015 (US3)
5. T016 (analyze) → T017/T018 (parallel checks) → T019 (PR)

Expected total effort: ≤1 operator-day of authoring (most content distilled from the already-landed `quickstart.md` into runtime-facing form — mirrors spec 008's effort profile).

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and shippable
- No test tasks — this slice produces procedural documentation + commit-format conventions, not code; Phase 3 session trial is the real validation surface
- Commit after each logical group of tasks (not each individual task) to keep history readable
- Stop at any checkpoint to validate the story independently
- **FR → contract → task traceability** (for Codex cross-review): Phase 2 T002 + T005 serve all FRs via scaffolding; T006 covers FR-001/002/003/005/006/007/009/010/013/014/017 + C1/C2/C4; T007 covers FR-004/005 + C5; T008 covers FR-002/018 + C1; T009 covers C2; T011 covers FR-008 + C2/C8; T012 covers E3/E6 cross-refs + C4; T013 covers FR-011/012 + C6; T014 covers FR-018 + C7 + E5; T017/T018 re-verify the whole chain against spec 001/005/008.
- Avoid: accidentally modifying `observations/drift-audits/**` (owned by spec 005/008; this slice only cross-references)
- Avoid: modifying spec 001's session-bundle contract (this slice consumes it; changes go in spec 001's own slice)
- Avoid: committing source code or CLI tooling in this slice (out of scope per spec FR-014 + plan Structure Decision)
