# Research: cc-connect Relocation

## Decision 1: Import the fork under a top-level `cc-connect/` prefix

**Decision**: Bring the current `mentatzoe/cc-connect` fork into this
repository under a top-level `cc-connect/` directory.

**Rationale**:

- It satisfies the operator's clarified outcome: *"just move the entire repo to
  inside this repo."*
- A top-level prefix makes the subordinate implementation surface easy to find
  from the repo root and easy to distinguish from governance artifacts.
- The local fork already contains the relevant agent/platform surfaces for this
  POC (`agent/claudecode`, `agent/codex`, `agent/gemini`,
  `platform/discord`, `cmd/cc-connect`), so importing the fork as-is preserves
  the real implementation surface rather than a partial copy.

**Alternatives considered**:

- Keep using `~/github/cc-connect` as an external clone: rejected because it
  weakens durable handoff and contradicts the clarified direction.
- Import only selected subdirectories: rejected because the operator asked for
  the entire repo and partial import would obscure provenance and maintenance.
- Flatten the repo into the root of `peer-coordination`: rejected because it
  would blur governance and implementation boundaries.

## Decision 2: Use a subtree-style history-preserving import

**Decision**: Treat the move as a subtree-style import into `cc-connect/`,
preserving the fork's history inside this repository.

**Rationale**:

- It produces a genuinely contained workspace without leaving behind nested-git
  semantics that collaborators have to reason about every day.
- It preserves history and makes future audits easier than a raw file copy.
- It aligns with the spec's split between **outcome** (full move under this
  repo) and **mechanics** (chosen during planning).

**Alternatives considered**:

- Raw copy of files: rejected because it loses history and provenance.
- Git submodule: rejected because it keeps the implementation surface external
  in operational terms, which is the opposite of the chosen outcome.
- Unprefixed merge of unrelated histories: rejected because it would collapse
  implementation files into the governance root and damage legibility.

## Decision 3: Add an explicit provenance and boundary note

**Decision**: Add a small peer-coordination-owned note in or adjacent to
`cc-connect/` documenting source fork, upstream lineage, and the governance vs
implementation boundary.

**Rationale**:

- Git remotes alone are not a durable artifact surface; they do not explain the
  maintenance contract to a reviewer entering from the repo root.
- The constitution and architecture both require the transport/non-governance
  split to remain explicit.
- The move should improve reviewability, not make the imported workspace feel
  like new policy.

**Alternatives considered**:

- Rely only on commit history: rejected because it is too implicit for
  day-to-day re-entry.
- Rely only on discussion #41: rejected because discussion history should index
  the work, not be the only place the boundary is explained.

## Decision 4: Update active references, not archive history

**Decision**: Update active planning/guidance docs that still point to the
standalone local clone, but leave archive material untouched unless it becomes
misleading in current work.

**Rationale**:

- Active docs need to describe the current implementation surface for re-entry.
- Archive material exists for traceability and should not be rewritten just to
  erase the old path.
- This keeps the implementation pass bounded.

**Alternatives considered**:

- Rewrite all historical references: rejected because it adds noise and weakens
  traceability.
- Leave active references stale: rejected because it breaks the artifact-driven
  handoff model.

## Decision 5: Verify by build/test plus documentation traceability

**Decision**: Verify the move with both code-surface checks and artifact-surface
checks.

**Rationale**:

- A successful import is not enough if the contained workspace stops building.
- A successful build is not enough if collaborators still cannot discover where
  transport work now lives.
- Phase 1 needs both transport readiness and durable re-entry.

**Verification targets**:

- `go build ./cmd/cc-connect` inside `cc-connect/`
- targeted `go test` for the POC-relevant surfaces:
  - `./platform/discord`
  - `./agent/claudecode`
  - `./agent/codex`
  - `./agent/gemini`
- root-doc traceability checks for `README.md`, `CLAUDE.md`, `ROADMAP.md`, and
  this spec chain

## Execution note: imported source revision

The contained workspace was imported from local source-fork commit
`127939d330cfeee7063da624d22cd0541b430e3d` on 2026-04-19 using a
history-preserving `git subtree add --prefix=cc-connect ...` flow.
