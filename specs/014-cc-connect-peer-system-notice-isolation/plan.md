# Implementation Plan: cc-connect Peer System Notice Isolation

**Branch**: `codex-014-cc-connect-peer-system-notice-isolation` | **Date**: 2026-05-12 | **Spec**: `specs/014-cc-connect-peer-system-notice-isolation/spec.md`  
**Input**: Feature specification from `specs/014-cc-connect-peer-system-notice-isolation/spec.md`

## Summary

Fix the PC-7 Castor/Vigil feedback loop by separating peer agent output from cc-connect system notices. The implementation carries peer-bot provenance into `core.Message`, prevents peer-bot pressure paths from emitting guardrail replies, and teaches the Discord adapter to record and ignore bridge system notice message IDs.

## Technical Context

**Language/Version**: Go (cc-connect workspace)  
**Primary Dependencies**: `discordgo`, existing cc-connect core/platform interfaces  
**Storage**: In-memory TTL cache for Discord system notice message IDs  
**Testing**: `go test` focused on `./core` and `./platform/discord`  
**Target Platform**: cc-connect Discord bridge running as the PC-7 launchd daemon  
**Project Type**: Go CLI/daemon contained under `cc-connect/`  
**Performance Goals**: No extra network calls on inbound message dispatch; bounded memory for notice IDs  
**Constraints**: Do not break normal human/operator guardrail feedback; do not filter normal peer agent output  
**Scale/Scope**: PC-7 pilot channel and same-daemon peer projects first; cross-daemon notice isolation deferred

## Constitution Check

- **Principle II - Transport Is Plumbing, Not Governance**: Pass. The slice changes Layer 1 delivery semantics only; it does not define peer coordination policy.
- **Principle IV - Human Arbitration and Explicit Consent**: Pass. The slice keeps operator feedback and interrupt posture intact.
- **Principle VI - Human-Legible, Not Over-Protocolized**: Pass. The slice removes bridge-generated noise from peer conversation rather than adding a peer protocol.
- **Downstream boundary**: Pass. Code changes stay inside the contained `cc-connect/` implementation surface; repo-root artifacts record the invariant.

## Project Structure

### Documentation

```text
specs/014-cc-connect-peer-system-notice-isolation/
├── spec.md
├── plan.md
├── tasks.md
├── analyze.md
└── checklists/
    └── requirements.md
```

### Source Code

```text
cc-connect/
├── core/
│   ├── message.go
│   ├── engine.go
│   └── engine_test.go
└── platform/
    └── discord/
        ├── discord.go
        └── discord_test.go
```

**Structure Decision**: No new packages unless tests show an existing file would become unclear. Prefer small helper functions and optional interfaces near existing core/platform boundaries.

## Design Notes

1. Add provenance fields to `core.Message`, for example `AuthorIsBot` and `AllowedPeerBot`.
2. Add an optional platform capability for system notice replies so core can mark guardrail replies without changing every platform implementation.
3. Implement the optional capability in Discord by sending through existing channel send paths and recording returned Discord message IDs in a package-level TTL cache.
4. Ignore cached system notice IDs in `handleMessageCreate` before allowlisted-peer-bot dispatch.
5. Gate core busy/rate-limit/overflow replies for `AllowedPeerBot` messages so peer-bot pressure never emits bridge guardrail text.

## Risk / Follow-Up

- If PC-7 later runs peer bots in separate cc-connect daemon processes, the in-memory ID cache will not span daemons. That topology should get a follow-up marker/shared-store design rather than content-prefix filtering.
- Existing broad `go test ./core` currently has unrelated macOS path assertion failures in this worktree. Verification for this slice uses focused core tests plus the full Discord package.
