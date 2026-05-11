# Contract: `peer-session tally <session-id>`

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)
**Research**: [../research.md](../research.md)

Operator-visible contract for the per-session KPI extraction subcommand.

---

## Invocation

```text
peer-session tally <session-id>
```

- Positional argument `<session-id>` is required; it matches the enclosing `observations/sessions/<session-id>/` directory name and `meta.json.session_id`.
- No additional flags in v1. Future flags (e.g., `--dry-run`, `--check`) are out of scope for spec 010.

**Working directory**: the command MUST be invoked from the repository root (same convention as spec 007's `peer-session init`).

---

## Preconditions

- `observations/sessions/<session-id>/` exists and is not a template-prefixed directory (`_` or `.` prefix).
- The bundle satisfies spec-001 FR-001..FR-011: `meta.json`, `interventions.json`, `drift-audit.json`, `transcript.md`, `summary.md` are present and parseable as their documented types.
- `meta.json.closed_at` is NOT `null` (FR-007 — unclosed sessions are refused).
- `fresh-reader-audit.json` MAY be absent (tally tolerates; per-session-clear reflects the gap).

---

## Outputs

### Success output

- Writes `observations/sessions/<session-id>/kpi.json` conforming to the KPIFile entity in `data-model.md` and the schema in `observations/sessions/_template/README.md`.
- Stdout: one line — `wrote observations/sessions/<session-id>/kpi.json` — followed by a human-readable summary of the top-level `per_session_clear` and any ambiguous sub-judgments.
- Exit code: `0`.

### Failure output

- On bundle incompleteness (spec-001 FR-001..FR-011 not satisfied): stderr names the missing/invalid files; no `kpi.json` is written; exit code `2`.
- On unclosed session (`meta.json.closed_at == null`): stderr names the condition; no `kpi.json` is written; exit code `3`.
- On invalid input (e.g., `interventions.json` contains an unknown intervention-type): stderr names the invalid field; no `kpi.json` is written; exit code `4`.
- On unexpected I/O or filesystem error: stderr contains the Python traceback; no `kpi.json` is written; exit code `1`.

---

## Idempotence

- Re-running `peer-session tally <session-id>` against a bundle whose inputs have not changed MUST produce a `kpi.json` with:
  - byte-identical `per_session_clear`
  - byte-identical `per_session_clear_breakdown`
  - byte-identical `inputs_hash`
  - byte-identical `intervention_count`, `intervention_type_tally`, `intervention_rate_per_turn`, `zero_turn_session`, `drift_audit_verdict`
- Only `tallied_at` may update.

Verification: spec SC-002 ("100% of re-runs produce byte-identical kpi.json modulo documented fields"). Unit test `test_tally.py::test_idempotence` diffs two sequential runs and asserts byte equality after stripping `tallied_at`.

---

## Special cases

| Condition | Behavior |
|---|---|
| `drift-audit.json` is the spec-001 placeholder `{"status": "pending-phase-2"}` | Tally succeeds; `per_session_clear_breakdown.h2_drift = "ambiguous"` with `reason` noting the placeholder; top-level `per_session_clear` rolls up per the composite rule. |
| `fresh-reader-audit.json` is absent | Tally succeeds; `per_session_clear_breakdown.h2_fresh_reader = "ambiguous"` with `reason: "fresh-reader-audit.json not yet authored"`. |
| `fresh-reader-audit.json` is present but `verdict` is `"inconclusive"` | Tally succeeds; `h2_fresh_reader = "ambiguous"` with the auditor's `reasoning` copied as the reason. |
| Transcript has zero peer turns | Tally succeeds; `intervention_rate_per_turn = null`, `zero_turn_session = true`, `h1_intervention_load = "ambiguous"` with `reason: "zero peer turns; intervention load undefined"`. |
| Bundle is incomplete per spec-001 FR-001..FR-011 | Refuse (exit code 2, see above). |
| Session is unclosed (`meta.json.closed_at == null`) | Refuse (exit code 3, see above). |

---

## Contract tests

Behavior tests (in `tests/peer_session/test_tally.py`):

1. **Happy path** — complete bundle produces `kpi.json` with correct fields and `per_session_clear = "cleared"` (when all inputs support it).
2. **Idempotence** — two sequential runs, byte-identical output modulo `tallied_at`.
3. **Staleness** — modifying `interventions.json` between runs produces a different `inputs_hash`.
4. **Missing FRA** — fresh-reader-audit.json absent → `h2_fresh_reader = "ambiguous"`, tally succeeds.
5. **Drift placeholder** — placeholder `drift-audit.json` → `h2_drift = "ambiguous"`, tally succeeds.
6. **Zero turns** — empty transcript → `intervention_rate_per_turn = null`, `zero_turn_session = true`.
7. **Bundle incomplete** — missing any spec-001 required file → refuse with exit code 2.
8. **Unclosed session** — `closed_at = null` → refuse with exit code 3.
9. **Invalid intervention type** — unknown type in `interventions.json` → refuse with exit code 4.
