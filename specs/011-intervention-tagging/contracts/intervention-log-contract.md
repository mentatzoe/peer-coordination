# Contract: Intervention Log Workflow

**Branch**: `011-intervention-tagging` | **Date**: 2026-05-05
**Input**: Phase 1 output. Workflow guarantees for producers and consumers of `interventions.json`.

## C1 - Input contract: closed or reviewable session bundle

Pre-conditions for post-session tagging:

1. `observations/sessions/<session-id>/` exists.
2. `meta.json` exists and contains `session_id`.
3. `transcript.md` exists. It may be synthetic for dry-runs.
4. `interventions.json` exists or can be initialized as `[]`.
5. The operator has enough transcript context to assign type, reason, attribution, actor, and target.

If a required input is missing, the workflow MUST halt before writing a partial intervention record.

## C2 - Output contract: valid top-level array

On success:

1. `interventions.json` is valid JSON.
2. The top-level value is an array.
3. Every array item conforms to [data-model.md](../data-model.md).
4. Empty array means no interventions occurred and is a valid evidence state.
5. The current file is the consumer-relevant version; prior versions are historical evidence in git.

## C3 - Add operation contract

`peer-session intervention add <session-id> ...` MUST:

1. Load and validate the current log before mutation.
2. Generate the next `iv-###` id if `--id` is omitted.
3. Build exactly one target object from `--target-turn`, `--start-turn`/`--end-turn`, or no target flags (`session` target).
4. Validate the new complete log before writing.
5. Refuse invalid type, attribution, timestamp, duplicate id, missing reason, or malformed target.
6. Preserve stable ids of existing records.

## C4 - Validate operation contract

`peer-session intervention validate <session-id>` MUST:

1. Read `observations/sessions/<session-id>/interventions.json`.
2. Validate all records against the data model.
3. Return success only when the log is conforming.
4. Report the first actionable validation failure for operator correction.

## C5 - Citation contract

Consumers MAY rely on:

- same-bundle key: `interventions.json#iv-###`
- cross-bundle key: `observations/sessions/<session-id>/interventions.json#iv-###`

A citation resolves only if exactly one record with that id exists. Consumers MUST NOT infer intervention type or reason from transcript prose when a cited record exists.

## C6 - Directive-intervention signal contract

H1 directive-intervention load is computed from records where:

```text
type == "directive_redirect" AND attribution == "operator_directed"
```

This is the authoritative per-session directive signal. KPI rollup owns aggregation and thresholds; this contract owns only the per-session signal.

## C7 - Amend-commit contract

Every intervention-log commit MUST be a session-bundle amend commit:

```text
session bundle amend: <session-id> — interventions[ <taxonomy-token>] @ <transcript-short-sha>
```

Tokens:

| Token | When |
|---|---|
| absent | initial non-placeholder log commit |
| `revision: missed-tag` | operator adds a missed intervention |
| `revision: target-correction` | target turn/span was corrected |
| `revision: reason-clarified` | reason text changed without changing type/target |
| `revision: taxonomy-correction` | type/attribution corrected |
| `revision: transcript-refresh` | transcript changed and targets were rechecked |

Revisions are follow-up commits only. Never use `git commit --amend` on a previously committed session bundle.

## C8 - Synthetic dry-run contract

The slice MUST include a synthetic dry-run demonstrating:

1. a transcript with at least three turns,
2. one single-turn intervention,
3. one span-targeted `directive_redirect`,
4. valid citation keys,
5. directive count of 1 by C6.

The dry-run lives under an underscore-prefixed directory so it is excluded from counted POC sessions.
