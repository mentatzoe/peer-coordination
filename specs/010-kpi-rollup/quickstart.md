# Quickstart: KPI Rollup

**Feature**: KPI Rollup
**Branch**: `010-kpi-rollup`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

End-to-end operator flow from a just-closed session bundle to a ratified per-run `poc-exit-<timestamp>.md`. Use this document as the happy-path walkthrough; consult [`observations/kpi-rollup/WORKFLOW.md`](../../observations/kpi-rollup/WORKFLOW.md) (authored by this slice) for the authoring-recipe details that cover ambiguity resolution and ratification.

---

## Prerequisites

- A closed session bundle exists under `observations/sessions/<session-id>/` with all spec-001 FR-001..FR-011 files committed (`meta.json`, `interventions.json`, `drift-audit.json`, `summary.md`, `transcript.md`). `meta.json.closed_at` is not `null`.
- The spec-008 drift-audit workflow has been run (or the operator has decided to tally now and re-run after drift audit; either path works).
- `peer-session` CLI is available from the repo root (spec-007 landed).

---

## Step 1 — Compute per-session KPIs

```text
peer-session tally <session-id>
```

Expected result:

- New file `observations/sessions/<session-id>/kpi.json` on disk.
- Stdout summary names `per_session_clear` and any sub-judgments flagged `ambiguous`.
- Commit the new file: `git add observations/sessions/<session-id>/kpi.json && git commit -m "bundle: kpi.json for <session-id>"`.

If the session has not yet had a fresh-reader audit authored, `per_session_clear` will be `ambiguous` with `h2_fresh_reader` as the reason. That is expected — proceed to Step 2.

---

## Step 2 — Author the fresh-reader audit

Follow [`observations/kpi-rollup/WORKFLOW.md`](../../observations/kpi-rollup/WORKFLOW.md) §"Authoring fresh-reader-audit.json".

- A fresh reader (a human who did not participate in the session and does not know it in depth beyond what the bundle preserves) reads the bundle and attempts to reconstruct: (1) the session goal, (2) each peer's contribution, (3) why the exchange resolved or failed.
- The operator then decides whether the fresh reader's reconstruction is materially correct (per `design/poc.md` H2 "Fresh-reader pass" definition).
- Result is written to `observations/sessions/<session-id>/fresh-reader-audit.json` with fields: `session_id`, `audited_at`, `auditor`, `verdict` (`pass`/`fail`/`inconclusive`), `reasoning`.
- Commit: `git add observations/sessions/<session-id>/fresh-reader-audit.json && git commit -m "bundle: fresh-reader-audit.json for <session-id>"`.

---

## Step 3 — Re-run tally to absorb the fresh-reader verdict

```text
peer-session tally <session-id>
```

Expected result:

- `kpi.json` is updated; `per_session_clear_breakdown.h2_fresh_reader` now reflects the verdict; the top-level `per_session_clear` may resolve from `ambiguous` to `cleared` or `not-cleared` depending on the composite judgment.
- Re-running tally against unchanged inputs produces byte-identical output modulo `tallied_at` (spec SC-002).
- Commit the updated `kpi.json`.

If `per_session_clear` is still `ambiguous`, the workflow's §"Resolving ambiguous per-session-clear" section explains how to resolve it per FR-018: amend the underlying bundle input that produced the ambiguity (most commonly `fresh-reader-audit.json`'s `verdict`, or running the real drift audit to replace the spec-001 placeholder in `drift-audit.json`) following spec 001 FR-014's amend-commit discipline, then re-run `peer-session tally`. `kpi.json` carries no override field — the re-run recomputes `per_session_clear` deterministically from the amended inputs.

---

## Step 4 — Repeat for each counted session

The POC's H1 decision rule requires 3–5 counted sessions (per `design/poc.md`). Repeat Steps 1–3 for each bundle before moving on to rollup.

---

## Step 5 — Produce the POC-exit rollup

```text
peer-session rollup
```

Expected result:

- New file `observations/poc-exit-YYYYMMDDTHHMMSSZ.md` on disk.
- `observations/poc-exit.md` symlink is created or updated to point to the new file.
- Stdout summary names the ratifiability state (`ratifiable` or `draft, not ratifiable`), the applied H1 decision rule, and any ambiguous session IDs.
- If any hard data gap is present (missing `kpi.json`, missing `fresh-reader-audit.json`, stale `kpi.json`, session-id collision), the command refuses with exit code 2 and no new file is written. Resolve the named gaps and re-run.
- Commit both the new per-run file and the updated `poc-exit.md` symlink: `git add observations/poc-exit-*.md observations/poc-exit.md && git commit -m "rollup: poc-exit <timestamp>"`.

---

## Step 6 — Ratify (or iterate)

Follow the workflow's §"Ratification gate".

- If the per-run file is marked `ratifiable`, the operator reviews the content, fills the ratification-gate subsection per the workflow's convention, and commits the ratified file.
- If the per-run file is marked `draft, not ratifiable` (ambiguous sessions enumerated or out-of-range):
  - For ambiguous sessions: follow the workflow to resolve each ambiguity per FR-018 — amend the underlying bundle input (e.g., `fresh-reader-audit.json`'s `verdict`, or commit the real drift audit over the spec-001 placeholder) via amend-commit and re-run `peer-session tally` to recompute `per_session_clear` deterministically; then re-run `peer-session rollup` to produce a new per-run file. No override field, no override-specific code path — resolution rides entirely on the amend-commit + re-tally loop.
  - For out-of-range: either the baseline is not yet complete (too few sessions) or the counted-session set has grown beyond the H1 decision-rule window (investigate). Do not force-ratify an out-of-range draft.

---

## Manual smoke-test checklist

Per the user memory rule "Interactive CLIs require manual testing," before declaring the slice complete, exercise:

- [ ] Happy-path tally on a synthetic complete bundle (unit fixture is not enough — run the real CLI from the repo root).
- [ ] Idempotent re-run of tally on the same bundle — diff output, confirm only `tallied_at` changed.
- [ ] Tally on a bundle with drift-audit placeholder — confirm `h2_drift = "ambiguous"` and tally succeeds.
- [ ] Tally on a bundle with missing `fresh-reader-audit.json` — confirm `h2_fresh_reader = "ambiguous"` and tally succeeds.
- [ ] Tally on a bundle with `closed_at = null` — confirm refuse with exit 3.
- [ ] Tally on a bundle with missing `interventions.json` — confirm refuse with exit 2.
- [ ] Rollup on a 3-session cleared set — confirm ratifiable per-run file, correct H1 decision rule `3/3`.
- [ ] Rollup with one missing `fresh-reader-audit.json` — confirm refuse with exit 2, pointer unchanged.
- [ ] Rollup with one ambiguous session — confirm draft per-run file written, ambiguous session enumerated.
- [ ] Second rollup run — confirm new per-run file, pointer updated, prior per-run file on disk unchanged.
- [ ] `observations/poc-exit.md` resolves to the latest per-run file (e.g., `readlink observations/poc-exit.md` matches the most recent per-run filename).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `peer-session tally` exits 2 with "missing interventions.json" | Bundle is incomplete | Run `peer-session init` (if still needed) and populate the missing file per spec 001 |
| `peer-session tally` exits 3 with "session is unclosed" | `meta.json.closed_at` is null | Close the session per spec 004 (Discord session controls) before tallying |
| `per_session_clear` is `ambiguous` after Step 3 re-run | One or more sub-judgments are ambiguous beyond fresh-reader | Check `per_session_clear_breakdown` reasons; resolve each (run drift audit, author FRA verdict, resolve h1_complementarity via workflow) |
| `peer-session rollup` exits 2 with "stale kpi.json" | An input file changed since `kpi.json` was written | Re-run `peer-session tally` against the affected session |
| `poc-exit.md` symlink is broken | A per-run file was deleted manually | Re-run `peer-session rollup` to regenerate pointer (the existing per-run history remains otherwise) |
