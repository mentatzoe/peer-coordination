# Feature Specification: Drift-Audit Workflow

**Feature Branch**: `008-drift-audit-workflow`
**Created**: 2026-04-19
**Status**: Draft
**Input**: Operationalize the ratified drift-audit rubric (`observations/drift-audits/RUBRIC.md` v1, landed via spec 005 / PR #50) as a repeatable post-session workflow that produces a committed `drift-audit.json` for every counted session bundle in Phase 2 / Phase 3. The rubric, the output schema, and the manual-audit procedure itself are owned by spec 005. This slice specifies the **workflow wrapper**: trigger, responsibility, two-auditor reconciliation, rubric-version pinning lifecycle, re-audit policy, and git integration — i.e. how the rubric is *applied* across sessions, not what the rubric *is*.

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifacts**:
  - [`design/poc.md`](../../design/poc.md) — "Per-session clear definitions" (H2 fresh-reader pass), measurement model rows for drift audit.
  - [`design/architecture.md`](../../design/architecture.md) — Layer 3 failure taxonomy (convergence / legibility / complementarity / intervention dependence).
  - [`VISION.md`](../../VISION.md) — H2 legibility hypothesis and "How we stay honest" (active drift-audit is part of the evaluation, not an afterthought).
- **Upstream spec dependencies (landed)**:
  - [`specs/005-drift-audit-rubric/spec.md`](../005-drift-audit-rubric/spec.md) — authoritative rubric spec (categories, severities, verdict, schema, calibration discipline).
  - [`specs/005-drift-audit-rubric/data-model.md`](../005-drift-audit-rubric/data-model.md) — canonical `drift-audit.json` schema this workflow produces.
  - [`specs/005-drift-audit-rubric/contracts/drift-audit-output.md`](../005-drift-audit-rubric/contracts/drift-audit-output.md) — output guarantees 1–5.
  - [`observations/drift-audits/RUBRIC.md`](../../observations/drift-audits/RUBRIC.md) — runtime rubric artifact; §4 manual-audit checklist and §7 LLM-judge prompt template.
  - [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) — FR-008 requires `drift-audit.json` inside the session bundle, FR-014 defines session-bundle amend-commit convention.
  - [`specs/006-discord-transcript-export/spec.md`](../006-discord-transcript-export/spec.md) — produces the `transcript.md` the audit reads.
- **Cross-slice dependencies (not blocking this spec)**:
  - Intervention-tagging mechanism — Codex-owned Phase 2 slice, not yet specced. The workflow consumes `interventions.json` as an input per spec 005's rubric but treats its shape as externally owned. This slice does not define intervention-tag semantics.
  - Session-bundle init CLI — Codex-owned [spec 007](../007-session-bundle-init-cli) (in-flight). Not blocking, but if it lands before this slice implements, the audit step can be wired into the same tool.
- **Downstream consumer (blocked on this + others)**:
  - KPI rollup / H2 evidence computation (Phase 5, not yet specced) — reads the `drift-audit.json` verdict + findings.
- **Roadmap workstream**: `Evaluation surface build` (Phase 2, Claude slice per [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41) staffing).
- **Staffing**: Claude lead (evaluation pipeline slice per #41); Codex cross-reviewer via the ratified autonomous-loop operating model; Zoe ratifies.
- **Scope boundary (explicit)**:
  - In scope: trigger, responsibility, auditor identity contract, two-auditor reconciliation, rubric-version pinning lifecycle, re-audit policy, git integration, committed artifact location, H2 integration call-out.
  - Out of scope: the rubric itself (owned by 005), the output schema (owned by 005), intervention-tag schema (separate Codex slice), LLM automation (deferred follow-on with entry criteria only), KPI rollup logic (separate downstream slice).

## User Scenarios & Testing *(mandatory)*

The "users" of the workflow are: the **operator** (ratifies counted sessions and runs or requests the primary audit), a **cross-reviewing agent or human auditor** (runs the independent audit that backs FR-016 tolerance from spec 005), and **downstream reviewers** (read the committed `drift-audit.json` as evidence input for H2 KPI and POC-exit synthesis).

### User Story 1 — Operator runs a single-auditor drift audit on a freshly-closed session bundle (Priority: P1)

As the operator, once a session bundle is closed per spec 001 (transcript exported, interventions logged, `pinned_rules_ref` pinned, session `closed_at` stamped), I apply the rubric's manual-audit checklist to produce a valid `drift-audit.json` committed inside the session bundle so the bundle is audit-complete and downstream KPI computation has a canonical input.

**Why this priority**: without a single-auditor path that reliably lands a committed audit per session, no counted session produces the evidence Phase 2 needs to exit or that Phase 3 sessions need to report. Two-auditor reconciliation and re-audit policy are both refinements on top of this atom.

**Independent Test**: hand the operator a closed session bundle in `observations/sessions/<session-id>/` with transcript + meta + interventions, have them follow the workflow, and verify the resulting `observations/sessions/<session-id>/drift-audit.json` conforms to the spec-005 schema, references the correct `rubric_version`, `session_id`, and `pinned_rules_ref`, and lands via a session-bundle amend commit per spec 001 FR-014.

**Acceptance Scenarios**:

1. **Given** a closed session bundle with `transcript.md`, `meta.json` (including `pinned_rules_ref`, `closed_at`, `session_id`), and `interventions.json`, **When** the operator follows the workflow, **Then** `drift-audit.json` appears at `observations/sessions/<session-id>/drift-audit.json` with `rubric_version` equal to the commit hash of `observations/drift-audits/RUBRIC.md` at audit start time, `auditor` populated, and `audited_at` as an RFC3339 UTC timestamp.
2. **Given** the primary audit commits, **When** any peer or reviewer re-checks the bundle, **Then** `observations/sessions/<session-id>/` contains the full post-session artifact set (transcript, meta, interventions, drift-audit, summary per spec 001) in one directory.
3. **Given** the session bundle is missing a required input (e.g. `pinned_rules_ref` absent in `meta.json`), **When** the operator attempts the workflow, **Then** the workflow halts before producing a partial audit and surfaces which input is missing, so the upstream bundle-close step is corrected rather than papered over.

---

### User Story 2 — Cross-reviewing auditor runs an independent audit and the workflow reconciles against spec 005's tolerance (Priority: P1)

As a cross-reviewing agent (or second human auditor), for counted sessions, I run my own pass of the rubric against the same bundle and my findings are reconciled with the primary auditor's against the FR-016 tolerance from spec 005 so the session's audit is backed by independent confirmation, matching constitution v1.5.0's independent-review principle.

**Why this priority**: spec 005 specifies the tolerance (±1 on `load_bearing_findings_count` for ≤200-turn sessions) but does not specify the reconciliation *workflow*. Without that, two-auditor mode is theoretical. Counted sessions need independent confirmation per the constitution.

**Independent Test**: give the same closed bundle to the operator and a cross-reviewer independently, have each produce a draft `drift-audit.json` per the workflow, and verify the reconciliation step produces a single committed `drift-audit.json` that records the reconciliation outcome (agreed / within-tolerance / reconciled-by-operator-arbitration) and both auditor identities.

**Acceptance Scenarios**:

1. **Given** the primary auditor and the cross-reviewer each produce a draft audit against the same bundle and rubric version, **When** the reconciliation step runs, **Then** if `|primary.load_bearing_findings_count − cross.load_bearing_findings_count| ≤ 1`, the workflow records agreement and commits a single reconciled `drift-audit.json` citing both auditors.
2. **Given** the two drafts diverge beyond tolerance, **When** the reconciliation step runs, **Then** the workflow records the disagreement explicitly and triggers an operator-arbitrated resolution path (see FR-008) before committing a final `drift-audit.json`.
3. **Given** a counted session, **When** only a single-auditor audit is attempted, **Then** the session is not eligible to count toward Phase 3 H1/H2 evidence rollup until a cross-reviewer pass lands — the workflow surfaces this as a pending state rather than silently accepting single-auditor evidence.

---

### User Story 3 — Auditor re-runs the audit after the rubric evolves, preserving historical reconstructibility (Priority: P2)

As an auditor, when spec 005's RUBRIC.md evolves between sessions (calibration commit), I need a re-audit path that refreshes a prior session's `drift-audit.json` against the new rubric version while leaving the historical evidence trail for the prior rubric version intact, so past sessions can be re-evaluated against calibrated rules without losing the audit trail that answered H2 at the time.

**Why this priority**: spec 005's reproducibility rule says "past audits remain valid against their own rubric version," but consumers of the evidence (POC exit synthesis) may want a re-audit against the calibrated rubric. Without a defined re-audit policy, this becomes ad-hoc. Priority P2 because the primary audit path (US1/US2) is higher value and must land first.

**Independent Test**: start from a session bundle whose `drift-audit.json` pins rubric version `A`, evolve the rubric to version `B` via a calibration commit, request a re-audit, verify the workflow produces a new `drift-audit.json` pinning `B`, and verify the commit history preserves the prior `A`-pinned audit as evidence (via git, not in the live file).

**Acceptance Scenarios**:

1. **Given** a session bundle with `drift-audit.json` pinning `rubric_version: A`, **When** a re-audit is requested against `rubric_version: B`, **Then** the committed `drift-audit.json` is replaced (not appended) with the `B`-pinned audit, and the commit message records the prior rubric version being superseded.
2. **Given** the re-audit lands, **When** a reviewer later wants to reconstruct the original `A`-pinned audit, **Then** they can retrieve it from git history via the session bundle's commit log — no live-file aggregation is required.
3. **Given** a Phase 3 session's `drift-audit.json` at the time of POC-exit synthesis, **When** the synthesizer reads the current bundle, **Then** they read the currently-pinned audit; rubric evolution between audits is not silently applied.

---

### Edge Cases

- **Zero-turn or near-empty transcript**: the workflow MUST still produce a `drift-audit.json` (possibly with empty `findings[]` and `verdict: "no_drift"`) rather than skipping, so every closed bundle carries audit evidence.
- **Missing `pinned_rules_ref` (legacy / pre-spec-003 bundles)**: the workflow MUST halt before producing a partial audit and surface the missing input; it does not guess or substitute.
- **Auditor aborts mid-audit**: a draft `drift-audit.json` MUST NOT be committed to the bundle; reconciliation/commit is an all-or-nothing step.
- **Cross-auditor unavailable for a session the operator declares counted**: the workflow records the session as "single-auditor, ineligible for H1/H2 counted evidence" and still commits the single-auditor audit for posterity; the counted flag moves elsewhere (out of scope here — see KPI rollup slice).
- **Rubric commit is uncommitted or detached at audit start time**: the workflow MUST refuse to run; `rubric_version` has to resolve to a committed SHA per spec 005.
- **Concurrent audits on the same bundle**: the second commit must rebase/merge cleanly; the workflow does not itself serialize, it relies on git's commit-ordering.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The workflow MUST take a closed session bundle (per spec 001 close definition) as its sole input and produce `drift-audit.json` at `observations/sessions/<session-id>/drift-audit.json`, conforming to the spec-005 schema.
- **FR-002**: The workflow MUST pin `rubric_version` to the git commit hash of `observations/drift-audits/RUBRIC.md` at audit start time. The rubric file MUST resolve to a committed SHA; uncommitted or detached rubric state is an FR-001 halt condition.
- **FR-003**: The workflow MUST record, in every committed `drift-audit.json`, `auditor` (string identifier for the auditor), `audited_at` (RFC3339 UTC), and `audited_by` (one of `manual`, `hybrid`, `llm_assisted` per spec 005 schema).
- **FR-004**: The workflow MUST support two modes: **single-auditor** (operator or delegate; default for exploratory / non-counted sessions) and **two-auditor** (primary + cross-reviewer; default for counted sessions eligible for H1/H2 evidence). Mode choice is recorded on the bundle, not inside `drift-audit.json` itself (the schema already records the committed outcome, not the mode).
- **FR-005**: In two-auditor mode, the workflow MUST require both auditors to complete an independent pass against the same `rubric_version` and the same committed bundle inputs before the reconciliation step runs. Sequential (audit-then-review) is acceptable only if the reviewer commits to the rubric without reading the first pass — the workflow treats this as an operator-attested independence, not enforced isolation.
- **FR-006**: In two-auditor mode, the reconciliation step MUST apply the FR-016 tolerance from spec 005 (±1 on `load_bearing_findings_count` for ≤200-turn sessions; spec 005's tolerance applies as-is, not re-derived here). If the two drafts are within tolerance, a reconciled `drift-audit.json` MUST be committed citing both auditors (`auditor` field lists both identities, comma-separated, per spec 005's schema acceptance of string identity).
- **FR-007**: If the two drafts diverge beyond tolerance, the workflow MUST NOT commit a reconciled audit until the divergence is resolved. The workflow MUST record the divergence publicly (e.g. via the session PR / discussion) so the rubric-calibration trigger from spec 005 §6.3 is visible.
- **FR-008**: The workflow MUST define an **operator-arbitrated resolution path** for above-tolerance divergence: the operator reviews both drafts, decides which findings stand, and commits the resulting `drift-audit.json` with `auditor: "<operator-id> (arbitrating <primary-id>/<cross-id>)"` so the arbitration trail is explicit. An operator-arbitrated audit is sufficient on its own for the session to remain eligible as counted-session evidence (evidence continuity is preserved; the POC is not blocked by early rubric ambiguity). However, the workflow MUST emit a **discoverable arbitration-event signal** on the commit so that POC-exit synthesis and any mid-POC calibration review can count arbitration events across sessions and decide whether a rubric-calibration commit is owed per spec 005 §6.3. Concretely: the amend-commit message MUST include the token `[arbitrated]` after the standard prefix, e.g. `session bundle amend: <session-id> — drift-audit [arbitrated] @ <rubric-version-short-sha>`. The token is grep-able from git history with no extra tooling.
- **FR-009**: The workflow MUST commit `drift-audit.json` via a session-bundle amend commit per spec 001 FR-014. The commit subject MUST include the rubric version (short SHA). Subject format: `session bundle amend: <session-id> — drift-audit[ <taxonomy-token>] @ <rubric-version-short-sha>` (taxonomy token per `contracts/workflow-contracts.md` C4 — absent / `[arbitrated]` / `two-auditor-upgrade` / `re-run, supersedes <old-sha>`). Auditor identity is recorded on the `drift-audit.json.auditor` field per spec 005's schema, not in the commit subject; if auditor detail or arbitration rationale is helpful for reviewers, the workflow MAY include it in the commit *body* (not subject).
- **FR-010**: The workflow MUST be idempotent: running the workflow twice on the same bundle with the same rubric version and the same auditor identity MUST produce a byte-identical `drift-audit.json` (modulo `audited_at` timestamp). Repeat operator intent is surfaced by commit history, not by file append.
- **FR-011**: The workflow MUST support **re-audit against an evolved rubric**: a new audit replaces the prior committed `drift-audit.json` (not appended), the commit message records the prior rubric version being superseded (`session bundle amend: <session-id> — drift-audit re-run @ <new-rubric-sha>, supersedes <old-rubric-sha>`), and the prior audit remains accessible via git history.
- **FR-012**: Re-audit is triggered via two paths, both of which the workflow MUST support: (a) **explicit operator request** on a specific bundle — always valid, regardless of rubric-version state; and (b) **POC-exit rubric-version sweep** — at the point where POC-exit synthesis prepares the final H1/H2 evidence roll-up, all counted-session audits are swept and bundles whose `rubric_version` predates the synthesis-time RUBRIC.md HEAD are flagged as re-audit-eligible. The sweep produces a sweep artifact listing each eligible bundle, its pinned rubric version, and the synthesis-time rubric HEAD, so the operator decides per-bundle whether to re-audit before the final roll-up. The sweep is bounded to the POC-exit moment; this slice does NOT specify continuous/periodic detection between sessions.
- **FR-013**: The workflow MUST NOT depend on LLM availability for v1. The manual path per spec 005 RUBRIC.md §4 is the sole committed-artifact producer in this slice. LLM-assisted authoring is acknowledged via FR-014 below but not operationalized in this spec.
- **FR-014**: The workflow MUST document the **entry criteria for LLM-assisted authoring** (deferred to a later slice): ≥2 counted sessions have been audited manually with two-auditor reconciliation landing within tolerance, spec 005 §7's LLM-judge prompt template is the authoring substrate, and manual ratification is the gate. This slice does NOT specify the automation, CLI, or orchestration of the LLM path.
- **FR-015**: The workflow MUST call out the **cross-slice consumption of `interventions.json`**: the rubric reads interventions as context input per spec 005, but this slice treats the intervention-tag schema as owned by the Codex intervention-tagging slice. If intervention-tag shape evolves, this workflow does not need a matching update unless the rubric itself evolves to depend on new tag semantics (in which case the update lives in 005, not here).
- **FR-016**: The workflow MUST compose with H2 KPI evidence as specified in spec 005 RUBRIC.md §8: the committed `drift-audit.json.verdict` is the authoritative drift input to H2 per-session clear-definition; downstream KPI rollup (Phase 5) reads it directly and MUST NOT re-derive drift findings.
- **FR-017**: The workflow MUST require `session_id`, `rubric_version`, and `pinned_rules_ref` cross-references in every committed `drift-audit.json` (redundant with spec 005 schema but repeated here as a workflow-level invariant, since the workflow is the producer).
- **FR-018**: The workflow MUST surface, when declining to produce an audit (missing inputs, uncommitted rubric, halted reconciliation), a non-silent failure message referencing which FR or bundle-close precondition is unmet, so bundle-producers fix upstream rather than work around.

### Key Entities

- **Session bundle** *(owned by spec 001; workflow input)*: the directory at `observations/sessions/<session-id>/` containing `transcript.md`, `meta.json`, `interventions.json`, and (after this workflow lands) `drift-audit.json`.
- **Drift-audit output** *(owned by spec 005; workflow output)*: the `drift-audit.json` file conforming to spec 005's data model, committed inside the session bundle via an amend commit.
- **Rubric version** *(owned by spec 005; workflow input reference)*: the git commit SHA of `observations/drift-audits/RUBRIC.md` at audit start time. Pinned on the output; never inferred retroactively.
- **Auditor identity** *(workflow-level; recorded on the output)*: a string identifying the human or agent running the audit. Primary + cross-reviewer in two-auditor mode are recorded together. No structured shape beyond what spec 005's schema already accepts.
- **Audit mode** *(workflow-level; recorded on the bundle, not inside `drift-audit.json`)*: `single-auditor` or `two-auditor`; determines whether the reconciliation step runs. Counted sessions eligible for H1/H2 evidence require `two-auditor`.
- **Reconciliation outcome** *(workflow-level; recorded in the commit message; not a new field on `drift-audit.json`)*: `agreed` (within tolerance; default commit prefix) or `operator-arbitrated` (diverged beyond tolerance, resolved by operator; commit message carries the `[arbitrated]` token per FR-008). An arbitrated session remains counted-eligible; the token is the discoverable calibration signal.
- **Re-audit sweep artifact** *(POC-exit-scoped; workflow-level)*: a one-shot artifact produced at POC-exit synthesis listing each counted-session bundle, its `rubric_version`, and the synthesis-time RUBRIC.md HEAD, so the operator decides per-bundle whether to re-audit before the final roll-up. Location and exact shape are delegated to the POC-exit synthesis slice; this slice only requires that the sweep be supported by the workflow.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator following the workflow produces a valid, committed `drift-audit.json` for a closed session bundle in ≤15 operator-minutes per ≤200-turn bundle (aligns with RUBRIC.md §4's target).
- **SC-002**: In Phase 3, for counted sessions audited under two-auditor mode, the primary and cross-reviewer passes agree within spec 005 FR-016 tolerance on ≥90% of sessions — the calibration trigger from spec 005 §6.3 fires on ≤10% of counted sessions.
- **SC-003**: 100% of closed, counted session bundles committed to `observations/sessions/` carry a non-placeholder `drift-audit.json` within 24 operator-hours of session close, with a valid `rubric_version` pinning a committed RUBRIC.md SHA.
- **SC-004**: Re-auditing a past session bundle against an evolved rubric produces a new `drift-audit.json` while the prior-rubric audit remains reconstructible from git history in 100% of re-audits (no live-file history needed).
- **SC-005**: A downstream KPI-rollup consumer can read the `drift-audit.json.verdict` field directly from the session bundle directory without out-of-band context or auditor-specific tooling in 100% of audit-complete bundles.
- **SC-006**: A reviewer asking "what rubric version did this session's audit apply?" can answer in ≤30 seconds using the single file `observations/sessions/<session-id>/drift-audit.json`.

## Assumptions

- The session bundle is produced by the spec 001 / spec 006 / spec 007 chain and is closed before the workflow runs. The workflow does not open, seal, or otherwise mutate the bundle beyond the single amend commit for `drift-audit.json`.
- The rubric (`observations/drift-audits/RUBRIC.md`) is the committed Phase 2 artifact landed via spec 005. The workflow consumes it as an external reference; it does not modify the rubric or propose rubric changes.
- Intervention-tag schema is owned by the Codex-owned intervention-tagging slice. The workflow consumes `interventions.json` opaquely — whatever shape spec 005's rubric expects is fine; this slice does not require the tag schema to be finalized.
- Auditor identity is a free-text string (per spec 005's schema). Structured auditor roles (operator / cross-reviewing-agent / external-human) are not a schema concern; human convention governs the string content.
- **Two-auditor mode in the POC usually means human + LLM-judge**, not two humans. POC staffing is thin — one operator (Zoe) plus an LLM judge per spec 005 §7 (active from Phase 3 session 3+) is the realistic cross-reviewer configuration. FR-005's "sequential audit-then-review with operator-attested independence" explicitly allows this; the LLM judge reads the same bundle + rubric version without seeing the first pass, and the operator attests to that independence when committing the reconciliation. Early Phase 3 sessions (before LLM judge is calibrated) may run as single-auditor and are surfaced as ineligible for H1/H2 counted evidence until a cross-reviewer pass lands.
- Spec 005's tolerance rule (FR-016) is the authoritative cross-auditor agreement threshold. This slice does not re-derive the tolerance.
- LLM-assisted authoring is explicitly deferred. This slice sets only entry criteria (≥2 calibrated manual audits) for a future slice; it does not specify the automation itself.
- Counted-session criteria (H1/H2 evidence eligibility) live in a later KPI rollup slice. This workflow surfaces whether a session is `two-auditor` complete, but whether the session "counts" is a downstream judgment.

## Dependencies

- **Upstream (landed)**: spec 001 (session bundle), spec 005 (rubric + schema), spec 006 (transcript export). All three are merged to `main` at the time this spec is drafted.
- **Upstream (in-flight, non-blocking)**: spec 007 (session-bundle init CLI, Codex-owned). If 007 lands before this slice implements, the audit invocation can plug into the same tooling surface; if not, the workflow is specified as a procedure independent of any CLI.
- **Cross-slice (Codex-owned, non-blocking)**: intervention-tagging mechanism. The workflow treats `interventions.json` shape as externally owned.
- **Downstream (blocks)**: KPI rollup / H2 evidence synthesis (Phase 5, not yet specced) depends on the committed `drift-audit.json.verdict` being the authoritative drift evidence.
- **Constitutional**: aligns with constitution v1.5.0 — artifact-first discipline (all audit state lives in `observations/sessions/<id>/`), independent review (two-auditor mode for counted sessions), session-scoped artifacts (one audit per session-id, not cross-session aggregation).
