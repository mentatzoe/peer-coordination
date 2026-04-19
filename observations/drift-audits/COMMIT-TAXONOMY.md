# Commit-Message Taxonomy: Drift-Audit Amend Commits

**Runtime reference** — grep-able vocabulary for every amend commit that lands a `drift-audit.json` inside a session bundle. Derived from [spec 008 contract C4](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md) and [spec 001 FR-014](../../specs/001-session-bundle-skeleton/spec.md).

Every audit amend commit MUST follow this subject format:

```
session bundle amend: <session-id> — drift-audit[ <taxonomy-token>] @ <rubric-short-sha>
```

The taxonomy token slot is optional (absent for the default case) and taxonomy-tagged for any non-default case. Auditor identity does NOT appear in the subject — it lives on `drift-audit.json.auditor` per [spec 005 data-model](../../specs/005-drift-audit-rubric/data-model.md); put auditor detail or arbitration rationale in the commit *body* when helpful.

---

## Tokens

### 1. *(absent)* — default case

```
session bundle amend: 2026-05-01-first-dry-run — drift-audit @ abc1234
```

**Use when**: single-auditor audit, OR two-auditor audit where drafts agreed within spec 005 FR-016 tolerance (±1 on `load_bearing_findings_count` for ≤200-turn sessions).

**Discoverable by**: `git log -1 --format='%s' -- observations/sessions/<id>/drift-audit.json`

---

### 2. `[arbitrated]` — operator-arbitrated divergence

```
session bundle amend: 2026-05-01-first-dry-run — drift-audit [arbitrated] @ abc1234
```

**Use when**: two-auditor mode, drafts diverged beyond tolerance, operator reviewed both and committed the final audit (per [spec 008 FR-008](../../specs/008-drift-audit-workflow/spec.md) → operator arbitration keeps session counted-eligible AND emits a discoverable calibration signal).

**Discoverable by**: `git log --all --grep='\[arbitrated\]' --format='%H %s'` — this is the **arbitration ledger**. POC-exit synthesis and mid-POC calibration review count arbitration events across counted sessions to decide whether a rubric-calibration commit is owed per [spec 005 §6.3](../../specs/005-drift-audit-rubric/spec.md).

**Commit body recommendation**: name the primary + cross-reviewer identities and a one-line rationale for which findings the operator kept/dropped. Example:

```
session bundle amend: 2026-05-01-first-dry-run — drift-audit [arbitrated] @ abc1234

Operator arbitration. Primary=Zoe found 3 load-bearing findings;
cross=LLM-judge-v1 found 1. Arbitrated to 2 after dropping LLM's
false-positive on the pinned 🤔 emoji.
```

---

### 3. `two-auditor-upgrade` — single → two-auditor upgrade

```
session bundle amend: 2026-05-01-first-dry-run — drift-audit two-auditor-upgrade @ abc1234
```

**Use when**: a prior audit was single-auditor (Path A) and a cross-reviewer pass is now landing to make the session counted-eligible for H1/H2 evidence. Rubric version typically unchanged; if it also evolved, combine with token 4.

**Discoverable by**: `git log --all --grep='two-auditor-upgrade' --format='%H %s'` — useful for POC-exit synthesis to distinguish sessions that reached counted-eligibility via upgrade vs always-counted.

---

### 4. `re-run, supersedes <old-rubric-short-sha>` — rubric evolution

```
session bundle amend: 2026-05-01-first-dry-run — drift-audit re-run, supersedes abc1234 @ def5678
```

**Use when**: the rubric evolved (calibration commit on `RUBRIC.md`) and a past bundle's audit is being refreshed against the new version. The prior audit remains retrievable via `git show <prior-commit>:observations/sessions/<id>/drift-audit.json`.

**Discoverable by**: `git log --all --grep='supersedes' --format='%H %s'`

---

## Combining tokens

Multiple tokens MAY appear when an event is compound. Examples:

- **Arbitrated re-audit against evolved rubric**:
  ```
  session bundle amend: 2026-05-01-first-dry-run — drift-audit [arbitrated] re-run, supersedes abc1234 @ def5678
  ```
- **Upgrade to two-auditor AND rubric evolution**:
  ```
  session bundle amend: 2026-05-01-first-dry-run — drift-audit two-auditor-upgrade re-run, supersedes abc1234 @ def5678
  ```
- **Arbitrated upgrade + rubric evolution** (rare — all three happening together):
  ```
  session bundle amend: 2026-05-01-first-dry-run — drift-audit [arbitrated] two-auditor-upgrade re-run, supersedes abc1234 @ def5678
  ```

Token order convention: `[arbitrated]` first (bracket draws the eye), `two-auditor-upgrade` next, `re-run, supersedes ...` last.

---

## Grep reference card

```bash
# All drift-audit amends:
git log --all --grep='— drift-audit' --format='%H %s'

# Arbitration ledger (calibration signal):
git log --all --grep='\[arbitrated\]' --format='%H %s'

# Upgrade ledger:
git log --all --grep='two-auditor-upgrade' --format='%H %s'

# Re-audit ledger:
git log --all --grep='supersedes' --format='%H %s'

# For a specific session:
git log --all --format='%H %s' -- observations/sessions/<session-id>/drift-audit.json
```

---

## Cross-references

- [`WORKFLOW.md`](WORKFLOW.md) — the procedure that produces these commits
- [`specs/008-drift-audit-workflow/contracts/workflow-contracts.md`](../../specs/008-drift-audit-workflow/contracts/workflow-contracts.md) C4 — the authoritative contract this file documents
- [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md) FR-014 — the bundle-amend-commit convention this taxonomy extends
