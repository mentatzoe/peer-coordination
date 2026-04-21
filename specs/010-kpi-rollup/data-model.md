# Phase 1 Data Model: KPI Rollup

**Feature**: KPI Rollup
**Branch**: `010-kpi-rollup`

This document defines the data entities this slice introduces or consumes. Full serialized schemas (field types, enums, examples, fill-in guidance) live in `observations/sessions/_template/README.md` per the FR-023 clarification; this file carries the conceptual model, relationships, and validation rules.

---

## Entities

### `KPIFile` — `observations/sessions/<session-id>/kpi.json`

The deterministic per-session KPI record written by `peer-session tally`. New to spec 010; additive to the spec-001 bundle shape.

**Fields (conceptual — see template README for the serialized schema):**
- `session_id` — must match the enclosing directory name and `meta.json.session_id`.
- `tallied_at` — ISO-8601 timestamp with at least second precision (FR-003).
- `inputs_hash` — SHA-256 hex digest over the canonicalized inputs per research §1.
- `intervention_count` — integer, total count from `interventions.json`.
- `intervention_type_tally` — object mapping each intervention-type in the spec-001 FR-011 frozen taxonomy to a count (with zeros for absent types).
- `intervention_rate_per_turn` — decimal OR `null` when `zero_turn_session` is `true`.
- `zero_turn_session` — boolean; `true` iff the transcript has no peer turns.
- `drift_audit_verdict` — snapshot copied from `drift-audit.json`'s verdict field (opaque pass-through from spec 008).
- `per_session_clear` — top-level composite: `cleared | not-cleared | ambiguous`.
- `per_session_clear_breakdown` — object with the six sub-judgments from research §4, each `cleared | not-cleared | ambiguous` plus an optional `reason` for non-cleared or ambiguous results.
- `notes` — optional free-text field for `peer-session tally` to record diagnostic notes (e.g., "drift-audit.json is still the spec-001 placeholder").

**Validation rules:**
- `session_id` MUST match directory name (FR-003, FR-015).
- `tallied_at` MUST be present and ISO-8601 parseable.
- `inputs_hash` MUST be present; absence is a hard error (SC-002 idempotence depends on this).
- `intervention_type_tally` MUST contain all six taxonomy keys (safety_stop, clarification, directive_redirect, drift_catch, close_or_resume, other), each with a non-negative integer count.
- `per_session_clear` MUST follow the composite rule: `not-cleared` if any breakdown entry is `not-cleared`; `ambiguous` if any is `ambiguous` and none are `not-cleared`; `cleared` only if all are `cleared`.

**State transitions:**
- `absent` → `created` — first successful `peer-session tally` run.
- `created` → `recomputed` — subsequent `peer-session tally` runs update `tallied_at`, `inputs_hash`, and any changed fields but preserve `session_id`.
- `stale` — detected at rollup time by comparing `inputs_hash` against a freshly computed hash of current bundle inputs. Staleness is surfaced but not auto-resolved; operator re-runs tally.

---

### `FreshReaderAudit` — `observations/sessions/<session-id>/fresh-reader-audit.json`

The operator-authored H2 fresh-reader verdict per session. New to spec 010; additive to the spec-001 bundle shape. Resolved by the 2026-04-21 clarification session.

**Fields (conceptual):**
- `session_id` — must match the enclosing directory name.
- `audited_at` — ISO-8601 timestamp, at least second precision.
- `auditor` — the fresh reader's handle or identity.
- `verdict` — one of `pass`, `fail`, `inconclusive`.
- `reasoning` — free-text operator note describing what the fresh reader could and couldn't reconstruct from the preserved bundle (per poc.md's H2 definition).

**Validation rules:**
- Presence is NOT required by `peer-session tally`; tally tolerates absence and marks `per_session_clear_breakdown.h2_fresh_reader = "ambiguous"`.
- Presence IS required by `peer-session rollup` (hard gap per FR-013).
- `verdict` MUST be exactly one of the three enum values; unknown values are a tally/rollup error.

**State transitions:**
- `absent` — fresh-reader audit has not yet been authored.
- `authored` — operator completes via the workflow and commits.
- Mutation after commit: handled like spec 001 FR-014 — amend via a follow-up commit; no history rewrite.

---

### `POCExitFile` — `observations/poc-exit-<timestamp>.md`

The per-run rollup artifact, one per successful `peer-session rollup` invocation. New to spec 010. Resolved by the 2026-04-21 clarification toward the per-run-files model.

**Sections (required per FR-012):**
- Header with the rollup run timestamp.
- Counted-session total (`T` per research §9).
- Applied H1 decision-rule result (or out-of-range surface if `T < 3` or `T > 5`).
- Per-session-clear summary (one row per counted session, showing `per_session_clear` + breakdown highlights).
- H2 fresh-reader pass-rate across counted sessions.
- Episode-record completeness across counted sessions.
- Ratifiability state: `ratifiable` or `draft, not ratifiable`.
- Ratification-gate subsection (operator fills on ratification per the workflow).

**Immutability:**
- Once committed, a `POCExitFile` MUST NOT be rewritten or redacted (FR-025). Amendments to prior rollup sessions — e.g., adding ratification — are handled per the workflow's ratification convention (either editing the ratification-gate subsection of that specific file, or a documented follow-up commit).

---

### `POCExitPointer` — `observations/poc-exit.md`

A POSIX symlink whose target is the most recent `POCExitFile`. Created by the first successful rollup and updated (unlink + symlink) by each subsequent successful rollup per research §3.

**Validation rules:**
- MUST resolve to an existing `POCExitFile` in the same directory.
- MUST be updated atomically relative to the per-run file write (the per-run file is written first; the pointer is updated only if the write succeeded).

---

### `IntersessionRollupSnapshot` — in-memory only; never serialized

The ephemeral aggregate computed by `peer-session rollup` when processing the counted-session set. Consumes `KPIFile` + `FreshReaderAudit` per session and produces exactly one `POCExitFile`.

**Computed fields:**
- `counted_session_total` — number of bundles that passed discovery + completeness checks.
- `cleared_count` — count where `per_session_clear == "cleared"`.
- `not_cleared_count` — count where `per_session_clear == "not-cleared"`.
- `ambiguous_count` — count where `per_session_clear == "ambiguous"`.
- `decidable_total` — `cleared_count + not_cleared_count` (research §9).
- `h1_stable_coord_pass` — per research §9 decision rule.
- `h1_intervention_load_pass` — ditto.
- `h1_complementarity_pass` — ditto.
- `h2_fresh_reader_pass_rate` — `pass`-count over `decidable_total` (or total, depending on how `ambiguous` is counted — consistent with research §9).
- `h2_drift_pass` — all counted sessions have no load-bearing drift.
- `h2_episode_record_completeness` — 100% (hard gate per FR-013).
- `ratifiability` — `ratifiable` iff `ambiguous_count == 0` and `decidable_total` is in range; else `draft, not ratifiable`.
- `ambiguous_sessions` — list of session IDs flagged ambiguous; enumerated in the artifact.
- `out_of_range` — `true` iff `decidable_total < 3` or `decidable_total > 5`.

---

## Relationships

```text
SessionBundle (spec 001)                  <- already landed
  ├── meta.json
  ├── interventions.json
  ├── drift-audit.json                    <- spec 008
  ├── summary.md                          <- spec 009 (parallel work, this slice does not couple)
  ├── transcript.md
  ├── kpi.json                            <- NEW (this slice) — derived from all bundle files
  └── fresh-reader-audit.json             <- NEW (this slice) — operator-authored

ObservationsSurface
  └── poc-exit-<timestamp>.md             <- NEW (this slice) — aggregates kpi.json + fresh-reader-audit.json
  └── poc-exit.md  (symlink)              <- NEW (this slice) — points to latest

WorkflowSurface
  └── observations/kpi-rollup/
      └── WORKFLOW.md                     <- NEW (this slice) — operator authoring recipe
```

---

## Invariants

- **I1 (determinism)**: For any unchanged session bundle, re-running `peer-session tally` produces a `KPIFile` with byte-identical `per_session_clear`, `per_session_clear_breakdown`, `inputs_hash`, `intervention_count`, `intervention_type_tally`, `intervention_rate_per_turn`, `zero_turn_session`, and `drift_audit_verdict` fields. Only `tallied_at` is permitted to change.
- **I2 (non-destructive rollup)**: For any successful rollup run, a new `POCExitFile` is created and the `POCExitPointer` is updated; all prior `POCExitFile` instances remain unchanged.
- **I3 (schema additivity)**: The spec-001 bundle shape is extended only by optional-at-init, required-at-evaluation files (`kpi.json`, `fresh-reader-audit.json`). No spec-001 FR-001..FR-011 required file is modified or removed by this slice.
- **I4 (no transport coupling)**: No entity in this slice imports from or depends on the contained `cc-connect/` workspace at runtime (FR-021).
- **I5 (intervention-type taxonomy stability)**: `intervention_type_tally` keys match the spec-001 FR-011 frozen taxonomy exactly. Adding a new type requires a spec amendment there, not here.
