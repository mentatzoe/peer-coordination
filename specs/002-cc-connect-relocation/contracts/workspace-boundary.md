# Contract: Workspace Boundary

## Purpose

Define the collaborator-facing contract for the contained `cc-connect/`
workspace once it is moved under this repository.

## Required Guarantees

1. **Location guarantee**
   - The implementation-facing transport workspace lives at a clearly named
     top-level path: `cc-connect/`.

2. **Authority guarantee**
   - `cc-connect/` is an implementation surface.
   - `VISION.md`, `design/`, the constitution, and approved specs remain the
     authoritative governance/design surface.

3. **Provenance guarantee**
   - The contained workspace includes or is paired with a durable note
     explaining source fork, upstream lineage, and maintenance intent.

4. **Traceability guarantee**
   - A collaborator can trace from `ROADMAP.md` and discussion #41 to the active
     spec/review thread and then to the contained workspace commit that executed
     the move.

5. **Re-entry guarantee**
   - A collaborator re-entering the slice does not need operator memory of prior
     sessions. Repo artifacts are sufficient.

## Non-Goals

- This contract does not decide the exact git command sequence for the import.
- This contract does not amend canonical design or constitutional artifacts.
- This contract does not define Phase 2 evaluation logic or session-bundle
  schema.

## Acceptance Check

The contract is satisfied when:

- `cc-connect/` exists and is populated
- active docs point to it as the implementation surface
- provenance is legible
- build/test and review traceability checks pass
