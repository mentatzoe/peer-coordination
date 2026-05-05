# Intervention Taxonomy and Commit Conventions

**Runtime reference** - schema, citation, directive-count signal, and amend-commit tokens for `interventions.json`.

Derived from [spec 011](../../specs/011-intervention-tagging/spec.md) and `design/poc.md`'s POC minimum intervention taxonomy.

## Record schema

Every record in `observations/sessions/<session-id>/interventions.json` MUST include:

| Field | Required shape |
|---|---|
| `id` | `iv-###`, unique within the session |
| `taxonomy_version` | `poc-v1` |
| `at` | RFC3339 UTC timestamp, e.g. `2026-05-05T17:00:00Z` |
| `type` | one of the taxonomy values below |
| `reason` | non-empty operator-readable reason |
| `attribution` | `operator_directed` or `agent_self_flagged` |
| `actor` | human or peer handle |
| `target` | turn, span, or session object |

Optional:

| Field | Shape |
|---|---|
| `notes` | free-text string; consumers must not depend on it |

## Type taxonomy (`poc-v1`)

| Type | Use when | H1 directive signal |
|---|---|---|
| `safety_stop` | Operator halted or stopped the session for safety/boundary reasons | No |
| `clarification` | Operator asked for clarification, restatement, or context expansion | No |
| `directive_redirect` | Operator directed peers toward a specific path or out of a loop/dead end | Yes if `operator_directed` |
| `drift_catch` | Operator or peer flagged legibility drift, hidden shorthand, undeclared convention, or out-of-record context | No |
| `close_or_resume` | Operator explicitly closed, stopped, or resumed the session outside safety-stop cases | No |
| `other` | No fixed type fits; reason explains why | No by default |

Do not invent new types inside a session. A recurring `other` pattern should become a future taxonomy-version proposal.

## Attribution

| Attribution | Meaning |
|---|---|
| `operator_directed` | The operator made the intervention or explicitly directed the session behavior. |
| `agent_self_flagged` | A peer identified that intervention/correction was needed; the operator later ratified it into the log. |

H1 directive-intervention load uses only:

```text
type == "directive_redirect" AND attribution == "operator_directed"
```

## Targets

Turn target:

```json
{ "kind": "turn", "turn_ref": "2026-05-05T17:00:30Z" }
```

Span target:

```json
{
  "kind": "span",
  "start_turn_ref": "2026-05-05T17:01:00Z",
  "end_turn_ref": "2026-05-05T17:01:45Z"
}
```

Session target:

```json
{ "kind": "session" }
```

Use span for one continuous multi-turn redirect. Use multiple records only when the operator made distinct interventions with distinct reasons.

## Citation keys

Same bundle:

```text
interventions.json#iv-001
```

Cross-bundle or POC-level artifact:

```text
observations/sessions/<session-id>/interventions.json#iv-001
```

Resolution rule: open the array, find exactly one record with matching `id`, then read type/reason/attribution from that record. Do not re-derive intervention meaning from the transcript when the log exists.

## Commit subject format

All intervention-log commits are session-bundle amend commits:

```text
session bundle amend: <session-id> — interventions[ <taxonomy-token>] @ <transcript-short-sha>
```

`<transcript-short-sha>` is the commit short SHA of the transcript version tagged by the operator.

Tokens:

| Token | Use when |
|---|---|
| absent | Initial non-placeholder log commit, including `[]` |
| `revision: missed-tag` | A missed intervention was added after initial commit |
| `revision: target-correction` | Existing record target changed |
| `revision: reason-clarified` | Reason text changed |
| `revision: taxonomy-correction` | Type or attribution corrected |
| `revision: transcript-refresh` | Transcript changed and targets were rechecked |

Examples:

```text
session bundle amend: 2026-05-05-dry-run — interventions @ abc1234
session bundle amend: 2026-05-05-dry-run — interventions revision: missed-tag @ abc1234
session bundle amend: 2026-05-05-dry-run — interventions revision: target-correction @ def5678
```

Never use `git commit --amend` on a previously committed bundle.

## Grep reference

```bash
# All intervention amend commits:
git log --all --grep='— interventions' --format='%H %s' -- observations/sessions/*/interventions.json

# All intervention revisions:
git log --all --grep='interventions revision' --format='%H %s' -- observations/sessions/*/interventions.json
```

