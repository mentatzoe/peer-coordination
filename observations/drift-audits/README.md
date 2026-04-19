# Drift Audits

This directory holds the canonical **drift-audit rubric** for the peer-coordination POC. The rubric evaluates whether a session's preserved transcript + pinned-rules state exhibits H2 legibility drift (undeclared conventions, private shorthand, hidden side channels, meaning-requires-context-outside-the-record). Used post-session in Phase 2 and Phase 3.

**Authoritative spec**: [`specs/005-drift-audit-rubric/spec.md`](../../specs/005-drift-audit-rubric/spec.md).
**Parent framework**: [`design/poc.md`](../../design/poc.md) Measurement model + H2 legibility observables.
**Governing principle**: Constitution [Principle VI](../../.specify/memory/constitution.md) — coordination is human-legible, not over-protocolized.

## What lives here

- [`RUBRIC.md`](RUBRIC.md) — the substantive audit procedure: category definitions, severity rules, verdict logic, manual-audit checklist, LLM-judge prompt template.
- [`CHANGELOG.md`](CHANGELOG.md) — convenience log of rubric changes. Git log is authoritative.
- This `README.md` — workflow + cross-refs.

## What does NOT live here

- Per-session audit outputs (`drift-audit.json`). Those live with their session bundles at `observations/sessions/<session-id>/drift-audit.json` per [spec 001 FR-008](../../specs/001-session-bundle-skeleton/spec.md).
- Governance / design content. This directory is Layer 3 evaluation content only; see `VISION.md`, `design/architecture.md`, `design/poc.md` for the canonical framework.

## Authoring workflow

1. **Propose**: rubric changes come from either (a) the operator, (b) a cross-reviewing agent identifying drift patterns the rubric misses, or (c) a calibration trigger per FR-016 (cross-auditor disagreement above tolerance).
2. **Ratify**: the operator decides whether the rubric should change.
3. **Commit**: the operator updates `RUBRIC.md` (and/or the category-defs section, severity rules, checklist, prompt template). Commit message follows the convention `drift-audit-rubric: <short summary>` per [spec 005 FR-013](../../specs/005-drift-audit-rubric/spec.md).
4. **One logical change per commit**. Rationale belongs in the commit message.
5. **Re-audit against the new rubric only for sessions run under the new rubric version.** Past sessions'  `drift-audit.json.rubric_version` points to an earlier commit — those audits remain valid against their own rubric content.

## Commit-reference contract with session bundles

Every `drift-audit.json` per [data-model](../../specs/005-drift-audit-rubric/data-model.md) records `rubric_version`. That field is:

- **Preferred**: the commit hash of this `RUBRIC.md` at audit time.
- **Fallback**: inline snapshot for pre-rubric sessions (should be rare after this directory lands).

A reviewer can always check out the referenced commit and read `observations/drift-audits/RUBRIC.md` to get the exact procedure the audit used.

## Versioning discipline

- Rubric changes are **discrete commits** with `drift-audit-rubric: <summary>` messages per FR-013/014.
- Rubric changes happen **between sessions**, not during a live session (analogous to pinned-rules changes from spec 003 closing the session).
- Calibration triggers per FR-016: when two independent auditors produce `load_bearing_findings_count` values differing by more than ±1 on a ≤200-turn session, that's a signal to tighten the rubric. Commit the clarification; re-run the audit.
- Each rubric version remains reachable via its commit hash as long as `main` history is preserved.

## Operator-only authoring (Phase 1)

- Agents do NOT commit to `observations/drift-audits/` autonomously in Phase 1. Agents may propose rubric changes via discussion threads or via drift-audit output annotations; operator ratifies and commits.
- Rationale: analogous to pinned-rules in spec 003 — peers should not be able to modify their own evaluation criteria. Applies Principle IV (operator as final arbiter).

## Cross-references

- [`specs/005-drift-audit-rubric/spec.md`](../../specs/005-drift-audit-rubric/spec.md) — authoritative spec
- [`specs/005-drift-audit-rubric/plan.md`](../../specs/005-drift-audit-rubric/plan.md) — implementation plan
- [`specs/005-drift-audit-rubric/data-model.md`](../../specs/005-drift-audit-rubric/data-model.md) — `drift-audit.json` schema + entity definitions
- [`specs/005-drift-audit-rubric/contracts/drift-audit-output.md`](../../specs/005-drift-audit-rubric/contracts/drift-audit-output.md) — consumer contract
- [`specs/005-drift-audit-rubric/quickstart.md`](../../specs/005-drift-audit-rubric/quickstart.md) — operator manual-audit walkthrough
- [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md) — session bundle consumer contract (where `drift-audit.json` lives)
- [`specs/003-pinned-rules-authoring/spec.md`](../../specs/003-pinned-rules-authoring/spec.md) — pinned rules (what the rubric audits against)
- [`design/poc.md`](../../design/poc.md) — H2 legibility observables + measurement model
- [`design/architecture.md`](../../design/architecture.md) — Layer 3 capability requirements
