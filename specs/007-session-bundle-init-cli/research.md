# Research: Session Bundle Init CLI

## Decision 1: Use a repo-root Python CLI with standard-library-only modules

- **Decision**: Implement `peer-session` as a thin executable at the repo root
  backed by Python 3.14 standard-library modules under `tools/peer_session/`.
- **Rationale**: This repo currently has no root CLI runtime, but Python 3 is
  already available in the working environment and can handle filesystem copy,
  JSON edits, TOML reads, and git subprocess calls without adding another build
  system. That keeps the tool obviously repo-owned and separate from the
  contained `cc-connect` Go workspace.
- **Alternatives considered**:
  - **New root Go module**: rejected because it adds a second compiled toolchain
    surface in a repo whose root is otherwise governance/docs-first, and it
    would look too much like an extension of `cc-connect` even without imports.
  - **Shell-only script**: rejected because JSON/TOML mutation, placeholder
    preservation, and cross-platform testability become brittle quickly.

## Decision 2: Put repeated session defaults in `observations/sessions/defaults.toml`

- **Decision**: The real local defaults file will live at
  `observations/sessions/defaults.toml`, with a committed
  `observations/sessions/defaults.example.toml` template for humans to copy.
- **Rationale**: The defaults belong next to the session bundles they configure,
  and TOML is human-editable while remaining parseable with Python's standard
  library via `tomllib`. Keeping the real file local and the example file
  committed matches the spec's "repo-local defaults file + template/sample"
  requirement without forcing operator-specific channel IDs or participant lists
  into git history.
- **Alternatives considered**:
  - **JSON defaults file**: rejected because it is less comfortable for manual
    editing and cannot carry comments cleanly.
  - **Top-level dotfile**: rejected because it weakens the artifact-local mental
    model and separates bundle defaults from `observations/sessions/`.

## Decision 3: Preserve unresolved placeholders instead of inventing new pre-session sentinels

- **Decision**: `peer-session init` will copy `_template/` and replace only the
  values that are truly mechanical at session-open time. Unresolved fields such
  as `close_reason`, `closed_at`, and qualitative markdown sections remain as
  template placeholders, while `meta.json.transcript_source` is removed
  entirely.
- **Rationale**: The bundle template already uses explicit `[FILL IN]`
  placeholders to mark pending work. Reusing that pattern keeps the initialized
  artifact human-legible and avoids inventing new null/enum semantics that
  would blur the difference between "not yet known" and "known to be null."
  `transcript_source` is the one exception because the clarified spec explicitly
  requires omission until a real transcript exists.
- **Alternatives considered**:
  - **Set unresolved fields to `null`**: rejected because it falsely implies the
    final schema allows those values to be null as a stable meaning.
  - **Introduce new placeholder enums such as `pending`**: rejected because that
    would silently redefine the session-bundle contract.

## Decision 4: Resolve `pinned_rules_ref` truthfully with commit-hash preference and inline fallback

- **Decision**: When `pinned-rules/current.md` is tracked at `HEAD` and has no
  uncommitted changes, write the current commit hash to `pinned_rules_ref`. If
  the rules file is dirty, untracked, or otherwise not safely representable by
  `HEAD`, write an inline snapshot object instead.
- **Rationale**: The spec prefers commit hashes because they are easier to audit,
  but a stale hash is worse than an inline fallback. The init command runs at
  session-open time, so provenance must describe the actual rules in force at
  that moment, not merely the last committed rules.
- **Alternatives considered**:
  - **Always use `git rev-parse HEAD`**: rejected because it can lie when the
    rules file has uncommitted edits.
  - **Hard-fail on dirty rules**: rejected because the bundle-init tool should
    remain usable even when the operator has not yet committed rule wording; the
    truthful inline fallback already exists in the schema.

## Decision 5: Keep per-session overrides narrow and explicit

- **Decision**: V1 override flags will cover the repeated defaults only:
  participant handles/roles and the Discord channel ID, plus an optional
  explicit defaults-file path.
- **Rationale**: This matches the clarified requirement without turning `init`
  into a large configuration surface. The defaults file remains the main source
  of repeated values; override flags only handle session-local deviations.
- **Alternatives considered**:
  - **No override flags**: rejected because the clarified spec requires them.
  - **Broad flag set for every metadata field**: rejected because it invites
    misuse of `init` as a general bundle editor rather than a bounded bootstrap
    command.

## Decision 6: Use temp-directory `unittest` coverage instead of adding a new third-party test stack

- **Decision**: Test the new CLI with Python's `unittest`, `tempfile`, and
  small git-fixture repositories created inside temporary directories.
- **Rationale**: The repository currently has no root Python packaging or test
  configuration. Standard-library tests are enough to verify filesystem copy,
  defaults overlay, session-id validation, pinned-rules provenance, and
  existing-directory failure behavior.
- **Alternatives considered**:
  - **Pytest**: rejected because it adds another repo-root dependency for a
    small utility slice.
  - **Manual-only verification**: rejected because the contract-bearing bundle
    transformations are easy to regress.
