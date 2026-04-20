# Workflow Contracts: Drift-Audit Workflow

**Branch**: `008-drift-audit-workflow` | **Date**: 2026-04-20
**Input**: Phase 1 output. Workflow-level guarantees this slice owns. The output artifact (`drift-audit.json`) has its own contracts in [`specs/005-drift-audit-rubric/contracts/drift-audit-output.md`](../../005-drift-audit-rubric/contracts/drift-audit-output.md); this file does not duplicate those.

This document specifies the guarantees an auditor, a downstream consumer (KPI rollup / POC-exit synthesis), or a future implementer of a CLI/LLM automation path can rely on *about the workflow*, independent of the output artifact's internal structure.

---

## C1 — Input contract: the workflow consumes a closed session bundle

**Pre-conditions** (all MUST hold; any absence is a halt condition per FR-018):

1. `observations/sessions/<session-id>/transcript.md` exists and is non-empty (zero-turn transcripts still produce a valid `transcript.md` file per spec 006).
2. `observations/sessions/<session-id>/meta.json` exists and contains:
   - `session_id` (string, non-empty)
   - `pinned_rules_ref` (git SHA resolvable in the repo)
   - `closed_at` (RFC3339 UTC, non-null)
3. `observations/sessions/<session-id>/interventions.json` exists (may be empty array / object per intervention-tagging slice's rules; workflow treats shape as opaque per R5).
4. `observations/drift-audits/RUBRIC.md` resolves to a committed git SHA at audit start time (uncommitted working-tree state halts).

**Halt behavior**: if any pre-condition fails, the workflow MUST NOT produce a partial or placeholder `drift-audit.json`, MUST surface a non-silent failure naming the specific unmet condition (referencing FR-018), and MUST leave the bundle untouched so the upstream close step can be corrected.

---

## C2 — Output contract: committed `drift-audit.json` conforming to spec 005

**Post-conditions** (on successful audit commit):

1. `observations/sessions/<session-id>/drift-audit.json` exists, conforms to [spec 005's data model](../../005-drift-audit-rubric/data-model.md), and passes spec 005's output guarantees 1–5.
2. The file is committed via a session-bundle amend commit per spec 001 FR-014.
3. The commit message follows the format in C4.
4. `drift-audit.json.rubric_version` equals the full 40-char git SHA pinned at audit start time (E3).
5. `drift-audit.json.session_id` equals the bundle's `meta.json.session_id`.
6. `drift-audit.json.pinned_rules_ref` equals the bundle's `meta.json.pinned_rules_ref`.

Downstream consumers (KPI rollup, POC-exit synthesis) MAY rely on 1–6 without re-deriving them.

---

## C3 — Idempotency contract

**Guarantee**: running the workflow twice on the same bundle with the same rubric version and the same auditor(s) MUST produce `drift-audit.json` contents that differ **only in the `audited_at` timestamp**.

**What this means in practice**:
- Findings, severities, rationales, verdict, `load_bearing_findings_count`, `rubric_version`, `session_id`, `pinned_rules_ref`, and `auditor` are deterministic given identical inputs and identical auditor judgment.
- `audited_at` is the only legitimate variable across re-runs by the same auditor.
- Idempotency relies on spec 005's canonical-form serialization (R3). This workflow does NOT add a new normalization rule.

**What idempotency does NOT guarantee**:
- Two different auditors producing byte-identical output — that's what two-auditor reconciliation exists for (C5).
- Stability across rubric-version changes — that's what re-audit (C6) exists for.

---

## C4 — Amend-commit message format contract

All `drift-audit.json` commits MUST be amend commits on the session bundle and MUST follow this message format:

```
session bundle amend: <session-id> — drift-audit[ <taxonomy-token>] @ <rubric-short-sha>
```

Where `<taxonomy-token>` is one of:

| Token | When | Counting signal |
|---|---|---|
| *(absent)* | Normal within-tolerance audit (single-auditor OR two-auditor agreed) | — |
| `[arbitrated]` | Two-auditor mode, diverged beyond tolerance, operator-arbitrated | Counted in arbitration-rate for calibration signal |
| `two-auditor-upgrade` | Prior audit was single-auditor; new audit is two-auditor | Upgrades counted-eligibility |
| `re-run, supersedes <old-rubric-short-sha>` | Re-audit against an evolved rubric version | Replaces prior audit; old preserved in git history |

**Multiple tokens MAY appear** when an event is compound (e.g. `[arbitrated] re-run, supersedes abc1234` for an arbitrated re-audit).

**Body content** (optional but recommended): link to the governing discussion / PR if any, and a one-line rationale for arbitration or re-audit. Spec 005 §6.1 rubric-commit-message discipline inspires the rationale-in-body-not-subject convention.

---

## C5 — Two-auditor reconciliation contract

**Applies when**: the audit is run in two-auditor mode.

**Guarantees**:

1. Primary and cross-reviewer MUST produce independent drafts against the same pinned rubric version (E3).
2. Independence is either enforced (reviewer never sees primary's draft before finalizing) or **operator-attested** (reviewer finalizes before seeing, and the operator signs off on that independence in the commit body). The workflow does NOT enforce isolation; it requires attestation.
3. Reconciliation compares `load_bearing_findings_count` against spec 005 FR-016 tolerance (±1 for ≤200-turn sessions).
4. If within tolerance: commit reconciled `drift-audit.json`, no taxonomy token (C4).
5. If diverged: operator arbitrates per FR-008 + E2; commit carries `[arbitrated]` (C4).
6. In either case, the `auditor` field on `drift-audit.json` lists both primary and cross-reviewer identities `+`-combined per spec 005's hybrid convention (e.g. `zoe+llm:claude-opus`), free-text within spec 005's schema.

**Does NOT guarantee**:
- That the cross-reviewer's findings are merged mechanically — arbitration is a human judgment, not a union/intersection of sets.
- That a single-auditor audit can be silently promoted without the upgrade path (R6 / C4 taxonomy token).

---

## C6 — Re-audit contract

**Applies when**: a session bundle already has a committed `drift-audit.json` and a new audit is initiated against a different rubric version OR by different auditors.

**Guarantees**:

1. Re-audit produces a **complete new artifact**, not a delta (per E4).
2. The new commit **replaces** the prior `drift-audit.json` in the working tree; the prior version is preserved only in git history.
3. The commit message carries the `re-run, supersedes <old-rubric-short-sha>` taxonomy token (C4).
4. The prior audit is retrievable via `git show <prior-commit>:observations/sessions/<session-id>/drift-audit.json`.
5. Re-audit MAY be triggered via:
   - explicit operator request (per-bundle, any time), OR
   - POC-exit rubric-version sweep (operator decides per-bundle after sweep).
6. Re-audit MAY change mode (single-auditor → two-auditor) via the upgrade path (R6 / C4 `two-auditor-upgrade` token).

**Does NOT guarantee**:
- That re-audits are automatically invoked on rubric-version change — that's the continuous-sweep case explicitly out of scope (FR-012 Q2→C decision).
- That re-audits produce different findings from the prior audit — they MAY be identical (if the rubric change didn't affect the categorization), in which case the commit still lands for history discipline.

---

## C7 — Arbitration-event discovery contract

**Applies to**: downstream consumers (POC-exit synthesis, KPI rollup, calibration review) who want to count arbitration events across counted sessions.

**Guarantees**:

1. Every operator-arbitrated reconciliation produces a commit whose subject contains the literal token `[arbitrated]` (C4).
2. `git log --all --grep='\[arbitrated\]' --format='%H %s'` returns the full arbitration ledger with no additional tooling.
3. The ledger is append-only (amend commits add to history, never rewrite prior commits).
4. Per-session arbitration status is reconstructible from the session's amend-commit history alone.

---

## C8 — Consumer contract: KPI rollup / H2 evidence

**Applies to**: the downstream Phase 5 KPI rollup slice (not yet specced) and any H2 per-session reviewer.

**Guarantees**:

1. Reading `drift-audit.json.verdict` directly is the authoritative drift-specific input for the session's H2 judgment — consumers MUST NOT re-derive drift findings (spec 005 §8, reinforced by this workflow's FR-016).
2. The workflow's commit discipline (C4–C7) means every counted-session bundle has an audit trail the consumer can read without bundle-specific context — the bundle directory and its git history are self-contained.
3. Upgrades and re-audits (C6) mean the *current* `drift-audit.json` is always the consumer-relevant version; older versions are historical evidence only.

---

## Contract summary (compact)

- **C1 Input**: closed bundle with transcript + meta + interventions + resolvable pinned_rules_ref + committed RUBRIC.md SHA; halt on any absence.
- **C2 Output**: committed `drift-audit.json` conforming to spec 005, in the bundle directory, cross-referencing session_id + rubric_version + pinned_rules_ref.
- **C3 Idempotency**: byte-identical modulo `audited_at` given identical inputs + auditors.
- **C4 Commit format**: `session bundle amend: <session-id> — drift-audit[ <taxonomy-token>] @ <rubric-short-sha>`.
- **C5 Two-auditor**: independent drafts → tolerance check → agreed (no token) or arbitrated (`[arbitrated]`).
- **C6 Re-audit**: full-artifact replacement, history-preserving, token-tagged.
- **C7 Arbitration ledger**: grep-able `[arbitrated]` tokens, append-only.
- **C8 Consumer read**: `drift-audit.json.verdict` is authoritative; current bundle artifact is always the relevant version.
