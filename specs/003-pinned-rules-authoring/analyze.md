# Analysis: Pinned-Rules Authoring and Exposure

**Input**: `spec.md`, `plan.md`, `tasks.md`, and the implementation under `pinned-rules/`.
**Date**: 2026-04-19
**Scope**: retrospective consistency check between specified, planned, tasked, and implemented. Retrofit analysis after the slice landed on `main` in `2b740e2`.

## Findings

### 1. Spec → plan

- All 14 FRs (FR-001 through FR-014) are reflected in `plan.md`'s FR-to-artifact mapping.
- Content-constraint FRs (FR-012 required content, FR-013 no governance duplication, FR-014 size cap) mapped to the seed `current.md` authoring step + a verify-length step.
- Success criteria SC-001–SC-005 are behavioral assertions, measured at runtime in Phase 3; not everything a plan can guarantee in advance. Acceptable.
- **No drift.**

### 2. Plan → tasks

- Plan's 7-step implementation sequence is covered by `tasks.md` T001–T008 across Phases 1–6.
- Non-steps in the plan are reflected as "Not in this task list" section in tasks.md.
- Self-resolved clarifications (T009) captured as a polish task mapping back to spec.md's "Clarifications applied" block.
- **No drift.**

### 3. Tasks → implementation

Cross-check against repo state at this branch's HEAD:

| Task | Expected artifact | Present on disk |
|---|---|---|
| T001 | `pinned-rules/` directory | ✓ |
| T002 | `pinned-rules/README.md` | ✓ |
| T003 | `pinned-rules/current.md` with v1 seed content | ✓ |
| T004 | `current.md` under 2000 rendered chars | ✓ (measured 1475 rendered chars) |
| T005 | Commit-discipline section in `README.md` | ✓ |
| T006 | Session-break-on-rules-change section in `README.md` | ✓ |
| T007 | Cross-reference to spec 001 FR-010 in `README.md` | ✓ |
| T008 | `pinned-rules/CHANGELOG.md` stub with v1 seed entry | ✓ |
| T009 | "Clarifications applied" section in `spec.md` | ✓ |

**No drift.**

### 4. Implementation → spec

Content check on `pinned-rules/current.md` against FR-012 required content:

| FR-012 required element | Present in seed |
|---|---|
| Emoji palette definition (✅ 👀 🤔 🚫 ⏸️) | ✓ with defined semantics per emoji |
| `!stop` / `!resume` semantics | ✓ |
| Turn-taking expectations as heuristics | ✓ (yielding / claiming / building) |
| Escalation path for unresolved ambiguity | ✓ (address operator + state question) |
| Reference to governing principles (Principle VI) | ✓ (references section at bottom) |

FR-013 (no governance text duplication): seed cites constitution / POC / architecture by reference, does not restate. ✓

FR-014 (under 1500 rendered chars for single Discord pin): 1475 chars. ✓ (tight; next amendment may trigger the FR-007 split pattern).

**No drift.**

## Cross-artifact consistency

- `spec.md` ↔ `design/poc.md`: pinned-rules change closes session; session close triggers match (`pinned_rules_change` in the close_reason enum). Consistent.
- `spec.md` ↔ `design/architecture.md` Layer 2: rules content is a thin visible norm set; architecture says norms come from a separate artifact (this spec's `current.md`) made visible in-channel (via Discord pin). Consistent.
- `spec.md` ↔ `specs/001-session-bundle-skeleton/spec.md`: `pinned_rules_ref` contract in spec 001 FR-010 is honored by the commit-hash-ref workflow documented in `pinned-rules/README.md`. Cross-links present in both directions.
- `spec.md` ↔ constitution Principle VI: rules framing (heuristics over protocol, human-legible) matches. Rules cite the principle without duplicating. Consistent.

## Follow-up items surfaced by this analysis

None substantive. One watch-item for future amendments:

- FR-014's 1500-char soft limit is already tight at 1475 chars. The next substantive amendment may trip it, triggering FR-007's split pattern (summary pin + repo link). Not a bug in v1; just a design budget to keep in mind.

## Verdict

**No drift detected.** Spec 003 scaffolding is internally consistent, consistent with spec 001's consumer contract, and consistent with the canonical design artifacts. Ready for Phase 1 exit-gate consideration on the Claude side.
