# Quickstart: Discord Transcript Export

**Feature**: `006-discord-transcript-export`
**Audience**: operator and cross-reviewers validating the transcript-export
workflow.

## Preferred path

1. Complete or stop a Discord-backed session.
2. Ensure the target bundle directory already exists at
   `observations/sessions/<session-id>/` with a valid `meta.json`.
3. Run the transcript export command from the contained `cc-connect/` workspace
   against that session bundle:

   ```bash
   go run -tags no_web ./cmd/cc-connect transcript export \
     --config ./config.toml \
     --project my-project \
     --session-dir ../observations/sessions/<session-id>
   ```

   By default the command uses `meta.json.opened_at` / `meta.json.closed_at` as
   the session window. Use `--after` / `--before` only when the bound channel
   contains surrounding chatter that needs trimming.
4. Inspect the resulting `transcript.md` for:
   - chronological order
   - author + timestamp per turn
   - no obvious unrelated chatter
5. Confirm `meta.json.transcript_source == "export"` if no material manual
   repair was needed.

## Fallback path

Use fallback when:

- preferred export fails completely
- export returns obviously incomplete data
- operator must materially repair or complete the transcript

Fallback outcomes:

- fully manual transcript → `transcript_source: "reauthored"`
- exported transcript plus operator repair/completion →
  `transcript_source: "hybrid"`

Record fallback provenance explicitly:

```bash
go run -tags no_web ./cmd/cc-connect transcript source \
  --session-dir ../observations/sessions/<session-id> \
  --source hybrid
```

## Verification checks

- A referenced turn timestamp from `interventions.json` resolves to exactly one
  transcript turn.
- Transcript timestamps are ISO-8601 and unique within the session.
- A fresh reviewer can read the transcript without raw Discord payload context.
- The bundle does not falsely claim `transcript_source: "export"` after manual
  repair.

## Fast-follow note

- `specs/001-session-bundle-skeleton/spec.md` and the bundle template still
  name the native plugin fetch path explicitly as the preferred Discord export
  mechanism. This slice implements the equivalent preferred export path inside
  `cc-connect`. No contract change is implied, but the wording should be
  normalized in a follow-on doc patch rather than silently changed here.
