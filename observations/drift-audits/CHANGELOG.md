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
