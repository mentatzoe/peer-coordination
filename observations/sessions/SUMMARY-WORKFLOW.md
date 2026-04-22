# Session-Summary Workflow (v1 scaffolding)

**Runtime artifact** — how auditors actually author the qualitative `summary.md` for a closed session bundle, commit it against a conforming amend-commit format, revise when needed, and (optionally) invite peer-audit without rewriting bundle history.

**Authoritative spec**: [`specs/009-session-summary-workflow/spec.md`](../../specs/009-session-summary-workflow/spec.md).
**Runtime companions**: paired with [`observations/drift-audits/WORKFLOW.md`](../drift-audits/WORKFLOW.md) (spec 008 drift-audit procedure) — drift-audit MUST land before summary authoring begins.
**Scope boundary**: this file is the operator-facing procedure. The `summary.md` structural invariants are owned by [spec 009 spec.md FR-003 + FR-010](../../specs/009-session-summary-workflow/spec.md); the `drift-audit.json` schema (which summaries cite) is owned by [spec 005 data-model](../../specs/005-drift-audit-rubric/data-model.md); bundle file list is owned by [spec 001](../../specs/001-session-bundle-skeleton/spec.md). This file does not redefine any of them.

---

## When to use which path

| Situation | Path |
|---|---|
| Closed session bundle, operator composes prose AND records verdicts (simplest) | **Path A — Single-author** |
| Closed session bundle, peer agent (Dalgos / Vigil) or delegated human drafts prose; operator edits + records verdicts + commits | **Path B — Agent-drafted + operator-ratified** |
| Prior `summary.md` exists; needs correction (typo, late H2 verdict, drift-refresh after spec 008 Path C re-audit) | **Path C — Revision** |
| Prior `summary.md` exists; peer reviewer audits it post-commit (optional, adds to discoverable peer-audit ledger) | **Path D — Peer-audit** |

> **Path A vs Path B is the operator's per-session choice**, per FR-004 tiered discipline. Neither is "default" — the operator applies their effort / fairness / compression heuristic. Both produce a single committed `summary.md`; only the commit-body `Mode:` line and drafter-identity attribution differ.

---

## Prerequisites (common to all paths)

Verify before starting any summary:

1. `observations/sessions/<session-id>/` exists and the bundle is closed per [spec 001](../../specs/001-session-bundle-skeleton/spec.md):
   - `transcript.md` present (non-empty; zero-turn transcripts still produce a valid file per spec 006).
   - `meta.json` has `session_id`, `pinned_rules_ref`, `closed_at`.
   - `interventions.json` present as an array of intervention objects per spec 001 FR-011 (empty array = valid empty case).
   - `drift-audit.json` committed per the spec 008 workflow ([`observations/drift-audits/WORKFLOW.md`](../drift-audits/WORKFLOW.md)).
2. Working tree is clean of unrelated changes.
3. You have write access to the session bundle's branch / main per `docs/ways-of-working/pull-requests.md`.

If any prerequisite fails, see **Halt conditions** below; fix upstream first — do not produce a partial `summary.md`.

---

## Path A — Single-author

*Filled by US1 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) Path A until this section lands.*

## Path B — Agent-drafted + operator-ratified

*Filled by US1 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) Path B until this section lands.*

## Path C — Revision

*Filled by US3 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) Path C until this section lands.*

## Path D — Peer-audit

*Filled by US3 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) Path D until this section lands.*

---

## Halt conditions

*Filled by US1 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) "Halt conditions" until this section lands.*

---

## Post-commit sanity checks

*Filled by US1 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) "Post-commit sanity checks" until this section lands.*

---

## Downstream consumption

*Filled by US1 — pointer to spec 005 §8 equivalent + contract C8 about KPI rollup reading verdict lines directly.*

---

## LLM-assisted authoring (deferred)

*Filled by US1 — entry-criteria block for the deferred LLM-assisted path per FR-014 + FR-015.*

---

## Cross-references

- **Spec chain**: [`specs/009-session-summary-workflow/spec.md`](../../specs/009-session-summary-workflow/spec.md) → [`plan.md`](../../specs/009-session-summary-workflow/plan.md) → [`tasks.md`](../../specs/009-session-summary-workflow/tasks.md)
- **Contracts**: [`specs/009-session-summary-workflow/contracts/workflow-contracts.md`](../../specs/009-session-summary-workflow/contracts/workflow-contracts.md) (C1–C8)
- **Quickstart** (spec-facing walkthrough): [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md)
- **Commit taxonomy**: [`SUMMARY-TAXONOMY.md`](SUMMARY-TAXONOMY.md) — grep-able vocabulary for summary amend commits
- **Drift-audit runtime companion**: [`../drift-audits/WORKFLOW.md`](../drift-audits/WORKFLOW.md) (spec 008)
- **Rubric content**: [`../drift-audits/RUBRIC.md`](../drift-audits/RUBRIC.md) (spec 005)
- **Bundle contract**: [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md) FR-007 (summary presence), FR-008 (drift-audit presence), FR-012 (required content), FR-014 (bundle-amend-commit convention)
- **Per-session clear definitions**: [`design/poc.md`](../../design/poc.md) — the judgment thresholds for H1 stability / H1 complementarity / H2 fresh-reader-pass
- **H2 composition reminder**: the `## Drift` section's consumer-direction rules mirror spec 008 contract C8 — consumers MUST read `drift-audit.json.verdict` directly, not re-derive

---

## Scope boundary (explicit)

- **In scope**: authoring procedure (Paths A/B), revision + peer-audit lifecycle (Paths C/D), hybrid inverted-pyramid structure for `summary.md`, drift-citation discipline.
- **Out of scope**: rubric content (spec 005 / `RUBRIC.md`), drift-audit procedure (spec 008 / `drift-audits/WORKFLOW.md`), `drift-audit.json` schema (spec 005 `data-model.md`), per-object intervention-tag schema (Codex slice — top-level array-of-objects shape honored per spec 001 FR-011), LLM automation (deferred follow-on with entry criteria below), KPI rollup (Phase 5 slice).
