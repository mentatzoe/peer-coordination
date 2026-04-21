# Data Model: Session-Summary Workflow

**Branch**: `009-session-summary-workflow` | **Date**: 2026-04-21
**Input**: Phase 1 output. Workflow-level entities only. `summary.md` is prose-first Markdown rather than a JSON schema, so this document describes **structural invariants** and **workflow-level entities** (mode, revision, peer-audit event) rather than a field-by-field schema.

## Relationship to upstream schemas

- **Drift-audit schema**: owned by [`specs/005-drift-audit-rubric/data-model.md`](../005-drift-audit-rubric/data-model.md). Consumed as a pointer via FR-008 + the drift-section Drift-audit citation entity (E5 below). Not redefined here.
- **Session bundle shape**: owned by [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) (FR-007 + FR-008 + FR-012 + FR-014). The summary is one of five files in the bundle; this slice adds no new bundle-level entities.
- **Intervention-tag shape**: owned by the Codex intervention-tagging slice (not yet specced). Summary may reference intervention types informally (FR-016); the shape is opaque here.

What this slice OWNS:

- The required-section invariants of `summary.md` (per spec 001 FR-012 + spec 009 FR-003 + FR-010 inverted-pyramid ordering).
- Workflow-level entities that live in commit messages, commit bodies, or the structural layout of `summary.md` (not as new artifact files).

---

## Structural invariants of `summary.md`

Every committed `summary.md` MUST contain these four top-level Markdown sections, in this order (per FR-010, clarify Q2):

1. **Seed** — anchor section. Plain-prose statement of what the session was for. Answers "what question or task was in play?"
2. **Verdicts** — structural section. Exactly three list-bullet lines following the R2 format (E3 below). Value + rationale per KPI.
3. **Drift** — structural section. Cites `drift-audit.json.verdict` verbatim and references specific load-bearing findings by `turn_ref` or `category` (per FR-008). Prose allowed for rationale, but verdict citation is non-negotiable.
4. **What happened** — free-form prose section. Per-peer contributions, coordination patterns, turn-by-turn nuance. Reader-facing body. No length cap; no sub-heading template.

The section headings MUST be `## Seed`, `## Verdicts`, `## Drift`, `## What happened` (exact text, in order). The top of the file has a conventional `# <session-id> — <short human title>` heading and optional metadata line(s) before the first `## Seed` section.

**Example skeleton**:

```markdown
# 2026-05-01-spec-010-split — Dalgos × Vigil on the spec 010 split

## Seed
<one-paragraph statement of the session's question or task>

## Verdicts
- **H1 stability**: `clear` — <rationale>
- **H1 complementarity**: `clear` — <rationale>
- **H2 fresh-reader-pass**: `pending` — <rationale>

## Drift
Verdict: `minor_drift` (see drift-audit.json @ abc1234). One warn-severity
finding on hidden_channel_reference at turn 11...

## What happened
<free-form prose: per-peer contributions, coordination patterns, ...>
```

---

## Workflow-level entities

### E1 — Author Mode

**What it represents**: whether a given session's summary is produced by the operator alone (single-author) or by a delegated drafter with operator ratification (agent-drafted + operator-ratified). Set per-session by the operator (clarify Q1 → tiered).

**Where it lives**: in the session's amend-commit body (not on `summary.md` itself, not in the subject). Commit body MUST carry one of:

- `Mode: single-author`
- `Mode: agent-drafted, drafted-by: <agent-id-or-human-id>, ratified-by: <operator-id>`

**Values**: `single-author` | `agent-drafted`

**Assignment rule**: the operator chooses per-session using their effort / fairness / compression heuristic (per spec Context + clarify Q1 rationale). No "default" at spec time — both are first-class.

**Transitions**: none within a single summary. If mode should change retroactively (e.g. an agent-drafted summary is re-authored single-author), the revision path (E4) applies.

---

### E2 — Verdict Line

**What it represents**: one of the three KPI judgments (H1 stability, H1 complementarity, H2 fresh-reader-pass) inside the Verdicts section of `summary.md`. The authoritative per-session KPI input the downstream rollup reads (per FR-017).

**Where it lives**: inside the `## Verdicts` section of `summary.md` as a Markdown list bullet. Exactly three verdict lines per summary.

**Format** (per R2, grep-stable):

```
- **<KPI name>**: `<value>` — <rationale>
```

Where:

- `<KPI name>` is exactly one of: `H1 stability`, `H1 complementarity`, `H2 fresh-reader-pass`.
- `<value>` is exactly one of: `clear`, `partial`, `fail`, `pending`, backtick-quoted.
- `<rationale>` is free-form prose, no length cap, starts after an em-dash (`—`).

**Grep discovery**:

```bash
grep -E '^- \*\*H[12] ' summary.md
```

Returns all three verdict lines; further regex can extract the value.

**Validation rules**:

- Exactly three verdict lines per summary (no more, no fewer).
- One per KPI name (no duplicates).
- Value MUST be one of the four enum values; anything else is a schema violation.
- Rationale MUST be non-empty (at least a clause explaining the value).

**"Pending" semantics**: reserved for verdicts that require an asynchronous step not complete at commit time (most commonly H2's fresh-reader test). Acceptable at initial commit; resolution triggers the revision path (E4).

---

### E3 — Drift Citation

**What it represents**: the summary's reference to the upstream `drift-audit.json` — verdict + specific findings — stated in the `## Drift` section per FR-008.

**Where it lives**: inside the `## Drift` section of `summary.md`. Not a separate field.

**Invariants**:

- MUST cite `drift-audit.json.verdict` verbatim (one of `no_drift` / `minor_drift` / `load_bearing_drift` per spec 005's schema).
- MUST reference specific load-bearing findings by `turn_ref` or `category` when `drift-audit.json.findings[]` contains entries with `severity: "finding"`.
- MUST NOT introduce a drift category or severity that is absent from `drift-audit.json.findings[]` (per FR-008, no re-derivation).
- MUST cite the drift-audit commit short SHA (matches the `@ <drift-audit-short-sha>` in the amend commit subject) so the summary's drift reference is traceable to the specific audit version.

**If drift is refreshed via spec 008 Path C (re-audit)**: the summary MUST be revised per E4 with the `revision: drift-refresh, supersedes <old-drift-short-sha>` taxonomy token, and the drift section updated to cite the new verdict.

---

### E4 — Revision Event

**What it represents**: a subsequent follow-up amend commit that corrects a previously-committed `summary.md` (typo, late-arriving H2 verdict, drift-refresh, peer-audit-incorporation, etc.).

**Where it lives**: session-bundle git history. Append-only — the prior summary version remains reconstructible via `git show <prior-commit>:observations/sessions/<session-id>/summary.md`.

**Invariants**:

- MUST be a follow-up commit (NEVER `git commit --amend` on the prior commit — per spec 001 FR-014).
- MUST include `revision: <reason>` in the amend-commit subject's taxonomy-token slot (per R1).
- MAY flip verdict values (e.g. `pending` → `clear` for H2) or amend prose.
- Replaces `summary.md` fully; the revised file reflects the new state. No delta encoding.

**Commit message format** (per R1):

```
session bundle amend: <session-id> — summary revision: <reason> @ <drift-audit-short-sha>
```

Special sub-case when triggered by drift-audit re-audit:

```
session bundle amend: <session-id> — summary revision: drift-refresh, supersedes <old-drift-short-sha> @ <new-drift-short-sha>
```

**Grep discovery**:

```bash
git log --all --grep='summary revision' --format='%H %s' -- observations/sessions/<session-id>/summary.md
```

---

### E5 — Peer-Audit Event

**What it represents**: an optional post-commit peer review of a `summary.md` that previously landed, recorded as a follow-up amend commit per FR-018 + clarify Q3.

**Where it lives**: session-bundle git history, as a commit whose subject carries the `[peer-audited by <id>]` token.

**Invariants**:

- MUST be a follow-up commit, NOT a revision to the summary file itself — the `summary.md` file may be unchanged by a peer-audit commit (if the reviewer had no findings or their observations are recorded only in the commit body). If the reviewer's observations lead to changes in `summary.md`, those changes land in the same commit (a "peer-audit + revision" combined commit — token combo allowed).
- MUST cite the reviewer identity in the token: `[peer-audited by Dalgos]`, `[peer-audited by Vigil]`, `[peer-audited by <human-name>]`, etc.
- Commit body SHOULD record the reviewer's findings or "no material findings" + any wording changes incorporated.
- Does NOT require operator ratification (the reviewer's audit is a reviewer-owned artifact; the operator retains authority over the final summary via their ability to further revise).

**Counting semantics**:

- A peer-audit ledger sweep returns `N_peer_audited / N_counted_sessions`. The POC-exit synthesis slice may use this ratio as an independent-review-coverage signal without requiring every counted session to have a peer audit.
- Combined with spec 008's arbitration-ledger, the operator can see which counted sessions have (a) been drift-arbitrated and (b) been summary-peer-audited — giving a dual independent-review lens on the Phase 3 evidence set.

**Commit message format** (per R1):

```
session bundle amend: <session-id> — summary [peer-audited by <id>] @ <drift-audit-short-sha>
```

Combined with revision:

```
session bundle amend: <session-id> — summary [peer-audited by Dalgos] revision: wording-cleanup @ <drift-audit-short-sha>
```

**Grep discovery**:

```bash
git log --all --grep='peer-audited' --format='%H %s' -- observations/sessions/*/summary.md
```

Returns the full peer-audit ledger across all session summaries.

---

### E6 — Drift-Audit Version Pin

**What it represents**: the short SHA of the `drift-audit.json` commit the summary was drafted against, recorded in the amend-commit subject's `@ <drift-audit-short-sha>` slot.

**Where it lives**: amend-commit subject. Not a field on `summary.md` itself (summary's drift section cites the same SHA in prose — per E3 — so the information lives both on the commit and in the text).

**Invariants**:

- MUST resolve to a committed state of `observations/sessions/<session-id>/drift-audit.json`.
- MUST be the short SHA (typically 7 chars) for commit-subject readability — parallel to spec 008's `<rubric-short-sha>` convention.
- Once set on a committed summary, the value does NOT change retroactively. A drift-audit re-audit triggers a summary revision (E4) with `revision: drift-refresh, supersedes <old-drift-short-sha>` — the old pin remains on the prior commit.

---

## State transitions (workflow-level)

Session-summary state machine (per bundle):

```text
(closed bundle with drift-audit.json committed, no summary yet)
   │
   ├── single-author path ──→ summary.md committed (Mode: single-author)
   │        │
   │        ├── optional: operator revises ──→ summary revision follow-up commit
   │        │
   │        └── optional: peer-audits ──→ summary peer-audit follow-up commit
   │
   └── agent-drafted path ──→ draft authored → operator ratifies + commits
                                                    │
                                                    summary.md committed
                                                    (Mode: agent-drafted, drafted-by: <id>, ratified-by: <operator-id>)
                                                    │
                                                    ├── optional: operator revises
                                                    │
                                                    └── optional: peer-audits

(any committed summary)
   │
   ├── drift-audit re-audited upstream ──→ summary revision: drift-refresh follow-up commit
   │
   ├── H2 fresh-reader test completes ──→ summary revision: H2-verdict-resolved follow-up commit
   │
   └── peer reviewer audits post-commit ──→ summary [peer-audited by <id>] follow-up commit
```

No hidden states; every transition corresponds to a discoverable git commit. No state lives outside the bundle directory + git history.

---

## Cross-references to entities owned elsewhere

| Entity | Owner | Used by this workflow as |
|---|---|---|
| Session Bundle (transcript + meta + interventions + drift-audit + summary) | [spec 001](../001-session-bundle-skeleton/spec.md) | Input contract — summary lives in the bundle directory |
| Transcript (`transcript.md`) | [spec 006](../006-discord-transcript-export/spec.md) | Input — summary may reference transcript turns by timestamp |
| Pinned Rules snapshot (via `meta.json.pinned_rules_ref`) | [spec 003](../003-pinned-rules-authoring/spec.md) | Consumed context — summary may cite rules-in-force when relevant |
| `drift-audit.json` schema | [spec 005 data-model](../005-drift-audit-rubric/data-model.md) | Consumer contract — summary cites verdict + findings, never re-derives |
| Drift-audit workflow (amend-commit conventions, C8 consumer discipline) | [spec 008](../008-drift-audit-workflow/spec.md) | Model for this slice's commit-taxonomy pattern; consumer discipline inherited |
| Intervention-tag schema | Codex slice (not yet specced) | Consumed opaquely via `interventions.json`; summary may reference tag types informally |
| Per-session clear-definition criteria (H1 stability, H1 complementarity, H2 fresh-reader-pass) | [`design/poc.md`](../../design/poc.md) | Judgment thresholds for verdict values; not re-specified |

---

## Not-owned entities (explicit non-scope)

- `drift-audit.json` schema — owned by spec 005 data-model. This slice only references it.
- Intervention-tag schema — owned by the Codex slice. This slice consumes opaquely.
- KPI rollup schema + cross-session aggregation entities — Phase 5 slice, not yet specced.
- LLM prompt template for summary automation — deferred follow-on, not in this slice's scope.
