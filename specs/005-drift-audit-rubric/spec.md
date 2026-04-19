# Feature Specification: Drift-Audit Rubric

**Feature Branch**: `claude-005-drift-audit-rubric`
**Created**: 2026-04-19
**Status**: Draft
**Input**: Define the drift-audit rubric — the schema + scoring procedure that produces `drift-audit.json` per session bundle. The rubric evaluates whether a session's transcript + pinned-rules state exhibits H2 legibility drift (undeclared conventions, private shorthand, hidden side channels, meaning-requires-context-outside-the-record). Used in Phase 2 + Phase 3 per `design/poc.md` measurement model. The spec defines the artifact shape + audit procedure; the exact scoring weights are calibrated against real sessions in Phase 3 and are out of scope for this initial spec.

## Context *(added for peer-coordination flavor; not part of the template)*

- **Parent artifacts**:
  - [`design/poc.md`](../../design/poc.md) — "Per-session clear definitions" (H2 fresh-reader pass), "H2 — Legibility observables" (drift-audit item), "Measurement model" (drift audit row).
  - [`design/architecture.md`](../../design/architecture.md) — Layer 3 capabilities, specifically "A minimal failure taxonomy that distinguishes at least convergence failure, legibility failure, complementarity failure, and intervention dependence."
  - [`VISION.md`](../../VISION.md) — H2 legibility hypothesis and "How we stay honest" (active drift-audit is part of the evaluation, not an afterthought).
- **Consumer contract**:
  - [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) FR-008: each session bundle must contain `drift-audit.json`. Placeholder `{"status": "pending-phase-2"}` is accepted for Phase 1; this spec defines the real shape.
- **Roadmap workstream**: `Evaluation surface build` (Phase 2, Claude slice per [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41) staffing).
- **Related specs**:
  - [`specs/003-pinned-rules-authoring/spec.md`](../003-pinned-rules-authoring/spec.md) — the rules artifact the rubric audits against.
  - Intervention-tagging mechanism (Codex Phase 2 slice, not yet specced) — separate from this rubric; intervention log is input context, not a drift-audit output.
- **Staffing**: Claude lead (evaluation pipeline slice per #41); Codex cross-reviewer via Zoe relay at implementation-complete checkpoint per the ratified autonomous-loop operating model.

## User Scenarios & Testing *(mandatory)*

The "users" of the rubric are, in priority order: the operator (runs the audit post-session and ratifies findings), a cross-reviewing agent (applies the rubric to produce `drift-audit.json`), and an uninvolved human reviewer (uses the output to answer the H2 fresh-reader-pass clear-definition).

### User Story 1 — Operator produces an auditable `drift-audit.json` per session (Priority: P1)

As the operator, after a Phase 3 session's bundle is assembled, I need to apply the drift-audit rubric to the transcript + pinned-rules snapshot and produce a `drift-audit.json` that enumerates any undeclared-convention drift observed, so the session's H2 KPI input is auditable.

**Why this priority**: without a real drift-audit artifact (not just a placeholder), Phase 2 cannot exit its gate and Phase 3's sessions produce incomplete evidence for H2. This is the MVP atom of the slice.

**Independent Test**: hand the operator a Phase 3 session bundle (transcript + pinned-rules commit hash + intervention log), have them apply the rubric procedure to produce a valid `drift-audit.json`, and verify a cross-reviewer can reach the same or compatible conclusions from the same inputs.

**Acceptance Scenarios**:

1. **Given** a completed session bundle with `transcript.md`, `meta.json` (including `pinned_rules_ref`), and `interventions.json`, **When** the operator runs the drift-audit procedure per this spec, **Then** the resulting `drift-audit.json` conforms to the schema defined here and any findings cite specific transcript turn timestamps.
2. **Given** two auditors (e.g., operator and a cross-reviewing agent) apply the rubric to the same bundle, **When** they compare outputs, **Then** their `load_bearing_findings_count` agrees to within a tolerance the rubric defines (see FR-013).

### User Story 2 — Rubric supports calibration from real sessions (Priority: P1)

As the operator, when early Phase 3 sessions surface drift categories or edge cases the rubric didn't anticipate, I need the rubric to be revisable with discrete commits and a version reference so past-session audits remain reproducible against their own rubric version.

**Why this priority**: the POC measurement model explicitly says the rubric is *calibrated* after the first one or two sessions. Without version-stability, re-auditing past sessions against an evolved rubric would produce inconsistent evidence.

**Independent Test**: update the rubric in a discrete commit (`drift-audit-rubric: <summary>`), verify past `drift-audit.json` outputs retain their `rubric_version` field pointing at the earlier commit, and verify re-running the audit against the new rubric produces a distinguishable new output.

**Acceptance Scenarios**:

1. **Given** a past session's `drift-audit.json` records `rubric_version: "<commit-A>"`, **When** the rubric evolves to `<commit-B>`, **Then** the past audit still resolves to commit-A's rubric content.
2. **Given** the rubric evolves between Phase 3 sessions, **When** a new session's audit is run, **Then** the new `drift-audit.json` records the current rubric commit hash.

### User Story 3 — Rubric composes with H2 per-session clear definition (Priority: P2)

As a reviewer computing the H2 fresh-reader KPI, I need the drift-audit output to feed directly into the H2 clear-definition judgment without requiring me to re-derive drift findings by hand.

**Why this priority**: H2's per-session clear definition (per `design/poc.md`) depends on whether the preserved episode record is sufficient for a fresh reader. Undeclared-convention drift is one of the ways the record becomes insufficient; the rubric's findings are the evidence input for that judgment.

**Independent Test**: given a bundle's `drift-audit.json` with findings, have a reviewer answer the H2 fresh-reader-pass clear-definition using the audit output as direct evidence, and verify the reasoning is traceable.

**Acceptance Scenarios**:

1. **Given** a bundle's `drift-audit.json` has `load_bearing_findings_count: 0` and verdict `no_drift`, **When** a reviewer applies the H2 clear-definition, **Then** undeclared-convention drift is not the reason H2 fails (other reasons may still cause it to fail).
2. **Given** a bundle's `drift-audit.json` has one or more `load_bearing_findings`, **When** a reviewer applies the H2 clear-definition, **Then** those findings are cited in the H2 judgment rationale.

### Edge Cases

- **A peer references a pinned-rule that was pinned under a different `pinned_rules_ref`**: the audit must anchor against the commit referenced in the session's `meta.json`, not whatever is currently pinned.
- **Off-palette emoji appears but is not load-bearing**: the rubric records it as `severity: info` but does not count it toward `load_bearing_findings_count`. Not every convention deviation is a failure; only those that carry coordination-load matter for H2.
- **Reviewer disagreement on whether a pattern is "private shorthand" vs "reasonable shared-context inference"**: rubric provides a judgment-call rule (FR-010) and expects per-session annotation of disagreements.
- **Hidden side-channel reference without direct quote**: if a peer says "as discussed earlier" referring to content not in the transcript, the rubric flags it as `hidden_channel_reference` even without a direct quote of the side-channel content.
- **Bundle missing `transcript.md` or `pinned_rules_ref`**: audit cannot run; the bundle is incomplete per spec 001, and `drift-audit.json` records `status: "blocked — incomplete bundle"` rather than fabricating findings.
- **LLM-assisted audit disagrees with operator manual audit**: per FR-015, operator manual judgment wins and the LLM's output is recorded as `auditor: llm_assisted` with operator annotations.

## Requirements *(mandatory)*

### Functional Requirements

**Output shape (`drift-audit.json`):**

- **FR-001**: Each session bundle's `drift-audit.json` MUST be a single JSON object conforming to the schema defined in the authoring workflow docs (produced in `/speckit.plan` outputs).
- **FR-002**: The object MUST contain the following top-level fields:
  - `rubric_version` — commit hash of `observations/drift-audits/RUBRIC.md` at audit time, OR inline snapshot for pre-rubric sessions
  - `session_id` — matches the bundle's `meta.json.session_id`
  - `pinned_rules_ref` — matches the bundle's `meta.json.pinned_rules_ref`
  - `audited_at` — ISO-8601 timestamp of when the audit was run
  - `audited_by` — one of `manual`, `llm_assisted`, `hybrid`
  - `auditor` — handle of the auditor (operator handle, or agent identifier if `llm_assisted`)
  - `findings` — array of finding objects (may be empty)
  - `load_bearing_findings_count` — integer count of findings with `severity: finding` (the KPI-relevant subset)
  - `verdict` — one of `no_drift`, `minor_drift`, `load_bearing_drift`
- **FR-003**: Each object in `findings` MUST contain: `category`, `severity`, `quote`, `turn_ref`, `rationale`.
- **FR-004**: `category` MUST be one of a fixed enum: `undeclared_emoji`, `undeclared_abbreviation`, `private_shorthand`, `hidden_channel_reference`, `off_palette_load_bearing`, `other`. The taxonomy may evolve via rubric-version commits, but additions are explicit and backwards-compatible (old audits with the old enum remain valid).
- **FR-005**: `severity` MUST be one of: `info` (noted, not KPI-relevant), `warn` (possible drift, may or may not be load-bearing per operator judgment), `finding` (load-bearing drift confirmed).
- **FR-006**: `turn_ref` MUST be the ISO-8601 timestamp of the referenced transcript turn (canonical turn key per spec 001 FR-009). Maps to the transcript timestamp; no separate turn-id scheme.
- **FR-007**: `verdict` MUST be computed deterministically from findings: `no_drift` iff zero findings with `severity: finding` or `warn`; `minor_drift` iff one or more `warn` and zero `finding`; `load_bearing_drift` iff one or more `finding`.

**Audit procedure:**

- **FR-008**: The audit procedure MUST be applicable manually (without tooling) in the early Phase 3 sessions; the spec includes the checklist the operator walks through per session.
- **FR-009**: The audit procedure MUST be applicable with LLM-assistance after the rubric is calibrated (per measurement-model row in `design/poc.md`); the spec includes the prompt template / input shape that an LLM-judge takes.
- **FR-010**: When categorizing a pattern as `private_shorthand` vs permissible shared-context inference, the rubric's rule is: if an uninvolved human reviewer cannot reach the same meaning by reading `transcript.md` + the pinned-rules at `pinned_rules_ref` + the intervention log, the pattern is `private_shorthand`. Otherwise, it is not drift.
- **FR-011**: Audit MUST run **post-session only** per the measurement model's observer-effect constraint. Nothing in the audit procedure runs during a live session.
- **FR-012**: If the bundle is incomplete (missing required files per spec 001), the audit MUST NOT fabricate findings. Output `{ "status": "blocked", "reason": "<specific missing artifact>" }` with no `findings` key.

**Rubric versioning:**

- **FR-013**: The rubric content itself MUST live at `observations/drift-audits/RUBRIC.md` (the substantive procedure doc) with version history via git commits. Commit message convention: `drift-audit-rubric: <summary>`. Analogous to the pinned-rules workflow in spec 003.
- **FR-014**: Each rubric change is a discrete commit; findings produced under a specific commit remain reproducible by checking out that commit and re-reading `RUBRIC.md`.

**Calibration + agreement:**

- **FR-015**: When manual and LLM-assisted audits disagree on a specific finding, the operator's manual judgment is authoritative. The LLM output is preserved in `drift-audit.json` with the operator's override annotations; the audit is then tagged `audited_by: hybrid`.
- **FR-016**: The rubric MUST support a cross-auditor-agreement tolerance: if two independent auditors (operator + cross-reviewing agent) produce `load_bearing_findings_count` values within ±1 on a session of ≤200 turns, that counts as agreement. Larger divergences trigger a rubric-calibration review.

**Scope boundaries:**

- **FR-017**: This spec MUST NOT cover: the intervention-tagging mechanism (Codex Phase 2 slice), the KPI rollup script (separate Phase 2 spec), the session-summary workflow (separate Phase 2 spec), or any modifications to `transcript.md` / `meta.json` / `interventions.json` schemas (defined in spec 001).
- **FR-018**: This spec MUST NOT introduce live-session instrumentation, agent-facing drift feedback, or any mechanism that changes agent behavior mid-session.

### Key Entities

- **Drift-audit output**: the `drift-audit.json` artifact per session bundle. Conforms to FR-001 through FR-007. Produced by an auditor (operator, LLM-judge, or hybrid). Consumed by the H2 per-session clear-definition and the POC KPI rollup.
- **Rubric**: the procedure + category definitions + severity rules that govern how findings are produced. Lives at `observations/drift-audits/RUBRIC.md`. Version-controlled via git commits; referenced from `drift-audit.json.rubric_version`.
- **Finding**: a single instance of observed drift in a session. Has category, severity, quote, turn reference, and rationale. Load-bearing findings (severity: finding) are the ones that feed H2 failure determinations.
- **Auditor**: the actor producing the audit. One of: operator (manual), LLM-as-judge (automated, post-session), or hybrid (LLM drafts, operator ratifies with overrides).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every counted Phase 3 session bundle, `drift-audit.json` is present with a valid rubric version reference and either `findings: [...]` (possibly empty) or `status: "blocked"`. No session produces a placeholder or missing audit output.
- **SC-002**: Two independent auditors (operator + cross-reviewing agent) applying the rubric to the same bundle agree on `load_bearing_findings_count` within the FR-016 tolerance in ≥80% of cases. Disagreements above the tolerance trigger a rubric-calibration commit.
- **SC-003**: A reviewer computing the H2 fresh-reader-pass clear-definition using `drift-audit.json` as direct input can answer clear/not-clear without re-deriving findings from the transcript, in ≥80% of audited sessions. The remaining 20% is acceptable as edge cases where H2 judgment extends beyond drift (e.g., transcript completeness issues).
- **SC-004**: Rubric calibration happens via discrete commits; past audit outputs remain reproducible by checking out their `rubric_version` commit in 100% of sessions.
- **SC-005**: The manual audit procedure fits in ≤15 operator-minutes per session on a typical 3–5 session set (target, not hard limit).

## Assumptions

- The POC substrate is Discord; references to pinning mechanics and emoji palettes assume the Discord-shaped surface per `design/poc.md`. Substrate-portable abstractions are deferred.
- Sessions have a reviewable transcript in `transcript.md` per spec 001 FR-009. The audit procedure assumes timestamp + author per turn and unique timestamps within a session.
- The pinned rules referenced by `pinned_rules_ref` are stable under the git commit (guaranteed by spec 003's workflow).
- LLM-assistance for drift audit is deferred to after the first 1–2 Phase 3 sessions per the measurement-model calibration step. The initial manual procedure does not depend on LLM availability.
- Operator bandwidth for manual audits is acceptable for 3–5 Phase 3 sessions + 1–2 Phase 4 Gemini sessions. If the POC grows beyond that scale, LLM-assistance becomes mandatory.
- Intervention tagging is specified separately (Codex Phase 2 slice). This rubric reads `interventions.json` as additional context but does not depend on specific intervention categories beyond the taxonomy in spec 001 FR-011.

## Dependencies

- Depends on [`specs/001-session-bundle-skeleton/spec.md`](../001-session-bundle-skeleton/spec.md) — consumer contract (`drift-audit.json` placement, transcript timestamp uniqueness, `pinned_rules_ref` semantics).
- Depends on [`specs/003-pinned-rules-authoring/spec.md`](../003-pinned-rules-authoring/spec.md) — the rules artifact the rubric audits against.
- Does NOT depend on spec 004 (`discord-session-controls`) — drift audit is post-session and substrate-behavior-agnostic.
- Does NOT depend on any unspecified Phase 2 intervention-tagging mechanism — reads intervention log as context, not as a driver.
- Blocks: Phase 2 gate (evaluation-pipeline-exists) cannot clear until the rubric is in place and has been mock-run against a synthetic or prior transcript.

## Clarifications

### Session 2026-04-19

Per the operator directive authorizing autonomous speckit progression, the following ambiguities were surfaced by the `/speckit.clarify` taxonomy scan and self-resolved inline rather than asking the operator. Cross-reviewer may amend retroactively via follow-up commits.

- Q: What is the drift category enum scope? → A: Five minimum categories aligned with `design/poc.md`'s H2 legibility observables (`undeclared_emoji`, `undeclared_abbreviation`, `private_shorthand`, `hidden_channel_reference`, `off_palette_load_bearing`) plus `other` as escape hatch. Alternatives (finer subcategories, severity-only without categories) rejected — explicit categories provide explainability without forcing premature ontology. (FR-004)
- Q: What turn-reference scheme does `findings[].turn_ref` use? → A: Spec 001's canonical turn key (ISO-8601 timestamp, unique within session per FR-009). Alternatives (sequential turn IDs, character offsets) rejected for consistency with spec 001. (FR-006)
- Q: Where does the rubric content live? → A: `observations/drift-audits/RUBRIC.md` — scope-local to the evaluation surface, analogous to the `pinned-rules/current.md` pattern. Alternative (`specs/005-drift-audit-rubric/rubric.md`) rejected because specs are design artifacts, not runtime-referenced content. (FR-013)
- Q: How is the verdict computed? → A: Deterministically from findings per FR-007; not auditor-assigned. Prevents judgment-stacking where an auditor could game the verdict independent of findings. (FR-007)
- Q: Who wins when manual and LLM-assisted audits disagree? → A: Operator manual judgment is authoritative per Constitution Principle IV (operator as final arbiter); LLM output preserved with operator override annotations. (FR-015)

### Clarify coverage report (2026-04-19)

| Category | Status | Note |
|---|---|---|
| Functional Scope & Behavior | Clear | 3 user stories, 18 FRs, FR-017/FR-018 out-of-scope boundary |
| Domain & Data Model | Clear | `Drift-audit output`, `Rubric`, `Finding`, `Auditor` entities defined |
| Interaction & UX Flow | Clear | Manual, LLM-assisted, hybrid paths all covered in US1–3 |
| Non-Functional Quality — Performance | Clear | SC-005: ≤15 operator-minutes per session target |
| Non-Functional Quality — Observability | Clear | `drift-audit.json` output schema is the observability artifact |
| Non-Functional Quality — Security/Privacy | Clear | Transcripts already redacted upstream per spec 001 FR-015; rubric reads but does not introduce new secrets |
| Integration & External Dependencies | Clear | Dependencies on spec 001, 003, design docs enumerated |
| Edge Cases & Failure Handling | Clear | 6 edge cases in spec; FR-012 handles incomplete bundles |
| Constraints & Tradeoffs | Clear | Five clarifications above document tradeoffs explicitly |
| Terminology & Consistency | Clear | Key Entities section defines canonical terms |
| Completion Signals | Clear | 5 SCs with measurable criteria |
| Misc / Placeholders | Clear | No TODO markers, no NEEDS CLARIFICATION markers |

No critical ambiguities remain after the self-resolved pass. Spec is ready to proceed to `/speckit.plan`.
