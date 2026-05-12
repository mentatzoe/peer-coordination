# Session Bundles Changelog

Convenience log of session-bundle runtime-surface changes. Git log is authoritative; this file is a human-readable summary for runtime-directory evolution.

## 2026-04-22 — workflow v1 (single-author + agent-drafted paths landed)

Session-summary workflow scaffolding per [spec 009](../../specs/009-session-summary-workflow/spec.md) — complements the existing session-bundle skeleton (spec 001) + drift-audit workflow (spec 008) with the runtime-facing summary-authoring procedure.

New files:

- [`SUMMARY-WORKFLOW.md`](SUMMARY-WORKFLOW.md) — how auditors author `summary.md` for a closed session bundle. Currently landed: Path A (single-author) + Path B (agent-drafted + operator-ratified) + Halt conditions + Post-commit sanity checks + Downstream consumption + LLM-assisted authoring entry criteria. Paths C (revision) and D (peer-audit) land in follow-on commits within this slice.
- [`SUMMARY-TAXONOMY.md`](SUMMARY-TAXONOMY.md) — grep-able vocabulary for summary amend commits: four taxonomy tokens (absent / `[peer-audited by <id>]` / `revision: <reason>` / `revision: drift-refresh, supersedes <old-sha>`), combined-token examples, and the drift-audit version pinning convention. Mirrors spec 008's `observations/drift-audits/COMMIT-TAXONOMY.md` pattern.

Updated files:

- [`_template/summary.md`](_template/summary.md) — refactored to the hybrid inverted-pyramid structure (Seed → Verdicts → Drift → What happened) per spec 009 FR-010. Per-peer contributions + observed coordination patterns now live within `## What happened` as free-form prose (no fixed sub-heading required) per FR-003. Verdict lines follow the R2 grep-stable format for downstream KPI rollup parsing.
- [`README.md`](README.md) — point running auditors at `SUMMARY-WORKFLOW.md` alongside the existing bundle-workflow docs; disambiguate the bundle-level authoring discipline (here) from the summary-authoring procedure (in `SUMMARY-WORKFLOW.md`).

Authored by Claude; operator-reviewed. Single-author + agent-drafted MVP ships first; revision + peer-audit lifecycle paths follow in Phase 5 of the spec 009 tasks.
