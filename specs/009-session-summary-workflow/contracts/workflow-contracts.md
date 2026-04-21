# Workflow Contracts: Session-Summary Workflow

**Branch**: `009-session-summary-workflow` | **Date**: 2026-04-21
**Input**: Phase 1 output. Workflow-level guarantees this slice owns. The consumed artifacts (`drift-audit.json`, bundle files) have their own contracts in spec 005 + spec 001; this file does not duplicate those.

This document specifies the guarantees an auditor, a downstream consumer (KPI rollup / POC-exit synthesis), or a future implementer of a CLI/LLM automation path can rely on *about the workflow*, independent of the summary's prose content.

---

## C1 — Input contract: closed bundle with drift-audit landed

**Pre-conditions** (all MUST hold; any absence is a halt condition per FR-002 + FR-018):

1. `observations/sessions/<session-id>/transcript.md` exists and is non-empty (zero-turn transcripts still produce a valid file per spec 006).
2. `observations/sessions/<session-id>/meta.json` exists and contains:
   - `session_id` (string, non-empty)
   - `pinned_rules_ref` (git SHA resolvable in the repo)
   - `closed_at` (RFC3339 UTC, non-null)
3. `observations/sessions/<session-id>/interventions.json` exists (may be empty array/object per the Codex intervention-tagging slice; workflow treats the shape opaquely).
4. `observations/sessions/<session-id>/drift-audit.json` exists and is committed (workflow halts if drift-audit has not landed per spec 008). The drift-audit's commit short SHA is the `<drift-audit-short-sha>` referenced throughout.
5. The bundle's working tree is clean of unrelated uncommitted changes (the summary amend commit should land cleanly on top of a committed bundle).

**Halt behavior**: if any pre-condition fails, the workflow MUST NOT produce a partial or placeholder `summary.md`, MUST surface a non-silent failure naming the specific unmet condition (referencing FR-002/FR-018), and MUST leave the bundle untouched so the upstream producer (spec 001 bundle-close, spec 006 transcript export, spec 008 drift-audit workflow) can be corrected.

---

## C2 — Output contract: committed `summary.md` conforming to structural invariants

**Post-conditions** (on successful summary commit):

1. `observations/sessions/<session-id>/summary.md` exists, is valid Markdown, and contains all four top-level sections in order: `## Seed` → `## Verdicts` → `## Drift` → `## What happened` (per FR-010 + data-model structural invariants).
2. The `## Verdicts` section contains exactly three list-bullet lines in the R2 grep-stable format, one per KPI (`H1 stability`, `H1 complementarity`, `H2 fresh-reader-pass`), with values in `{clear, partial, fail, pending}` and non-empty rationales.
3. The `## Drift` section cites `drift-audit.json.verdict` verbatim and references specific load-bearing findings by `turn_ref` or `category` per FR-008. No drift category or severity is introduced that is absent from `drift-audit.json.findings[]`.
4. The `## Seed` section is non-empty.
5. The `## What happened` section is non-empty (may be brief for short sessions, but not omitted).
6. The file is committed via a session-bundle amend commit per C4.
7. The commit body carries the `Mode:` line per E1 (single-author or agent-drafted + identities).

Downstream consumers (KPI rollup, POC-exit synthesis) MAY rely on 1–6 without re-deriving.

---

## C3 — Structural determinism, not prose determinism

**Guarantee**: given identical inputs (same bundle + same drift-audit SHA + same auditor), two runs of the workflow produce summaries whose **structural content** is deterministic:

- Section headings and ordering identical.
- Verdict values identical (assuming auditor is making the same judgment call — if they flip values, that's auditor uncertainty, not workflow non-determinism).
- Drift citation identical (same `drift-audit.json.verdict`, same cited findings).

**Not guaranteed** (and explicitly acceptable):

- Prose wording, sentence length, or rhetorical framing inside the Seed, Drift (rationale), or What happened sections.
- Which transcript turns get called out in the prose body vs which are glossed over.
- Author-voice differences between single-author and agent-drafted modes.

**Why this is not like spec 008 C3**: `drift-audit.json` is schema-first (deterministic modulo timestamp); `summary.md` is prose-first. Constitution v1.5.0 Principle VI (human-legible, not over-protocolized) forbids imposing byte-identical prose — subjective judgment is inherent to qualitative evaluation.

**What downstream consumers can safely assume**: the load-bearing values (verdicts + drift citation) are deterministic; the prose body is author-voice-variable.

---

## C4 — Amend-commit message format contract

All `summary.md` commits MUST be amend commits on the session bundle (per spec 001 FR-014) and MUST follow this message format (per R1):

```
session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>
```

Where `<taxonomy-token>` is one of:

| Token | When | Counting signal |
|---|---|---|
| *(absent)* | Initial summary commit, single-author OR agent-drafted (default case) | Bundle has a committed summary |
| `[peer-audited by <id>]` | Follow-up commit recording a post-commit peer-audit event (E5) | Counted in peer-audit ledger for independent-review coverage |
| `revision: <reason>` | Follow-up commit correcting a previously-committed summary (E4) | Counted in revision ledger; may indicate late-arriving H2 verdicts, typos, wording cleanup |
| `revision: drift-refresh, supersedes <old-drift-short-sha>` | Follow-up commit refreshing the drift citation after spec 008 Path C re-audit | Ties summary revisions to drift-audit re-audits for traceability |

**Multiple tokens MAY appear** when an event is compound (e.g. `[peer-audited by Vigil] revision: wording-cleanup` for a peer-audit that also incorporated the reviewer's wording suggestion).

**Token ordering** (when combined): `[peer-audited by <id>]` first (bracket draws the eye), then `revision: <reason>`.

**Body content** (REQUIRED for initial commit, RECOMMENDED for revisions/peer-audits):

- Initial commit body MUST include the `Mode: single-author` or `Mode: agent-drafted, drafted-by: <id>, ratified-by: <id>` line per E1.
- Revision/peer-audit commit body MUST include a one-line `<reason>` expansion or a `No material findings` note.

**Never**: `git commit --amend` on a previously-committed summary — per C6 + spec 001 FR-014.

---

## C5 — Two-author (agent-drafted + operator-ratified) lifecycle contract

**Applies when**: the operator chooses agent-drafted mode per FR-004.

**Guarantees**:

1. Only the operator commits. Drafter identity is recorded in the commit body (`drafted-by:` line) but the drafter does NOT have commit authority on the session bundle.
2. Drafter produces `summary.md` (or optionally a working-file draft); operator reviews, edits as needed, writes the three H1/H2 verdicts themselves per FR-005, and commits.
3. No draft-and-final separation at the git-commit layer: one commit per summary. Any pre-commit drafts are authoring-tool artifacts, not bundle-layer evidence, and MUST NOT be committed to the bundle.
4. Operator ratification is the act of commit. There is no separate "ratified" state machine or timestamp beyond the commit metadata itself.
5. Verdict values are ALWAYS operator-written. The drafter MAY propose verdict values in their draft, but the operator re-evaluates and writes the final values; the commit represents operator attestation.

**Does NOT guarantee**:

- That the drafter's proposed verdict values match the final committed values — the operator may change them freely before commit.
- That the drafter and operator agree on framing — if there is material disagreement, the operator's framing wins (Principle IV).

---

## C6 — Revision contract (append-only, spec 001 FR-014 compliance)

**Applies when**: a committed summary needs correction.

**Guarantees**:

1. Revisions are ALWAYS follow-up session-bundle amend commits. NEVER `git commit --amend` on the prior commit.
2. The revised file replaces the prior version in the working tree; the prior version is preserved in git history.
3. The revision commit's subject carries the `revision: <reason>` taxonomy token per C4.
4. The prior version is retrievable via `git show <prior-commit>:observations/sessions/<session-id>/summary.md`.
5. Revisions may update any section of `summary.md`, including flipping verdict values (e.g. `H2 fresh-reader-pass: pending` → `clear`).
6. A revision MAY trigger on an upstream drift-audit re-audit (E4 special sub-case), in which case the subject uses `revision: drift-refresh, supersedes <old-drift-short-sha>`.

**Enforcement**: lesson from spec 008 PR #66 review (I1 finding): the workflow's runtime-facing docs + quickstart MUST state "never `git commit --amend` on session bundles" explicitly and give the follow-up-commit recipe for every failure mode the operator might encounter (failed sanity check, late-arriving verdict, wording fix, drift-refresh).

---

## C7 — Peer-audit ledger contract (grep-able discovery)

**Applies to**: downstream consumers who want to count independent-review coverage across counted Phase 3 sessions.

**Guarantees**:

1. Every peer-audit of a committed summary produces a commit whose subject contains the literal token `[peer-audited by <id>]` per C4.
2. `git log --all --grep='peer-audited' --format='%H %s' -- observations/sessions/*/summary.md` returns the full peer-audit ledger with no additional tooling.
3. The ledger is append-only (new peer-audits add history, never rewrite prior commits).
4. Per-session peer-audit status is reconstructible from the session's amend-commit history alone.
5. Reviewer identity is captured inside the token — the consumer can count unique reviewers, identify which agents or humans have audited which sessions, and cross-reference against the arbitration ledger (spec 008 C7) for sessions that received both kinds of independent review.

**Combined with spec 008 C7**: a POC-exit reviewer can compute per-session:

- Had drift-arbitration? (spec 008 `[arbitrated]` ledger)
- Had summary peer-audit? (spec 009 `[peer-audited by <id>]` ledger)

Dual-ledger analysis gives POC-exit synthesis an independent-review coverage picture that doesn't require any new artifact.

---

## C8 — Consumer contract: KPI rollup / H1 & H2 evidence

**Applies to**: the downstream Phase 5 KPI rollup slice (not yet specced) and any H1/H2 per-session reviewer.

**Guarantees**:

1. The three per-session verdict lines in the `## Verdicts` section are the authoritative per-session KPI input. Consumers MUST NOT re-derive verdicts from prose (this workflow's FR-017, mirrors spec 008 C8 drift-consumer discipline).
2. The verdict-line format (R2) is grep-stable: consumers can extract all three verdicts with a single regex without LLM assistance.
3. The `## Drift` section cites `drift-audit.json.verdict` verbatim — consumers of drift evidence read the cited `drift-audit.json` directly, not the summary prose.
4. The commit amend trail (E4 revisions + E5 peer-audits) provides lifecycle metadata for sessions whose initial commit had `pending` verdicts — consumers can detect whether a `pending` was later resolved by reading the latest revision.
5. The current `summary.md` on disk is always the consumer-relevant version; older versions are historical evidence only.

**Does NOT guarantee**:

- That the prose "What happened" section has a consistent shape across sessions or auditors — consumers that want narrative evidence use a human-or-LLM reader against the prose, not a mechanical parser.
- That per-peer contribution counts (for H1 complementarity aggregation) can be mechanically extracted — that's a rollup-slice design question if the rollup decides it needs prose-level data beyond the verdict lines.

---

## Contract summary (compact)

- **C1 Input**: closed bundle with transcript + meta + interventions + drift-audit.json committed + RUBRIC.md-committed (via spec 008's own pre-conditions). Halt on any absence.
- **C2 Output**: committed `summary.md` with 4 required sections, 3 verdict lines in R2 format, drift citation, prose body. Commit body carries `Mode:` line.
- **C3 Determinism**: structural invariants + verdict values deterministic; prose author-voice-variable.
- **C4 Commit format**: `session bundle amend: <id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>`.
- **C5 Two-author**: drafter proposes, operator writes verdicts + commits; single commit, no draft retained in bundle.
- **C6 Revision**: follow-up commits only, no `--amend`; `revision: <reason>` token.
- **C7 Peer-audit ledger**: `[peer-audited by <id>]` tokens, grep-able, append-only.
- **C8 Consumer read**: verdict lines via R2 grep; drift verdict via direct citation; no prose re-derivation.
