# Quickstart: Intervention-Tagging Workflow

**Branch**: `011-intervention-tagging` | **Date**: 2026-05-05
**Input**: Operator-facing walkthrough for a closed bundle and the synthetic dry-run.

## Prerequisites

- A session bundle exists at `observations/sessions/<session-id>/`.
- `transcript.md`, `meta.json`, and `interventions.json` are present.
- `interventions.json` may be `[]`.

## Add a single-turn clarification

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main([
  "intervention", "add", "2026-05-05-example",
  "--type", "clarification",
  "--reason", "Operator asked Vigil to restate the proposed next step.",
  "--at", "2026-05-05T17:00:40Z",
  "--actor", "Zoe",
  "--attribution", "operator_directed",
  "--target-turn", "2026-05-05T17:00:30Z"
]))'
```

Resulting record:

```json
{
  "id": "iv-001",
  "taxonomy_version": "poc-v1",
  "at": "2026-05-05T17:00:40Z",
  "type": "clarification",
  "reason": "Operator asked Vigil to restate the proposed next step.",
  "attribution": "operator_directed",
  "actor": "Zoe",
  "target": {
    "kind": "turn",
    "turn_ref": "2026-05-05T17:00:30Z"
  }
}
```

## Add a multi-turn directive redirect

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main([
  "intervention", "add", "2026-05-05-example",
  "--type", "directive_redirect",
  "--reason", "Operator redirected both peers out of a loop and back to the session seed.",
  "--at", "2026-05-05T17:02:00Z",
  "--actor", "Zoe",
  "--attribution", "operator_directed",
  "--start-turn", "2026-05-05T17:01:00Z",
  "--end-turn", "2026-05-05T17:01:45Z"
]))'
```

Span redirects are one record unless the operator made multiple distinct interventions with different reasons.

## Validate a log

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main([
  "intervention", "validate", "2026-05-05-example"
]))'
```

Validation checks:

- top-level array
- required fields
- fixed type taxonomy
- attribution enum
- RFC3339 UTC timestamps
- unique ids
- target object shape
- span start before span end

## Cite an intervention

Same bundle:

```text
interventions.json#iv-002
```

Across bundles:

```text
observations/sessions/2026-05-05-example/interventions.json#iv-002
```

Consumers read `type`, `reason`, and `attribution` directly from the cited record.

## Compute the directive signal

For H1 directive-intervention load, count:

```text
type == "directive_redirect" AND attribution == "operator_directed"
```

The synthetic dry-run included with this slice has directive count `1`.

## Commit

Initial intervention log commit:

```bash
SID=2026-05-05-example
TX_SHA=$(git log -1 --format=%H -- "observations/sessions/$SID/transcript.md")
TX_SHORT=$(git rev-parse --short "$TX_SHA")
git add "observations/sessions/$SID/interventions.json"
git commit -m "session bundle amend: $SID — interventions @ $TX_SHORT"
```

Revision:

```bash
git add "observations/sessions/$SID/interventions.json"
git commit -m "session bundle amend: $SID — interventions revision: missed-tag @ $TX_SHORT" \
           -m "Added iv-003 after post-session review found a missed drift_catch."
```

Never use `git commit --amend` on a previously committed session bundle.

## Synthetic dry-run

The committed dry-run is under:

```text
observations/sessions/_synthetic/011-intervention-tagging-dry-run/
```

Check it manually:

```bash
python -c 'from pathlib import Path; from tools.peer_session.interventions import validate_interventions_file; validate_interventions_file(Path("observations/sessions/_synthetic/011-intervention-tagging-dry-run/interventions.json")); print("valid")'
```

Expected:

- `iv-001` cites `interventions.json#iv-001`
- `iv-002` is a span-targeted `directive_redirect`
- directive signal count is 1
