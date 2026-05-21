# KPI rollup workflow (spec 010)

**Runtime artifact** — how operators capture the human-judgment KPI inputs that
`peer-session tally` and `peer-session rollup` cannot derive deterministically,
how they resolve ambiguous per-session-clear judgments via amend-commits, and
how they ratify a per-run `poc-exit-<timestamp>.md`. Paired with the deterministic
CLI surface and the schemas in [`../sessions/_template/README.md`](../sessions/_template/README.md).

**Authoritative spec**: [`specs/010-kpi-rollup/spec.md`](../../specs/010-kpi-rollup/spec.md).
**Scope boundary**: this file is the operator-facing procedure. Schemas for
`kpi.json` and `fresh-reader-audit.json` live in
[`../sessions/_template/README.md`](../sessions/_template/README.md); this file
does not duplicate them (per spec 010 FR-023).

---

## When to use which section

| Situation | Path |
|---|---|
| Counted session has closed; H2 fresh-reader audit not yet run | **§A — Authoring `fresh-reader-audit.json`** |
| You need to record H3 complementarity narrative across peers | **§B — Recording H3 complementarity** |
| A counted session's `per_session_clear` is `ambiguous` | **§C — Resolving ambiguity via amend-commit** |
| `peer-session rollup` produced a `poc-exit-<timestamp>.md` and you need to sign off | **§D — Ratification gate** |

The full happy-path operator walkthrough lives in
[`specs/010-kpi-rollup/quickstart.md`](../../specs/010-kpi-rollup/quickstart.md).
This file expands the human-judgment steps within that walkthrough.

---

## §A — Authoring `fresh-reader-audit.json`

The H2 fresh-reader test asks: *Can a reader who did not participate in the
session reconstruct what happened from the bundle alone?* Per `design/poc.md`'s
H2 definition, "fresh reader" means a human who did not participate in the
session and does not know it in depth beyond what the bundle preserves.

### Step 1 — Pick a fresh reader

The fresh reader MUST:

- not have participated in the session, AND
- not have been briefed about the session beyond the contents of the bundle on
  disk, AND
- be willing to read the full bundle (`transcript.md`, `meta.json`,
  `interventions.json`, `drift-audit.json`, `summary.md`) and attempt a
  reconstruction.

The fresh reader MAY be an operator other than the session operator, a peer
who was not in the session, an LLM-judge once that path is calibrated, or any
external reviewer. POC staffing is thin; one fresh reader is sufficient per
session.

### Step 2 — Read the bundle and attempt reconstruction

The fresh reader reads `observations/sessions/<session-id>/` end-to-end and
attempts to reconstruct, in their own words:

1. the session goal or seed prompt,
2. each peer's distinct useful contribution,
3. why the exchange resolved (or did not).

No re-derivation of drift findings — that's owned by the drift-audit
(`drift-audit.json`, spec 005/008). The fresh-reader test is about
*legibility of the preserved bundle*, not re-litigation of drift content.

### Step 3 — Author `fresh-reader-audit.json`

Write the file at `observations/sessions/<session-id>/fresh-reader-audit.json`
matching the schema in [`../sessions/_template/README.md`](../sessions/_template/README.md).
A copy of `_template/fresh-reader-audit.json` with `[FILL IN]` markers is a
useful starting point; replace each marker:

- `session_id` — MUST match `meta.json.session_id`.
- `audited_at` — ISO-8601 UTC timestamp at seconds precision.
- `auditor` — the fresh reader's handle or identity (e.g. `"vesper"`,
  `"vesper (Phase 3 reviewer)"`).
- `verdict` — one of:
  - `pass` — fresh reader's reconstruction is materially correct.
  - `fail` — fresh reader cannot reconstruct, or reconstruction has
    load-bearing errors.
  - `inconclusive` — fresh reader could partially reconstruct, but at least
    one load-bearing component (goal, a peer's contribution, or the
    resolution) is unclear.
- `reasoning` — short free-text note describing what the reader could and
  couldn't reconstruct.

Commit:

```bash
git add observations/sessions/<session-id>/fresh-reader-audit.json
git commit -m "bundle: fresh-reader-audit.json for <session-id>"
```

### Step 4 — Re-run tally to absorb the verdict

```bash
peer-session tally <session-id>
```

`kpi.json` is regenerated. `per_session_clear_breakdown.h2_fresh_reader`
reflects the new verdict; the top-level `per_session_clear` may resolve from
`ambiguous` to `cleared` / `not-cleared` if no other sub-judgment is still
pending.

Commit the updated `kpi.json` (`peer-session tally` is idempotent modulo
`tallied_at`; see spec 010 FR-004).

---

## §B — Recording H3 complementarity narrative

H3 (complementarity) is a per-session and cross-session narrative judgment per
`design/poc.md`'s "Per-session clear definitions" and the H3 framing in
§"Success / Failure / KPI Framework". `peer-session tally` does not read a
structured complementarity field — `per_session_clear_breakdown.h1_complementarity`
is sourced from the `**H1 complementarity**` verdict line in `summary.md` (see
the SUMMARY-TAXONOMY).

### Where to record it

- **Per-session narrative**: `observations/sessions/<session-id>/summary.md`
  under the **What happened** section, per the spec-009 summary workflow
  (`observations/sessions/SUMMARY-WORKFLOW.md`). The cleared-criterion text in
  `design/poc.md` ("session summary can point to at least one distinct useful
  contribution from each peer") is the authoring target. Setting the
  `**H1 complementarity**` line in **Verdicts** to `clear` / `partial` / `fail`
  / `pending` is what `peer-session tally` reads back into the breakdown.
- **Cross-session narrative**: the per-run `poc-exit-<timestamp>.md` does not
  carry an H3 narrative section; H3 is a synthesis-time concern, addressed in
  the ratification step (§D) where the operator may attach a free-text
  reflection on H3 across the counted set.

### Why no structured field

`design/poc.md` frames H3 as a qualitative complementarity claim. A structured
"H3 score" would force a totalisation the POC explicitly rejects. The verdict
line in `summary.md` carries the per-session judgment; the rest is prose.

---

## §C — Resolving ambiguity via amend-commit

`peer-session tally` marks a sub-judgment `ambiguous` when the input that
sources it is missing, inconclusive, or absent (e.g. fresh-reader-audit not yet
authored, drift-audit still on the spec-001 placeholder, summary.md verdict
line is `pending` or absent).

Resolution rides entirely on **amend-commits on the underlying bundle input**,
per spec 010 FR-018. No override field exists in `kpi.json`; tally re-derives
`per_session_clear` deterministically from the amended inputs.

### Amend targets per sub-judgment

| Sub-judgment | Amend target (what to fix and commit) |
|---|---|
| `h1_stable_coordination` | `summary.md` `**H1 stability**` verdict line. |
| `h1_intervention_load` | `interventions.json` (if intervention tagging was incomplete) or `transcript.md` (if peer turns were undercounted by the export). Only legitimate corrections; never inflate to clear a verdict. |
| `h1_complementarity` | `summary.md` `**H1 complementarity**` verdict line — change `pending` / `partial` to `clear` / `fail` once the qualitative judgment is settled. |
| `h2_fresh_reader` | `fresh-reader-audit.json` — change `verdict` from `inconclusive` to `pass` / `fail` once the fresh reader's review concludes. |
| `h2_drift` | `drift-audit.json` — replace the spec-001 Phase-2-pending placeholder with the real drift-audit output (run the drift-audit workflow at `observations/drift-audits/WORKFLOW.md`). |
| `h2_episode_record` | A `cleared` sub-judgment here means the bundle satisfied spec-001 at tally time; if it later regressed, restore the missing/empty file. |

### Pre-commit review expectation

Amend-commits on bundle inputs MUST be reviewable in isolation:

- Use a commit message that names the specific bundle, the specific amend
  target, and the specific reason. Example:
  `bundle: <session-id> fresh-reader-audit.json verdict pass — fresh reader confirmed reconstruction`.
- Do NOT bundle amend-commits across multiple sessions or multiple sub-judgments
  in one commit. One amend, one commit.
- Never rewrite the original commit — always land a follow-up amend commit per
  spec 001 FR-014's discipline.

### After the amend commit

Re-run tally and commit the refreshed `kpi.json`:

```bash
peer-session tally <session-id>
git add observations/sessions/<session-id>/kpi.json
git commit -m "bundle: re-tally <session-id> after <amend-target> amend"
```

If all six sub-judgments now resolve to `cleared` / `not-cleared` (no
ambiguous), the session is rollup-ready. Re-run `peer-session rollup` to
produce a new per-run file.

---

## §D — Ratification gate for `poc-exit-<timestamp>.md`

Each successful `peer-session rollup` run writes a new
`observations/poc-exit-<timestamp>.md` file. Ratification is per-file: a
ratified per-run file remains ratified even when a later rollup adds a newer
per-run file.

### Step 1 — Inspect the per-run file's ratifiability state

Open the latest per-run file (`observations/poc-exit.md` is a symlink resolving
to it):

- `ratifiable` — operator may sign off; no ambiguity gates remain.
- `draft, not ratifiable` — do NOT force-sign. Either ambiguous sessions exist
  (resolve per §C, re-run rollup) or the counted set is out of range
  (re-investigate the session set).

### Step 2 — Review the rollup body

Walk the per-run file top-to-bottom:

- H1 decision-rule verdict — does the cleared count meet the applied threshold
  (3/3, 3/4, or 4/5)?
- H2 observations — is the fresh-reader pass-rate, drift verdict, and
  episode-record completeness consistent with what you expected per session?
- Per-session table — any session whose row surprises you? Open its
  `kpi.json` and `fresh-reader-audit.json` to corroborate.

### Step 3 — Fill the ratification-gate section

Within the per-run file's `## Ratification gate` subsection:

- Change `[ ]` to `[x]` on the **Ratified** line.
- Fill **Ratifier** with the operator handle.
- Fill **Ratified at** with an ISO-8601 UTC timestamp at seconds precision.
- Fill **Notes** with any free-text reflection — including H3 complementarity
  narrative across the counted set, if you want it captured here.

Commit:

```bash
git add observations/poc-exit-<timestamp>.md
git commit -m "rollup: ratify poc-exit-<timestamp> — <one-line reflection>"
```

### Step 4 — Treat ratification as durable

A ratified per-run file is the operator's signed POC-exit record at that point
in time. Subsequent rollups MUST NOT overwrite or delete it (spec 010 FR-025).
A later rollup that supersedes the analysis simply produces its own per-run
file and updates the `poc-exit.md` pointer; prior per-run files (ratified or
not) remain on disk and in git history.

If a ratified per-run file later turns out to be wrong, the path forward is
analytical — amend the offending bundle input per §C, re-run `peer-session
rollup`, ratify the new per-run file with a note explaining the revision — not
rewriting history.

---

## Cross-references

- **Spec chain**: [`specs/010-kpi-rollup/spec.md`](../../specs/010-kpi-rollup/spec.md) →
  [`plan.md`](../../specs/010-kpi-rollup/plan.md) →
  [`tasks.md`](../../specs/010-kpi-rollup/tasks.md)
- **Contracts**:
  [`tally-cli-behavior.md`](../../specs/010-kpi-rollup/contracts/tally-cli-behavior.md),
  [`rollup-cli-behavior.md`](../../specs/010-kpi-rollup/contracts/rollup-cli-behavior.md)
- **Quickstart** (full operator walkthrough):
  [`specs/010-kpi-rollup/quickstart.md`](../../specs/010-kpi-rollup/quickstart.md)
- **Bundle schemas**: [`../sessions/_template/README.md`](../sessions/_template/README.md)
  (per FR-023)
- **Bundle authoring discipline**: [`../sessions/README.md`](../sessions/README.md)
  + spec-001 FR-014 amend-commit convention.
- **Drift-audit workflow**: [`../drift-audits/WORKFLOW.md`](../drift-audits/WORKFLOW.md)
  (cited from §C `h2_drift` amend path)
- **Summary workflow**: [`../sessions/SUMMARY-WORKFLOW.md`](../sessions/SUMMARY-WORKFLOW.md)
  (cited from §A and §C `h1_*` verdict line amend paths)

---

## Scope boundary (explicit)

- **In scope**: fresh-reader-audit authoring, H3 narrative placement,
  ambiguity-resolution amend-commit discipline, ratification gate.
- **Out of scope**: `kpi.json` / `fresh-reader-audit.json` serialisation
  details (template README), drift-audit rubric content (spec 005),
  intervention-tag shape (spec 011), LLM-assisted KPI extraction (deferred
  per spec 008 FR-014 pattern), Phase 4 Gemini-extension rollup.
