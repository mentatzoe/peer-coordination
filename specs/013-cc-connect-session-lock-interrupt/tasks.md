---
description: "Task list for cc-connect session-lock interrupt implementation"
---

# Tasks: cc-connect Session-Lock Interrupt

**Input**: Design documents from `/specs/013-cc-connect-session-lock-interrupt/`  
**Prerequisites**: spec.md, research.md, data-model.md, contracts/interrupt-contract.md, plan.md, quickstart.md

**Tests**: New regression test required for the stuck-lock path; targeted core and Discord tests; full `go test ./...` before PR.

## Phase 1: Setup

- [x] T001 Claim slice `013-cc-connect-session-lock-interrupt` in `ACTIVE-SLICES.md` with branch, worktree, phase, and do-not-touch surfaces.
- [x] T002 Verify upstream issue `mentatzoe/cc-connect#3` has no newer comments changing requirements.
- [x] T003 Read cc-connect local development guidance and project Layer 1 interrupt requirements.

## Phase 2: Root Cause

- [x] T004 Trace message lock path in `cc-connect/core/engine.go` and `cc-connect/core/session.go`.
- [x] T005 Confirm lock lives in `core.Session.busy`; Discord only normalizes controls and gates the visible session surface.
- [x] T006 Identify stuck path: post-`EventResult` waits on `pendingSend` do not observe `state.stopSignal()`.

## Phase 3: Speckit Artifacts

- [x] T007 Create `specs/013-cc-connect-session-lock-interrupt/spec.md`.
- [x] T008 Record clarify decisions in the spec.
- [x] T009 Create `research.md`, `data-model.md`, `contracts/interrupt-contract.md`, `quickstart.md`, and checklist.
- [x] T010 Create `plan.md` and this `tasks.md`.

## Phase 4: Implementation

- [x] T011 Add interruptible pending-send wait helper in `cc-connect/core/engine.go`.
- [x] T012 Use helper for all post-result pending-send waits before auto-compress, queued-turn processing, and final return.
- [x] T013 Add `/cancel` and `/interrupt` command aliases for canonical stop.
- [x] T014 Add Discord `!cancel` and `!interrupt` normalization to `/stop`.
- [x] T015 Add regression test in `cc-connect/core/engine_test.go` for result delivered + send blocked + `/stop` releases lock.

## Phase 5: Verification

- [x] T016 Run `gofmt` on changed Go files.
- [x] T017 Run targeted core interrupt tests.
- [ ] T018 Run `go test ./core ./platform/discord`.
- [ ] T019 Run full `go test ./...`.
- [x] T020 Run Speckit analysis and record results in `analyze.md`.

## Phase 6: Delivery

- [x] T021 Update `ROADMAP.md` interrupt-path status in the branch.
- [x] T022 Commit changes.
- [ ] T023 Open PR and cross-reference PC-68 plus upstream `cc-connect#3`.
- [ ] T024 Comment on upstream `cc-connect#3` with the PR/fix reference.
- [ ] T025 Post final Multica comment and move PC-68 to review.
