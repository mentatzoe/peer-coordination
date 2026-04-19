# Data Model: Drift-Audit Workflow

**Branch**: `008-drift-audit-workflow` | **Date**: 2026-04-20
**Input**: Phase 1 output. Workflow-level entities only. The `drift-audit.json` output schema itself is owned by spec 005 — this document references it rather than duplicating it.

## Relationship to spec 005's data model

The file [`specs/005-drift-audit-rubric/data-model.md`](../005-drift-audit-rubric/data-model.md) defines the schema + validation rules + guarantees for the `drift-audit.json` artifact: `Finding`, `Auditor`, `rubric_version`, `load_bearing_findings_count`, `verdict`, etc.

**This workflow consumes that schema unchanged.** Spec 008 does NOT redefine any field on `drift-audit.json`, does NOT add new schema fields, and does NOT re-specify validation rules on the output. If the output schema needs to evolve, that evolution is owned by spec 005, not this slice.

What this slice DOES own is a set of **workflow-level entities** that exist at the procedure layer — they live in commit messages, ACTIVE-SLICES references, or the session-bundle git history — not as fields on `drift-audit.json`.

---

## Workflow-level entities

### E1 — Audit Mode

**What it represents**: whether a given session's audit is produced by one auditor (single-auditor mode) or two (two-auditor mode, primary + cross-reviewer).

**Where it lives**: in the session's amend-commit message taxonomy, not on `drift-audit.json`. Spec 005's schema already captures the committed outcome (finalized findings + verdict); mode is workflow state and need not be re-materialized on the artifact.

**Values**: `single-auditor` | `two-auditor`

**Assignment rule**: two-auditor is the default for counted sessions (eligible for H1/H2 evidence per the KPI rollup slice when it lands). Single-auditor is acceptable for exploratory or pre-calibration sessions but surfaces as ineligible for counted evidence until upgraded (see R6).

**Transitions**:
- `single-auditor` → `two-auditor` via upgrade path (R6); old audit preserved in git history.
- Once `two-auditor` with a committed reconciled audit, the session does NOT transition back.

**Encoded in commit message**: `single-auditor` is the default (no token); `two-auditor-upgrade` is the explicit upgrade token.

---

### E2 — Reconciliation Outcome

**What it represents**: in two-auditor mode, the result of comparing the primary and cross-reviewer drafts against spec 005's FR-016 tolerance.

**Where it lives**: the amend-commit message taxonomy (bracket-token for arbitration; plain for within-tolerance).

**Values**:
- `agreed` — drafts within tolerance; reconciled `drift-audit.json` commits with no special token.
- `operator-arbitrated` — drafts diverged beyond tolerance; operator decides which findings stand; commit carries `[arbitrated]` token per R1.

**No third "blocked-pending-calibration" value** in this slice — the FR-008 resolution (Q1→C) is that arbitration is always sufficient to commit; the calibration signal is the discoverable `[arbitrated]` token, not a hold-state.

**Relationship to spec 005's `auditor` field**: when `operator-arbitrated`, the `auditor` field records both auditor identities + the operator identity as arbitrator, e.g. `"Zoe (arbitrating Dalgos/LLM-judge-v1)"`. Free-text string consistent with spec 005's schema.

---

### E3 — Rubric-Version Pin

**What it represents**: the exact commit SHA of `observations/drift-audits/RUBRIC.md` against which a given audit was produced.

**Where it lives**:
- Full 40-char SHA on `drift-audit.json.rubric_version` (owned by spec 005's schema; this slice only pins the value at audit start time).
- Short SHA (7–12 chars) in the amend commit message for human readability (per R4).

**Invariants**:
- MUST resolve to a committed state of `RUBRIC.md`. Uncommitted working-tree state is a halt condition (FR-002 / FR-018).
- MUST be pinned at **audit start time**, not at reconciliation time, so primary and cross-reviewer run against the same snapshot in two-auditor mode (FR-005).
- Once pinned on a committed `drift-audit.json`, the value never changes retroactively. A subsequent rubric calibration commit produces a new rubric version; re-audits against the new version are a re-audit (FR-011), not an update of the prior audit.

---

### E4 — Re-Audit Event

**What it represents**: a subsequent audit of a session bundle that has a prior committed `drift-audit.json`, producing a replacement artifact that supersedes the prior one.

**Where it lives**: session-bundle git history. The prior audit remains reconstructible via `git show <prior-commit>:observations/sessions/<session-id>/drift-audit.json`.

**Trigger paths** (per FR-012 Q2→C):
1. **Explicit operator request** — operator chooses a specific bundle for re-audit at any time.
2. **POC-exit rubric-version sweep** — at POC-exit synthesis time, bundles with `rubric_version` predating the synthesis-time RUBRIC.md HEAD are swept; per-bundle re-audit decision lies with the operator.

**Encoded in commit message**: `re-run, supersedes <old-rubric-sha>` in the taxonomy slot.

**Invariants**:
- Re-audit MUST produce a new, complete `drift-audit.json` (not a delta or patch).
- Prior audit MUST be discoverable via git history (no history rewriting).
- Re-audit MAY flip mode (single-auditor → two-auditor, via R6 upgrade path).
- Re-audit MAY change rubric version; the new artifact pins the new version.

---

### E5 — Arbitration Event

**What it represents**: a discrete operator-arbitrated reconciliation, discoverable by commit-message grep across Phase 3 session bundles.

**Where it lives**: session-bundle commit history, specifically amend commits carrying the `[arbitrated]` token in the subject line.

**Invariants**:
- MUST appear on the amend commit for the reconciled `drift-audit.json`, not on a separate commit.
- MUST be grep-discoverable with `git log --all --grep='\[arbitrated\]'` (plain-text match, no regex fragility).
- MUST NOT duplicate into `drift-audit.json` as a field (that would violate spec 005 scope).

**Counting semantics**:
- A sweep across counted Phase 3 sessions returns `N_arbitrations / N_counted_sessions`. Spec 005 §6.3 calibration trigger ("cross-auditor disagreement above tolerance") fires when this ratio is high enough to indicate rubric ambiguity — the threshold decision is operator-owned; this slice only guarantees the signal is visible.

---

### E6 — POC-Exit Sweep Artifact

**What it represents**: the one-shot enumeration at POC-exit synthesis of counted-session bundles and their pinned rubric versions compared against the synthesis-time RUBRIC.md HEAD.

**Where it lives**: location delegated to the POC-exit synthesis slice (not yet specced). This slice does NOT own the artifact's path, template, or rendering.

**Minimum content** (for the synthesis slice to satisfy this workflow's dependency):
- one row per counted session bundle
- each row records: `session_id`, pinned `rubric_version`, synthesis-time `RUBRIC.md` HEAD SHA, and whether the pinned version == HEAD (so stale bundles are visually identifiable)
- identifies stale bundles eligible for re-audit; does NOT mandate re-audit

**This slice's only requirement**: the underlying data (per-session `rubric_version` in `drift-audit.json`) is reliably available. That's guaranteed by FR-002 + FR-017 + spec 005's schema.

---

## Cross-references to other entities (owned elsewhere)

| Entity | Owner | Used by this workflow as |
|---|---|---|
| `drift-audit.json` schema (Finding, Auditor, verdict, etc.) | [spec 005 data-model](../005-drift-audit-rubric/data-model.md) | Output contract — this workflow produces conforming instances |
| Session Bundle (transcript + meta + interventions) | [spec 001](../001-session-bundle-skeleton/spec.md) | Input contract — this workflow consumes closed bundles |
| Pinned Rules snapshot | [spec 003](../003-pinned-rules-authoring/spec.md) | Consumed by the rubric (spec 005 §4 Step 1); this workflow reads `meta.json.pinned_rules_ref` to locate it |
| Transcript export format | [spec 006](../006-discord-transcript-export/spec.md) | Input — `transcript.md` inside the bundle is produced by spec 006 |
| Intervention-tag schema | Codex slice (not yet specced) | Consumed opaquely via `interventions.json` (R5) |
| RUBRIC.md versioning | [spec 005](../005-drift-audit-rubric/spec.md) + `observations/drift-audits/RUBRIC.md` | Version source of truth — this workflow pins to its git SHA at audit start |

---

## State transitions (workflow-level)

Session bundle audit state machine (per bundle):

```text
(closed bundle, no audit yet)
   │
   ├── single-auditor path ──→ single-auditor audit committed
   │        │
   │        └── upgrade path (R6) ──→ two-auditor audit committed (replaces)
   │
   └── two-auditor path
            │
            ├── agreed ──→ reconciled audit committed (no token)
            │
            └── diverged beyond tolerance ──→ operator-arbitrated ──→ reconciled audit committed ([arbitrated])

(any committed audit)
   │
   ├── rubric evolves ──→ re-audit via explicit request ──→ replacement committed (re-run, supersedes ...)
   │
   └── at POC-exit synthesis ──→ sweep flags as stale ──→ operator decides per-bundle
                                                            │
                                                            ├── re-audit ──→ replacement committed
                                                            │
                                                            └── accept as-is ──→ no action
```

No hidden states; every transition corresponds to a discoverable git commit.
