# Tasks: cc-connect Peer System Notice Isolation

**Input**: Design documents from `/specs/014-cc-connect-peer-system-notice-isolation/`  
**Prerequisites**: spec.md, research.md, data-model.md, contracts/peer-system-notice-isolation.md, plan.md, quickstart.md

**Tests**: Required. Use TDD for all behavior changes; focused core and Discord tests are acceptance criteria.

## Phase 1: Setup

- [x] T001 Create Speckit feature branch `014-cc-connect-peer-system-notice-isolation`.
- [x] T002 Claim slice in `ACTIVE-SLICES.md`.
- [x] T003 Read project canon, session re-entry protocol, and cc-connect code surfaces.

## Phase 2: Speckit Artifacts

- [x] T004 Write `spec.md` with PC-76 scope and acceptance criteria.
- [x] T005 Write `research.md`, `data-model.md`, contract, and `quickstart.md`.
- [x] T006 Write `plan.md` and this task list.

## Phase 3: Tests First

- [x] T007 Add failing Discord test for allowlisted peer bot final output dispatch with peer-bot provenance.
- [x] T008 Add failing Discord test for ignoring allowlisted peer bot reply notices.
- [x] T009 Add failing core tests for silent peer-bot rate-limit, queue-ack, overflow, and dropped-queue behavior.
- [x] T010 Add focused core tests proving human/operator rate-limit and busy feedback remains.
- [x] T011 Run targeted tests and confirm they fail for the intended missing behavior.

## Phase 4: Implementation

- [x] T012 Add `MessageAuthorKind` / `FromPeerBot()` in `cc-connect/core/message.go`.
- [x] T013 Set peer-bot provenance in `cc-connect/platform/discord/discord.go`.
- [x] T014 Filter allowlisted peer-bot Discord reply notices in `cc-connect/platform/discord/discord.go`.
- [x] T015 Carry peer-bot provenance into `queuedMessage`.
- [x] T016 Suppress peer-bot guardrail feedback in rate-limit, queue, overflow, and queued-drop paths.

## Phase 5: Verification

- [x] T017 Run `gofmt` on changed Go files.
- [x] T018 Run focused core tests.
- [x] T019 Run focused Discord tests.
- [x] T020 Run broader feasible cc-connect tests and record caveats.
- [x] T021 Complete artifact consistency analysis in `analyze.md`.

## Phase 6: Delivery

- [x] T022 Commit changes.
- [x] T023 Push branch / open PR if GitHub auth is available.
- [ ] T024 Mirror substantive outcome to GitHub and Multica.
- [ ] T025 Move PC-76 to `in_review`.
