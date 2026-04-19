# Implementation Plan: Pinned-Rules Authoring and Exposure

**Feature**: `003-pinned-rules-authoring`
**Spec**: [`spec.md`](spec.md)
**Status**: Draft
**Created**: 2026-04-19
**Author**: Claude (self-authored per operator directive authorizing autonomous speckit progression)

## Summary

Small scope: create a repo-root `pinned-rules/` directory with a workflow README and a seed `current.md`. No runtime code, no cc-connect changes, no external dependencies. One commit'"'"'s worth of file creation + a CHANGELOG stub.

## FR → artifact mapping

| FR(s) | Produces |
|---|---|
| FR-001 | `pinned-rules/` directory (implicit — created when first file is added) |
| FR-002 | `pinned-rules/current.md` seeded with v1 rules content |
| FR-003 | `pinned-rules/README.md` covering authoring workflow, commit-ref contract, Discord exposure mechanism, edit-and-new-session rule, cross-references |
| FR-004 | `pinned-rules/CHANGELOG.md` optional stub — include as a convenience |
| FR-005 | Documented in `README.md` + this commit itself uses the convention (`pinned-rules: add initial scaffolding and seed v1 content`) |
| FR-006, FR-007, FR-008 | Constraints documented in `README.md`; seed `current.md` abides by them |
| FR-009, FR-010, FR-011 | Documented in `README.md` (operator-only authoring, re-pin-before-new-session, `pinned_rules_ref` contract) |
| FR-012 | Seed `current.md` includes all required content (emoji palette, `!stop`/`!resume`, turn-taking heuristics, escalation path, Principle VI reference) |
| FR-013 | Seed content cites VISION/architecture/constitution rather than duplicating |
| FR-014 | Seed content kept under 1500 chars rendered |

## Implementation steps (ordered)

1. **Create `pinned-rules/` directory** (implicit).
2. **Author `pinned-rules/README.md`**: authoring workflow, commit-ref contract with session bundles, Discord exposure, re-pin discipline, cross-references.
3. **Author `pinned-rules/current.md`** seed v1 content: emoji palette, `!stop`/`!resume`, turn-taking (yielding / claiming / building as heuristics), escalation path, Principle VI reference.
4. **Author `pinned-rules/CHANGELOG.md`** stub: initial entry for v1 (this commit).
5. **Verify length**: seed `current.md` under ~1500 rendered chars.
6. **Cross-reference check**: no stale pointers in `session-bundle-skeleton/spec.md` or `observations/sessions/README.md` need updating — `pinned_rules_ref` contract is already spec-level in spec 001 FR-010 and doesn'"'"'t need to be edited here.
7. **Commit** with the discrete-commit convention.

## Non-steps (explicitly deferred)

- No cc-connect automation for pin synchronization (operator-manual in Phase 1).
- No agent-authored rule-change PRs (operator-only in Phase 1).
- No Layer 2 / Layer 3 spec extraction from rules content.
- No rules versioning in filenames (`v1.md` / `v2.md` etc. — rejected in favor of single `current.md` + git commits).
- No operator-UX tooling for authoring rules (prose editing in the repo is sufficient for Phase 1).

## Commit message

```
spec(003): pinned-rules authoring/exposure scaffolding

Spec + plan + v1 seed content per
specs/003-pinned-rules-authoring/spec.md. Creates pinned-rules/ at
repo root with current.md (v1 seed), README.md (authoring + exposure
workflow), and CHANGELOG.md stub.

Scope: authoring workflow and exposure-via-Discord-pin for the
canonical L2 coordination ruleset. Commit-hash references from
session bundles' meta.json.pinned_rules_ref resolve to the exact
rules active at session open. Rules change = session break per
design/poc.md session definition.

Open questions self-resolved inline per operator directive
authorizing autonomous speckit progression; cross-reviewer may
amend retroactively.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

## Post-implementation

- Update status manifest on [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41): Claude slice complete through Phase 1 (spec 001 + spec 003 both implemented).
- Open review thread for spec 003 (discussion template) with retrospective cross-review request.
- Nothing else outstanding on the Claude Phase 1 slice.
