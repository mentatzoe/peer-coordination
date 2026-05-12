# Tasks: cc-connect Peer System Notice Isolation

**Input**: `spec.md`, `plan.md`  
**Prerequisites**: PC-76 created and assigned; isolated branch/worktree active

## Phase 1: Setup

- [X] T001 Create PC-76 child issue for the PC-7 transport blocker.
- [X] T002 Create isolated worktree and branch `codex-014-cc-connect-peer-system-notice-isolation`.
- [X] T003 Register the slice in `ACTIVE-SLICES.md`.
- [X] T004 Scaffold compact Speckit artifacts under `specs/014-cc-connect-peer-system-notice-isolation/`.

## Phase 2: Failing Tests First

- [X] T005 [P] Add core test: peer-bot busy queue accepts without sending `MsgMessageQueued`.
- [X] T006 [P] Add core test: peer-bot rate-limit path drops/logs without sending `MsgRateLimited`.
- [X] T007 [P] Add core test: peer-bot queue overflow returns without sending `MsgPreviousProcessing`.
- [X] T008 [P] Add Discord test: allowlisted peer bot system notice message ID is ignored.
- [X] T009 [P] Add Discord test: normal allowlisted peer bot message still dispatches without mention.
- [X] T010 Verify the new tests fail against current code for the expected reason.

## Phase 3: Implementation

- [X] T011 Add peer-bot provenance fields to `core.Message`.
- [X] T012 Set provenance fields from Discord `handleMessageCreate`.
- [X] T013 Add optional system-notice reply capability in core/platform boundary.
- [X] T014 Implement Discord system-notice sending and process-wide TTL message ID cache.
- [X] T015 Use system-notice reply path for queue/rate-limit/previous-processing notices that remain human-visible.
- [X] T016 Suppress guardrail replies for allowlisted peer-bot busy/rate-limit/overflow paths.

## Phase 4: Verification

- [X] T017 Run focused core tests for queue/rate-limit behavior.
- [X] T018 Run full Discord package tests.
- [X] T019 Run targeted existing peer-bot visibility tests.
- [X] T020 Add `analyze.md` with spec/plan/tasks consistency findings.
- [X] T021 Report PC-76 status back on PC-7 and PC-76.

## Out of Scope

- Live daemon rebuild/restart before the code patch is green.
- Starting PC-7 preflight or counted Session 1.
- Thread-mode repair.
