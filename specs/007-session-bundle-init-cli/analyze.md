# Analysis: Session Bundle Init CLI

**Input**: `spec.md`, `plan.md`, `tasks.md`, and the implemented repo-owned CLI under `peer-session`, `tools/peer_session/`, and `tests/peer_session/`.
**Date**: 2026-04-19
**Scope**: retrospective consistency check between the clarified spec, implementation plan, generated tasks, and shipped `peer-session init` behavior before PR/review handoff.

## What speckit-analyze checks

The `analyze` stage looks for drift between:

1. **Spec → plan**: are the slice requirements represented in the implementation plan?
2. **Plan → tasks**: are the planned behaviors and files broken into executable tasks?
3. **Tasks → implementation**: are the completed tasks reflected on disk?
4. **Implementation → spec**: does the resulting CLI satisfy the slice contract without quietly changing the bundle rules?

Drift in any direction is a finding.

## Findings

### 1. Spec → plan

- The plan preserves the spec's core position: repo-owned Python CLI, no `cc-connect` imports, filesystem-first bundle initialization, defaults file + override flags, truthful `pinned_rules_ref`, and omission of `meta.json.transcript_source` at init time.
- FR-001 through FR-012 are all represented in `plan.md`'s implementation strategy and the Phase 0 design decisions.
- Success criteria SC-001 through SC-004 are runtime/operator outcomes, but the plan includes the concrete CLI surface and test approach needed to support them.
- **No drift.**

### 2. Plan → tasks

- The plan's repo-root CLI/package structure maps directly to setup/foundational tasks T001–T008.
- The plan's init-only MVP path maps to US1 tasks T009–T013.
- The plan's initialized-bundle clarity/defaults behavior maps to US2 tasks T014–T018.
- The plan's truthful pinned-rules provenance and future-extensible CLI boundary map to US3 tasks T019–T023.
- The verification and consistency gate in the plan map to polish tasks T024–T026.
- **No drift.**

### 3. Tasks → implementation

Cross-checked against the current `007-session-bundle-init-cli` branch head:

| Task area | Expected artifact | Present on disk |
|---|---|---|
| Repo-root CLI surface | `peer-session`, `tools/peer_session/cli.py` | ✓ |
| Defaults handling | `observations/sessions/defaults.example.toml`, `tools/peer_session/defaults.py` | ✓ |
| Bundle-init library | `tools/peer_session/bundle_init.py` | ✓ |
| Pinned-rules provenance helper | `tools/peer_session/git_refs.py` | ✓ |
| Test suite | `tests/peer_session/test_bundle_init.py`, `tests/peer_session/test_cli.py`, `tests/peer_session/test_support.py` | ✓ |
| Operator docs | `observations/sessions/README.md`, `specs/007-session-bundle-init-cli/quickstart.md` | ✓ |

Specific task claims verified by implementation:

- T001–T004: the repo-owned executable, package scaffold, ignore coverage, defaults template, and argparse CLI skeleton are all present.
- T005–T008: defaults loading, pinned-rules provenance resolution, template/session-id validation, bundle-copy primitives, and shared temp-repo test helpers are all implemented.
- T009–T013: tests and implementation cover successful init, CLI entrypoint success/failure propagation, invalid/existing-target failures, and `meta.json` mechanical field population.
- T014–T018: tests and implementation cover override precedence, omission of `transcript_source`, preservation of pending placeholders, required-template-file failures, and local-defaults/operator docs.
- T019–T023: tests and implementation cover clean-vs-dirty pinned-rules behavior, the init-only CLI surface, and the documented future-extension boundary.

**No drift.**

### 4. Implementation → spec

- FR-001/FR-012: the command surface is `peer-session`, v1 is `init` only, and the CLI remains repo-owned under `tools/peer_session/` rather than `cc-connect`.
- FR-002/FR-005/FR-011: `initialize_bundle()` creates the target bundle from `_template/` and fails cleanly if the target already exists.
- FR-003/FR-004/FR-006/FR-010: `meta.json` is rewritten only for the mechanical fields the slice owns, while qualitative/late-session placeholders remain intact and `transcript_source` is removed entirely.
- FR-007: implementation uses Python standard library only and does not import or require `cc-connect`.
- FR-008/FR-009: `observations/sessions/defaults.example.toml`, `defaults.py`, and CLI override flags provide the specified local-defaults pattern.
- Provenance behavior from the contract is honored: clean `pinned-rules/current.md` yields a commit hash; dirty rules fall back to an inline snapshot.

One current limitation is worth naming explicitly:

- The tests and implementation cover the contract-bearing init path and key edge cases, but the bundle-init library does not yet enforce richer participant-shape validation beyond "at least one peer, one operator handle, and a channel ID." That is acceptable within the current slice contract because the defaults schema is intentionally narrow and role construction is deterministic.

**No drift.**

## Cross-artifact consistency

- `spec.md` ↔ `specs/001-session-bundle-skeleton/spec.md`: the init CLI copies the canonical bundle skeleton and avoids redefining bundle structure; it only fills or removes the fields the clarified `007` spec owns.
- `spec.md` ↔ `observations/sessions/README.md`: the new local-defaults section now matches the planned `peer-session init` workflow instead of leaving bundle-init purely manual.
- `spec.md` ↔ constitution: the implementation stays artifact-first and repo-owned, keeps human-authored surfaces visibly pending, and does not move governance into the contained transport workspace.

## Follow-up items surfaced by this analysis

- None blocking for this slice.
- A future follow-up could broaden validation around malformed defaults content or more explicit participant-shape error messages, but the current behavior already satisfies the bounded v1 contract.

## Verdict

**No drift detected.** The slice is internally consistent across spec, plan, tasks, and implementation. `peer-session init` is implemented as the repo-owned, init-only bundle bootstrap command the slice called for, with targeted `unittest` coverage and the expected `analyze.md` artifact in place.
