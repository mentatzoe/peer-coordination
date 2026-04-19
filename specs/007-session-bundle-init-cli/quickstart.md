# Quickstart: Session Bundle Init CLI

## Goal

Create a new pre-session bundle from the canonical template without manual copy
work, while keeping pending fields visibly unfinished.

## 1. Prepare local defaults

Copy the committed sample to the local defaults path:

```bash
cp observations/sessions/defaults.example.toml observations/sessions/defaults.toml
```

Fill in the repeated session defaults you expect to reuse, especially:

- operator handle
- peer handles
- Discord channel ID

## 2. Initialize a new bundle

From the repository root, run:

```bash
./peer-session init 2026-04-20-dry-run-one
```

This creates:

```text
observations/sessions/2026-04-20-dry-run-one/
```

and fills the mechanical metadata in `meta.json`.

## 3. Override session-local values when needed

If a single session needs different participants or a different channel, pass
explicit overrides:

```bash
./peer-session init 2026-04-20-dry-run-one \
  --channel-id 123456789012345678 \
  --peer codex \
  --peer claude \
  --operator zoe
```

The defaults file remains the baseline; flags win for that one run.

## 4. Inspect the initialized bundle

After a successful run:

- the full template file set exists in the new bundle directory
- `meta.json` includes `session_id`, `opened_at`, `participants`,
  `pinned_rules_ref`, `substrate`, and `channel_id`
- `meta.json.transcript_source` is absent
- unresolved session-close and qualitative fields still show template
  placeholders so the operator can finish them later

## 5. Expected failure modes

- If the target session directory already exists, `init` fails instead of
  overwriting it.
- If `_template/` is missing required files, `init` fails clearly.
- If `pinned-rules/current.md` is dirty, init still succeeds but writes an
  inline `pinned_rules_ref` snapshot instead of a misleading commit hash.

## 6. Verification checkpoint

The initialized bundle is now ready to be completed during and after the
session. `peer-session init` is finished once the directory exists and the
mechanical metadata is truthfully populated.
