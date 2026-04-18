# Implementation Plan: Agent-Initiated Emoji Reactions

**Branch**: `003-agent-initiated-reactions` | **Date**: 2026-04-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-agent-initiated-reactions/spec.md`

## Summary

Add an agent-session transport primitive that lets an agent add and remove emoji reactions on channel messages, scoped to the agent's own reactions. Implementation lives in the `mentatzoe/cc-connect` Discord platform adapter. Agent sessions call the primitive through the cc-connect `core` interfaces; the Discord adapter translates to `discordgo` reaction API calls with internal rate-limit handling, structured WARN-level failure logging, and a per-channel per-agent failure-rate metric. Suppressed when the channel is in `!stop` state per the Transport MVP Spec.

## Technical Context

**Language/Version**: Go 1.21+ (matches `go.mod` in `mentatzoe/cc-connect`)
**Primary Dependencies**: `discordgo` (Discord API library already used by cc-connect's Discord platform adapter); cc-connect's `core.Platform`, `core.Agent`, `core.AgentSession` interfaces; no new external deps expected.
**Storage**: N/A — reactions are platform-authoritative state; agent-side is stateless. Idempotency is enforced by checking current message state, not local cache.
**Testing**: `go test ./...` per cc-connect convention. Unit tests at `platform/discord/reactions_test.go`. Integration tests exercise the agent-session surface end-to-end via stub platform in `core/`.
**Target Platform**: Same as cc-connect daemon — Linux, macOS, Windows (wherever cc-connect runs). No new platform dependencies.
**Project Type**: Go package additions within the cc-connect monorepo; no new top-level services.
**Performance Goals**: Reaction add/remove latency SHOULD land within Discord API's standard reaction propagation time (typically <500ms p95). Not a hot path.
**Constraints**: MUST NOT block agent session on reaction emission (FR-008). Internal rate-limit handling via `discordgo`'s built-in retry with backoff.
**Scale/Scope**: Pilot-scale — handful of reactions per agent session, tens per channel per minute at most. Discord's per-user rate limit (~5 reactions/sec per channel) is the binding upper constraint.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Checked against `.specify/memory/constitution.md` v1.3.0.

| Principle | Status | Notes |
|---|---|---|
| I. Constitution Is Canonical | ✓ Pass | Plan subordinate to the constitution; no redefinition of governance. |
| II. Transport Is Plumbing, Not Governance | ✓ Pass | This feature IS transport plumbing. Plan deliberately does not encode coordination heuristics. |
| III. Scratchpad First, Then Promotion | ✓ Pass | Spec clarified (4 resolved Qs), PR opened, plan follows after operator signal. |
| IV. Human Arbitration and Explicit Consent | ✓ Pass | Plan does not absorb operator approval authority. FR-013's `!stop` deferral respects the operator-as-arbiter invariant. |
| V. Parallel Work Requires Explicit Ownership | ✓ Pass | Owner: Dalgos (Claude). Expected file surface in cc-connect: `platform/discord/reactions.go`, `platform/discord/reactions_test.go`, possibly `core/agent.go` for interface extension. Documented before coding. |
| VI. Coordination Is Human-Legible, Not Over-Protocolized | ✓ Pass | Plan implements the *primitive* only — no "react with 👀 on inbound" or similar heuristics in the code. Verified by checking that no plan-level decision requires semantic knowledge of emoji meaning. |

**No violations.** Complexity Tracking section below left empty.

## Project Structure

### Documentation (this feature)

```text
specs/003-agent-initiated-reactions/
├── spec.md              # Feature specification (clarified)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (agent-session interface extension)
└── checklists/
    └── requirements.md  # Spec quality checklist (already satisfied)
```

### Source Code (in the downstream `mentatzoe/cc-connect` repo)

```text
cc-connect/
├── core/
│   ├── agent.go (or new reactor.go) # Define optional Reactor interface + supporting types per contracts/agent-session-reactor.md
│   └── engine.go                    # Route reaction requests from sessions to platform
├── platform/
│   └── discord/
│       ├── discord.go               # Register Reactor capability
│       ├── reactions.go             # NEW — add/remove reaction impl via discordgo
│       └── reactions_test.go        # NEW — unit tests
└── tests/
    └── integration/
        └── reactions_test.go        # NEW — end-to-end test with stub platform
```

Design decision locked: **optional capability interface** (`core.Reactor`), not interface extension on `AgentSession`. See `contracts/agent-session-reactor.md` for the Go signature.

**Structure Decision**: Additive changes to cc-connect's existing `platform/discord/` package, with a narrow interface extension at the `core/` boundary. No new top-level packages or services. The feature is implemented as a capability interface (`Reactor`) so platforms that don't support reactions (if any) can opt out cleanly — consistent with the "optional capability interfaces" pattern already used in cc-connect (`CardSender`, `InlineButtonSender`, `ProviderSwitcher`).

## Complexity Tracking

*(No constitution-check violations. Section left empty.)*
