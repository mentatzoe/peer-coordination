# Implementation Plan: Discord Transcript Export

**Branch**: `[006-discord-transcript-export]` | **Date**: 2026-04-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-discord-transcript-export/spec.md`

## Summary

Add a post-session export path inside the contained `cc-connect/` workspace that
can materialize Discord channel history into a session bundle's
`transcript.md`, while keeping transcript provenance explicit in `meta.json`
and preserving the turn-reference contract expected by spec `001`. The plan
chooses an operator-facing CLI/export workflow rather than live-session
instrumentation so transcript capture stays artifact-driven and composable with
the existing bundle pattern.

## Technical Context

**Language/Version**: Go 1.25.0 in the contained `cc-connect/` workspace; Markdown/JSON for bundle artifacts  
**Primary Dependencies**: `github.com/bwmarrin/discordgo`, existing `cc-connect` Discord config/session plumbing, session-bundle files under `observations/sessions/`  
**Storage**: Git-tracked session bundle files (`transcript.md`, `meta.json`) plus Discord message history fetched at export time  
**Testing**: targeted `go test` coverage around transcript rendering/export behavior plus bundle-shape verification on fixture data  
**Target Platform**: Discord-backed Phase 1 / Phase 2 operator workflow in the contained `cc-connect/` workspace  
**Project Type**: Governance/spec repo with subordinate Go transport workspace and repo-local artifact bundle surface  
**Performance Goals**: Export a typical dry-run transcript fast enough for operator post-session use; preserve chronological correctness and stable turn references over raw throughput  
**Constraints**: Must honor spec `001` FR-009/FR-010, remain post-session only, avoid redefining bundle schema beyond transcript-related fields, support an explicit fallback path when export is unavailable, and keep unrelated channel chatter out of the bundle  
**Scale/Scope**: One bounded operator-facing export slice for Discord session bundles; no multi-platform generalization, no KPI logic, no live capture

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I — Constitution Is Canonical**: Pass. The slice implements the
  already-ratified session-bundle contract rather than redefining it.
- **Principle II — Transport Is Plumbing, Not Governance**: Pass. This is
  Layer 1 record preservation work only.
- **Principle III — Scratchpad First, Then Promotion**: Pass. The slice is
  proceeding through spec/plan/tasks artifacts under `specs/006-*`.
- **Principle IV — Human Arbitration and Explicit Consent**: Pass. The operator
  remains in the loop for session window selection, fallback use, and provenance
  truthfulness.
- **Principle V — Parallel Work Requires Explicit Ownership**: Pass. This is a
  Codex-owned transport slice under the ratified staffing split.
- **Principle VI — Coordination Is Human-Legible, Not Over-Protocolized**:
  Pass. The output is a human-readable transcript artifact, not a hidden binary
  export or opaque payload dump.

**Post-design check**: Still passes. The selected design keeps transcript
capture post-session, explicit, and artifact-driven without moving evaluation
or governance into transport code.

## Project Structure

### Documentation (this feature)

```text
specs/006-discord-transcript-export/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── transcript-export-behavior.md
└── tasks.md
```

### Source Code (repository root)

```text
cc-connect/
├── cmd/cc-connect/
│   ├── main.go
│   └── [new transcript export command file]
├── platform/discord/
│   ├── discord.go
│   └── [possible shared fetch/render helper or tests]
└── docs/
    └── discord.md

observations/sessions/
└── <session-id>/
    ├── meta.json
    └── transcript.md
```

**Structure Decision**: Keep operator-facing export orchestration in
`cc-connect/cmd/cc-connect/` and reusable Discord-fetch/render logic in
`cc-connect/platform/discord/` only if shared helpers are justified. The slice
writes into the existing repo-local session bundle surface rather than creating
another artifact location.

## Phase 0: Research Decisions

See [research.md](./research.md) for the decisions that harden this plan:

1. Use a post-session CLI export workflow rooted in an existing session bundle,
   not live runtime auto-capture.
2. Use Discord message timestamps normalized to UTC RFC3339 with fractional
   seconds preserved as the canonical turn key so spec `001` uniqueness holds.
3. Treat the bundle's `meta.json` as the source of session window/provenance
   truth, with explicit update rules for `transcript_source`.
4. Keep export failure explicit and operator-recoverable rather than silently
   fabricating a partial transcript.

## Phase 1: Design Outputs

- [data-model.md](./data-model.md) defines the export request, transcript turn,
  and provenance-update entities.
- [contracts/transcript-export-behavior.md](./contracts/transcript-export-behavior.md)
  defines the operator-visible contract for export success, fallback, and turn
  stability.
- [quickstart.md](./quickstart.md) captures the expected operator flow for
  producing `transcript.md` from a Discord-backed session bundle.

## Implementation Strategy

1. Add a bounded operator-facing export command in the contained
   `cc-connect/` workspace that targets an existing session bundle.
2. Read `observations/sessions/<session-id>/meta.json` to determine the Discord
   source surface and time window, rather than asking the operator to restate
   everything manually.
3. Fetch Discord message history for that bounded window, render it into
   chronological markdown turns, and preserve unique timestamp-based turn keys.
4. Write or replace `transcript.md` and update `meta.json.transcript_source`
   truthfully as `export`, `reauthored`, or `hybrid`.
5. Make failure modes explicit: if preferred export cannot produce a trustworthy
   transcript, tell the operator to use the fallback path rather than claiming
   success.
6. Add focused tests for transcript rendering, timestamp uniqueness, provenance
   updates, and failure-path behavior.

## Complexity Tracking

No constitutional violations or exceptional complexity justifications are
currently required.
