# Implementation Plan: cc-connect Peer System Notice Isolation

**Branch**: `014-cc-connect-peer-system-notice-isolation` | **Date**: 2026-05-12 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/014-cc-connect-peer-system-notice-isolation/spec.md`

## Summary

Add explicit inbound author provenance to cc-connect core, set it from Discord `allow_from_bots`, ignore allowlisted peer-bot Discord replies as bridge notices, and suppress sender-facing guardrail replies for peer-bot-originated messages while preserving human/operator feedback.

## Technical Context

**Language/Version**: Go 1.25 in the contained `cc-connect/` workspace  
**Primary Dependencies**: Go stdlib; `github.com/bwmarrin/discordgo`; existing cc-connect core engine/session abstractions  
**Storage**: No persistent schema change; in-memory message and queue metadata only  
**Testing**: Targeted `go test ./core -run ...` and `go test ./platform/discord -run ...`; broader package tests as time/environment permits  
**Target Platform**: Discord parent-channel pilot path in the contained `cc-connect/` workspace  
**Project Type**: Go transport/service patch under the peer-coordination governance repo  
**Performance Goals**: No measurable throughput change; classification is O(1) per message  
**Constraints**: Preserve peer final output ingestion; do not broad-match localized guardrail strings; preserve human/operator feedback; do not start PC-7 smoke/preflight  
**Scale/Scope**: One narrow Phase 1 transport blocker for two-peer Discord parent-channel runs

## Constitution Check

- **I. Constitution Is Canonical**: Pass. The slice implements a promoted transport blocker without changing governance.
- **II. Transport Is Plumbing, Not Governance**: Pass. The fix is Layer 1 provenance and delivery isolation only.
- **III. Scratchpad First, Then Promotion**: Pass. PC-76 is captured in a Speckit chain before implementation.
- **IV. Human Arbitration and Explicit Consent**: Pass. Operator feedback remains visible and the smoke retry is not started here.
- **V. Parallel Work Requires Explicit Ownership**: Pass. `ACTIVE-SLICES.md` records owner, branch, worktree, and do-not-touch surfaces.
- **VI. Coordination Is Human-Legible, Not Over-Protocolized**: Pass. The patch prevents hidden bridge chatter from entering peer runtime context without adding peer coordination protocol.

## Project Structure

```text
specs/014-cc-connect-peer-system-notice-isolation/
├── spec.md
├── research.md
├── data-model.md
├── contracts/
│   └── peer-system-notice-isolation.md
├── quickstart.md
├── plan.md
├── tasks.md
└── analyze.md

cc-connect/
├── core/message.go
├── core/engine.go
├── core/engine_test.go
├── platform/discord/discord.go
└── platform/discord/discord_test.go
```

## Implementation Notes

- Add `MessageAuthorKind` and `Message.FromPeerBot()`.
- Set `AuthorKind: MessageAuthorPeerBot` in Discord only for `allow_from_bots` authors.
- Ignore allowlisted peer-bot Discord replies before core dispatch.
- Carry `authorKind` into `queuedMessage`.
- Suppress peer-bot notices in rate-limit, queue-ack, overflow/previous-processing, and queued-drop paths.
- Keep existing human/operator feedback untouched.

## Complexity Tracking

No constitutional violations. No complexity exceptions required.
