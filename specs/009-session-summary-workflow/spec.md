# Feature Specification: Session-Summary Workflow

**Feature Branch**: `009-session-summary-workflow`
**Created**: 2026-04-20
**Status**: Draft
**Input**: Operationalize the post-session procedure that produces `observations/sessions/<session-id>/summary.md` — the human-readable qualitative account required by [spec 001 FR-012](../001-session-bundle-skeleton/spec.md) — as a repeatable workflow complementing the now-landed drift-audit workflow ([spec 008](../008-drift-audit-workflow/spec.md)). Without `summary.md`, counted Phase 3 sessions cannot produce consumable H1/H2 evidence for POC-exit synthesis. This slice owns the **authoring workflow** (trigger, responsibility, content-completeness invariants, commit discipline, drift-audit integration, H1/H2 composition); it does NOT own the KPI rollup (Phase 5 slice) or LLM-assisted authoring automation (deferred).

## Clarifications

### Session 2026-04-20

- Q: Author discipline — single-author, two-role, or tiered? → A: Tiered (operator decides per-session). Default is not prescribed yet; the operator applies the effort / fairness / compression heuristic per session. Both paths (single-author and agent-drafted + operator-ratified) are supported; explicit mode recorded on the commit.
- Q: Summary structure — strict template, free-form prose, or hybrid? → A: Hybrid with inverted-pyramid ordering — **Seed** (anchor) → **Verdicts** (strict labeled lines for H1 stability / H1 complementarity / H2 fresh-reader-pass) → **Drift** (verdict + finding citations from `drift-audit.json`) → **What happened** (free-form prose: per-peer contributions, coordination patterns, turn-by-turn nuance). Reader who only needs the load-bearing values can stop after the first ~15 lines; a fresh-reader doing the H2 test reads to the end. Verdicts near the top so the downstream KPI rollup can parse them cheaply.
- Q: Cross-review discipline — single-author, required cross-reviewer, or optional with ledger? → A: Optional cross-reviewer as a follow-up amend commit. Initial commit is single-author (or agent-drafted + operator-ratified per Q1). If a peer auditor reviews after commit, they land a follow-up amend with a `[peer-audited by <id>]` token in the commit subject so the audit is discoverable via `git log --all --grep='peer-audited'`. Reuses spec 008's commit-taxonomy pattern; no new mechanism. Not required for counted-session eligibility, but the ledger gives POC-exit synthesis a count of which counted sessions got peer-audited.

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifacts**:
  - [`design/poc.md`](../../design/poc.md) — "Per-session clear definitions" (H1 stability + H1 complementarity + H2 fresh-reader pass) and measurement model.
  - [`design/architecture.md`](../../design/architecture.md) — Layer 3 evaluation artifacts + capability requirements.
  - [`VISION.md`](../../VISION.md) — H1 convergence + H2 legibility hypotheses the summary's verdicts support.
- **Upstream spec dependencies (landed)**:
  - [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) — FR-012 mandates the `summary.md` sections and lives-in-bundle location; FR-014 defines the session-bundle amend-commit convention this workflow extends.
  - [`specs/005-drift-audit-rubric/spec.md`](../005-drift-audit-rubric/spec.md) — rubric context that the drift section references.
  - [`specs/006-discord-transcript-export/spec.md`](../006-discord-transcript-export/spec.md) — produces `transcript.md` the summarizer reads.
  - [`specs/008-drift-audit-workflow/spec.md`](../008-drift-audit-workflow/spec.md) + [`contracts/workflow-contracts.md`](../008-drift-audit-workflow/contracts/workflow-contracts.md) C8 — defines how the summary consumes `drift-audit.json.verdict` without re-deriving findings.
  - [`specs/003-pinned-rules-authoring/spec.md`](../003-pinned-rules-authoring/spec.md) — pinned-rules snapshot referenced via `meta.json.pinned_rules_ref` that the summary may cite for rules-in-force context.
- **Cross-slice dependency (non-blocking)**: intervention-tagging schema is owned by the Codex slice (not yet specced). The summary may cite intervention types/reasons but this workflow treats the tag shape as opaque.
- **Downstream consumer (blocks)**: KPI rollup logic / framing (Phase 5 slice, not yet specced) — reads `summary.md` H1/H2 verdicts directly per FR-017 below.
- **Roadmap workstream**: `Evaluation surface build` (Phase 2, Claude slice per [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41) staffing).
- **Staffing**: Claude lead (evaluation pipeline slice per #41); Codex cross-reviewer via the ratified autonomous-loop operating model; Zoe ratifies.
- **Scope boundary (explicit)**:
  - In scope: trigger, responsibility, required-sections invariants, commit discipline, drift-audit integration (cite, don't re-derive), H1/H2 verdict composition, revision lifecycle.
  - Out of scope: the rubric itself (spec 005), the drift-audit procedure (spec 008), `drift-audit.json` schema (spec 005 data-model), intervention-tag schema (Codex slice), cross-session aggregation / KPI rollup (Phase 5 slice), LLM-assisted summary authoring (deferred follow-on; may share entry-criteria shape with spec 008 FR-014).

## User Scenarios & Testing *(mandatory)*

The "users" of the workflow are: the **operator** (runs or delegates the summary authoring, ratifies H1/H2 verdicts), a **delegated summarizer** (a peer agent or human reviewer who may compose the prose under operator ratification if the author-discipline clarification resolves that way), and **downstream consumers** (uninvolved human reviewer executing the H2 fresh-reader test; the KPI rollup slice reading H1/H2 verdicts).

### User Story 1 — Operator produces a committed `summary.md` for a closed session (Priority: P1)

As the operator, once a session's transcript, interventions, and drift-audit have landed in the bundle, I compose (or ratify a delegated composition of) `summary.md` containing the session goal/seed, per-peer contribution summary, observed coordination patterns, notable drift cross-referenced from `drift-audit.json.verdict`, and my verdicts on H1 stability / H1 complementarity / H2 fresh-reader-pass. Committing `summary.md` closes the session bundle's Phase 2 evidence surface: it now carries both the quantitative drift-audit and the qualitative summary required for KPI rollup.

**Why this priority**: without a committed `summary.md` path, spec 001 FR-012 is undelivered at runtime — every counted Phase 3 session either produces no qualitative evidence or produces ad-hoc summaries that downstream KPI rollup cannot reliably read. This is the MVP atom of the slice.

**Independent Test**: given a closed session bundle with transcript + meta + interventions + drift-audit.json committed, follow the workflow and verify (a) `summary.md` lands at `observations/sessions/<session-id>/summary.md` via a session-bundle amend commit, (b) the file contains all five FR-012 required sections, (c) H1 stability / H1 complementarity / H2 verdicts are each recorded with operator-attributed rationale, and (d) the drift section cites `drift-audit.json.verdict` directly (not a re-derivation from transcript).

**Acceptance Scenarios**:

1. **Given** a closed session bundle with all upstream artifacts (`transcript.md`, `meta.json`, `interventions.json`, `drift-audit.json`) committed, **When** the operator follows the workflow, **Then** `summary.md` appears at `observations/sessions/<session-id>/summary.md` carrying: session goal/seed; per-peer contribution summary (one block per peer, each naming at least one distinct contribution); observed coordination patterns (loops, dominance, directive-redirects the operator made, etc.); drift section citing `drift-audit.json.verdict` plus any load-bearing `finding`-severity findings by reference; three explicit verdict lines for H1 stability / H1 complementarity / H2 fresh-reader-pass with rationale.
2. **Given** the summary is committed, **When** a reviewer opens the bundle directory, **Then** the full post-session evidence set (transcript + meta + interventions + drift-audit + summary) is present in a single directory with no out-of-band context required.
3. **Given** a session where the bundle is missing a required upstream input (e.g. `drift-audit.json` hasn't landed), **When** the operator attempts the workflow, **Then** the workflow halts before producing a partial `summary.md` and surfaces which input is missing, so drift-audit lands first per spec 008 before summary authoring begins.

---

### User Story 2 — Summary cites drift-audit, does not re-derive drift findings (Priority: P1)

As the operator (or a delegated summarizer), when I write the "notable drift" section of `summary.md`, I cite `drift-audit.json.verdict` directly and reference specific `findings[]` entries by their `turn_ref` + `category` rather than re-deriving drift findings from the transcript, so the summary's drift narrative stays consistent with the drift-audit workflow's ratified artifact and downstream KPI rollup has a single source of truth.

**Why this priority**: without this discipline, the summary's drift narrative and the committed `drift-audit.json` can disagree, making the bundle's evidence internally inconsistent and forcing downstream consumers to reconcile two accounts. Spec 008's contract C8 already specifies "consumers MUST NOT re-derive drift findings" — this slice enforces it at the summary-authoring boundary.

**Independent Test**: given a bundle whose `drift-audit.json.verdict` is `load_bearing_drift` with 2 specific findings, follow the workflow and verify the committed `summary.md` drift section (a) names the verdict verbatim, (b) references the specific findings by `turn_ref` or `category`, and (c) does not introduce a drift category or severity assertion that is absent from `drift-audit.json.findings[]`.

**Acceptance Scenarios**:

1. **Given** a `drift-audit.json` with `verdict: "load_bearing_drift"` and 2 findings, **When** the summary is written, **Then** the drift section names the verdict and cross-references each load-bearing finding by `turn_ref` or category; no new drift category is introduced.
2. **Given** a `drift-audit.json` with `verdict: "no_drift"` and empty findings, **When** the summary is written, **Then** the drift section states the verdict and notes drift is not the blocker for H2 (aligns with [spec 008 contract C8](../008-drift-audit-workflow/contracts/workflow-contracts.md) + RUBRIC.md §8's verdict-to-H2 composition table); no speculative drift discussion is added.
3. **Given** the operator disagrees with the committed `drift-audit.json` after drafting the summary, **When** resolving the disagreement, **Then** the operator re-audits via spec 008 Path C (not in the summary), updating `drift-audit.json` first, then refreshes the summary's drift section to cite the re-audited verdict.

---

### User Story 3 — Summary revision preserves bundle history (Priority: P2)

As the operator, when a summary needs correction after commit (typo, late operator verdict on an initially-pending H2 judgment, rewording after peer audit feedback), I land a follow-up session-bundle amend commit rather than rewriting git history, so the bundle's evidence trail remains append-only per spec 001 FR-014 and the prior summary version is reconstructible via git history.

**Why this priority**: without a defined revision path, operators may be tempted to `git commit --amend` on summaries — which violates spec 001 FR-014 and loses the audit trail. P2 because US1 + US2 are the MVP evidence-production atoms; revision discipline is hygiene that must land but does not block early Phase 3 sessions.

**Independent Test**: commit an initial `summary.md`, then amend via follow-up commit per the workflow, and verify (a) the current `summary.md` reflects the correction, (b) the prior version is retrievable via `git show <prior-commit>:observations/sessions/<session-id>/summary.md`, and (c) git history is NOT rewritten (no force-push, no `--amend` on the initial summary commit).

**Acceptance Scenarios**:

1. **Given** a committed initial `summary.md`, **When** the operator corrects a typo via the revision path, **Then** a follow-up session-bundle amend commit lands with a clear `<reason>` in the subject, the file reflects the correction, and the prior version is preserved in git history.
2. **Given** the summary had a `pending` H2 verdict at initial commit (uninvolved-reviewer test not yet run), **When** the reviewer completes the test and the operator records the final verdict, **Then** the revision lands as a follow-up amend commit rather than a history-rewriting `--amend`, and the prior `pending` version remains retrievable.
3. **Given** the drift-audit is re-audited (per spec 008 Path C) and the summary's drift citation becomes stale, **When** the summary is updated to cite the new verdict, **Then** the summary revision lands as a follow-up amend commit referencing both the new drift-audit commit and the superseded prior summary.

---

### Edge Cases

- **Zero-turn or near-empty session**: the workflow MUST still produce a `summary.md` (with per-peer contribution summary noted as "no substantive contribution" and H1/H2 verdicts recorded — likely all `fail` or `pending`) rather than skipping, so every closed bundle carries qualitative evidence.
- **Missing `drift-audit.json`**: the workflow MUST halt before producing a partial summary and surface the missing input; it does not speculate about drift verdict or stand in for spec 008's procedure.
- **Pending H2 verdict at initial commit**: acceptable — the initial summary may record `H2 verdict: pending (fresh-reader test not yet run)` with the expectation that a revision lands once the test completes. The workflow does NOT require H2 verdict at initial commit if the fresh-reader review is asynchronous.
- **Peer agent disputes operator verdict on H1 stability**: the operator's verdict is authoritative per constitution v1.5.0 Principle IV. Peer agents may record their disagreement in the commit body or a follow-up discussion, but the committed H1/H2 verdicts are operator-owned.
- **Summarizer is not the operator**: see FR-004 clarification. If the author-discipline clarification chooses two-role, a delegated summarizer may compose prose subject to operator ratification; if single-author, only the operator composes.
- **Cross-session aggregation discovery**: not this slice's concern. If the operator discovers a cross-session pattern while writing a single-session summary, that pattern belongs in POC-exit synthesis (Phase 5), not this summary.
- **Revision of a summary whose drift citation is now stale**: the operator MUST update the citation to reference the current `drift-audit.json.verdict` (re-audits per spec 008 Path C replace the drift file in-place; summaries citing the prior verdict must be refreshed per US3).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The workflow MUST take a closed session bundle as its input and produce `summary.md` at `observations/sessions/<session-id>/summary.md`. The bundle is considered closed (eligible for summary authoring) when `transcript.md`, `meta.json` (with `closed_at` stamped), `interventions.json`, and `drift-audit.json` are all committed.
- **FR-002**: If any upstream input is missing from the bundle at summary-authoring time, the workflow MUST halt before producing a partial `summary.md` and surface which input is missing (non-silent failure). The workflow does NOT stand in for upstream close steps or for spec 008's drift-audit authoring.
- **FR-003**: The committed `summary.md` MUST contain, at minimum, the five required content elements mandated by spec 001 FR-012: **session goal or seed** (what the session was for, what question or task was in play); **per-peer contribution summary** (one block per peer, naming each peer's distinct contributions and whether they were taken up by the other peer); **observed coordination patterns** (loops, dominance, interruptions, operator directive-redirects — the qualitative texture the drift-audit does not capture); **notable drift** (cross-referencing `drift-audit.json.verdict` per FR-008); **operator verdict on H1 stability / H1 complementarity / H2 fresh-reader-pass** (per FR-006). FR-010 pins these five content elements to four top-level headings: goal → `## Seed`, verdict → `## Verdicts`, drift → `## Drift`, AND **both** per-peer contributions + coordination patterns → `## What happened` (free-form prose, no fixed sub-heading required). Spec 001 FR-012 is a content-presence requirement; FR-010 is the structural discipline that packages that content into four grep-stable headings while letting the qualitative narrative flow as prose in the bottom section.
- **FR-004**: The workflow MUST support two author-discipline modes and the operator chooses per-session: (a) **single-author** — operator composes prose AND records verdicts, no ratification step; (b) **agent-drafted + operator-ratified** — a peer agent (Dalgos, Vigil) or delegated human composes the prose draft, operator edits as needed, records the H1/H2 verdicts themselves per FR-005, and commits. The mode choice MUST be recorded in the commit body via a `Mode: single-author` or `Mode: agent-drafted, drafted-by: <agent-id>, ratified-by: <operator-id>` line so downstream reviewers can tell which path produced the summary. The operator's per-session heuristic for choosing: level of effort needed, fairness of the output, level of compression / subjectivity acceptable for that session. Neither mode is "default" at spec time — both are first-class and selection is operational. The deferred LLM-assisted authoring path per FR-015 is distinct: it refers to prompt-template automation without a peer-agent intermediary, not agent-drafted-human-ratified.
- **FR-005**: The operator is the authoritative voice on H1 stability / H1 complementarity / H2 fresh-reader-pass verdicts per constitution v1.5.0 Principle IV, regardless of who composed the prose. Peer-agent-produced summaries (if two-role is chosen in FR-004) require operator ratification before commit.
- **FR-006**: Each of the three KPI verdicts (H1 stability, H1 complementarity, H2 fresh-reader-pass) MUST appear as an explicit labeled list-bullet line in the `## Verdicts` section of `summary.md` (format pinned in FR-010), with a value of one of `clear` / `partial` / `fail` / `pending` and a short rationale. "Pending" is reserved for verdicts that require an asynchronous step not complete at commit time (e.g. H2's fresh-reader test); all three verdicts being "pending" at initial commit is acceptable but triggers the revision path (US3) when they resolve.
- **FR-007**: The per-session clear-definition criteria per [`design/poc.md`](../../design/poc.md) define the judgment threshold for each verdict. The workflow MUST reference those definitions rather than re-specifying them; if they evolve, the summary procedure absorbs the change via pointer, not by re-spec.
- **FR-008**: The drift section in `summary.md` MUST cite `drift-audit.json.verdict` verbatim and reference specific load-bearing findings by `turn_ref` and/or `category`. The summary MUST NOT assert a drift category or severity absent from `drift-audit.json.findings[]`. If the operator disagrees with the drift-audit, they re-audit via spec 008 Path C first, then refresh the summary — the disagreement path never lives in the summary text.
- **FR-009**: The workflow MUST commit `summary.md` via a session-bundle amend commit per spec 001 FR-014. Commit subject format: `session bundle amend: <session-id> — summary[ <taxonomy-token>] @ <drift-audit-short-sha>` where `<drift-audit-short-sha>` is the commit short SHA of the `drift-audit.json` the summary is drafted against (pinning the drift-citation's provenance). The taxonomy-token slot mirrors spec 008's COMMIT-TAXONOMY pattern — absent for the default case, plus any slice-defined tokens (token set derived during plan phase).
- **FR-010**: The committed `summary.md` MUST follow a **hybrid inverted-pyramid structure**: a short **Seed** section anchoring what the session was about, followed by strict labeled **Verdicts** lines (one per KPI — H1 stability / H1 complementarity / H2 fresh-reader-pass — each with a `clear` / `partial` / `fail` / `pending` value and a short rationale), followed by a **Drift** section citing `drift-audit.json.verdict` + load-bearing findings per FR-008, followed by a **What happened** free-form prose section covering per-peer contributions, coordination patterns, and turn-by-turn nuance. The ordering MUST be Seed → Verdicts → Drift → What happened so downstream KPI rollup can read verdicts from the first section of the file without parsing prose, and so a reviewer who only needs load-bearing values can stop after the verdicts block. The Verdicts section's line format MUST be grep-stable: `- **H1 stability**: \`<value>\` — <rationale>` (or equivalent Markdown list-bullet form with the KPI name bold, the value in backticks, and the rationale after an em-dash). Free-form prose elsewhere preserves constitution v1.5.0 Principle VI human-legibility.
- **FR-011**: The workflow MUST support **summary revision** via follow-up session-bundle amend commits (spec 001 FR-014 append-only discipline). The prior summary version MUST remain reconstructible via git history. The workflow MUST NOT use `git commit --amend` on a previously-committed summary — revisions are always follow-up commits.
- **FR-012**: If a summary revision is triggered by a drift-audit re-audit (spec 008 Path C), the revised summary MUST cite the refreshed `drift-audit.json.verdict` and the commit message MUST reference the superseded drift-audit short SHA for traceability (mirrors spec 008's `supersedes` token pattern).
- **FR-013**: The workflow MUST document the trigger: bundle is closed (per spec 001 close definition) AND `drift-audit.json` has landed (per spec 008 workflow commit). Authoring a summary before drift-audit lands is a halt condition per FR-002.
- **FR-014**: The workflow MUST NOT depend on LLM availability for v1. The manual path (operator or human delegated summarizer) is the sole committed-artifact producer in this slice. LLM-assisted authoring is acknowledged as a deferred follow-on via FR-015 but not operationalized here.
- **FR-015**: The workflow MUST document the **entry criteria for LLM-assisted summary authoring** (deferred to a later slice): mirrors spec 008 FR-014's entry-criteria pattern — ≥2 counted sessions landed with manual summaries, operator has defined an LLM prompt template suitable for the structure chosen in FR-010, manual ratification remains the gate. This slice does NOT specify the automation.
- **FR-016**: The workflow MUST honor spec 001 FR-011's top-level storage shape for `interventions.json` (array of intervention objects; empty array = valid empty case) and MUST treat the **per-object intervention-tag schema** as opaque per the Codex intervention-tagging slice (not yet specced). The summary MAY reference intervention types/reasons informally in prose (e.g. "the operator directive-redirected at turn 14 to break the loop"), but this workflow does NOT depend on a specific per-object tag schema and does NOT define intervention-reference syntax.
- **FR-017**: The workflow MUST compose with downstream KPI rollup (Phase 5, not yet specced): the summary's explicit H1/H2 verdict lines (FR-006) are the authoritative input the rollup reads. The rollup MUST NOT re-derive H1/H2 verdicts from prose. If FR-010 chooses a strict heading template, the rollup can parse mechanically; if free-form, the rollup specifies its own human-or-LLM reader.
- **FR-018**: The workflow MUST support **optional peer audit as a follow-up amend commit** rather than a required pre-commit cross-reviewer pass. Initial summary commits are single-author (or agent-drafted + operator-ratified per FR-004) and MUST NOT be blocked on peer-audit availability. When a peer reviewer audits a committed summary, they MUST land a follow-up session-bundle amend commit whose subject includes the token `[peer-audited by <id>]` so the audit is discoverable via `git log --all --grep='peer-audited'`. The commit body records the audit reviewer's findings (or "no material findings") and any wording changes incorporated. Counted-session eligibility does NOT require a peer audit — but the ledger lets POC-exit synthesis count which counted sessions received one. This reuses spec 008's bracket-token commit-taxonomy pattern without introducing a new mechanism.

### Key Entities

- **Session bundle** *(owned by spec 001; workflow input)*: the directory at `observations/sessions/<session-id>/` containing `transcript.md`, `meta.json`, `interventions.json`, `drift-audit.json`, and (after this workflow lands) `summary.md`.
- **Summary output** *(workflow output; owned by this slice)*: the `summary.md` file at the session bundle root, conforming to FR-003's required-sections invariant. Plain markdown prose per constitution v1.5.0 Principle VI.
- **Session goal / seed** *(summary-level content entity)*: plain-prose statement of what the session was for — the question, task, or exchange topic the operator opened the session to explore. First required section of the summary.
- **Per-peer contribution record** *(summary-level content entity; appears once per peer in each summary)*: identifies each peer by name/handle and enumerates at least one distinct contribution the peer made that was taken up by the other peer (H1 complementarity evidence).
- **H1 stability verdict** *(summary-level content entity)*: explicit labeled line with value `clear` / `partial` / `fail` / `pending` and rationale, judging whether the session cleared H1 stability per `design/poc.md` definition (operator did not directive-redirect on majority of substantive turns, no persistent loop, no one-sided dominance).
- **H1 complementarity verdict** *(summary-level content entity)*: explicit labeled line with same value enum, judging whether each peer contributed at least one distinct useful thing taken up by the other.
- **H2 fresh-reader-pass verdict** *(summary-level content entity)*: explicit labeled line with same value enum, judging whether an uninvolved human reviewer can reconstruct goal/roles/outcome from the bundle and the operator ratifies that reconstruction as materially correct. "Pending" acceptable until the fresh-reader test runs asynchronously; resolution triggers a revision per US3.
- **Drift-audit citation** *(summary-level reference; schemas owned by spec 005/008)*: the drift section's explicit pointer to `drift-audit.json.verdict` and specific load-bearing `findings[]` entries. Not a new schema — citation discipline only.
- **Author identity** *(workflow-level; recorded in commit body or optional summary frontmatter)*: identifies who composed the prose. If FR-004 chooses two-role, the commit body records summarizer + operator-ratifier identities separately. Single-author case records only the operator.
- **Revision event** *(workflow-level, recorded in amend-commit subject)*: a follow-up commit correcting a previously-committed summary. Preserves prior version in git history per FR-011; cites a superseded drift-audit SHA per FR-012 when the revision is drift-audit-triggered.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator following the workflow produces a valid, committed `summary.md` for a closed session bundle in ≤20 operator-minutes per ≤200-turn bundle (allowance covers drafting + drift-citation verification + verdict-rationale writing; targets realistic operator load for small-N Phase 3).
- **SC-002**: 100% of closed counted session bundles carry a non-placeholder `summary.md` within 48 operator-hours of drift-audit landing — the full post-session evidence set (transcript + meta + interventions + drift-audit + summary) is present in a single directory for every counted session.
- **SC-003**: An uninvolved human reviewer executing the H2 fresh-reader test by reading only `observations/sessions/<session-id>/` (no out-of-band context) can produce a reconstruction the operator ratifies as materially correct in ≥80% of counted Phase 3 sessions (this SC doubles as the H2 KPI threshold per `design/poc.md`, measured across the Phase 3 session set).
- **SC-004**: 100% of summaries cite `drift-audit.json.verdict` verbatim and reference only findings present in `drift-audit.json.findings[]` (no re-derived drift categories). Verified by inspection of Phase 3 summaries against their co-landed drift-audit files.
- **SC-005**: Summary revisions (US3) preserve prior versions in git history in 100% of revision cases — no `--amend` on previously-committed summaries, no history-rewriting operations.
- **SC-006**: A downstream KPI-rollup consumer can extract each session's three H1/H2 verdicts from the committed `summary.md` without out-of-band context in 100% of audit-complete bundles (mechanical parseability if FR-010 → strict template; human-or-LLM readability if FR-010 → free-form — either way, the verdict lines are discoverable in the committed file).

## Assumptions

- The session bundle is produced by the spec 001 / spec 006 / spec 007 chain and closed before this workflow runs. The workflow does not open, seal, or mutate the bundle beyond adding `summary.md` and any subsequent revision commits.
- `drift-audit.json` has landed per spec 008's workflow before summary authoring begins. The summary workflow does not wait on drift-audit automatically; it halts if drift-audit is absent per FR-002.
- Intervention-tag schema is owned by the Codex intervention-tagging slice. The workflow consumes `interventions.json` opaquely per FR-016.
- The operator is the authoritative voice on H1/H2 verdicts per constitution v1.5.0 Principle IV. "Authoritative voice" does NOT mean "sole composer" — see FR-004 clarification for whether a delegated summarizer may compose prose.
- Fresh-reader-pass (H2) may be asynchronous — an uninvolved human reviewer is not always available at session close. "Pending" verdict at initial commit is acceptable and expected early in Phase 3.
- Downstream KPI rollup depends on this slice's FR-010 structure decision. The rollup slice is explicitly out of scope here but sizing its scope depends on whether summaries are strict-template or free-form.
- LLM-assisted summary authoring is explicitly deferred. Entry criteria documented in FR-015; operationalization lives in a future slice.
- POC sessions are small-N (~3–5 Phase 3 counted sessions per `design/poc.md`). The workflow is human-executed per session; no batch or continuous-scan infrastructure.

## Dependencies

- **Upstream (landed)**: spec 001 (bundle + FR-012 + FR-014), spec 003 (pinned-rules, cited as rules-in-force context), spec 004 (session controls — close is the upstream trigger), spec 005 (rubric definition the drift-audit cites), spec 006 (transcript input), spec 008 (drift-audit workflow + `drift-audit.json` schema + contract C8 consumer discipline).
- **Cross-slice (Codex-owned, non-blocking)**: intervention-tagging mechanism — `interventions.json` shape consumed opaquely.
- **Downstream (blocks)**: KPI rollup logic / framing (Phase 5 slice, not yet specced) — reads `summary.md` H1/H2 verdicts per FR-017.
- **Constitutional**: aligns with constitution v1.5.0 — (I) canonical, (IV) human arbitration (operator owns H1/H2 verdicts), (V) parallel work ownership (ACTIVE-SLICES row claimed), (VI) human-legible (summary is prose, not machine schema).
