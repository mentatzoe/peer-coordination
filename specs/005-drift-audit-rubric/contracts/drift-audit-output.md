# Contract: `drift-audit.json` Output Artifact

**Feature**: `005-drift-audit-rubric`
**Consumers**: (1) H2 per-session clear-definition judgment per `design/poc.md`; (2) POC KPI rollup (separate Phase 2 spec); (3) cross-auditor agreement checks per FR-016; (4) fresh agent session pickup per the artifact-driven operating model.

## Artifact location

- Path: `observations/sessions/<session-id>/drift-audit.json`
- Exists per session bundle (one per session)
- Spec 001 FR-008 makes the file mandatory; this contract defines what valid content looks like after Phase 2.

## Contract guarantees (what valid `drift-audit.json` promises consumers)

### Guarantee 1 — Schema conformance

A valid `drift-audit.json` conforms to one of two shapes defined in [`data-model.md`](../data-model.md):

- **happy path** (with findings): `rubric_version`, `session_id`, `pinned_rules_ref`, `audited_at`, `audited_by`, `auditor`, `findings`, `load_bearing_findings_count`, `verdict`
- **blocked path** (incomplete bundle): `rubric_version`, `status`, `reason`

Consumers can dispatch on presence/absence of `status: "blocked"` without deep parsing.

### Guarantee 2 — Verdict is KPI-ready

`verdict` is deterministic from `findings[]` per FR-007:

- `no_drift` ⇒ zero findings with severity `warn` or `finding`
- `minor_drift` ⇒ one or more `warn`, zero `finding`
- `load_bearing_drift` ⇒ one or more `finding`

Consumers computing H2 per-session clear-definition can read `verdict` + `load_bearing_findings_count` directly without re-deriving from findings.

### Guarantee 3 — Reproducibility via rubric version

`rubric_version` resolves to a reachable commit of `observations/drift-audits/RUBRIC.md`. A consumer checking out that commit reads the exact procedure the auditor used. Past audits remain reproducible as the rubric evolves.

### Guarantee 4 — Turn-ref resolvability

Every `Finding.turn_ref` is the ISO-8601 timestamp of a turn present in the session's `transcript.md`. Every `Finding.quote` is a substring of that turn's content. Cross-auditors and reviewers can anchor findings back to the source record.

### Guarantee 5 — Findings-to-verdict consistency

The `load_bearing_findings_count` integer equals the count of `findings[]` entries with `severity: "finding"`. The `verdict` follows the FR-007 rule applied to the same array. Consumers can cross-check by recomputing; a mismatch indicates a corrupted or hand-edited artifact and the consumer may refuse to use it.

### Guarantee 6 — Post-session only

The artifact is authored post-session. No agent or auditor touches it during live session operation (FR-011). Consumers never see partial/streaming drift-audit content.

## Non-guarantees (what the contract does NOT promise)

- **Inter-auditor exact agreement**: two independent auditors may reach different `findings[]` content. Agreement is bounded by the FR-016 tolerance (±1 on `load_bearing_findings_count` for ≤200-turn sessions). Consumers that need a single source of truth should prefer operator's audit or hybrid outputs.
- **Completeness of findings**: even a careful auditor may miss drift a second auditor catches. The rubric is calibrated over time; absence of findings is not proof of no drift.
- **Runtime enforcement**: nothing in this contract is checked by automated tooling at write time. Consumers are expected to validate schema conformance + guarantee 5 at read time.

## Consumer responsibilities

- **H2 clear-definition judgment**: consumer reads `verdict` + `load_bearing_findings_count` + selected `findings[]` rationales for the H2 fresh-reader-pass judgment per `design/poc.md`.
- **KPI rollup** (separate Phase 2 spec): consumer aggregates per-session verdicts + counts across the baseline session set.
- **Cross-auditor agreement check**: consumer running agreement test (FR-016) compares two auditors' `load_bearing_findings_count` for the same session; differences above tolerance trigger rubric-calibration review.
- **Fresh-agent pickup**: consumer reads the most recent `drift-audit.json` as part of session re-entry context.

## Evolution

- Schema changes happen via rubric-version commits. Old outputs remain valid against old rubrics; consumers should tolerate encountering pre-Phase-2 placeholder outputs (`{"status": "pending-phase-2"}`) until the Phase 2 rubric is in place and sessions are re-audited.
- Category enum additions are backwards-compatible per FR-004: consumers encountering unknown categories should treat them as `other` for counting purposes.
- `audited_by` enum is closed under the three current values; additions require this contract to be amended explicitly.
