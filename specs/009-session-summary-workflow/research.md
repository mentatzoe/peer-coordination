# Research: Session-Summary Workflow

**Branch**: `009-session-summary-workflow` | **Date**: 2026-04-21
**Input**: Decisions owed for Phase 0 planning, consolidating the three `/speckit.clarify` Q/As (FR-004, FR-010, FR-018) and the remaining best-practice choices for commit-taxonomy tokens, verdict-line format, and cross-slice consumption.

This slice's design space is procedure + git convention, not technology choice. The three `[NEEDS CLARIFICATION]` markers from specify were resolved during the clarify pass (see `spec.md` `## Clarifications` block). Research below consolidates the supporting rationale and pins the remaining operational conventions so Phase 1 artifacts (`data-model.md`, `contracts/workflow-contracts.md`, `quickstart.md`) can reference decisions rather than re-derive them.

---

## R1 — Commit-taxonomy tokens for summary amend commits

### Decision

Summary amend commits follow the same bracket-token taxonomy pattern established by spec 008's `COMMIT-TAXONOMY.md`, with a summary-specific token set. Full subject format:

```
session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>
```

Taxonomy tokens:

| Token | When | Counting signal |
|---|---|---|
| *(absent)* | Single-author OR agent-drafted + operator-ratified (default case, mode recorded in commit body) | — |
| `[peer-audited by <id>]` | Follow-up commit landing a peer-audit review of a previously-committed summary | Per FR-018 — `git log --all --grep='peer-audited' -- observations/sessions/*/summary.md` returns the audit ledger |
| `revision: <reason>` | Follow-up commit correcting a previously-committed summary (typo, late-arriving H2 verdict, rewording after peer feedback) | Discoverable with `git log --all --grep='summary revision'` |
| `revision: drift-refresh, supersedes <old-drift-short-sha>` | Follow-up commit when the cited `drift-audit.json` was re-audited per spec 008 Path C and the summary's drift section needs to cite the refreshed verdict | Traceability tying summary revisions to drift-audit re-audits |

`<drift-audit-short-sha>` is the commit short SHA of the `drift-audit.json` file the summary is drafted against — pinning the drift-citation's provenance so downstream readers can reconstruct which audit verdict the summary references.

### Rationale

- **Reuses spec 008's pattern**: the bracket-token + grep-able convention is already established and operator-familiar. No new mechanism needed.
- **Path-limited ledger stays honest**: peer-audit discovery is intentionally path-limited to `summary.md`, so a no-prose-change audit still needs a minimal file touch. The workflow uses a non-rendered HTML audit marker for that case rather than a sidecar file or an empty commit.
- **`<drift-audit-short-sha>` as version anchor**: parallel to how spec 008 uses `<rubric-short-sha>` for drift-audit commits. Gives the commit subject a stable "what version of the upstream input was this based on" signal.
- **Author-mode in commit body, not subject**: per FR-004 Q/A — mode choice (single-author vs agent-drafted) is recorded via a `Mode: single-author` or `Mode: agent-drafted, drafted-by: <id>, ratified-by: <id>` body line, not subject. Keeps the subject grep-signal focused on workflow events (peer audit, revision) rather than routine authoring metadata.
- **Revision reason inline**: putting `<reason>` after `revision:` rather than in a separate token keeps the subject one line and self-describing.

### Alternatives considered

- **Mode in subject (e.g. `[agent-drafted]`)** — rejected: clutters the subject for the common case; mode info is orthogonal to grep-worthy workflow events.
- **Separate sidecar file for peer-audit events** — rejected: adds a second artifact to manage; commit-message token plus a minimal non-rendered `summary.md` audit marker is still cheaper and keeps the ledger path-limited to the summary.
- **Reuse `[reviewed]` instead of `[peer-audited by <id>]`** — rejected: `[reviewed]` implies pre-commit review (as in spec 008 Path B two-auditor mode); `[peer-audited by <id>]` makes the post-commit nature and reviewer identity explicit.

---

## R2 — Verdict-line format (grep-stable)

### Decision

Each of the three KPI verdicts (H1 stability, H1 complementarity, H2 fresh-reader-pass) MUST appear in the Verdicts section as a Markdown list-bullet with this exact shape:

```
- **<KPI name>**: `<value>` — <rationale>
```

Where:

- `<KPI name>` is exactly one of `H1 stability`, `H1 complementarity`, `H2 fresh-reader-pass` (bold).
- `<value>` is backtick-quoted and exactly one of `clear`, `partial`, `fail`, `pending`.
- `<rationale>` is free-form prose after an em-dash (`—`), no length cap.

Worked examples:

```markdown
- **H1 stability**: `clear` — one directive-redirect at turn 8; no persistent loop; both peers active throughout.
- **H1 complementarity**: `partial` — Dalgos brought a distinct framing taken up by Vigil; Vigil's reciprocal contribution less clearly load-bearing.
- **H2 fresh-reader-pass**: `pending` — fresh-reader test scheduled for Friday.
- **H2 fresh-reader-pass**: `fail` — uninvolved reviewer couldn't reconstruct Vigil's second argument without the DM context referenced at turn 11.
```

### Rationale

- **Grep-stable**: downstream KPI rollup can extract all three verdicts with:
  ```bash
  grep -E '^\- \*\*H[12] ' summary.md | grep -oE '`(clear|partial|fail|pending)`'
  ```
  No LLM or complex parser needed.
- **Markdown-native**: renders cleanly in GitHub + terminal preview.
- **Rationale after em-dash**: human-readable, visually separates the value from the justification.
- **Backtick on value**: defends the value token against accidental substring collisions with prose (e.g. "`clear` after reviewing" grep-matches cleanly; "I think this is clear" does not).

### Alternatives considered

- **YAML frontmatter for verdicts** — rejected: splits the document into two cognitive surfaces (frontmatter vs prose); less natural for a human-legible document. KPI rollup parsing is only marginally easier with YAML vs grep-a-Markdown-list.
- **Free-form prose verdicts without structural constraint** — rejected in clarify Q2 (that was the non-recommended Option B). Parsing cost for downstream rollup grows unbounded.
- **Separate `verdicts.yaml` sidecar** — rejected: adds a file to the bundle that duplicates the summary's verdict information; single-source-of-truth principle says verdict lives once, in the summary.

---

## R3 — Idempotency (or lack thereof) for summary authoring

### Decision

Unlike spec 008's `drift-audit.json` (which is byte-identical modulo `audited_at` per that slice's FR-010), `summary.md` is **prose, not schema**, and idempotency is **not a workflow guarantee**. Two auditors producing summaries for the same bundle will produce different prose. Two re-runs by the same auditor will produce similar-but-not-identical prose.

What IS deterministic:

- **Structural invariants**: section ordering (Seed → Verdicts → Drift → What happened) is fixed per FR-010.
- **Verdict values**: for the same auditor on the same inputs, verdict values (`clear` / `partial` / `fail` / `pending`) should be stable; divergence signals auditor uncertainty, not workflow non-determinism.
- **Drift citation**: the cited `drift-audit.json.verdict` and specific findings are deterministic (they're just pointers to a fixed file).

What is NOT deterministic (and is acceptable):

- Prose wording, section length, choice of transcript turn to call out, rhetorical framing.
- Author voice differences between single-author and agent-drafted modes.

Contract C3 in `contracts/workflow-contracts.md` captures this as "structural determinism, not prose determinism."

### Rationale

- **Prose is irreducibly subjective**: "observed coordination patterns" is a judgment call about which turns mattered; two good-faith auditors will highlight different texture.
- **Constitution v1.5.0 Principle VI** (human-legible, not over-protocolized): forcing byte-identical prose would require mechanical templates that defeat the point of free-form prose sections.
- **Downstream consumers read the verdict lines + cited drift-audit, not the prose body**: KPI rollup only depends on what IS deterministic (FR-010's verdict-line format, FR-008's drift citations).

### Alternatives considered

- **Require byte-identical output modulo timestamps** — rejected: would force structured-schema representation; defeats the hybrid-prose decision from clarify Q2.
- **Add an `author_hash` field for tamper detection** — rejected: adds schema where none is needed; git commit SHA already provides immutability at the history layer.

---

## R4 — Two-author-mode lifecycle (agent-drafted + operator-ratified)

### Decision

Per FR-004 Q/A (tiered author discipline), when the operator chooses agent-drafted mode, the lifecycle is:

1. **Drafter produces** `summary.md` (or a `summary.draft.md` working file) against the bundle — standalone draft, no review loop.
2. **Operator reviews** the draft, makes direct edits as needed (no formal revision cycle), and records the three H1/H2 verdicts themselves per FR-005.
3. **Operator commits** via the single amend commit with `Mode: agent-drafted, drafted-by: <agent-id>, ratified-by: <operator-id>` in the commit body.

Key discipline:

- **No ratification-pending state on disk**: draft files MAY exist during authoring but MUST be removed (or `.gitignore`-filtered) before commit. Only the ratified `summary.md` lands in git.
- **Operator edits are not tracked separately**: the committed artifact reflects the ratified output; the draft vs final diff is not preserved in bundle git history (it can be preserved via PR review comments if useful, but the workflow does not require it).
- **Verdicts are ALWAYS operator-written**: the drafter MAY propose verdicts in the draft, but the operator re-evaluates and writes the final verdicts. The operator may lift the drafter's proposed rationale verbatim if they agree, but the act of commit = operator attestation.

### Rationale

- **Keeps the evidence trail clean**: one commit per summary, one artifact per bundle. Draft/final separation is authoring-tooling detail, not evidence-layer concern.
- **Identity contract is simple**: commit body records both identities; no per-section attribution needed.
- **Verdict authority is unambiguous**: operator writes the verdicts = operator owns them per Principle IV.

### Alternatives considered

- **Preserve draft files in git as part of the bundle** — rejected: adds noise to `observations/sessions/<id>/`, duplicates the committed summary, and invites cross-reading confusion about which version is authoritative.
- **Two-commit lifecycle (draft commit → ratified commit)** — rejected: doubles bundle-commit count for every agent-drafted session; the draft is ephemeral by design.
- **Require the drafter to submit via PR** — rejected: adds PR cycle latency for internal agent-to-operator handoff; operator ratification via commit body is sufficient.

---

## R5 — Revision lifecycle (append-only, no `--amend`)

### Decision

Per FR-011 and spec 001 FR-014, revisions to a committed `summary.md` are **always follow-up amend commits**, never `git commit --amend` on the prior commit. The revision commit:

- Subject includes `revision: <reason>` in the taxonomy-token slot per R1.
- Body describes what changed and why.
- File reflects the revised content; the prior version is retrievable via `git show <prior-commit>:observations/sessions/<session-id>/summary.md`.

The same discipline that spec 008 applied to drift-audit re-runs (R6 token patterns) applies here — the workflow explicitly forbids `--amend` per the hard lesson from the spec 008 Codex review (PR #66's I1 finding).

### Rationale

- **Spec 001 FR-014 compliance**: "Never rewrite history on session bundles; the amend commit is the durable record of the correction."
- **Audit trail preservation**: every summary version lands in git, discoverable via `git log --all --follow -- observations/sessions/<id>/summary.md`.
- **Lesson from spec 008**: the PR #66 review caught a `git commit --amend` instruction in WORKFLOW.md that conflicted with spec 001 FR-014. This slice avoids the same defect by making append-only revision explicit at spec + plan + contract + quickstart levels.

### Alternatives considered

- **Allow `--amend` within a short time window (e.g. before push)** — rejected: creates a gray zone that operators will abuse ("just this one time"); simpler rule is "always follow-up, no exceptions".
- **Squash revision commits into the original** — rejected: same objection as `--amend`; destroys audit trail.

---

## R6 — Consumer contract for KPI rollup (Phase 5 slice)

### Decision

The downstream KPI rollup slice (not yet specced, Phase 5) reads `summary.md` through the verdict-line format (R2) and the committed drift-citation (FR-008). Specifically:

- **H1/H2 KPIs**: extract all `clear` / `partial` / `fail` / `pending` values from the Verdicts section using the R2 grep pattern.
- **Drift-KPI composition**: the summary's Drift section cites `drift-audit.json.verdict` verbatim (FR-008). The KPI rollup reads that citation and cross-references the bundle's `drift-audit.json` directly — it does NOT parse drift findings out of the summary prose.
- **Per-peer contribution counting** (for H1 complementarity aggregation): the rollup may read the prose "What happened" section via human-or-LLM reader if it wants per-session complementarity evidence; OR it may rely entirely on the H1 complementarity verdict line. Hybrid structure supports both.

This workflow explicitly does NOT specify the rollup — just the contract it will consume.

### Rationale

- **Forward compatibility**: if Phase 5 rollup wants mechanical parsing, verdict lines are grep-parseable. If it wants qualitative synthesis, the prose body is there.
- **Single source of truth**: verdict values live once in the summary's Verdicts section; drift findings live once in `drift-audit.json`. No duplication, no reconciliation burden.
- **Matches spec 008 C8 pattern**: same consumer-direction discipline — "consumers MUST NOT re-derive." Here: rollup MUST NOT re-derive verdicts from prose.

### Alternatives considered

- **Require summaries to also emit a `verdicts.json` sidecar** — rejected: duplicates the verdict lines that already live in `summary.md`; violates single-source principle; increases authoring cost for no clear rollup benefit (grep is sufficient).
- **Spec the rollup here** — rejected: out of scope; rollup slice has its own design considerations (cross-session aggregation, threshold decisions) that belong in a dedicated slice.

---

## Consolidated output

- **FR-004 author discipline** (clarify Q1): tiered — operator picks single-author or agent-drafted per-session; mode in commit body (R4).
- **FR-010 summary structure** (clarify Q2): hybrid inverted-pyramid (Seed → Verdicts → Drift → What happened); verdict lines follow R2 grep-stable format.
- **FR-018 cross-review discipline** (clarify Q3): optional post-commit peer audit via follow-up `[peer-audited by <id>]` token (R1); no-change peer-audits append a non-rendered `summary.md` audit marker so the path-limited ledger remains complete.
- **Revision lifecycle**: append-only follow-up commits per R5, inherit spec 001 FR-014; no `--amend`.
- **Commit format**: `session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>` (R1).
- **Idempotency**: structural determinism only, not prose determinism (R3).
- **Consumer contract**: KPI rollup reads verdict lines via grep (R2) + cited drift-audit directly; doesn't re-derive (R6).

All decisions above are reflected in `data-model.md`, `contracts/workflow-contracts.md`, and `quickstart.md` in Phase 1.
