# Intervention-Tagging Workflow (v1 scaffolding)

**Runtime artifact** - how the operator authors, validates, cites, and revises `interventions.json` inside a session bundle.

**Authoritative spec**: [`specs/011-intervention-tagging/spec.md`](../../specs/011-intervention-tagging/spec.md).
**Runtime companion**: [`INTERVENTIONS-TAXONOMY.md`](INTERVENTIONS-TAXONOMY.md) for the taxonomy, schema, citation keys, and commit-message tokens.
**Scope boundary**: this is a post-session annotation workflow. Live Discord slash commands or bridge integrations are out of scope for v1.

---

## When to use which path

| Situation | Path |
|---|---|
| No interventions occurred | **Path A - Empty log** |
| Operator records one or more post-session tags | **Path B - Add tags** |
| Operator checks the log before summary/drift/KPI consumption | **Path C - Validate** |
| Existing committed log needs correction or missed tag | **Path D - Revision** |

## Prerequisites

Before tagging:

1. `observations/sessions/<session-id>/` exists.
2. `meta.json` has the same `session_id`.
3. `transcript.md` exists and contains the turn timestamps the operator wants to target.
4. `interventions.json` exists; `[]` is valid if no interventions occurred.
5. The operator is doing post-session review. Live notes are scratch input only until committed here.

If any prerequisite fails, fix the bundle first. Do not commit a partial intervention record.

## Path A - Empty log

If no interventions occurred, keep:

```json
[]
```

Validate before summary authoring:

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main(["intervention", "validate", "<session-id>"]))'
```

Commit as an evidence state:

```bash
SID=<session-id>
TX_SHA=$(git log -1 --format=%H -- "observations/sessions/$SID/transcript.md")
TX_SHORT=$(git rev-parse --short "$TX_SHA")
git add "observations/sessions/$SID/interventions.json"
git commit -m "session bundle amend: $SID — interventions @ $TX_SHORT"
```

## Path B - Add tags

Use the repo-owned CLI to append one tag at a time. The tool validates the current log, builds the target object, validates the resulting log, then writes the file.

Single-turn target:

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main([
  "intervention", "add", "<session-id>",
  "--type", "clarification",
  "--reason", "Operator asked Vigil to restate the next step.",
  "--at", "2026-05-05T17:00:45Z",
  "--actor", "Zoe",
  "--attribution", "operator_directed",
  "--target-turn", "2026-05-05T17:00:30Z"
]))'
```

Span target:

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main([
  "intervention", "add", "<session-id>",
  "--type", "directive_redirect",
  "--reason", "Operator redirected both peers out of a loop and back to the seed.",
  "--at", "2026-05-05T17:02:00Z",
  "--actor", "Zoe",
  "--attribution", "operator_directed",
  "--start-turn", "2026-05-05T17:01:00Z",
  "--end-turn", "2026-05-05T17:01:45Z"
]))'
```

Session target (no turn flags):

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main([
  "intervention", "add", "<session-id>",
  "--type", "close_or_resume",
  "--reason", "Operator closed the session after the work resolved.",
  "--at", "2026-05-05T17:04:00Z",
  "--actor", "Zoe",
  "--attribution", "operator_directed"
]))'
```

Agent self-flag:

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main([
  "intervention", "add", "<session-id>",
  "--type", "drift_catch",
  "--reason", "Vigil self-flagged that its shorthand depended on off-record context.",
  "--at", "2026-05-05T17:03:20Z",
  "--actor", "Vigil",
  "--attribution", "agent_self_flagged",
  "--target-turn", "2026-05-05T17:03:00Z"
]))'
```

Operator ratification is still required: a peer self-flag becomes bundle evidence only after the operator records it in `interventions.json`.

## Path C - Validate

Run validation before summary authoring and before drift/KPI consumers use the log:

```bash
python -c 'from tools.peer_session.cli import main; raise SystemExit(main(["intervention", "validate", "<session-id>"]))'
```

Validation checks:

- top-level array
- unique `iv-###` ids
- required fields
- `taxonomy_version == "poc-v1"`
- type taxonomy values
- attribution enum
- RFC3339 UTC timestamps
- valid target shape
- target turn/span timestamps present in `transcript.md`

## Path D - Revision

Use this when the log was already committed and the operator finds a missed tag, typo, target mistake, or transcript correction.

**Never use `git commit --amend` on a session bundle.** Revisions are follow-up amend commits so prior evidence remains reconstructible.

1. Edit via `peer-session intervention add` for missed tags, or manually correct the existing record when preserving the same id matters.
2. Validate with Path C.
3. Commit with a revision token:

```bash
SID=<session-id>
TX_SHA=$(git log -1 --format=%H -- "observations/sessions/$SID/transcript.md")
TX_SHORT=$(git rev-parse --short "$TX_SHA")
git add "observations/sessions/$SID/interventions.json"
git commit -m "session bundle amend: $SID — interventions revision: missed-tag @ $TX_SHORT" \
           -m "Added iv-003 after post-session review found a missed drift_catch."
```

Common revision reasons live in [`INTERVENTIONS-TAXONOMY.md`](INTERVENTIONS-TAXONOMY.md).

Verify history:

```bash
git log --all --follow --format='%H %s' -- "observations/sessions/$SID/interventions.json"
git show <prior-commit>:"observations/sessions/$SID/interventions.json"
```

## Downstream discipline

- Summary and drift-audit cite records by `interventions.json#iv-###`.
- H1 directive load counts `directive_redirect` records whose attribution is `operator_directed`.
- Consumers do not infer extra interventions from transcript prose when the log is present.

