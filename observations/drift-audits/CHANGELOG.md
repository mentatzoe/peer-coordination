# Drift-Audit Rubric Changelog

Convenience log of rubric changes. Git log is authoritative; this file is a human-readable summary.

## 2026-04-19 — v1 seed

Initial scaffolding per [spec 005](../../specs/005-drift-audit-rubric/spec.md).

RUBRIC.md v1 covers:

- Category definitions for the six drift categories: `undeclared_emoji`, `undeclared_abbreviation`, `private_shorthand`, `hidden_channel_reference`, `off_palette_load_bearing`, `other`
- Severity rules (`info` / `warn` / `finding`) and disambiguation guidance
- Verdict logic (deterministic from findings per FR-007)
- Manual-audit checklist (4-step walkthrough, ≤15 min target)
- How to author `drift-audit.json` with a worked example
- Versioning and calibration workflow
- LLM-judge prompt template (for Phase 3 session 3+ use after initial calibration)
- H2 per-session clear-definition composition guide

Authored by Claude (auto-seed); operator + Phase 3 sessions to calibrate as drift patterns emerge.

## 2026-04-20 — workflow v1 (single-auditor path landed)

Drift-audit workflow scaffolding per [spec 008](../../specs/008-drift-audit-workflow/spec.md) — complements the spec 005 rubric with the runtime-facing execution procedure.

New files:

- [`WORKFLOW.md`](WORKFLOW.md) — how auditors run the rubric on a closed session bundle. Currently landed: Path A (single-auditor) end-to-end, Halt conditions, Post-commit sanity checks, Cross-references. Paths B (two-auditor) and C (re-audit / upgrade) land in follow-on commits within this slice.
- [`COMMIT-TAXONOMY.md`](COMMIT-TAXONOMY.md) — grep-able vocabulary for audit amend-commits: absent (default) / `[arbitrated]` / `two-auditor-upgrade` / `re-run, supersedes <sha>`. Includes the arbitration-ledger grep convention that feeds calibration signal per RUBRIC.md §6.3.

Updated files:

- [`README.md`](README.md) — point running auditors at `WORKFLOW.md`; disambiguate this README as the rubric-authoring workflow (distinct from the audit-execution workflow now in `WORKFLOW.md`).

Authored by Claude; operator-reviewed. Single-auditor MVP ships first; counted-session two-auditor mode + re-audit follow in subsequent phases of spec 008.
