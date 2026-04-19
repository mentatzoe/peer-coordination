# Drift-Audit Workflow (v1 scaffolding)

**Runtime artifact** — how auditors actually run the drift-audit procedure on a closed session bundle and commit the result. Paired with [`RUBRIC.md`](RUBRIC.md) (which defines *what* drift is) — this file defines *how* the audit is executed, reconciled, committed, and re-audited.

**Authoritative spec**: [`specs/008-drift-audit-workflow/spec.md`](../../specs/008-drift-audit-workflow/spec.md).
**Scope boundary**: this file is the operator-facing procedure. Schema for `drift-audit.json` is owned by [spec 005 data-model](../../specs/005-drift-audit-rubric/data-model.md); rubric content is owned by [`RUBRIC.md`](RUBRIC.md). This file does not redefine either.

---

## When to use which path

| Situation | Path |
|---|---|
| Closed session bundle, exploratory / pre-calibration audit, single auditor | **Path A — Single-auditor** |
| Closed session bundle, counted Phase 3 session, independent review required | **Path B — Two-auditor** |
| Prior audit exists, rubric evolved OR upgrading single → two-auditor | **Path C — Re-audit / upgrade** |

> **Counted sessions require Path B** for H1/H2 evidence eligibility per constitution v1.5.0 Principle IV (independent review). Single-auditor audits on counted sessions must be upgraded via Path C before the session is eligible.

---

## Prerequisites (common to all paths)

Verify before starting any audit:

1. `observations/sessions/<session-id>/` exists and is closed per [spec 001](../../specs/001-session-bundle-skeleton/spec.md):
   - `transcript.md` present (non-empty; zero-turn transcripts still produce a valid file per [spec 006](../../specs/006-discord-transcript-export/spec.md))
   - `meta.json` present with `session_id`, `pinned_rules_ref`, `closed_at`
   - `interventions.json` present (may be empty per the Codex intervention-tagging slice; this workflow treats the shape opaquely)
2. `observations/drift-audits/RUBRIC.md` has no uncommitted working-tree changes (rubric version must resolve to a committed SHA per [FR-002](../../specs/008-drift-audit-workflow/spec.md)).
3. You have write access to the session bundle's branch / main, per [`docs/ways-of-working/pull-requests.md`](../../docs/ways-of-working/pull-requests.md).

If any prerequisite fails, see **Halt conditions** below — fix upstream first; do not paper over.

---

## Path A — Single-auditor audit

*Filled by US1 — see `specs/008-drift-audit-workflow/quickstart.md` Path A until this section lands.*

## Path B — Two-auditor audit (counted sessions)

*Filled by US2 — see `specs/008-drift-audit-workflow/quickstart.md` Path B until this section lands.*

## Path C — Re-audit and single→two upgrade

*Filled by US3 — see `specs/008-drift-audit-workflow/quickstart.md` Path C until this section lands.*

---

## Halt conditions

*Filled by US1 — see `specs/008-drift-audit-workflow/quickstart.md` "Halt conditions" until this section lands.*

---

## Post-commit sanity checks

*Filled by US1 — see `specs/008-drift-audit-workflow/quickstart.md` "Sanity checks" until this section lands.*

---

## Downstream consumption

*Filled by US3 — pointer to spec 005 §8 + contract C8 about consumers reading `drift-audit.json.verdict` directly.*

---

## Cross-references

- **Spec chain**: [`specs/008-drift-audit-workflow/spec.md`](../../specs/008-drift-audit-workflow/spec.md) → [`plan.md`](../../specs/008-drift-audit-workflow/plan.md) → [`tasks.md`](../../specs/008-drift-audit-workflow/tasks.md)
- **Contracts**: [`specs/008-drift-audit-workflow/contracts/workflow-contracts.md`](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md) (C1–C8)
- **Quickstart** (operator walkthrough, more verbose): [`specs/008-drift-audit-workflow/quickstart.md`](../../specs/008-drift-audit-workflow/quickstart.md)
- **Commit taxonomy**: [`COMMIT-TAXONOMY.md`](COMMIT-TAXONOMY.md) — grep-able vocabulary for audit amend commits
- **Rubric content**: [`RUBRIC.md`](RUBRIC.md) (spec 005)
- **Bundle contract**: [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md) FR-008 (where `drift-audit.json` lives), FR-014 (bundle-amend-commit convention)
- **H2 composition**: spec 005 §8 and workflow contract C8

---

## Scope boundary (explicit)

- **In scope**: audit execution procedure, reconciliation, commit format, re-audit and upgrade paths.
- **Out of scope**: rubric content (spec 005 / `RUBRIC.md`), `drift-audit.json` schema (spec 005 `data-model.md`), intervention-tag shape (Codex slice), LLM automation (deferred follow-on; entry criteria documented in the Path B LLM-judge block), KPI rollup (Phase 5 slice).
