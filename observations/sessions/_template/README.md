# Session bundle template

Copy this directory to `observations/sessions/<session-id>/` to start a new session bundle. `<session-id>` follows `YYYY-MM-DD-<short-slug>` per [`../README.md`](../README.md).

The `_` prefix on this directory excludes it from being counted as a real session by downstream tooling. Do **not** rename this directory.

## Per-file schemas

JSON files can't carry inline comments, so schema documentation lives here.

### `meta.json` schema

```
{
  "session_id": "<YYYY-MM-DD-short-slug>",
  "opened_at": "<ISO-8601 timestamp, >=second precision>",
  "closed_at": "<ISO-8601 timestamp or null>",
  "close_reason": "<one of: operator_close | pinned_rules_change | stop_no_resume>",
  "participants": [
    { "handle": "<handle-1>", "role": "peer" },
    { "handle": "<handle-2>", "role": "peer" },
    { "handle": "<operator-handle>", "role": "operator" }
  ],
  "pinned_rules_ref": "<commit-hash>" | { "inline": "<raw pinned-rules content>" },
  "substrate": "discord",
  "channel_id": "<discord-channel-snowflake>",
  "transcript_source": "<export | reauthored | hybrid>"
}
```

Fields:
- `session_id`: MUST match the directory name exactly.
- `opened_at` / `closed_at`: ISO-8601 with at least second precision. `closed_at` is `null` only if the session ended without an explicit close trigger.
- `close_reason`: one of the three enum values matching the POC session model (`design/poc.md`'s "What closes a session?" list). `idle_timeout` is **not** a close reason in the POC model — idle gates operator re-open, it does not close sessions on its own.
- `participants`: array of objects, each with `handle` and `role`. Role semantics live at the schema boundary so Phase 2 rollups and Phase 4 (variable peer count) can distinguish peers from operator without guessing by position. Role is one of `peer` or `operator`. Keep handles stable across sessions for trend analysis.
- `pinned_rules_ref`: prefer a commit hash if the pinned rules live in git; inline snapshot is the fallback.
- `substrate`: always `discord` in Phase 1. Additional substrates will come in later phases.
- `channel_id`: Discord channel snowflake the session ran in.
- `transcript_source`: which path produced `transcript.md` — `export` (preferred), `reauthored` (operator wrote by hand), or `hybrid` (mixed).

### `interventions.json` schema

```
[
  {
    "at": "<ISO-8601 timestamp, >=second precision>",
    "type": "<one of: safety_stop | clarification | directive_redirect | drift_catch | close_or_resume | other>",
    "reason": "<free-text operator note>",
    "target_turn": "<optional: ISO-8601 timestamp string of a transcript turn>"
  },
  ...
]
```

Type taxonomy is fixed per `design/poc.md` measurement model; do not invent new types without spec amendment.

`target_turn`, when present, MUST be the ISO-8601 timestamp of a turn in `transcript.md`. Turn timestamps are unique within a session per FR-009, so the timestamp is the canonical turn key — no separate `turn_id` scheme is needed.

- `safety_stop` — any `!stop` or equivalent halting action taken for safety reasons.
- `clarification` — operator asks a peer to clarify or restate something.
- `directive_redirect` — operator directs the conversation in a specific direction (risk of operator effectively orchestrating).
- `drift_catch` — operator flags a legibility / in-group-shorthand drift.
- `close_or_resume` — explicit `!stop` or `!resume` outside the safety-stop case.
- `other` — anything that doesn't fit the above. Use sparingly; if a pattern recurs, propose a new type via spec amendment.

An empty array (`[]`) is valid if no interventions occurred.

### `drift-audit.json` schema (placeholder)

```
{
  "status": "pending-phase-2"
}
```

Replace with the real rubric output once the drift-audit rubric spec lands.

## How to fill the template

1. `cp -r observations/sessions/_template/ observations/sessions/<session-id>/`
2. Open each file and replace `[FILL IN]` placeholders.
3. Remove this `README.md` from the copy (it's template documentation, not per-session content) — or leave it if it helps the next operator; it's advisory.
4. Commit per the authoring discipline in [`../README.md`](../README.md).
