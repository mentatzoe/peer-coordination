# Data Model: Discord Transcript Export

**Feature**: `006-discord-transcript-export`
**Date**: 2026-04-19
**Purpose**: Define the entities and invariants involved in exporting Discord
history into a session bundle transcript.

## Entities

### `Transcript Export Request`

The operator-initiated request to materialize `transcript.md` for one existing
session bundle.

**Fields**:

| Field | Required | Meaning |
|---|---|---|
| `session_id` | yes | Target bundle directory under `observations/sessions/` |
| `channel_id` | yes | Discord channel or thread ID associated with the session |
| `opened_at` | yes | Lower bound for export window |
| `closed_at` | no | Upper bound for export window when known |
| `mode` | yes | `export`, `reauthored`, or `hybrid` outcome intent |

**Relationships**:

- Reads from `observations/sessions/<session-id>/meta.json`
- Produces or updates `observations/sessions/<session-id>/transcript.md`

### `Transcript Turn`

One rendered message entry in `transcript.md`.

**Fields**:

| Field | Required | Meaning |
|---|---|---|
| `timestamp` | yes | Canonical ISO-8601 turn key, UTC-normalized, unique within the session |
| `author` | yes | Human-readable author label used by reviewers |
| `content` | yes | Rendered message body |
| `source_message_id` | no | Discord source message ID retained only if needed for diagnostics |

**Validation rules**:

- `timestamp` must be unique within the transcript
- transcript order is chronological ascending by `timestamp`
- each turn must remain readable without Discord raw JSON context

### `Transcript Provenance Update`

The bundle metadata change that records how `transcript.md` was produced.

**Fields**:

| Field | Required | Meaning |
|---|---|---|
| `transcript_source` | yes | One of `export`, `reauthored`, `hybrid` |
| `updated_at` | yes | When the transcript artifact was last materially changed |
| `notes` | no | Optional operator note if fallback or repair was required |

**Validation rules**:

- `export` means the transcript came from the preferred export path without
  material manual repair
- `reauthored` means the transcript was produced manually because export was not
  usable
- `hybrid` means export succeeded partially but the operator materially repaired
  or completed the transcript

## Invariants

- `Transcript Export Request.session_id` must match the target bundle's
  `meta.json.session_id`
- every `Transcript Turn.timestamp` must be resolvable by downstream
  `interventions.json.target_turn` / `drift-audit.json.turn_ref` references
- `Transcript Provenance Update.transcript_source` must describe reality rather
  than the preferred path the operator hoped to use
- a failed preferred export must not leave the bundle falsely marked as
  `transcript_source: "export"`
