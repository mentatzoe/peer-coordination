# Contract: `peer-session init`

## Purpose

Define the operator-visible behavior for the repo-owned session-bundle init CLI.

## Command surface

```text
peer-session init <session-id> [--defaults PATH] [--peer HANDLE ...] [--operator HANDLE] [--channel-id ID]
```

## Preconditions

- Command is run from a repository checkout that contains:
  - `observations/sessions/_template/`
  - `pinned-rules/current.md`
- `<session-id>` follows the session-bundle naming rule from
  `observations/sessions/README.md`
- `observations/sessions/<session-id>/` does not already exist
- Effective participant/channel defaults can be resolved from the defaults file
  and/or CLI flags

## Success behavior

On success, the command MUST:

1. Copy `observations/sessions/_template/` to
   `observations/sessions/<session-id>/`.
2. Replace the mechanical fields in the copied `meta.json`:
   - `session_id`
   - `opened_at`
   - `participants`
   - `pinned_rules_ref`
   - `substrate`
   - `channel_id`
3. Preserve visibly pending placeholders for values not knowable at init time.
4. Remove `transcript_source` from the initialized `meta.json`.
5. Exit with status `0`.

## Provenance behavior

- If `pinned-rules/current.md` is cleanly represented by `HEAD`,
  `pinned_rules_ref` MUST be the current commit hash.
- If not, `pinned_rules_ref` MUST be an inline snapshot object rather than an
  inaccurate commit hash.

## Failure behavior

The command MUST fail clearly, without partial overwrite of an existing bundle,
when:

- the target bundle directory already exists
- the template directory or a required template file is missing
- the session ID is invalid
- effective required defaults cannot be resolved

Failure returns a non-zero exit code and leaves any pre-existing bundle
untouched.

## Non-goals for v1

- No overwrite or rerun-repair mode
- No `setup`, `validate`, or judge-prep commands
- No `cc-connect` daemon interaction or package imports
- No attempt to complete transcript, close metadata, summary, interventions, or
  drift-audit content
