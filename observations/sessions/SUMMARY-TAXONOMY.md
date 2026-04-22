# Commit-Message Taxonomy: Session-Summary Amend Commits

**Runtime reference** — grep-able vocabulary for every amend commit that lands a `summary.md` inside a session bundle, revises a previously-committed summary, or records a post-commit peer-audit event. Derived from [spec 009 contract C4](../../specs/009-session-summary-workflow/contracts/workflow-contracts.md) and [spec 001 FR-014](../../specs/001-session-bundle-skeleton/spec.md). Follows the same bracket-token + `@ <short-sha>` convention as [spec 008 `observations/drift-audits/COMMIT-TAXONOMY.md`](../drift-audits/COMMIT-TAXONOMY.md).

Every summary amend commit MUST follow this subject format:

```
session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>
```

Where `<drift-audit-short-sha>` is the commit short SHA (typically 7 chars) of the `drift-audit.json` the summary is drafted against — pinning the summary's drift-citation provenance so a reader can reconstruct which audit version the summary references. Author-mode (single-author vs agent-drafted) lives in the commit **body** via a `Mode:` line per FR-004 — NOT in the subject — so subject grep-signals stay focused on lifecycle events rather than routine authoring metadata.

**Never**: `git commit --amend` on a previously-committed `summary.md`. All corrections are follow-up amend commits per spec 001 FR-014. The lesson from spec 008 PR #66's I1 finding applies here too.

---

## Tokens

### 1. *(absent)* — default case (initial commit)

```
session bundle amend: 2026-05-01-spec-010-split — summary @ abc1234
```

**Use when**: initial summary commit, either single-author (Path A) OR agent-drafted + operator-ratified (Path B). Mode is recorded in the commit body.

**Discoverable by**: `git log -1 --format='%s' -- observations/sessions/<id>/summary.md`

**Commit body requirement** (initial commits only): MUST include one of:

- `Mode: single-author`
- `Mode: agent-drafted, drafted-by: <agent-or-human-id>, ratified-by: <operator-id>`

Follow-up commits (tokens #2–#4) do NOT carry a new `Mode:` line — the mode of the original authoring is inherited.

---

### 2. `[peer-audited by <id>]` — post-commit peer-audit event

```
session bundle amend: 2026-05-01-spec-010-split — summary [peer-audited by Vigil] @ abc1234
```

**Use when**: a peer reviewer (another agent, operator colleague, or uninvolved human) audits a previously-committed summary. May be combined with `revision:` if the audit incorporates wording changes — see combined-token examples below.

**Discoverable by**: `git log --all --grep='peer-audited' --format='%H %s' -- observations/sessions/*/summary.md`

This is the **peer-audit ledger** per [spec 009 contract C7](../../specs/009-session-summary-workflow/contracts/workflow-contracts.md). POC-exit synthesis and any mid-POC independent-review-coverage review count peer-audits across counted sessions here. Peer-audit is NOT required for counted-session eligibility — but when it happens, the ledger is the discoverable signal.

**Commit body recommendation**: name the reviewer identity and either "No material findings" OR a one-line summary of findings and any wording changes incorporated. Example:

```
session bundle amend: 2026-05-01-spec-010-split — summary [peer-audited by Vigil] @ abc1234

Peer audit by Vigil. Disagree with H1 complementarity verdict (I read it as
partial, not clear because Vigil's reciprocal contribution at turn 14 wasn't
clearly load-bearing). Flagging for operator judgment — no summary change
requested.
```

---

### 3. `revision: <reason>` — revision commit (not drift-refresh)

```
session bundle amend: 2026-05-01-spec-010-split — summary revision: typo-fix @ abc1234
```

**Use when**: a previously-committed summary needs correction — typo / wording cleanup / late-arriving H1 or H2 verdict resolved / operator updates rationale after peer feedback. The `<reason>` is free-form but convention-driven:

| `<reason>` convention | When |
|---|---|
| `revision: typo-fix` | Spelling / grammar correction with no semantic change |
| `revision: wording-cleanup` | Minor rewording that doesn't change verdicts |
| `revision: H2-verdict-resolved` | `H2 fresh-reader-pass: pending` → concrete value after the fresh-reader test completes |
| `revision: H1-stability-resolved` / `revision: H1-complementarity-resolved` | Analogous for H1 verdicts |
| `revision: <short reason>` | Any other revision with a self-describing slug |

**Discoverable by**: `git log --all --grep='summary revision' --format='%H %s' -- observations/sessions/*/summary.md`

The revision commit's file-level change reflects the correction; the prior version remains retrievable via `git show <prior-commit>:observations/sessions/<id>/summary.md`. Per spec 001 FR-014, this is an append-only history discipline — **never** `git commit --amend`.

---

### 4. `revision: drift-refresh, supersedes <old-drift-short-sha>` — drift-refresh revision

```
session bundle amend: 2026-05-01-spec-010-split — summary revision: drift-refresh, supersedes abc1234 @ def5678
```

**Use when**: the cited `drift-audit.json` was re-audited per spec 008 Path C, producing a new drift-audit commit SHA. The summary's `## Drift` section must be refreshed to cite the new verdict, and the summary's own commit pins the new drift-audit short SHA at the end. The token body carries the superseded old drift-audit short SHA for traceability — the reader can tie the summary revision to the drift-audit re-audit that triggered it.

**Discoverable by**: `git log --all --grep='drift-refresh' --format='%H %s' -- observations/sessions/*/summary.md`

---

## Combining tokens

Multiple tokens MAY appear when an event is compound. Examples:

- **Peer-audit that incorporates wording changes**:
  ```
  session bundle amend: 2026-05-01-spec-010-split — summary [peer-audited by Dalgos] revision: wording-cleanup @ abc1234
  ```
- **Peer-audit resolving a late H2 verdict**:
  ```
  session bundle amend: 2026-05-01-spec-010-split — summary [peer-audited by Vigil] revision: H2-verdict-resolved @ abc1234
  ```
- **Rare: peer-audit + drift-refresh** (both lifecycle events on one commit):
  ```
  session bundle amend: 2026-05-01-spec-010-split — summary [peer-audited by Dalgos] revision: drift-refresh, supersedes abc1234 @ def5678
  ```

**Token ordering convention** (when combined): `[peer-audited by <id>]` first (bracket draws the eye), `revision: <reason>` second. Mirrors spec 008's `[arbitrated]` → `two-auditor-upgrade` → `re-run, supersedes ...` ordering rule.

---

## Grep reference card

```bash
# All summary amends across all sessions:
git log --all --grep='— summary' --format='%H %s' -- observations/sessions/*/summary.md

# Peer-audit ledger (independent-review coverage signal):
git log --all --grep='peer-audited' --format='%H %s' -- observations/sessions/*/summary.md

# Revision ledger (lifecycle evolution):
git log --all --grep='summary revision' --format='%H %s' -- observations/sessions/*/summary.md

# Drift-refresh ledger (summaries following drift-audit re-audits):
git log --all --grep='drift-refresh' --format='%H %s' -- observations/sessions/*/summary.md

# For a specific session:
git log --all --format='%H %s' -- observations/sessions/<session-id>/summary.md

# Dual-ledger cross-reference (summaries peer-audited AND drift-arbitrated):
# (combine spec 008's [arbitrated] grep with spec 009's [peer-audited] grep across sessions)
git log --all --grep='\[arbitrated\]' --format='%H' > /tmp/drift-arbitrated.txt
git log --all --grep='peer-audited' --format='%H' > /tmp/summary-peer-audited.txt
# Compare the two lists per session-id to see which counted sessions have dual independent review.
```

---

## Drift-audit version pinning

The `@ <drift-audit-short-sha>` suffix on every summary amend commit pins which drift-audit version the summary is drafted against. This is the `E6 Drift-Audit Version Pin` entity from [spec 009 data-model](../../specs/009-session-summary-workflow/data-model.md).

- **Commit subject**: short SHA (typically 7 chars) for readability.
- **`summary.md` Drift section**: cites the same drift-audit via `(see drift-audit.json @ <short-sha>)` in prose.
- **Consistency**: the short SHA in the commit subject and the short SHA in the `summary.md` Drift section MUST match at initial commit. Drift-refresh revisions update both.

Retrieve the drift-audit short SHA before committing:

```bash
SID=<session-id>
DA_SHA=$(git log -1 --format=%H -- "observations/sessions/$SID/drift-audit.json")
DA_SHORT=$(git rev-parse --short "$DA_SHA")
echo "Drafting summary against drift-audit @ $DA_SHA (short: $DA_SHORT)"
```

### Finding summaries authored against a specific drift-audit version

```bash
# All summaries drafted against drift-audit short SHA abc1234:
git log --all --grep="@ abc1234" --format='%H %s' -- observations/sessions/*/summary.md
```

Useful for cross-referencing which summaries are stale after a drift-audit re-audit per spec 008 Path C — those summaries typically need a `revision: drift-refresh, supersedes <old-short-sha>` follow-up commit to refresh the drift citation.

### Re-audit → drift-refresh flow

When spec 008 Path C lands a new `drift-audit.json` for a session, any previously-committed summary citing the old drift-audit becomes stale on its drift section. The lifecycle:

1. Spec 008 Path C commits a new `drift-audit.json` (new commit SHA).
2. This workflow's Path C revision fires with `revision: drift-refresh, supersedes <old-drift-short-sha>` token (taxonomy token #4 above).
3. The summary's `## Drift` section is updated to cite the new verdict + new short SHA.
4. The new amend commit's subject pins the new `@ <drift-audit-short-sha>`; the token body carries the superseded old SHA for traceability.

Cross-references [spec 009 data-model E3 (Drift Citation) + E4 (Revision Event) + E6 (Drift-Audit Version Pin)](../../specs/009-session-summary-workflow/data-model.md).

---

## Cross-references

- [`SUMMARY-WORKFLOW.md`](SUMMARY-WORKFLOW.md) — the procedure that produces these commits
- [`specs/009-session-summary-workflow/contracts/workflow-contracts.md`](../../specs/009-session-summary-workflow/contracts/workflow-contracts.md) C4 — the authoritative contract this file documents
- [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md) FR-014 — the bundle-amend-commit convention this taxonomy extends
- [`../drift-audits/COMMIT-TAXONOMY.md`](../drift-audits/COMMIT-TAXONOMY.md) (spec 008) — the prior-art pattern being reused; the arbitration ledger for spec 008 complements the peer-audit ledger here
