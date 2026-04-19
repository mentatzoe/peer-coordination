# Research: Drift-Audit Rubric (Phase 0)

**Feature**: `005-drift-audit-rubric`
**Date**: 2026-04-19
**Purpose**: Resolve any remaining unknowns from `spec.md` Technical Context and check that the rubric design doesn't duplicate or contradict prior work.

## Decisions

### Decision: Category enum is 5+1 (not deeper, not shallower)

**Choice**: `undeclared_emoji | undeclared_abbreviation | private_shorthand | hidden_channel_reference | off_palette_load_bearing | other`

**Rationale**:

- The five non-`other` categories map 1-to-1 onto `design/poc.md`'s H2 legibility observables section: *"new emoji uses not in the shared palette; abbreviations that require context to decode; message patterns that only make sense between the specific agents; hidden-channel usage."* `off_palette_load_bearing` is the finer-grained emoji case where an emoji IS in the palette but is used with meaning not defined by the rules.
- `other` is the operator-escape-hatch for drift that doesn't fit the five — gives evolvability without committing to premature ontology.
- Deeper categorization (subcategories per emoji usage, per shorthand type, etc.) premature until Phase 3 sessions reveal real patterns. The rubric can evolve via git commits (FR-013/014).
- Shallower categorization (severity-only, no category) rejected: loses explainability, makes cross-auditor agreement harder to reason about.

**Alternatives considered**:

- **3 categories** (structural drift / shorthand drift / hidden-context drift). Too coarse; collapses `undeclared_emoji` and `private_shorthand` which carry different audit procedures.
- **10+ categories** with per-drift-type subcategories. Too granular; each subcategory needs its own audit procedure + Phase 3 calibration, which we don't have calibration data for yet.
- **Free-text category field**. Maximally evolvable but destroys cross-auditor agreement and KPI computability.

### Decision: Verdict computed deterministically from findings, not auditor-assigned

**Choice**: `verdict` is a pure function of `findings` array: `no_drift` iff zero non-info findings; `minor_drift` iff only `warn` findings; `load_bearing_drift` iff any `finding` severity.

**Rationale**:

- Separates the judgment step (category + severity per finding) from the aggregation step (verdict). Each auditor's judgment is per-finding; the verdict is not a place to override that judgment.
- Prevents judgment-stacking: an auditor can't set `verdict: no_drift` if they've recorded a `severity: finding` entry; the contradiction is structurally impossible.
- Makes KPI rollup deterministic from bundle content alone (no human-in-the-loop read).

**Alternatives considered**:

- **Auditor-assigned verdict with findings as evidence**. More flexible, but allows inconsistent reports — auditor could record a `finding` but say verdict is `no_drift` because "it didn't affect the session." We want those to be separate observations: if it was load-bearing, it was a finding; if not, severity is `warn` or `info`.
- **Numeric score** (e.g., `drift_score: 0.0–1.0`). Deterministic but requires calibration weights we don't have yet.

### Decision: Rubric content at `observations/drift-audits/RUBRIC.md`, versioned via git

**Choice**: single-file canonical rubric + git commits as versions. Analogous to `pinned-rules/current.md` pattern from spec 003.

**Rationale**:

- Consistent mental model with spec 003: `current.md` for pinned rules, `RUBRIC.md` for the drift-audit procedure. Each is single-file + git-commit-versioned + commit-hash-referenced from consumer outputs.
- Reproducibility: auditors produce `drift-audit.json` with `rubric_version: <commit hash>`. Later re-audits or disagreement-resolution can check out the exact commit.
- `observations/drift-audits/` lives in the evaluation surface (Layer 3), not under `specs/` — the rubric is runtime content, not design content.

**Alternatives considered**:

- **Spec-file-embedded rubric** (rubric in `specs/005-drift-audit-rubric/rubric.md`). Rejected: specs are design artifacts; runtime content belongs elsewhere.
- **Multi-file versioning** (`RUBRIC-v1.md`, `RUBRIC-v2.md`). Rejected for same reason spec 003 rejected per-version files: git is the VCS; duplicating with filename versions creates drift.
- **JSON rubric** (machine-readable). Rejected for Phase 2: rubric needs to read prose-level ("a pattern is private shorthand iff..."). JSON schema lives in `data-model.md` for the output, but the procedure itself is prose.

### Decision: Manual audit bootstraps LLM-assistance; not LLM-first

**Choice**: manual-by-operator for Phase 2 first 1–2 sessions. LLM-assistance enabled from Phase 3 session 3+ after rubric calibrates against real data. Hybrid (LLM drafts + operator ratifies) allowed throughout; operator judgment wins on disagreement (FR-015).

**Rationale**:

- Matches `design/poc.md` measurement-model row: *"Manual review in early sessions, then LLM-assisted post-session audit once the rubric is calibrated."*
- Calibration needs ground-truth data; without 1–2 manual-audited sessions, an LLM-as-judge can't be benchmarked for agreement.
- Constitution Principle IV: operator is final arbiter. Encoded in FR-015.

**Alternatives considered**:

- **LLM-first from day 1**. Rejected: no calibration anchor; would produce unvalidated drift findings.
- **Pure manual** (no LLM at all). Rejected: operator cost unscaleable past a handful of sessions; measurement-model explicitly plans for LLM-assistance post-calibration.

### Decision: Rubric reads intervention log as context, doesn't depend on specific intervention categories

**Choice**: rubric's audit procedure may reference `interventions.json` entries for context (e.g., if operator flagged `drift_catch` in real-time, that's a hint for the auditor). But the rubric's category enum is independent of the intervention-type taxonomy from spec 001 FR-011.

**Rationale**:

- Intervention tagging (Codex's Phase 2 slice) is specified separately; this rubric should not hard-code dependency on its exact category enum.
- Drift catch from the operator is input-hint, not ground truth. The rubric produces findings independent of whether the operator tagged them live.

**Alternatives considered**:

- **Rubric category enum exactly matches intervention category enum**. Rejected: couples two slices that should evolve independently; intervention taxonomy is about operator-facing control actions, rubric taxonomy is about post-hoc drift classification.

## Dependencies + Integration

- **spec 001 (session-bundle-skeleton)**: rubric output lives at `observations/sessions/<session-id>/drift-audit.json`, the path spec 001 FR-008 established. Bundle completeness invariants (SC-004) include drift-audit being present. Consumer contract is fully respected.
- **spec 003 (pinned-rules-authoring)**: rubric audits against the pinned rules at the session's `pinned_rules_ref` commit. Assumes spec 003's workflow (commit-hash preferred, inline fallback) is honored.
- **spec 004 (discord-session-controls)**: independent. Drift audit is post-session and substrate-agnostic.

## Open questions from Phase 0 (none)

All identified unknowns resolved inline in the decisions above. No blocker-level research gaps.
