# Implementation Plan: Discord Session Controls

**Branch**: `[004-discord-session-controls]` | **Date**: 2026-04-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-discord-session-controls/spec.md`

## Summary

Add the missing Layer 1 control surface for the Phase 1 Discord probe inside
the contained `cc-connect/` workspace: explicit channel binding, operator-only
session opening/closing semantics, and safe `!stop` / `!resume` handling. The
plan keeps channel binding inside the Discord platform adapter and reuses
existing `core.SessionManager` primitives for "new session" behavior rather
than inventing a parallel lifecycle subsystem.

## Technical Context

**Language/Version**: Go 1.25.0 in the contained `cc-connect/` workspace; Markdown for slice artifacts  
**Primary Dependencies**: `github.com/bwmarrin/discordgo`, existing `cc-connect/core` engine and session manager, existing Discord platform tests  
**Storage**: Existing cc-connect session JSON store plus in-memory Discord runtime state  
**Testing**: `go test ./platform/discord ./core` plus targeted dry-run verification in Discord  
**Target Platform**: Discord via the contained `cc-connect/` bridge  
**Project Type**: Governance/spec repo with subordinate Go transport workspace  
**Performance Goals**: No material regression in normal Discord message handling; session controls must be safe and predictable in dry runs  
**Constraints**: Must align with `design/poc.md` session definition, preserve existing Discord features unless explicitly tightened, treat the 1-hour idle threshold as operator-facing rather than runtime-enforced in this slice, identify the Phase 1 operator from the first `allow_from` entry, and keep transcript export out of scope  
**Scale/Scope**: One bounded transport slice touching Discord config, inbound filtering, and runtime session-control behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I — Constitution Is Canonical**: Pass. The plan implements the
  already-ratified POC session model; it does not redefine policy.
- **Principle II — Transport Is Plumbing, Not Governance**: Pass. The slice
  only operationalizes channel binding and session controls inside Layer 1.
- **Principle III — Scratchpad First, Then Promotion**: Pass. This is a proper
  spec/plan slice with artifacts under `specs/004-*`.
- **Principle IV — Human Arbitration and Explicit Consent**: Pass. The operator
  remains the only session opener/closer in the runtime model.
- **Principle V — Parallel Work Requires Explicit Ownership**: Pass. This is a
  Codex-owned transport slice under the ratified staffing split.
- **Principle VI — Coordination Is Human-Legible, Not Over-Protocolized**:
  Pass. The controls are minimal and map directly to the current POC session
  rules (`!stop`, `!resume`, operator-only open).

**Post-design check**: Still passes. The selected design keeps policy in the
POC doc and implements only the minimum Layer 1 behavior needed for dry runs.

## Project Structure

### Documentation (this feature)

```text
specs/004-discord-session-controls/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── session-control-behavior.md
└── tasks.md
```

### Source Code (repository root)

```text
cc-connect/
├── config.example.toml
├── docs/discord.md
├── platform/discord/
│   ├── discord.go
│   └── discord_test.go
└── core/
    ├── engine.go
    ├── session.go
    └── session_test.go
```

**Structure Decision**: Keep Discord-specific gating and command interception in
`cc-connect/platform/discord/`, only touching `core/` where reuse of
existing session-manager behavior is necessary for "open a new session"
semantics.

## Phase 0: Research Decisions

See [research.md](./research.md) for the hardening decisions behind this plan:

1. Add explicit Discord `channel_id` binding at the platform config layer and
   enforce it before dispatch.
2. Model session-open/session-closed state as a transport gate, not a new
   governance artifact.
3. Reuse existing session-manager "new session" behavior to ensure `!resume`
   opens a fresh logical session.
4. Treat thread-isolated Discord threads as subordinate to the configured bound
   surface, not as an escape hatch around channel binding.

## Phase 1: Design Outputs

- [data-model.md](./data-model.md) defines the runtime state and config entities
  introduced by this slice.
- [contracts/session-control-behavior.md](./contracts/session-control-behavior.md)
  defines the expected runtime behavior for channel binding and `!stop` /
  `!resume`.
- [quickstart.md](./quickstart.md) captures the dry-run verification flow.

## Implementation Strategy

1. Extend Discord platform configuration with explicit channel binding for the
   Phase 1 probe surface.
2. Enforce bound-surface filtering in both message and interaction entry paths
   before any dispatch into the engine.
3. Add a Discord runtime gate for session state:
   `closed` by default for the bound surface, `open` only by operator seed or
   explicit `!resume`, `closed` again by `!stop`.
4. Reuse existing session-manager new-session/reset behavior so `!resume`
   creates a fresh logical session rather than reviving the stopped one.
5. Add focused Discord-platform tests for bound-channel filtering, peer-post
   rejection while closed, and `!stop` / `!resume` semantics.
6. Update config/docs examples so the new binding and control behavior are
   operable without off-record knowledge.

## Complexity Tracking

No constitutional violations or exceptional complexity justifications are
currently required.
