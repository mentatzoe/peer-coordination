# Implementation Plan: Session Bundle Skeleton

**Feature**: `001-session-bundle-skeleton`
**Spec**: [`spec.md`](spec.md)
**Status**: Draft
**Created**: 2026-04-19
**Author**: Claude (self-authored per operator directive authorizing autonomous speckit progression)

## Summary

The spec is small and mostly about creating durable scaffolding (directory + README + `_template/` with 5 stub files). No runtime code, no cc-connect changes, no dependencies landing first. Implementation is a single commit'"'"'s worth of file creation.

## FR → artifact mapping

| FR(s) | Produces |
|---|---|
| FR-001 | `observations/sessions/` directory (implicit — created when first file is added). |
| FR-002, FR-003 | Naming convention documented in `observations/sessions/README.md`. |
| FR-004 through FR-008 | File list documented in `observations/sessions/README.md` + `_template/` has one stub per required file. |
| FR-009 | `_template/transcript.md` stub with `[FILL IN]` turn format + source-selection note. |
| FR-010 | `_template/meta.json` stub with full required keys + placeholder values. |
| FR-011 | `_template/interventions.json` stub as empty array + comment showing the per-entry shape. |
| FR-012 | `_template/summary.md` stub with required section headings. |
| FR-013, FR-014, FR-015 | Commit-discipline + redaction paragraph in `observations/sessions/README.md`. |
| FR-016 | `observations/sessions/README.md` itself. |
| FR-017 | `_template/` directory with the 5 stub files + a one-line header in each pointing to the spec. |

## Implementation steps (ordered)

1. **Author `observations/sessions/README.md`**. Sections: purpose, naming rule (FR-002/003), required artifacts (FR-004-008), authoring discipline (FR-013-015), pointers to `specs/001-session-bundle-skeleton/spec.md` and `design/poc.md` Layer 3 artifact bundle.
2. **Create `observations/sessions/_template/`** directory.
3. **Author `_template/transcript.md`**: header line pointing to spec; `[FILL IN]` turn format showing timestamp + author + content; a note about preferred transcript source per FR-009.
4. **Author `_template/meta.json`**: all required keys from FR-010 with `[FILL IN]` string placeholders; include `transcript_source` field (default `"export"`); comments explaining each field via a companion `_template/README.md` rather than JSON comments (JSON doesn'"'"'t support comments cleanly).
5. **Author `_template/interventions.json`**: empty array `[]` with a one-example commented entry in the companion `_template/README.md`.
6. **Author `_template/summary.md`**: required section headings from FR-012 as placeholders.
7. **Author `_template/drift-audit.json`**: placeholder object `{"status": "pending-phase-2"}` per FR-008.
8. **Author `_template/README.md`**: explains how to copy and fill the template; shows per-file schemas since JSON can'"'"'t carry inline comments; links to spec.
9. **Verify layout**: `ls` the tree to confirm all 5 required files + the companion README are present in `_template/` and the parent `observations/sessions/README.md` exists.
10. **Commit** with one atomic commit message (see below).

## Non-steps (explicitly deferred)

- No actual session bundles created in this commit. The first real bundle lands when Phase 3 sessions begin.
- No KPI rollup script. That'"'"'s a separate Phase 2 spec.
- No drift-audit rubric detail. The stub just holds the placeholder.
- No intervention-tagging UX code. This spec defines storage shape only.
- No transcript export tooling. The operator or a later spec picks that up.

## Commit message

```
spec(001): implement session bundle skeleton

Land the scaffolding per specs/001-session-bundle-skeleton/spec.md:
- observations/sessions/README.md explaining the bundle pattern
- observations/sessions/_template/ with stubs for transcript.md,
  meta.json, interventions.json, summary.md, drift-audit.json
- observations/sessions/_template/README.md documenting the per-file
  schemas (since JSON does not carry comments)

All five functional requirement groups (directory layout, required
artifacts, schemas, authoring discipline, README + template) are
satisfied at the skeleton level. First real bundle lands in Phase 3.

Open questions in spec were self-resolved with best-judgment defaults
per operator directive authorizing autonomous speckit progression;
cross-reviewer (Codex) may push back retroactively via amend commits.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

## Post-implementation

- Update status manifest on [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41) with stage → `implementation-complete`.
- Post on [discussion #43](https://github.com/mentatzoe/peer-coordination/discussions/43) with the commit hash, the self-clarified open questions, and a cross-review request pinging both Zoe (for relay) and Codex.
- Close-out item for later: `CLAUDE.md` stale Transport MVP table (separate from this spec; tracked as Finding 5 of #39 and my commitment on #41).
