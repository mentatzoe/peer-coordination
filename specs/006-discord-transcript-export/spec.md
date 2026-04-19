# Feature Specification: Discord Transcript Export

**Feature Branch**: `006-discord-transcript-export`
**Created**: 2026-04-19
**Status**: In Review
**Input**: User description: "Implement Discord transcript export for session bundles: export Discord message history into observations/sessions/<session-id>/transcript.md with chronological turns, ISO-8601 timestamp + author per turn, transcript_source provenance in meta.json, and an operator fallback when export is unavailable."

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifacts**:
  - [`design/poc.md`](../../design/poc.md) — Phase 1 requires transcript export as part of the baseline substrate build and the dry-run artifact bundle.
  - [`design/architecture.md`](../../design/architecture.md) — Layer 1 preserves the episode record; Layer 3 depends on that preserved record.
- **Primary consumer contract**:
  - [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) FR-009 defines what `transcript.md` must contain and how `meta.json.transcript_source` is recorded.
- **Related slice**:
  - PR-merged `004-discord-session-controls` established channel binding and session lifecycle. This slice fills the remaining Phase 1 transcript-preservation gap.
- **Roadmap workstream**:
  - `Baseline substrate build` in [`ROADMAP.md`](../../ROADMAP.md).
- **Staffing**:
  - Codex lead (transport / substrate), Claude expected as cross-reviewer per the Phase 1 staffing split.

## User Scenarios & Testing *(mandatory)*

The users of this feature are, in priority order: the operator creating a session bundle, the cross-reviewer reading the preserved transcript, and any downstream artifact pipeline that depends on stable transcript turns.

### User Story 1 — Operator exports a usable Discord transcript into the session bundle (Priority: P1)

As the operator, after a Discord-backed session ends, I need a preferred export path that turns the channel history into `observations/sessions/<session-id>/transcript.md` so the bundle preserves the actual exchange instead of relying on hand reconstruction.

**Why this priority**: this is the remaining Phase 1 substrate gap between a live Discord session and a reviewable session bundle. Without it, dry runs still depend on manual transcript authoring.

**Independent Test**: given a Discord channel with a completed session and a target session-bundle directory, run the export flow and verify `transcript.md` is produced in chronological order with timestamp + author per turn.

**Acceptance Scenarios**:

1. **Given** a completed Discord session in the bound channel, **When** the operator runs the transcript-export workflow for a target `<session-id>`, **Then** the workflow writes `observations/sessions/<session-id>/transcript.md` containing the channel exchange in chronological order with ISO-8601 timestamps and author labels.
2. **Given** the exported transcript and the session bundle's `meta.json`, **When** a cross-reviewer reads the bundle, **Then** they can determine that the transcript came from the preferred export path because `meta.json.transcript_source` records `export`.

### User Story 2 — Operator has an explicit fallback when export is unavailable (Priority: P1)

As the operator, if the preferred Discord export path is unavailable or incomplete, I need a documented fallback that still produces a bundle-compatible transcript artifact without silently dropping the session.

**Why this priority**: spec `001` explicitly treats export failure as a real edge case. The system needs an operator-usable fallback path rather than an implicit failure mode.

**Independent Test**: simulate export unavailability, follow the fallback path, and verify the resulting bundle still contains a valid `transcript.md` plus a truthful `meta.json.transcript_source` value.

**Acceptance Scenarios**:

1. **Given** the preferred export path fails or is blocked, **When** the operator uses the fallback path, **Then** `transcript.md` still exists and `meta.json.transcript_source` records `reauthored` or `hybrid` as appropriate.
2. **Given** an incomplete export that requires operator repair, **When** the operator completes the transcript manually, **Then** the final bundle remains structurally valid and the provenance is explicit rather than pretending the transcript is purely exported.

### User Story 3 — Downstream reviewers can anchor other bundle artifacts to transcript turns (Priority: P2)

As a downstream reviewer or tool, I need the exported transcript to preserve stable, unique turn references so intervention logs and drift audits can point back to the exact turns they reference.

**Why this priority**: Phase 2 and Phase 3 bundle consumers already rely on transcript timestamps as the canonical turn key. If export does not preserve that contract, later slices will drift or break.

**Independent Test**: export a transcript, then verify an `interventions.json.target_turn` or `drift-audit.json.findings[].turn_ref` can resolve back to a unique turn in `transcript.md`.

**Acceptance Scenarios**:

1. **Given** an exported `transcript.md`, **When** another artifact references a turn by ISO-8601 timestamp, **Then** that timestamp resolves to exactly one turn within the transcript.
2. **Given** multiple Discord messages occur close together, **When** the transcript is rendered, **Then** the output still preserves a stable chronological order and unique per-turn timestamp keys for the session bundle contract.

### Edge Cases

- Discord export returns partial history or omits some messages; fallback path must allow operator repair without hiding that the transcript became `hybrid`.
- The channel contains non-session chatter before or after the session; export workflow must let the operator bound the exported window to the intended session.
- Multiple messages share the same wall-clock second; the rendered transcript still needs a unique per-turn key compatible with spec `001`'s turn-reference contract.
- Discord export tooling is temporarily unavailable or upstream integration breaks; bundle production must not dead-end.
- Export includes Discord-specific formatting or markup that harms reviewability; the rendered transcript should stay human-readable enough for H1/H2 review use.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a preferred workflow for exporting Discord session history into `observations/sessions/<session-id>/transcript.md`.
- **FR-002**: The preferred export workflow MUST preserve transcript turns in chronological order.
- **FR-003**: Every exported turn in `transcript.md` MUST include, at minimum, an author label and an ISO-8601 timestamp with at least second precision.
- **FR-004**: The exported transcript format MUST remain compatible with [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) FR-009, including the requirement that turn timestamps act as the canonical turn key for downstream artifacts.
- **FR-005**: The export workflow MUST produce or preserve a unique turn reference for each transcript turn within a session, even when source messages occur within the same second.
- **FR-006**: The workflow MUST record transcript provenance in the session bundle's `meta.json.transcript_source` as one of `export`, `reauthored`, or `hybrid`.
- **FR-007**: The workflow MUST support an operator fallback path when preferred export is unavailable, blocked, or incomplete.
- **FR-008**: When the operator fallback path is used exclusively, the resulting bundle MUST still contain a valid `transcript.md` and `meta.json.transcript_source: "reauthored"`.
- **FR-009**: When the preferred export path is used but the operator materially repairs or completes the transcript, the resulting bundle MUST record `meta.json.transcript_source: "hybrid"`.
- **FR-010**: The workflow MUST allow the operator to target a specific session window or otherwise avoid silently bundling unrelated channel traffic before or after the intended session.
- **FR-011**: The transcript rendering MUST remain human-readable enough for downstream H1/H2 review, rather than preserving Discord raw payloads verbatim.
- **FR-012**: The workflow MUST leave enough provenance or source-reference information in the bundle metadata for a reviewer to understand how the transcript was produced.
- **FR-013**: If the preferred export path fails entirely, the workflow MUST fail explicitly and direct the operator to the fallback path rather than producing a misleading partial success.
- **FR-014**: This slice MUST NOT redefine session-bundle schema outside transcript-related fields already owned by spec `001`.
- **FR-015**: This slice MUST NOT introduce live-session instrumentation or evaluation logic; it only covers transcript preservation from Discord into the bundle surface.

### Key Entities

- **Transcript Export Workflow**: the preferred operator path that turns Discord session history into bundle-compatible `transcript.md`.
- **Transcript Turn**: one rendered message entry in `transcript.md`, carrying the canonical timestamp + author pair used by downstream references.
- **Transcript Source Provenance**: the `meta.json.transcript_source` value describing whether a transcript is `export`, `reauthored`, or `hybrid`.
- **Session Window**: the subset of bound-channel history intended to belong to one session bundle.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a completed Discord dry run, the operator can produce a bundle-compatible `transcript.md` in under 10 minutes using the preferred export path.
- **SC-002**: 100% of exported transcripts for counted sessions include chronological turns with author + timestamp and a truthful `meta.json.transcript_source` value.
- **SC-003**: Downstream reviewers can resolve referenced turns from `interventions.json` or `drift-audit.json` back to exactly one transcript turn in ≥95% of test cases without operator clarification.
- **SC-004**: When preferred export is unavailable, the operator can still complete the session bundle via the fallback path without leaving the session unbundled.

## Assumptions

- Discord is the only substrate in scope for this slice.
- The preferred export path may use an MCP/plugin-based Discord fetch path, but the exact implementation mechanism is not fixed at the spec level.
- Session bundle structure and non-transcript fields remain governed by spec `001`.
- Operator judgment is acceptable for bounding the intended session window when channel history contains surrounding chatter.
- If uniqueness cannot be guaranteed by raw Discord timestamps alone, the rendering may need a deterministic disambiguation rule layered on top of source timestamps, as long as the transcript remains reviewable and stable.
