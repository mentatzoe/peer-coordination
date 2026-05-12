# Research: Intervention-Tagging Workflow

**Branch**: `011-intervention-tagging` | **Date**: 2026-05-05
**Input**: Clarification decisions and planning unknowns from [spec.md](spec.md).

## Decision 1: Required authoring path is post-session annotation

**Decision**: The operator MUST produce the committed `interventions.json` after transcript availability and before summary authoring. Live notes are allowed as scratch input only.

**Rationale**: `design/poc.md` already names a post-session annotation window and warns that evaluation should remain passive/post-session. Post-session tagging avoids distorting live peer behavior and lets the operator review transcript context before assigning type/reason.

**Alternatives considered**:

- **Live Discord slash command**: rejected for v1 because it requires transport/UI work and risks changing live behavior.
- **Both live and post-session as first-class evidence**: rejected for v1 because it creates conflict rules between live and reviewed tags; the reviewed post-session log should be the single source of truth.

## Decision 2: Preserve top-level array shape

**Decision**: `interventions.json` remains a top-level JSON array; each record carries its own `taxonomy_version`.

**Rationale**: spec 001, current README, and `_template/interventions.json` all define `[]` as the valid empty case. Changing to an object wrapper would break existing bundle-init tooling and adjacent consumers. A per-record version field gives schema traceability without changing the artifact envelope.

**Alternatives considered**:

- **Object wrapper with `taxonomy_version` and `records`**: cleaner metadata shape, but incompatible with spec 001 and the existing template.
- **No version field**: lower friction but weakens reproducibility when taxonomy changes after early POC sessions.

## Decision 3: Stable session-local ids plus citation keys

**Decision**: Intervention records use `iv-###` ids unique within the session. Same-bundle citation keys use `interventions.json#iv-###`; cross-bundle citations use `observations/sessions/<session-id>/interventions.json#iv-###`.

**Rationale**: downstream artifacts need a stable pointer that survives reason/target corrections. Session-local ids are easier for operators to read than UUIDs and sufficient because bundle path scopes uniqueness.

**Alternatives considered**:

- **Timestamp-only citations**: rejected because multiple interventions can apply to the same turn or session.
- **UUIDs**: globally unique but too noisy for hand-authored session evidence.

## Decision 4: Target object supports turn, span, and session

**Decision**: `target` is one of turn, span, or session. Multi-turn redirects SHOULD be one span record.

**Rationale**: the issue explicitly asks per-turn vs per-span. A span object captures continuous operator intervention without inflating directive counts. A session target covers no-turn or whole-session interventions such as close/resume.

**Alternatives considered**:

- **One record per turn only**: inflates counts and obscures one intervention that spans several turns.
- **Span only**: cumbersome for common single-turn clarification tags.

## Decision 5: Attribution enum is mandatory and narrow

**Decision**: `attribution` is required and limited to `operator_directed` and `agent_self_flagged` in v1.

**Rationale**: H1 needs a clean operator-load numerator. Agent self-flags are useful as a coordination signal but should not be mixed into operator-directed intervention load. A narrow enum avoids prematurely modeling inference or automation sources.

**Alternatives considered**:

- **Free-text attribution**: flexible but not countable.
- **Broader enum including `system_inferred`**: rejected because system inference is out of scope for post-session manual tagging.

## Decision 6: Repo-owned CLI validates before writing

**Decision**: Implement `peer-session intervention add` and `peer-session intervention validate` in the existing `tools/peer_session/` package.

**Rationale**: spec 007 already created repo-owned session-bundle tooling and tests. Extending that surface keeps tagging in the bundle layer and gives the Phase 2 dry-run a real executable path without touching transport.

**Alternatives considered**:

- **Docs-only manual editing**: too easy to drift and does not satisfy "path works" as strongly.
- **Standalone script**: creates another operator surface when `peer-session` already exists.

## Decision 7: Commit subject pins transcript provenance

**Decision**: Intervention amend commits use `session bundle amend: <session-id> — interventions[ <taxonomy-token>] @ <transcript-short-sha>`.

**Rationale**: intervention tags are authored against the transcript. Pinning the transcript commit mirrors spec 008/009 `@ <short-sha>` conventions and lets reviewers reconstruct which transcript version was tagged.

**Alternatives considered**:

- **No SHA suffix**: easier, but weakens traceability after transcript corrections.
- **Pin pinned-rules ref**: rules matter for drift, but intervention tags point at transcript turns and operator actions.
