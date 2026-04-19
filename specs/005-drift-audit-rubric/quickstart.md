# Quickstart: Drift-Audit Rubric

**Feature**: `005-drift-audit-rubric`
**Audience**: the operator (Zoe) and any cross-reviewing agent running a drift audit on a Phase 3 session.

## Manual audit walkthrough (Phase 2 → early Phase 3)

Run once per session bundle, post-session. Target ≤15 operator-minutes per session (SC-005).

### 1. Gather inputs

Open the session bundle:

```
observations/sessions/<session-id>/
├── transcript.md        # the source of truth for findings
├── meta.json            # holds pinned_rules_ref
├── interventions.json   # context only; drift-catch entries are hints
├── summary.md           # reviewer context
└── drift-audit.json     # you'll replace this placeholder with real content
```

Look up the rubric at the session's moment:

```bash
# Read the current rubric (for the current audit):
less observations/drift-audits/RUBRIC.md

# Or pin to a specific rubric version if the rubric has evolved since the session was audited:
git show <rubric_version_commit>:observations/drift-audits/RUBRIC.md
```

Pin the pinned-rules at the session's commit:

```bash
git show $(jq -r '.pinned_rules_ref' observations/sessions/<session-id>/meta.json):pinned-rules/current.md
```

### 2. Walk through RUBRIC.md's manual-audit checklist

The rubric walks you through each category in order:

1. `undeclared_emoji` — scan transcript for any emoji, check against the palette in the session's pinned rules
2. `undeclared_abbreviation` — scan for abbreviations / acronyms not defined in the pinned rules and not obvious from context
3. `private_shorthand` — scan for message patterns whose meaning only makes sense to peers in the session (per FR-010 uninvolved-reviewer test)
4. `hidden_channel_reference` — scan for references to content not in the transcript (e.g., "as discussed earlier" with no earlier mention)
5. `off_palette_load_bearing` — palette-emoji used with a meaning the pinned rules don't define
6. `other` — anything else drift-shaped

For each candidate, apply the severity rule (in RUBRIC.md):

- `info` — noticed, not load-bearing
- `warn` — possibly load-bearing; operator should decide
- `finding` — load-bearing drift confirmed

### 3. Author `drift-audit.json`

Replace the placeholder with actual content:

```json
{
  "rubric_version": "<current RUBRIC.md commit hash from `git log -1 --format=%H observations/drift-audits/RUBRIC.md`>",
  "session_id": "<matches meta.json.session_id>",
  "pinned_rules_ref": "<matches meta.json.pinned_rules_ref>",
  "audited_at": "<ISO-8601 now>",
  "audited_by": "manual",
  "auditor": "<your handle>",
  "findings": [
    {
      "category": "...",
      "severity": "...",
      "quote": "...",
      "turn_ref": "<timestamp from transcript.md>",
      "rationale": "..."
    }
  ],
  "load_bearing_findings_count": <integer, matches count of findings with severity: finding>,
  "verdict": "<derived per FR-007>"
}
```

If there are no findings at all: `"findings": []`, `"load_bearing_findings_count": 0`, `"verdict": "no_drift"`.

### 4. Commit

Per the session bundle authoring discipline (spec 001 FR-014), this is a bundle-amend commit:

```
session bundle amend: <session-id> — drift-audit
```

Or, if the original bundle commit didn't include a real `drift-audit.json` (placeholder only), replacing the placeholder is an amend.

## Mock audit against a synthetic transcript (Phase 2 gate validation)

Phase 2's exit gate per `design/poc.md` is:

> "draft review pipeline exists: intervention-tagging path works, the draft rubric runs end-to-end on a synthetic or prior transcript, and the workflow does not require live-session observation"

To validate the rubric pre-Phase-3:

1. Author a synthetic transcript — 20–40 turns of plausible peer exchange, deliberately including 1–2 drift patterns per category.
2. Pin it at a test `pinned_rules_ref`.
3. Walk the manual audit procedure against it.
4. Check: does the operator catch the drift patterns? Are the severities reasonable? Does the `verdict` match expectations?
5. If the rubric misses something obvious, commit a `drift-audit-rubric: <summary>` patch refining the procedure.

The synthetic transcript doesn't need to be committed to `observations/sessions/` — it's a test input. It can live in `observations/drift-audits/` or be discarded after the mock run.

## LLM-assisted audit (Phase 3 session 3+)

Once the rubric is calibrated (typically after 1–2 manual Phase 3 sessions), the LLM-judge path is:

1. Read the rubric's LLM-judge prompt template (in `RUBRIC.md`).
2. Fill template slots: transcript, pinned rules at session's commit, intervention log, any session-specific context.
3. Invoke the LLM-judge (exact model / tooling is an operator choice not specified here).
4. Read the LLM's output as candidate findings.
5. Operator ratifies each finding (keep / severity-adjust / drop) per FR-015.
6. Author `drift-audit.json` with `audited_by: "hybrid"` (operator + LLM) or `"llm_assisted"` (LLM alone, no operator review).

## Cross-auditor agreement check

Per FR-016:

1. Auditor A produces their `drift-audit.json`.
2. Auditor B (another operator, another agent, or hybrid) independently produces theirs.
3. Compare `load_bearing_findings_count`: difference of ±1 for a ≤200-turn session is acceptable agreement.
4. Larger divergence → rubric needs calibration. Commit `drift-audit-rubric: clarify <category>` patch and re-audit.

## Common pitfalls

- **Treating `interventions.json` as ground truth**: operator drift-catch tags are hints, not verified findings. Apply the rubric afresh; the intervention log just tells you where to look first.
- **Quoting paraphrase instead of exact text**: `Finding.quote` must be a substring of the transcript turn (data-model integrity check). Don't summarize.
- **Assigning verdict manually**: don't. Derive it from findings per FR-007. Otherwise the `load_bearing_findings_count` ↔ `verdict` consistency can break.
- **Running audit during live session**: don't (FR-011). Audit is post-session only; observer-effect concern.
- **Editing committed `drift-audit.json` without amend-commit**: follow spec 001 FR-014 amend discipline; never rewrite bundle history.

## Cross-references

- [`../spec.md`](../spec.md) — authoritative spec
- [`../data-model.md`](../data-model.md) — full schema for `drift-audit.json`
- [`../contracts/drift-audit-output.md`](../contracts/drift-audit-output.md) — consumer contract for downstream
- [`../../../observations/drift-audits/RUBRIC.md`](../../../observations/drift-audits/RUBRIC.md) — runtime rubric (authored in `/speckit.implement`)
- [`../../../specs/001-session-bundle-skeleton/spec.md`](../../../specs/001-session-bundle-skeleton/spec.md) — consumer contract: `drift-audit.json` placement
- [`../../../design/poc.md`](../../../design/poc.md) — H2 per-session clear-definition + measurement model
