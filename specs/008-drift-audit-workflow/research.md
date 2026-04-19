# Research: Drift-Audit Workflow

**Branch**: `008-drift-audit-workflow` | **Date**: 2026-04-20
**Input**: Decisions owed for Phase 0, consolidating both spec-inline resolutions (FR-008, FR-012) and best-practice confirmations for commit-message, idempotency, and rubric-pinning conventions.

This slice's design space is mostly procedure + git convention, not technology choice. The two substantive ambiguities were resolved during `/speckit-specify` validation (operator-arbitrated + discoverable signal; re-audit via explicit request + POC-exit sweep). Research below consolidates the supporting rationale and pins the remaining operational conventions so `/speckit-plan`'s Phase 1 artifacts can reference decisions rather than re-derive them.

---

## R1 — Arbitration-signal commit token format

### Decision

The amend commit for an operator-arbitrated `drift-audit.json` MUST include the literal token `[arbitrated]` after the standard message prefix. Full format:

```
session bundle amend: <session-id> — drift-audit [arbitrated] @ <rubric-version-short-sha>
```

For non-arbitrated (within-tolerance or single-auditor) audits, the token is omitted:

```
session bundle amend: <session-id> — drift-audit @ <rubric-version-short-sha>
```

### Rationale

- **Grep-able with no tooling**: `git log --all --grep='\[arbitrated\]'` returns the arbitration ledger directly. A reviewer can count arbitrations across Phase 3 sessions in one command.
- **Readable in terminal and GitHub UI**: square-bracket convention matches how other repos flag commit taxonomy (e.g. `[breaking]`, `[wip]`).
- **Doesn't require a new field on `drift-audit.json`**: keeps spec 005's schema untouched — consistent with this slice's scope boundary.
- **Survives rebase / cherry-pick**: commit messages are retained across standard git operations; a `[arbitrated]` marker on an amend commit stays attached to the audit's history.
- **Does NOT rely on git trailers or git-notes**: both would add a second lookup surface; a bracketed token in the subject line is the cheapest legible convention.

### Alternatives considered

- **Separate `arbitration.json` sidecar** in the bundle — rejected: adds a second artifact to manage, and the audit's `auditor` field per FR-008 already records arbitration identity. Bracket token is a pointer, not duplicated state.
- **Git trailer `Arbitrated-By: <operator>`** — rejected: trailers are less discoverable (`git log --format=%B` needed), and GitHub UI doesn't surface them in the main commit list.
- **Prefix instead of suffix (`[arbitrated] session bundle amend: ...`)** — rejected: breaks the established `session bundle amend:` prefix that spec 001 FR-014 uses for bundle amend commits. Token placement preserves spec 001's prefix convention while adding a taxonomy marker.

---

## R2 — POC-exit rubric-version sweep shape

### Decision

The POC-exit rubric-version sweep is **one-shot, synthesis-triggered**. It produces a plain markdown artifact enumerating each counted-session bundle with its pinned `rubric_version` and the synthesis-time `RUBRIC.md` HEAD SHA. Location and exact template are **delegated to the POC-exit synthesis slice** (not yet specced). This slice requires only that:

1. the sweep be supported (i.e. the audit's `rubric_version` field is reliably pinned to a resolvable SHA — already guaranteed by FR-002 + FR-017),
2. re-audit on any swept bundle be invocable via the normal explicit-request path (FR-011 + FR-012a),
3. the workflow does NOT define continuous or periodic detection between sessions.

### Rationale

- **Bounded scope**: continuous detection would require a daemon / CI job / cron; POC staffing is too thin for that. The one-shot model puts the audit refresh question exactly where it matters (POC-exit synthesis) and nowhere else.
- **Delegation is honest**: the sweep artifact belongs to the POC-exit synthesis slice because that slice decides which bundles count and reads their verdicts. This slice's job is to ensure the workflow produces bundles sweep-eligible — not to own the sweep itself.
- **Aligns with spec 005's reproducibility rule**: "past audits remain valid against their own rubric version" is preserved; the sweep is advisory, not mandatory re-audit.

### Alternatives considered

- **Spec the sweep artifact shape in this slice** — rejected: would reopen scope into POC-exit synthesis concerns (which bundles count, how to decide re-audit yes/no, how to roll into KPI). Better delegated to the owning slice.
- **Mandatory re-audit of every counted bundle at POC-exit** — rejected: violates spec 005 §6.2 reproducibility principle and would mask early-Phase-3 rubric-calibration signal. Operator judgment per-bundle is the right granularity.
- **Continuous sweep (daemon / CI job)** — rejected: out of scope for POC, adds ops burden, and would conflict with spec 005 §6.4's "rubric changes between sessions, not during" rule if the daemon fired mid-session.

---

## R3 — Idempotency canonical form

### Decision

For FR-010 idempotency (same bundle + same rubric version + same auditor → byte-identical `drift-audit.json`, modulo timestamp), the workflow relies on spec 005's existing output-contract guarantees without adding a new canonical-form spec in this slice:

1. JSON key ordering follows spec 005's `data-model.md` canonical shape.
2. RFC3339 UTC timestamps with second precision (per spec 005's `audited_at` field).
3. `findings[]` is ordered by `turn_ref` ascending, then by `category` alphabetically — already specified in spec 005's guarantees.
4. `load_bearing_findings_count` is computed deterministically from `findings[]` (already spec 005).
5. `rubric_version` is the full commit SHA (40 chars), not short-form — spec 005's schema.

Only `audited_at` legitimately varies between re-runs by the same auditor on the same inputs.

### Rationale

- **No new canonical-form spec needed**: spec 005's data-model + output contract already pins the relevant determinism. FR-010's byte-identity claim is a consequence of spec 005's guarantees, not a new invariant.
- **Timestamp is the only legitimate variable**: FR-003 requires `audited_at` stamping, which changes per run. This is not a defect of idempotency; it's a property of "when did this audit happen."
- **Serialization discipline is operator-facing**: the author (operator or cross-reviewer) MUST use the schema-conforming serializer (manual authoring via text editor is acceptable; spec 005 `quickstart.md` walks through it).

### Alternatives considered

- **Re-spec a full canonical-form JSON normalization in this slice** — rejected: duplicates spec 005 and re-opens that spec's contract. This slice defers.
- **Add a hash field** (e.g. `audit_hash: <sha256 of canonical form>`) — rejected: introduces a new schema field (reopens spec 005); the amend-commit SHA already provides immutability at the git layer.

---

## R4 — Rubric-version SHA handling in commit messages vs artifact

### Decision

- **Commit message**: uses the **short SHA** (typically 7–12 chars) of `observations/drift-audits/RUBRIC.md` at audit start time for readability.
- **`drift-audit.json.rubric_version`**: uses the **full 40-char SHA** for reconstructibility.

Both MUST point to the same commit.

### Rationale

- Short SHA in commit message aligns with git's own log conventions and GitHub UI rendering.
- Full SHA in the artifact eliminates any ambiguity across repo forks or SHA collisions (exceedingly rare but not zero).
- Spec 005's `data-model.md` already specifies full SHA in the artifact; this decision only constrains the commit-message side.

### Alternatives considered

- **Full SHA in both** — rejected: commit messages become hard to read, and git-log UX is poor with 40-char tokens inline.
- **Short SHA in both** — rejected: short SHAs can collide across branches; the artifact is the evidence layer and needs the definitive pointer.

---

## R5 — Cross-slice intervention-tag shape — consumption model

### Decision

The workflow reads `interventions.json` **opaquely** — it passes the file through to the rubric procedure (spec 005 RUBRIC.md §4 Step 1) as context input without inspecting specific tag fields. If intervention-tag schema evolves (Codex slice lands later), this workflow does NOT require a matching update — the rubric's internal expectation of the tag shape is where any evolution would be absorbed.

### Rationale

- **Honors scope boundary**: spec explicitly defers intervention-tag semantics to the Codex slice.
- **Decouples workflow from tag evolution**: the workflow's surface is "rubric reads a bundle's `interventions.json`" — no specific tag-shape assumption at the workflow layer.
- **Forward-compatible**: whatever shape the intervention-tagging slice produces, the rubric consumes; the workflow's commit format and amend convention do not depend on tag content.

### Alternatives considered

- **Re-state expected tag fields in this slice** — rejected: duplicates the intervention-tagging slice's scope and creates a schema-sync liability.
- **Halt the workflow if `interventions.json` is missing or empty** — rejected: empty interventions is a valid session state (a session with zero interventions); the rubric procedure handles that case internally.

---

## R6 — Single-auditor → two-auditor upgrade path

### Decision

A session that initially lands a single-auditor audit MAY be upgraded to two-auditor by a later cross-reviewer pass. The upgrade runs the same re-audit path as FR-011: the new amend commit replaces the prior `drift-audit.json`, and the commit message explicitly records the upgrade:

```
session bundle amend: <session-id> — drift-audit two-auditor-upgrade @ <rubric-version-short-sha>
```

The original single-auditor audit remains accessible via git history. If the cross-reviewer disagrees beyond tolerance, the upgrade enters the FR-008 operator-arbitrated path.

### Rationale

- **Preserves counted-session eligibility**: early Phase 3 sessions may need to ship single-auditor (LLM judge not yet calibrated per spec 005 §7) and later upgrade. Without an upgrade path, those early sessions are stuck ineligible.
- **Uses existing primitives**: upgrade = re-audit with a new auditor identity and mode; no new commit format beyond the explicit token.
- **Visible ledger**: `two-auditor-upgrade` token parallels `[arbitrated]` — grep-able taxonomy of audit history.

### Alternatives considered

- **Upgrade by appending to the same `drift-audit.json`** — rejected: violates spec 005's output schema (findings array is a single pass per audit). Replacement with git-history preservation is cleaner.
- **Forbid upgrades** — rejected: would strand early-Phase-3 single-auditor sessions as permanently non-counted. Too rigid.

---

## Consolidated output

- **FR-008 arbitration signal**: `[arbitrated]` bracket-token in amend commit subject line.
- **FR-012 re-audit trigger**: explicit operator request (per-bundle, any time) + POC-exit synthesis sweep (one-shot, delegated artifact shape).
- **FR-010 idempotency**: inherits spec 005 data-model determinism; only `audited_at` legitimately varies.
- **Commit format**: `session bundle amend: <session-id> — drift-audit[ <taxonomy-token>] @ <rubric-short-sha>`, where `<taxonomy-token>` ∈ {absent, `[arbitrated]`, `two-auditor-upgrade`, `re-run, supersedes <old-sha>`}.
- **Rubric-version representation**: short SHA in commit, full SHA in artifact.
- **Intervention-tag shape**: consumed opaquely; no workflow-layer assumption.
- **Upgrade path**: single-auditor → two-auditor via re-audit, same artifact-replacement primitive as rubric-version re-audit.

All decisions above are reflected in `data-model.md`, `contracts/workflow-contracts.md`, and `quickstart.md` in Phase 1.
