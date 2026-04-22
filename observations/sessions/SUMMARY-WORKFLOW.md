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

Use this when the operator composes the prose AND records the H1/H2 verdicts directly. Typical cases: exploratory / pre-calibration sessions, sessions where the operator is the most direct observer, or when no peer-agent drafter is readily available.

### Step 1 — Pin the drift-audit version

```bash
cd <repo-root>
SID=<session-id>
DA_SHA=$(git log -1 --format=%H -- "observations/sessions/$SID/drift-audit.json")
DA_SHORT=$(git rev-parse --short "$DA_SHA")
echo "Drafting summary against drift-audit @ $DA_SHA (short: $DA_SHORT)"
```

If `drift-audit.json` isn't committed yet, **halt** — the drift-audit workflow ([`../drift-audits/WORKFLOW.md`](../drift-audits/WORKFLOW.md)) must land first. See **Halt conditions** below.

### Step 2 — Compose `summary.md` in the hybrid inverted-pyramid shape

Copy `_template/summary.md` into `observations/sessions/$SID/summary.md` and fill in the four top-level sections in order. Per spec 009 FR-010 the structure is Seed → Verdicts → Drift → What happened; per FR-003 the five required content elements are packaged as: goal → `## Seed`, verdicts → `## Verdicts`, drift → `## Drift`, per-peer contributions + coordination patterns → `## What happened` (both live as free-form prose in this bottom section).

Verdict lines in the `## Verdicts` section MUST follow this grep-stable format (one line per KPI, exactly three lines):

```markdown
- **H1 stability**: `<value>` — <rationale>
- **H1 complementarity**: `<value>` — <rationale>
- **H2 fresh-reader-pass**: `<value>` — <rationale>
```

Where `<value>` is one of `clear` / `partial` / `fail` / `pending` — backtick-quoted. See **Verdict rubric** below for the judgment thresholds.

### Step 3 — Write the Drift section by citing, not re-deriving

```bash
jq '.verdict' "observations/sessions/$SID/drift-audit.json"
jq '.findings[] | select(.severity=="finding")' "observations/sessions/$SID/drift-audit.json"
```

Cite the `verdict` verbatim in the `## Drift` section; reference each `severity: "finding"` entry by `turn_ref` or `category`. If verdict is `no_drift` with empty findings, state that drift is not the blocker for H2. **Do NOT** introduce a drift category or severity absent from `drift-audit.json.findings[]` — per FR-008, the drift-audit is the source of truth. If you disagree with it, re-audit via spec 008 Path C first, then refresh the summary.

### Step 4 — Commit as a session-bundle amend

```bash
git add "observations/sessions/$SID/summary.md"
git commit -m "session bundle amend: $SID — summary @ $DA_SHORT" \
           -m "Mode: single-author"
```

No taxonomy token on the subject — default single-author initial commit. The `Mode: single-author` body line is mandatory on initial commits per [SUMMARY-TAXONOMY.md](SUMMARY-TAXONOMY.md) token #1.

### Step 5 — Run sanity checks

See **Post-commit sanity checks** below. If any check fails, fix via Path C revision — **NEVER** `git commit --amend` per [spec 001 FR-014](../../specs/001-session-bundle-skeleton/spec.md) + [contract C6](../../specs/009-session-summary-workflow/contracts/workflow-contracts.md).

**Done.** Bundle now carries a committed single-author summary.

---

### Verdict rubric

Use these values (and only these) for each KPI. Judgment thresholds are defined in [`design/poc.md`](../../design/poc.md) "Per-session clear definitions" — this workflow references those definitions rather than re-specifying them; if they evolve, this procedure absorbs the change via pointer (per FR-007).

| Value | Meaning |
|---|---|
| `clear` | Session meets the KPI's clear-definition criteria in `design/poc.md`. |
| `partial` | Some criteria met, others partially; judgment call with rationale. |
| `fail` | KPI's criteria are NOT met. |
| `pending` | Requires an asynchronous step not yet complete (most commonly H2's fresh-reader test). Resolution triggers a Path C revision. |

Condensed from `design/poc.md` (read the source for full context):

- **H1 stability** — all of: (1) operator does not directive-redirect on majority of substantive turns, (2) no persistent loop/deadlock, (3) neither peer collapses into one-sided dominance.
- **H1 complementarity** — session can point to at least one distinct useful contribution from each peer that was taken up, answered, or built on.
- **H2 fresh-reader-pass** — an uninvolved human reviewer reads the preserved bundle and produces a reconstruction of goal / per-peer roles / why-it-resolved-or-failed, and the operator judges that reconstruction materially correct.

## Path B — Agent-drafted + operator-ratified

Use this when a peer agent (Dalgos, Vigil) or delegated human drafts the prose; the operator edits as needed, **writes the H1/H2 verdicts themselves** (per FR-005 — verdict authority is always operator-owned regardless of drafter), and commits.

### Step 1 — Drafter produces the draft

The drafter reads the bundle (`transcript.md`, `meta.json`, `interventions.json`, `drift-audit.json`) and authors `summary.md` directly at `observations/sessions/$SID/summary.md`. Alternatively, the drafter can write to `observations/sessions/$SID/summary.draft.md` as a scratch file (NOT committed). Drafter MAY propose verdict values but labels them clearly as draft proposals.

Structure discipline is the same as Path A Step 2 — drafter uses the hybrid inverted-pyramid template (Seed → Verdicts → Drift → What happened) with the grep-stable verdict-line format.

### Step 2 — Operator reviews, edits, writes verdicts

The operator opens `observations/sessions/$SID/summary.md`, edits the prose as needed, and **writes the three H1/H2 verdict lines themselves** per FR-005. The operator MAY copy the drafter's proposed verdict values verbatim if they agree, but the act of writing the verdicts in the final file represents the operator's attestation.

If the drafter used `summary.draft.md` as a scratch file, remove it before commit — drafts are authoring-tool artifacts, not bundle-layer evidence (per contract C5):

```bash
rm -f "observations/sessions/$SID/summary.draft.md"
```

### Step 3 — Verify the Drift section

Same as Path A Step 3. Drift-citation discipline is mode-independent: cite, don't re-derive. If the drafter proposed drift language that re-derives findings from transcript, correct it before commit.

### Step 4 — Pin the drift-audit version

Same as Path A Step 1.

### Step 5 — Commit as a session-bundle amend (operator commits)

```bash
git add "observations/sessions/$SID/summary.md"
git commit -m "session bundle amend: $SID — summary @ $DA_SHORT" \
           -m "Mode: agent-drafted, drafted-by: Dalgos, ratified-by: Zoe"
```

The `drafted-by:` field identifies the agent or human who produced the draft. `ratified-by:` identifies the operator. **Both MUST be present** for agent-drafted mode — this is the identity contract per FR-004 + contract C5.

No taxonomy token on the subject — initial commits (both Path A and Path B) land tokenless; only lifecycle events (peer-audit, revision) tag the subject.

### Step 6 — Run sanity checks

Same as Path A Step 5. See **Post-commit sanity checks** below.

**Done.** Bundle now carries a committed agent-drafted + operator-ratified summary.

## Path C — Revision

*Filled by US3 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) Path C until this section lands.*

## Path D — Peer-audit

*Filled by US3 — see [`specs/009-session-summary-workflow/quickstart.md`](../../specs/009-session-summary-workflow/quickstart.md) Path D until this section lands.*

---

## Halt conditions

Stop and fix upstream — do NOT produce a partial or placeholder `summary.md`, per FR-002 + FR-018. Every halt corresponds to a [contract C1](../../specs/009-session-summary-workflow/contracts/workflow-contracts.md) pre-condition that failed.

| Condition | Fix where |
|---|---|
| `observations/sessions/<session-id>/` does not exist | Confirm `<session-id>`; session may not be bundle-committed yet |
| `meta.json` missing or unreadable | Session-bundle close step ([spec 001](../../specs/001-session-bundle-skeleton/spec.md)) |
| `meta.json.pinned_rules_ref` unset | Session-bundle close step ([spec 001 FR-010](../../specs/001-session-bundle-skeleton/spec.md)) |
| `meta.json.closed_at` unset | Session is still open — close it first via the session-control path (spec 004) |
| `transcript.md` missing | Transcript export ([spec 006](../../specs/006-discord-transcript-export/spec.md)) |
| `interventions.json` missing | Intervention-tagging slice (Codex) — if intervention-tagging hasn't landed yet, log this as a Phase 2 blocker rather than running the summary without interventions context. When present, MUST be an array of intervention objects per spec 001 FR-011 (empty array = valid empty case). |
| `drift-audit.json` missing | Drift-audit workflow ([`../drift-audits/WORKFLOW.md`](../drift-audits/WORKFLOW.md), spec 008) — MUST land before summary authoring begins |
| Working tree has unrelated uncommitted changes | Stash or commit those first; summary amend should land clean |

**Non-silent failure principle** (per FR-002 / FR-018): when halting, surface the specific unmet condition to whoever is running the workflow (operator, agent-drafter, or future tooling). Don't silently produce a half-formed artifact or emit a placeholder. The bundle-producer upstream is the right place to fix.

---

## Post-commit sanity checks

Run these after every committed summary. **Check 5 applies only to initial commits** (Path A or Path B) — skip it for revision (Path C) or peer-audit (Path D) follow-up commits, which don't carry a new `Mode:` line (the mode is inherited from the initial commit).

If any check fails, fix via **Path C revision** — do **NOT** use `git commit --amend` per spec 001 FR-014 + contract C6.

```bash
SID=<session-id>
SUMMARY="observations/sessions/$SID/summary.md"

# 1. Required sections present in the correct inverted-pyramid order
grep -nE '^## (Seed|Verdicts|Drift|What happened)' "$SUMMARY"
# Expected: 4 matching lines, in the order Seed → Verdicts → Drift → What happened.

# 2. Three verdict lines, one per KPI, in the R2 grep-stable format
grep -E '^- \*\*H[12] (stability|complementarity|fresh-reader-pass)\*\*: `(clear|partial|fail|pending)`' "$SUMMARY"
# Expected: exactly 3 lines.

# 3. Drift section cites drift-audit.json (verdict name or file reference)
grep -E 'drift-audit\.json|no_drift|minor_drift|load_bearing_drift' "$SUMMARY"
# Expected: at least 1 match.

# 4. Commit subject format is valid
git log -1 --format='%s' -- "$SUMMARY"
# Expected: "session bundle amend: <sid> — summary[ <taxonomy-token>] @ <drift-short-sha>"

# 5. (Initial commits only) Commit body carries the Mode: line
# Skip this check for revision / peer-audit follow-up commits — they inherit mode from the initial commit.
git log -1 --format='%s' -- "$SUMMARY" | grep -qE 'revision:|\[peer-audited' \
  && echo "↷ skipping Mode check (follow-up commit)" \
  || git log -1 --format='%b' -- "$SUMMARY" | grep -E '^Mode:'
# Expected for initial commits: one match (Mode: single-author OR Mode: agent-drafted, ...)

# 6. Drift-audit SHA in subject resolves to an existing commit
DA_SHORT=$(git log -1 --format='%s' -- "$SUMMARY" | sed -E 's/.*@ ([a-f0-9]+)$/\1/')
git cat-file -e "$DA_SHORT" 2>/dev/null && echo "✓ drift-audit short SHA resolves: $DA_SHORT"
```

All six checks are cheap and fast — run them as a habit after every summary commit.

---

## Downstream consumption

Per [spec 009 FR-017](../../specs/009-session-summary-workflow/spec.md) + [contract C8](../../specs/009-session-summary-workflow/contracts/workflow-contracts.md), downstream consumers of summary evidence (Phase 5 KPI rollup, H1/H2 per-session reviewers, POC-exit synthesis) read the committed `summary.md` through two channels:

1. **Verdict lines** (the three list-bullet lines in `## Verdicts`) — authoritative per-session KPI input. Consumers MUST NOT re-derive H1/H2 verdicts from the `## What happened` prose. Mirrors spec 008 contract C8's cite-don't-re-derive discipline for drift.
2. **Drift citation** (the `drift-audit.json.verdict` cited in `## Drift`) — consumers of drift evidence read `drift-audit.json` directly via the short SHA in the commit subject; they do NOT parse drift findings from the summary prose.

Mechanical extraction of the three verdicts (no LLM needed):

```bash
grep -E '^- \*\*H[12] (stability|complementarity|fresh-reader-pass)\*\*: `(clear|partial|fail|pending)`' \
  observations/sessions/<session-id>/summary.md
```

Cross-session aggregation (e.g. "how many counted sessions had `clear` on all three KPIs?") is the Phase 5 KPI-rollup slice's concern. This workflow only guarantees the verdict lines are discoverable in each bundle without out-of-band context — the rollup slice specifies the aggregation logic when it's cut.

The current `summary.md` on disk is always the consumer-relevant version; older versions retrieved via `git show <prior-commit>:...` are historical evidence only. Revision and peer-audit follow-up commits (Paths C/D) update the live file; the lifecycle metadata lives in git history.

---

## LLM-assisted authoring (deferred)

Per [spec 009 FR-014 + FR-015](../../specs/009-session-summary-workflow/spec.md), **LLM-prompt-template automation for summary authoring is deferred to a later slice.** This is distinct from Path B (agent-drafted + operator-ratified), which is available now and uses peer agents (Dalgos, Vigil) as interactive drafters under operator ratification.

The deferred LLM-assisted path refers specifically to a future slice that would operationalize prompt-template authoring — i.e. feeding transcript + meta + interventions + drift-audit to an LLM and having it emit a prose draft — analogous to spec 005 RUBRIC.md §7's LLM-judge path for drift.

**Entry criteria** (gate for cutting the future LLM-assisted slice):

1. **Calibration evidence**: at least 2 counted Phase 3 sessions have landed manual summaries (Path A or Path B) so there is real data to calibrate a prompt template against.
2. **Operator prompt template**: the operator has defined an LLM prompt template suitable for the hybrid inverted-pyramid structure + R2 verdict-line format. The template must produce `summary.md` output conforming to FR-003 + FR-010 + FR-008 without manual post-processing beyond operator edits.
3. **Manual ratification gate**: operator ratification remains mandatory — LLM output is a draft, operator writes/approves the verdicts and commits. This mirrors spec 005 RUBRIC.md §7's operator-ratifies-LLM-output discipline.

This workflow does NOT operationalize the LLM automation. Until the future slice lands, all summaries are authored via Path A or Path B.

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
