# Data Model: Intervention-Tagging Workflow

**Branch**: `011-intervention-tagging` | **Date**: 2026-05-05
**Input**: Phase 1 output for the `interventions.json` artifact and workflow-level entities.

## Artifact envelope

`observations/sessions/<session-id>/interventions.json` is a JSON array.

```json
[
  {
    "id": "iv-001",
    "taxonomy_version": "poc-v1",
    "at": "2026-05-05T17:02:00Z",
    "type": "directive_redirect",
    "reason": "Operator redirected both peers back to the session goal after a loop.",
    "attribution": "operator_directed",
    "actor": "Zoe",
    "target": {
      "kind": "span",
      "start_turn_ref": "2026-05-05T17:00:30Z",
      "end_turn_ref": "2026-05-05T17:01:45Z"
    }
  }
]
```

Empty case:

```json
[]
```

No top-level object metadata is allowed in v1, preserving spec 001 compatibility.

## Entity: Intervention Record

| Field | Required | Type | Validation |
|---|---|---|---|
| `id` | Yes | string | `iv-###`, unique within the session |
| `taxonomy_version` | Yes | string | `poc-v1` for this POC taxonomy |
| `at` | Yes | string | RFC3339 UTC timestamp ending in `Z` |
| `type` | Yes | string | one of the taxonomy values below |
| `reason` | Yes | string | non-empty, operator-readable |
| `attribution` | Yes | string | `operator_directed` or `agent_self_flagged` |
| `actor` | Yes | string | non-empty human or peer identifier |
| `target` | Yes | object | one of the target shapes below |
| `notes` | No | string | optional extra context; consumers must not rely on it |

### Intervention type taxonomy (`poc-v1`)

| Type | Meaning | Counted as operator directive load? |
|---|---|---|
| `safety_stop` | Operator halted or stopped the session for safety or boundary reasons | No, unless KPI rollup later chooses to count safety separately |
| `clarification` | Operator asked for clarification, restatement, or context expansion | No |
| `directive_redirect` | Operator directed peers toward a specific path or away from a loop/dead end | Yes when `attribution == "operator_directed"` |
| `drift_catch` | Operator flagged legibility drift, hidden shorthand, undeclared convention, or out-of-record context | No; feeds H2/drift review context |
| `close_or_resume` | Operator explicitly closed, stopped, or resumed the session outside safety-stop cases | No |
| `other` | Intervention did not fit the fixed taxonomy | No by default; reason must explain why |

### Attribution enum

| Attribution | Meaning |
|---|---|
| `operator_directed` | The operator made the intervention or explicitly directed the session behavior. |
| `agent_self_flagged` | A peer identified that an intervention was needed or that its own behavior required correction; operator later ratified it into the log. |

## Entity: Target Reference

Exactly one target shape is allowed per intervention.

### Single-turn target

```json
{
  "kind": "turn",
  "turn_ref": "2026-05-05T17:00:30Z"
}
```

Validation:

- `turn_ref` MUST be an RFC3339 UTC timestamp.
- `turn_ref` SHOULD appear in `transcript.md`.

### Span target

```json
{
  "kind": "span",
  "start_turn_ref": "2026-05-05T17:00:30Z",
  "end_turn_ref": "2026-05-05T17:01:45Z"
}
```

Validation:

- Both refs MUST be RFC3339 UTC timestamps.
- `start_turn_ref` MUST be <= `end_turn_ref`.
- Both refs SHOULD appear in `transcript.md`.
- Use one span record for a continuous multi-turn redirect unless separate operator actions have separate reasons.

### Session target

```json
{
  "kind": "session"
}
```

Validation:

- No turn refs are present.
- Use when the intervention applies to the session as a whole or no specific transcript turn exists.

## Citation Key

Within the same bundle:

```text
interventions.json#iv-001
```

From another bundle or POC-level artifact:

```text
observations/sessions/<session-id>/interventions.json#iv-001
```

Resolution rule:

1. Open the referenced JSON array.
2. Find exactly one record with `id == <fragment>`.
3. Read `type`, `reason`, `attribution`, `actor`, and `target` from that record.
4. Do not infer a different intervention from transcript prose if the cited record is present.

## Workflow-level entities

### E1 - Initial Intervention Log

The first committed non-placeholder `interventions.json` for a session. It may be `[]`.

Commit subject:

```text
session bundle amend: <session-id> — interventions @ <transcript-short-sha>
```

### E2 - Revision Event

A follow-up amend commit that corrects or extends the log.

Commit subject:

```text
session bundle amend: <session-id> — interventions revision: <reason> @ <transcript-short-sha>
```

Common reasons: `missed-tag`, `target-correction`, `reason-clarified`, `taxonomy-correction`.

### E3 - Transcript Version Pin

The short SHA of the commit containing the transcript version the operator tagged against. It appears after `@` in every intervention amend commit. If transcript is corrected later, intervention tags may need a `revision: transcript-refresh` follow-up commit.

## Validation summary

A valid log satisfies:

- top-level JSON array
- unique ids
- required fields on every object
- allowed taxonomy/attribution values
- RFC3339 UTC timestamps
- exactly one valid target shape per record
- span start <= span end
- citation keys resolve to exactly one record
