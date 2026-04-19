# Quickstart: Execute cc-connect Relocation

## Goal

Import the implementation-facing `cc-connect` fork under this repository as a
contained `cc-connect/` workspace, then verify both code readiness and artifact
traceability.

## Preconditions

- `specs/002-cc-connect-relocation/spec.md` and `plan.md` are the current slice
  authority.
- The current source fork is available at `mentatzoe/cc-connect`.
- The operator decision to do a full move under this repo is already ratified in
  discussion #41.

## Execution Sequence

1. Confirm the working tree in `peer-coordination` is clean enough to isolate
   the relocation commit.
2. Import the current `mentatzoe/cc-connect` fork into a top-level
   `cc-connect/` path using the chosen history-preserving method.
3. Add the provenance/boundary note that explains:
   - source fork
   - upstream lineage
   - why `cc-connect/` is subordinate implementation, not policy
4. Update active docs that currently treat the standalone local clone as the
   implementation surface.
5. Run verification:
   - `go build ./cmd/cc-connect` inside `cc-connect/`
   - targeted tests for `platform/discord`, `agent/claudecode`, `agent/codex`,
     and `agent/gemini`
   - doc/path sanity checks for root guidance and planning artifacts
6. Commit the move with links back to the spec and review thread.
7. Post implementation-complete status to discussion #41 and request peer audit.

## Expected Outputs

- populated `cc-connect/` directory at repo root
- provenance/boundary note
- updated active docs
- implementation commit and status update in `#41`

## Verification / Handoff Checklist

- `cc-connect/` exists at repo root and includes the expected transport surfaces
- `cc-connect/README.peer-coordination.md` explains provenance and boundary
- root docs point to `cc-connect/` as the active implementation surface
- `go build ./cmd/cc-connect` succeeds inside `cc-connect/`
- targeted transport checks for Discord / Claude / Codex / Gemini surfaces
  complete successfully
- implementation-complete status is posted back to `#41` with commit/review
  links

## Latest Verification Result

- Import source revision: `127939d330cfeee7063da624d22cd0541b430e3d`
- Build verification: `make web && go build ./cmd/cc-connect`
- Targeted checks:
  - `go test ./platform/discord`
  - `go test ./agent/claudecode ./agent/codex ./agent/gemini`

All of the above passed in the contained workspace on 2026-04-19.

## Rollback Trigger

Pause and request peer review before continuing if:

- the import path risks collapsing governance and implementation into one
  surface
- provenance cannot be made legible after import
- the contained workspace no longer builds at the targeted entry points
