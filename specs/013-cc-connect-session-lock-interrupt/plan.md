# Implementation Plan: cc-connect Session-Lock Interrupt

**Branch**: `codex-013-cc-connect-session-lock-interrupt` | **Date**: 2026-05-05 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/013-cc-connect-session-lock-interrupt/spec.md`

## Summary

Fix the cc-connect Phase 1 interrupt path by making post-result `AgentSession.Send` completion waits interruptible. The root cause is in cc-connect core: the session lock is `core.Session.busy`, and the event loop could hold it after `EventResult` while blocking on `pendingSend`. `/stop` already marks the interactive state stopped and closes the agent asynchronously, but a blocked post-result send wait did not observe the stop signal. This plan adds an interruptible wait helper, command aliases (`/cancel`, `/interrupt`), Discord bang aliases (`!cancel`, `!interrupt`), and a regression test that verifies `/stop` releases the lock while `Send` remains blocked.

## Technical Context

**Language/Version**: Go 1.25 (cc-connect module)  
**Primary Dependencies**: Go stdlib; existing cc-connect core engine/session abstractions; Discord platform adapter.  
**Storage**: Existing session state under cc-connect `SessionManager`; no schema migration.  
**Testing**: `go test ./core -run 'TestCmdStop_ReleasesSessionLockWhenSendDoesNotReturnAfterResult|TestCmdStop_ReturnsWhileCloseBlockedAndStopsEventLoop'`; full `go test ./...` before PR.  
**Target Platform**: cc-connect contained workspace under `cc-connect/`; Discord pilot path.  
**Project Type**: Go service / transport substrate patch inside peer-coordination contained workspace.  
**Performance Goals**: Interrupt releases lock within seconds; regression budget under 2s.  
**Constraints**: Do not move governance into transport. Do not alter normal message queueing semantics. Keep `/stop` acknowledgement existing/localized. Preserve asynchronous agent close behavior.  
**Scale/Scope**: One active session key at a time; Phase 3 pilot uses two peer bots with separate cc-connect sessions.

## Constitution Check

- **I. Constitution Is Canonical**: Pass. Spec remains subordinate to constitution, `design/architecture.md`, and `design/poc.md`.
- **II. Transport Is Plumbing, Not Governance**: Pass. Patch is Layer 1 interruption/recovery only; no coordination policy changes.
- **III. Scratchpad First, Then Promotion**: Pass. PC-68 is promoted into this Speckit chain.
- **IV. Human Arbitration and Explicit Consent**: Pass. The operator gets a reliable explicit cancel path.
- **V. Parallel Work Requires Explicit Ownership**: Pass. `ACTIVE-SLICES.md` claims 013 and touches only declared surfaces.
- **VI. Coordination Is Human-Legible, Not Over-Protocolized**: Pass. Transcript shows a normal stop acknowledgement; no hidden protocol required.

## Project Structure

```text
specs/013-cc-connect-session-lock-interrupt/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── interrupt-contract.md
├── checklists/
│   └── requirements.md
├── tasks.md
└── analyze.md

cc-connect/
├── core/engine.go
├── core/engine_test.go
└── platform/discord/discord.go
```

## Implementation Notes

- Add `Engine.waitForPendingSend(sendDone, stopCh, debugMessage)` and use it at all post-result pending-send wait sites:
  - before auto-compress after `EventResult`
  - before starting a queued turn
  - before returning after the final result path
- Map `/cancel` and `/interrupt` to command id `stop`.
- Map Discord `!cancel` and `!interrupt` to `/stop`.
- Add regression test proving `/stop` releases `Session.busy` while `Send` remains blocked after `EventResult`.

## Complexity Tracking

No constitutional violations. No complexity exceptions required.
