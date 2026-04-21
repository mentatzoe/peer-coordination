# Contract: `peer-session rollup`

**Spec**: [../spec.md](../spec.md)
**Plan**: [../plan.md](../plan.md)
**Research**: [../research.md](../research.md)

Operator-visible contract for the cross-session KPI aggregation subcommand.

---

## Invocation

```text
peer-session rollup
```

- No positional argument in v1.
- No additional flags in v1. Future flags (e.g., `--include-template` for meta-diagnostics, `--emit-json` for CI integration) are out of scope.

**Working directory**: repository root.

---

## Preconditions

- `observations/sessions/` contains one or more non-template, non-hidden session bundle subdirectories.
- Each discovered bundle satisfies spec-001 FR-001..FR-011 AND has a committed `kpi.json` AND has a committed `fresh-reader-audit.json`. Any gap is a hard data gap per FR-013 and causes refusal.
- Each discovered bundle's `meta.json.session_id` is unique across the counted set (FR-015).
- Each `kpi.json.inputs_hash` matches a freshly computed hash of the current bundle inputs (staleness check per FR-005). Stale hashes are a hard data gap per FR-013.

---

## Discovery rules

- Iterate `observations/sessions/`; accept any subdirectory whose name does NOT start with `_` or `.` (consistent with spec 001 FR-017).
- For each accepted directory, verify bundle completeness and the presence of `kpi.json` + `fresh-reader-audit.json`. Collect session IDs into the counted-session set `S`.
- Reject on session-id collision: two entries in `S` with identical `meta.json.session_id`.

---

## Outputs

### Success output (ratifiable)

All counted sessions resolve to `per_session_clear ∈ {cleared, not-cleared}` (no ambiguous); `decidable_total` is in `[3, 5]`.

- Writes `observations/poc-exit-<YYYYMMDDTHHMMSSZ>.md` conforming to the POCExitFile entity in `data-model.md`. Ratifiability state: `ratifiable`.
- Removes `observations/poc-exit.md` (if present) and creates it as a symlink pointing to the newly written per-run file.
- Stdout: one line — `wrote observations/poc-exit-<timestamp>.md` — followed by the `ratifiable` status and the H1 decision-rule outcome summary.
- Exit code: `0`.

### Success output (draft — judgment gap only)

One or more counted sessions resolve to `per_session_clear == "ambiguous"`; all other hard conditions pass.

- Writes a per-run file marked `draft, not ratifiable` with the ambiguous session IDs enumerated in the artifact body.
- Updates the `poc-exit.md` symlink pointer.
- Stdout: `wrote observations/poc-exit-<timestamp>.md` + `draft, not ratifiable` + enumerated ambiguous session IDs.
- Exit code: `0` — this is a successful draft, not an error; the operator is expected to use the workflow to resolve ambiguity before the next run.

### Failure output (hard data gap)

Any of: missing `kpi.json`, missing `fresh-reader-audit.json`, stale `kpi.json.inputs_hash`, session-id collision, bundle incomplete per spec-001.

- No new per-run file is written.
- The `poc-exit.md` pointer (if present) is NOT updated; it continues to resolve to the most recent prior per-run file.
- Stderr enumerates the unresolved bundles with their specific failure reason.
- Exit code: `2`.

### Failure output (out-of-range counted-session total)

`decidable_total < 3` or `decidable_total > 5`.

- Writes a per-run file marked `draft, not ratifiable` with the out-of-range condition surfaced explicitly in the artifact (per FR-014, "surface, not silently mis-apply").
- Updates the `poc-exit.md` symlink pointer.
- Stdout: `wrote observations/poc-exit-<timestamp>.md` + `out-of-range` with the observed `decidable_total`.
- Exit code: `0` — the rollup ran successfully, the H1 decision rule simply does not apply yet.

Rationale: out-of-range is an operator-visible shape of the counted-session set (too few sessions yet, or too many — the latter implies a counting bug worth a manual review). It's not a tool error.

### Failure output (unexpected I/O)

- Stderr contains the Python traceback.
- Exit code: `1`.

---

## Per-run file structure (per FR-012 and data-model.md)

Each `poc-exit-<timestamp>.md` MUST contain the following sections in order:

1. **Header** — rollup run timestamp, ratifiability state (`ratifiable` or `draft, not ratifiable`), counted-session total.
2. **H1 decision rule outcome** — per-KPI pass/fail (stable coordination, intervention load, complementarity), showing the decision rule applied (3/3, 3/4, or 4/5) and the observed cleared-count.
3. **H2 observations** — fresh-reader pass-rate across decidable sessions, undeclared-convention drift verdict across counted sessions, episode-record completeness.
4. **Per-session table** — one row per counted session with columns: session_id, `per_session_clear`, and a compact breakdown indicator (e.g., `h1_sc=cleared, h1_int=cleared, h1_comp=ambiguous, h2_fr=cleared, h2_d=cleared, h2_er=cleared`).
5. **Ambiguous sessions** (present only if any are ambiguous) — list of session IDs with their ambiguous sub-judgments and the captured `reason` fields.
6. **Out-of-range note** (present only if `decidable_total` is outside `[3, 5]`).
7. **Ratification gate** — an operator-fillable subsection. When empty/unratified, the file's ratifiability state may be `ratifiable` but the operator has not yet signed off. When filled per the workflow, the file is operator-ratified.

---

## Contract tests

Behavior tests (in `tests/peer_session/test_rollup.py`):

1. **Happy path, 3 sessions cleared** — writes ratifiable per-run file, `poc-exit.md` symlink points to it, H1 decision rule `3/3` passes.
2. **Happy path, 4 sessions with 3 cleared + 1 not-cleared** — writes ratifiable per-run file, H1 decision rule `3/4` passes.
3. **Ambiguous session** — one session's `per_session_clear == "ambiguous"` → writes draft-marked per-run file, exits 0, ambiguous session enumerated.
4. **Missing kpi.json** — one counted bundle has no `kpi.json` → refuses with exit 2, no per-run file written, pointer unchanged.
5. **Missing fresh-reader-audit.json** — one counted bundle lacks FRA → refuses with exit 2.
6. **Stale kpi.json** — `inputs_hash` mismatch → refuses with exit 2.
7. **Session-id collision** — two bundles share a `meta.json.session_id` → refuses with exit 2.
8. **Out-of-range, 2 sessions** — `decidable_total == 2` → writes draft-marked per-run file with out-of-range surface, exits 0.
9. **Template excluded** — `_template/` present but not counted; doesn't affect totals.
10. **Symlink update** — second successful rollup run updates `poc-exit.md` to point to the newer per-run file; prior file remains on disk unchanged.
