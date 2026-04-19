# Data Model: cc-connect Relocation

## Entities

### ContainedTransportWorkspace

- **Description**: The imported `cc-connect/` implementation surface that now
  lives inside this repository.
- **Core fields**:
  - `path`: expected top-level location (`cc-connect/`)
  - `source_fork`: originating maintained fork (`mentatzoe/cc-connect`)
  - `source_upstream`: original upstream lineage (`chenhg5/cc-connect`)
  - `import_mode`: history-preserving contained import
  - `maintenance_owner`: transport-side owner for the current phase
  - `status`: planned, imported, verified
- **Validation rules**:
  - Must exist at a clearly named top-level path.
  - Must remain subordinate to repo-root governance artifacts.
  - Must have legible provenance after import.

### GovernanceSurface

- **Description**: The canonical policy/design artifacts that remain
  authoritative after the transport workspace is imported.
- **Core fields**:
  - `artifact_path`
  - `artifact_kind` (`constitution`, `vision`, `design`, `spec`, `roadmap`)
  - `authority_level`
  - `active_reference_state`
- **Validation rules**:
  - Must not be redefined by transport implementation alone.
  - Active docs must describe the contained transport workspace as subordinate.

### DocumentationReference

- **Description**: An active document pointer that tells collaborators where the
  transport implementation surface lives and how to interpret it.
- **Core fields**:
  - `source_document`
  - `target_path`
  - `reference_type` (`active`, `archive`)
  - `stale_state`
- **Validation rules**:
  - Active references must point to `cc-connect/` after import.
  - Archive references may retain the legacy local-clone path if clearly
    historical.

### HandoverTrail

- **Description**: The durable artifact chain for re-entry into this slice.
- **Core fields**:
  - `roadmap_reference`
  - `coordination_thread`
  - `review_thread`
  - `implementation_commit`
  - `stage`
  - `escalation_state`
- **Validation rules**:
  - Must be reconstructable without operator restitching.
  - Must link planning artifacts to implementation commits.

## State Transitions

### ContainedTransportWorkspace

`planned` -> `imported` -> `verified`

- `planned` when the spec/plan chain is complete but the repo import has not
  happened.
- `imported` when the workspace exists under `cc-connect/` with provenance
  scaffolding and doc updates staged.
- `verified` when build/test and traceability checks pass.

### DocumentationReference

`legacy-active` -> `updated-active` or `archived`

- `legacy-active` while an active document still points at the old standalone
  clone.
- `updated-active` once that document points to the contained workspace.
- `archived` when the reference remains only for historical traceability.
