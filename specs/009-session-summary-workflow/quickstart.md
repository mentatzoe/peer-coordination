# Quickstart: Session-Summary Workflow

**Branch**: `009-session-summary-workflow` | **Date**: 2026-04-21
**Audience**: operator (Zoe), delegated summarizer (Dalgos / Vigil / human reviewer), peer auditor. Walks through the four primary paths: single-author, agent-drafted + operator-ratified, revision, peer-audit.

This document assumes you have already read `observations/drift-audits/RUBRIC.md` and `observations/drift-audits/WORKFLOW.md` (spec 005 + spec 008). The summary workflow runs **after** the drift-audit workflow lands — bundle must have `drift-audit.json` committed before summary authoring begins (per C1 + FR-002).

---

## Prerequisites (common to all paths)

Verify before starting any summary:

1. `observations/sessions/<session-id>/` exists and the bundle is closed per [spec 001](../001-session-bundle-skeleton/spec.md):
   - `transcript.md` present (non-empty; zero-turn transcripts still produce a valid file).
   - `meta.json` has `session_id`, `pinned_rules_ref`, `closed_at`.
   - `interventions.json` present.
   - `drift-audit.json` committed (per spec 008 workflow).
2. Working tree is clean of unrelated changes.
3. You have write access to the session bundle's branch / main per `docs/ways-of-working/pull-requests.md`.

If any prerequisite fails, see **Halt conditions** below; fix upstream first.

---

## Path A — Single-author summary

Use this when the operator composes the prose AND records the H1/H2 verdicts directly. Typical cases: small / exploratory sessions, sessions where the operator is the most direct observer, or when no peer-agent drafter is readily available.

### Step 1 — Pin the drift-audit version

```bash
cd <repo-root>
SID=<session-id>
DA_SHA=$(git log -1 --format=%H -- "observations/sessions/$SID/drift-audit.json")
DA_SHORT=$(git rev-parse --short "$DA_SHA")
echo "Drafting summary against drift-audit @ $DA_SHA (short: $DA_SHORT)"
```

### Step 2 — Compose `summary.md`

Open `observations/sessions/$SID/summary.md` and write it in the hybrid inverted-pyramid order (per FR-010). Use this template:

```markdown
# <session-id> — <short human title>

## Seed
<one paragraph: what was the session for? what question or task was in play?>

## Verdicts
- **H1 stability**: `<clear|partial|fail|pending>` — <rationale>
- **H1 complementarity**: `<clear|partial|fail|pending>` — <rationale>
- **H2 fresh-reader-pass**: `<clear|partial|fail|pending>` — <rationale>

## Drift
Verdict: `<drift-audit.json.verdict>` (see `drift-audit.json` @ <$DA_SHORT>).
<rationale referencing specific load-bearing findings by turn_ref or category>

## What happened
<free-form prose: per-peer contributions, coordination patterns, turn-by-turn nuance>
```

### Verdict rubric

Use these values (and only these) for each KPI, per [`design/poc.md`](../../design/poc.md) per-session clear-definitions:

- `clear` — the session meets the KPI's clear-definition criteria.
- `partial` — some criteria met, others partially; judgment call with rationale.
- `fail` — the KPI's criteria are NOT met.
- `pending` — requires an asynchronous step not yet complete (most commonly H2's fresh-reader test).

See [`design/poc.md` "Per-session clear definitions"](../../design/poc.md) for the full criteria.

### Step 3 — Read `drift-audit.json` and write the Drift section

```bash
jq '.verdict, .findings[] | select(.severity=="finding")' "observations/sessions/$SID/drift-audit.json"
```

Cite the `verdict` verbatim. Reference each `severity: "finding"` entry by `turn_ref` or `category`. If verdict is `no_drift` with empty findings, state that drift is not the blocker for H2. Do NOT introduce a drift category or severity absent from `drift-audit.json.findings[]` (per FR-008).

### Step 4 — Commit as a session-bundle amend

```bash
git add "observations/sessions/$SID/summary.md"
git commit -m "session bundle amend: $SID — summary @ $DA_SHORT" \
           -m "Mode: single-author"
```

No taxonomy token on the subject — default single-author initial commit.

### Step 5 — Run sanity checks

See **Post-commit sanity checks** below. If any check fails, fix via the **Revision path (C / Path D)** below — NEVER `git commit --amend`.

**Done.** Bundle now has a committed single-author summary.

---

## Path B — Agent-drafted + operator-ratified summary

Use this when an agent (Dalgos, Vigil) or delegated human drafts the prose; the operator edits as needed, writes the H1/H2 verdicts themselves, and commits.

### Step 1 — Drafter produces the draft

The drafter reads the bundle (`transcript.md`, `meta.json`, `interventions.json`, `drift-audit.json`) and authors `summary.md` directly at `observations/sessions/$SID/summary.md`. Alternatively, the drafter can write to `observations/sessions/$SID/summary.draft.md` as a scratch file (NOT committed). Drafter MAY propose verdict values but labels them clearly as draft proposals.

### Step 2 — Operator reviews, edits, writes verdicts

The operator opens `observations/sessions/$SID/summary.md`, edits the prose as needed, and **writes the three H1/H2 verdict lines themselves** (per FR-005 — operator is authoritative on verdicts regardless of drafter). The operator MAY copy the drafter's proposed verdict values verbatim if they agree, but the act of writing the verdicts in the final file represents the operator's attestation.

If the drafter used `summary.draft.md` as a scratch file, remove it before commit:

```bash
rm -f "observations/sessions/$SID/summary.draft.md"
```

### Step 3 — Pin the drift-audit version

Same as Path A Step 1.

### Step 4 — Commit as a session-bundle amend (operator commits)

```bash
git add "observations/sessions/$SID/summary.md"
git commit -m "session bundle amend: $SID — summary @ $DA_SHORT" \
           -m "Mode: agent-drafted, drafted-by: Dalgos, ratified-by: Zoe"
```

The `drafted-by:` field identifies the agent or human who produced the draft. `ratified-by:` identifies the operator. Both MUST be present for agent-drafted mode.

### Step 5 — Run sanity checks

Same as Path A Step 5.

**Done.** Bundle now has a committed agent-drafted + operator-ratified summary.

---

## Path C — Summary revision

Use this when a committed summary needs correction (typo, late-arriving H2 verdict after the fresh-reader test, wording cleanup after peer feedback, or drift-refresh after spec 008 Path C re-audit).

### Step 1 — Identify the reason

Pick from:

- **typo / wording cleanup**: `revision: <short reason>`
- **late H2 verdict** (pending → resolved): `revision: H2-verdict-resolved`
- **late H1 verdict** (pending → resolved): `revision: H1-<stability|complementarity>-resolved`
- **drift-refresh** (upstream drift-audit re-audit per spec 008 Path C): `revision: drift-refresh, supersedes <old-drift-short-sha>`

### Step 2 — Edit `summary.md`

Open the file, make the correction. For drift-refresh, update the Drift section to cite the new verdict + re-pin `<drift-audit-short-sha>` in the subject. For verdict resolution, change `pending` to the resolved value and update the rationale.

### Step 3 — Pin the current drift-audit version

Same as Path A Step 1. For drift-refresh, the new `$DA_SHORT` differs from the superseded one.

### Step 4 — Commit as a follow-up session-bundle amend

**CRITICAL**: NEVER `git commit --amend` on the prior summary commit. Always a follow-up commit per [spec 001 FR-014](../001-session-bundle-skeleton/spec.md) + this slice's FR-011.

```bash
# Typo fix:
git commit -m "session bundle amend: $SID — summary revision: typo-fix @ $DA_SHORT"

# Late H2 verdict resolution:
git commit -m "session bundle amend: $SID — summary revision: H2-verdict-resolved @ $DA_SHORT" \
           -m "Fresh-reader test completed; H2 verdict resolved from pending to clear."

# Drift-refresh after spec 008 Path C re-audit:
OLD_DA_SHORT=<short-sha-of-superseded-drift-audit>
git commit -m "session bundle amend: $SID — summary revision: drift-refresh, supersedes $OLD_DA_SHORT @ $DA_SHORT" \
           -m "Drift-audit re-audited per spec 008 Path C; verdict changed from minor_drift to no_drift."
```

### Step 5 — Verify the prior version is preserved

```bash
git log --all --follow --format='%H %s' -- "observations/sessions/$SID/summary.md"
git show <prior-commit>:"observations/sessions/$SID/summary.md"
```

**Done.** Revision landed; prior version retrievable from git history.

---

## Path D — Peer-audit (optional follow-up)

Use this when a peer reviewer (another agent, operator colleague, or uninvolved human) audits a previously-committed summary. Peer-audit is **optional** per FR-018 — counted-session eligibility does not require it. But when it happens, the ledger lets POC-exit synthesis count independent-review coverage.

### Step 1 — Read the existing summary

```bash
SID=<session-id>
cat "observations/sessions/$SID/summary.md"
```

The reviewer reads the summary, cross-references the bundle inputs (transcript / meta / interventions / drift-audit), and forms an independent judgment.

### Step 2 — Decide audit outcome

One of:

- **No material findings**: the summary accurately represents the session; verdicts stand; no wording changes needed.
- **Wording suggestions**: minor edits to improve clarity without changing verdicts.
- **Material disagreement**: the reviewer disagrees with a verdict value or a factual claim. **NOT resolved by the peer-audit itself** — the reviewer records their disagreement; the operator decides whether to revise (Path C).

### Step 3 — Pin the current drift-audit version

```bash
DA_SHA=$(git log -1 --format=%H -- "observations/sessions/$SID/drift-audit.json")
DA_SHORT=$(git rev-parse --short "$DA_SHA")
```

### Step 4 — Commit the peer-audit event

If the summary's rendered prose does NOT change (no material findings OR disagreement-without-changes), append a non-rendered audit marker so the event still touches `summary.md` and appears in the path-limited peer-audit ledger:

```bash
printf '\n<!-- Peer audit: Vigil. No material findings. -->\n' >> "observations/sessions/$SID/summary.md"
git add "observations/sessions/$SID/summary.md"
git commit \
  -m "session bundle amend: $SID — summary [peer-audited by Vigil] @ $DA_SHORT" \
  -m "Peer audit by Vigil. No material findings."
```

Or for disagreement-without-changes:

```bash
printf '\n<!-- Peer audit: Vigil. Disagreement recorded; no summary text changes requested. -->\n' >> "observations/sessions/$SID/summary.md"
git add "observations/sessions/$SID/summary.md"
git commit \
  -m "session bundle amend: $SID — summary [peer-audited by Vigil] @ $DA_SHORT" \
  -m "Peer audit by Vigil. Disagree with H1 complementarity verdict (I read it as partial, not clear because Vigil's reciprocal contribution at turn 14 wasn't clearly load-bearing). Flagging for operator judgment — no summary change requested."
```

If the peer-audit incorporates wording changes from the reviewer:

```bash
git add "observations/sessions/$SID/summary.md"
git commit -m "session bundle amend: $SID — summary [peer-audited by Dalgos] revision: wording-cleanup @ $DA_SHORT" \
           -m "Peer audit by Dalgos. Incorporated two wording suggestions in the What happened section. No verdict changes."
```

### Step 5 — Verify the peer-audit ledger

```bash
git log --all --grep='peer-audited' --format='%H %s' -- "observations/sessions/$SID/summary.md"
```

**Done.** Peer-audit event landed; cumulative `git log --all --grep='peer-audited'` shows the full ledger across all sessions.

---

## Halt conditions

Stop and fix upstream if any of these hold (per C1):

| Condition | Fix where |
|---|---|
| `observations/sessions/<session-id>/` does not exist | Confirm `<session-id>`; session may not be bundle-committed yet |
| `meta.json` missing or unreadable | Session-bundle close step ([spec 001](../001-session-bundle-skeleton/spec.md)) |
| `meta.json.pinned_rules_ref` unset | Session-bundle close step ([spec 001 FR-010](../001-session-bundle-skeleton/spec.md)) |
| `meta.json.closed_at` unset | Session is still open — close it first via the session-control path (spec 004) |
| `transcript.md` missing | Transcript export ([spec 006](../006-discord-transcript-export/spec.md)) |
| `interventions.json` missing | Intervention-tagging slice (Codex) |
| `drift-audit.json` missing | Drift-audit workflow ([spec 008](../008-drift-audit-workflow/spec.md)) — MUST land before summary begins |
| Working tree has unrelated uncommitted changes | Stash or commit those first; summary amend should land clean |

**Non-silent failure principle** (per FR-002 / FR-018): when halting, surface the specific unmet condition. Do not produce a half-formed summary or placeholder.

---

## Post-commit sanity checks

Run these after every committed summary (Path A, B, C, or D). If any check fails, fix via **Path C (revision)** — do NOT use `git commit --amend`.

```bash
SID=<session-id>
SUMMARY="observations/sessions/$SID/summary.md"

# 1. Required sections present in the correct order
grep -nE '^## (Seed|Verdicts|Drift|What happened)' "$SUMMARY"
# Expected output: 4 matching lines, in that order.

# 2. Three verdict lines, one per KPI, in the R2 grep-stable format
grep -E '^- \*\*H[12] (stability|complementarity|fresh-reader-pass)\*\*: `(clear|partial|fail|pending)`' "$SUMMARY"
# Expected output: exactly 3 lines.

# 3. Drift section cites drift-audit.json (verdict name or file reference)
grep -E 'drift-audit\.json|no_drift|minor_drift|load_bearing_drift' "$SUMMARY"
# Expected output: at least 1 match in the Drift section.

# 4. Commit subject format is valid
git log -1 --format='%s' -- "$SUMMARY"
# Expected: "session bundle amend: <sid> — summary[ <taxonomy-token>] @ <drift-short-sha>"

# 5. Commit body carries the Mode: line (for initial commits)
git log -1 --format='%s' -- "$SUMMARY" | grep -qE 'revision:|\[peer-audited' \
  && echo "skipping Mode check (follow-up commit)" \
  || git log -1 --format='%b' -- "$SUMMARY" | grep -E '^Mode:'
# Expected for initial commits: one match (Mode: single-author OR Mode: agent-drafted, ...)

# 6. Drift-audit SHA in subject resolves to an existing commit
DA_SHORT=$(git log -1 --format='%s' -- "$SUMMARY" | sed -E 's/.*@ ([a-f0-9]+)$/\1/')
git cat-file -e "$DA_SHORT" 2>/dev/null && echo "✓ drift-audit short SHA resolves: $DA_SHORT"
```

All six checks are cheap and fast — run them as a habit after every summary commit.

---

## Cross-slice reminders

- **Rubric content + manual-audit procedure**: [`observations/drift-audits/RUBRIC.md`](../../observations/drift-audits/RUBRIC.md) (spec 005). Read if you need to understand why the drift-audit verdict is what it is — but don't re-derive findings in the summary prose.
- **Drift-audit workflow**: [`observations/drift-audits/WORKFLOW.md`](../../observations/drift-audits/WORKFLOW.md) (spec 008). Walked first before summary authoring begins.
- **Session bundle discipline**: [spec 001 FR-014](../001-session-bundle-skeleton/spec.md) — append-only commits, no `--amend`.
- **KPI rollup**: Phase 5 slice (not yet specced). The summary's verdict lines are the authoritative input; don't worry about the rollup during summary authoring.

---

## When in doubt

- Operator's verdict wins over drafter's proposed verdict.
- Summary cites drift, doesn't re-derive it — if you disagree with drift, re-audit (spec 008 Path C), don't rewrite the drift story in prose.
- Revisions are follow-up commits. Never `--amend`.
- Peer-audits are optional. Lack of a peer-audit is not a block on counted-session eligibility.
