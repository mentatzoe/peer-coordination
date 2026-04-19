# Data Model: Session Bundle Init CLI

## Overview

`peer-session init` creates a pre-session bundle from the canonical template and
applies a deterministic overlay of mechanical values. The initialized bundle is
an in-progress artifact: some fields are complete immediately, while others
remain visibly pending until the session runs and closes.

## Entities

### 1. Init Command Request

- **Fields**:
  - `session_id` — target bundle directory name; must match the session-bundle
    naming rule from `observations/sessions/README.md`
  - `defaults_path` — optional path override for the defaults file; defaults to
    `observations/sessions/defaults.toml`
  - `peer_handles` — optional repeated CLI override replacing the default peer
    list
  - `operator_handle` — optional CLI override for the operator handle
  - `channel_id` — optional CLI override for the Discord channel snowflake
- **Validation**:
  - `session_id` must be `YYYY-MM-DD-<slug>` with optional `-NN` suffix
  - target bundle directory must not already exist
  - `_template/` must exist and contain the required file set
  - effective participant list must contain at least one peer and exactly one
    operator entry

### 2. Session Defaults

- **Purpose**: Store repeated operator inputs that are stable across many
  sessions so `init` does not require retyping them.
- **Canonical location**: `observations/sessions/defaults.toml`
- **Committed sample**: `observations/sessions/defaults.example.toml`
- **Fields**:
  - `operator_handle`
  - `peer_handles` — ordered list
  - `substrate` — fixed to `discord` in v1 unless explicitly expanded later
  - `channel_id`
- **Rules**:
  - CLI overrides win over defaults-file values
  - missing required effective values cause a clear init failure
  - the example file documents the expected schema; the real defaults file is
    operator-local

### 3. Template Bundle Copy

- **Purpose**: Exact filesystem copy of `observations/sessions/_template/` into
  `observations/sessions/<session-id>/`
- **Required file set**:
  - `meta.json`
  - `transcript.md`
  - `interventions.json`
  - `summary.md`
  - `drift-audit.json`
  - `README.md`
- **Rules**:
  - copy happens before any metadata mutation
  - missing required template files are a hard failure
  - copied `README.md` remains advisory for the initialized bundle unless later
    workflow chooses to remove it

### 4. Initialized Meta Draft

- **Purpose**: `meta.json` after mechanical values are filled at init time
- **Fields filled immediately**:
  - `session_id`
  - `opened_at` — UTC ISO-8601 timestamp at init time
  - `participants` — derived from defaults/overrides as
    `[{handle, role}, ...]`
  - `pinned_rules_ref` — commit hash or inline snapshot
  - `substrate` — `discord`
  - `channel_id`
- **Fields intentionally left pending**:
  - `closed_at`
  - `close_reason`
- **Field intentionally removed**:
  - `transcript_source`
- **Rules**:
  - pending fields stay as clear template placeholders rather than being coerced
    into new sentinel values
  - `transcript_source` must be absent entirely until transcript completion

### 5. Pinned Rules Reference

- **Variants**:
  - `commit_hash` — preferred when `pinned-rules/current.md` matches committed
    `HEAD`
  - `inline_snapshot` — fallback object `{ "inline": "<raw rules text>" }`
- **Resolution rules**:
  - use commit hash only when `pinned-rules/current.md` is tracked and clean
  - use inline snapshot when the rules file is dirty, untracked, or otherwise
    not faithfully represented by `HEAD`

### 6. Initialized Bundle Surface

- **Purpose**: The newly created `observations/sessions/<session-id>/`
  directory as an operator-facing work surface for the coming session
- **State transitions**:
  - `missing` → `initialized` when `peer-session init` succeeds
  - `initialized` → `completed` through later manual or tool-assisted session
    updates outside this slice
- **Invariants**:
  - file set matches the template
  - mechanical metadata is filled deterministically
  - non-mechanical content remains visibly pending

## Relationships

- **Init Command Request** consumes **Session Defaults** and produces an
  **Initialized Bundle Surface**.
- **Initialized Meta Draft** lives inside the **Initialized Bundle Surface**.
- **Pinned Rules Reference** is a field within the **Initialized Meta Draft**.
- **Template Bundle Copy** is the precursor step that creates the filesystem
  surface the metadata overlay mutates.
