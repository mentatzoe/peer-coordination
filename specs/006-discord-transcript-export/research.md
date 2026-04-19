# Research: Discord Transcript Export

## Decision 1: Use a post-session CLI export workflow rooted in the session bundle

- **Decision**: implement transcript export as an operator-facing `cc-connect`
  command that works against an existing session bundle, rather than adding
  automatic live-session transcript capture inside the Discord runtime loop.
- **Rationale**: the POC already treats session bundles as post-session artifact
  surfaces. A CLI export keeps transcript generation artifact-driven, debuggable,
  and separate from live message handling. It also avoids coupling transcript
  persistence to runtime availability or reconnect behavior.
- **Alternatives considered**:
  - **Live runtime auto-write**: rejected because it introduces in-session
    artifact mutation and makes transcript persistence part of the transport
    event loop.
  - **External MCP/tool-only export outside `cc-connect/`**: rejected because
    the contained transport workspace is now the intended Phase 1 implementation
    surface for substrate-side work.

## Decision 2: Preserve Discord timestamps as UTC RFC3339 with fractional seconds

- **Decision**: use the original Discord message timestamp, normalized to UTC
  RFC3339 and preserving fractional seconds when present, as the canonical
  per-turn timestamp in `transcript.md`.
- **Rationale**: spec `001` requires ISO-8601 timestamps with at least second
  precision and uniqueness within a session. Fractional-second preservation
  satisfies both without inventing a parallel sequential turn-id scheme.
- **Alternatives considered**:
  - **Second-precision only**: rejected because same-second collisions are
    realistic and would break downstream `target_turn` / `turn_ref` integrity.
  - **Sequential synthetic turn IDs**: rejected because spec `001` already
    ratified timestamp strings as the canonical turn key.

## Decision 3: Treat `meta.json` as the source of windowing and provenance truth

- **Decision**: export should read the session bundle's existing `meta.json`
  for `channel_id`, `opened_at`, `closed_at`, and current `transcript_source`,
  then update only transcript-related provenance fields as needed.
- **Rationale**: session controls and bundle shape are already defined elsewhere.
  Reusing `meta.json` avoids duplicating session-boundary inputs on the CLI and
  reduces operator error.
- **Alternatives considered**:
  - **Operator passes all window/channel arguments manually every time**:
    rejected because it recreates information already captured in the bundle.
  - **Infer the window from channel history alone**: rejected because channel
    chatter outside the intended session is a known edge case.

## Decision 4: Explicit failure beats misleading partial success

- **Decision**: if preferred export cannot produce a trustworthy transcript, the
  command should fail explicitly and direct the operator toward the fallback
  path, instead of silently writing a partial transcript labeled as `export`.
- **Rationale**: the bundle must remain auditable. A believable-but-incomplete
  transcript is worse than a visible failure that pushes the operator to
  `reauthored` or `hybrid`.
- **Alternatives considered**:
  - **Always write partial output and let the operator notice later**: rejected
    because it makes provenance untrustworthy.
  - **Block fallback entirely until export works**: rejected because spec `001`
    already ratified explicit fallback behavior for transcript preservation.

## Decision 5: Minimal fast-follow may be needed on spec `001` wording

- **Decision**: implement the contained-workspace export path while keeping the
  contract centered on “Discord export rendered to markdown,” and treat the more
  specific `mcp__plugin_discord_discord__fetch_messages` wording in spec `001`
  as a likely fast-follow cleanup if it becomes misleading.
- **Rationale**: the ratified requirement is really about a preferred export
  path plus explicit fallback, not about preserving one exact tooling route
  forever.
- **Alternatives considered**:
  - **Delay this slice until spec `001` wording is amended first**: rejected
    because the dry-run substrate gap is more important than perfect wording
    symmetry at this moment.
