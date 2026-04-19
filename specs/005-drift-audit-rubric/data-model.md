# Data Model: Drift-Audit Rubric (Phase 1)

**Feature**: `005-drift-audit-rubric`
**Date**: 2026-04-19
**Purpose**: Formal schema for `drift-audit.json` per session bundle + entity definitions extracted from `spec.md`.

## Entities

### `Drift-Audit Output`

The single JSON object that serves as one session's drift-audit artifact. Lives at `observations/sessions/<session-id>/drift-audit.json` per spec 001 FR-008. Produced once per session (per-session bundle); amendable via bundle-amend commits.

**JSON shape (happy path)**:

```json
{
  "rubric_version": "<commit hash of observations/drift-audits/RUBRIC.md at audit time>",
  "session_id": "<matches meta.json.session_id>",
  "pinned_rules_ref": "<matches meta.json.pinned_rules_ref>",
  "audited_at": "<ISO-8601 timestamp>",
  "audited_by": "manual" | "llm_assisted" | "hybrid",
  "auditor": "<handle>",
  "findings": [<Finding>, ...],
  "load_bearing_findings_count": <integer>,
  "verdict": "no_drift" | "minor_drift" | "load_bearing_drift"
}
```

**JSON shape (blocked / incomplete bundle)**:

```json
{
  "rubric_version": "<commit hash>",
  "status": "blocked",
  "reason": "<specific missing artifact, e.g., 'transcript.md absent'>"
}
```

**Validation rules**:

| Field | Required | Constraint |
|---|---|---|
| `rubric_version` | yes | commit hash string, OR inline snapshot object (for pre-rubric sessions) |
| `session_id` | yes (happy path) | MUST match containing bundle's `meta.json.session_id` |
| `pinned_rules_ref` | yes (happy path) | MUST match containing bundle's `meta.json.pinned_rules_ref` |
| `audited_at` | yes (happy path) | ISO-8601 with at least second precision |
| `audited_by` | yes (happy path) | enum: `manual`, `llm_assisted`, `hybrid` |
| `auditor` | yes (happy path) | handle string; operator handle, agent identifier (e.g., `llm:claude-opus`), or combined (`zoe+llm:claude-opus`) for hybrid |
| `findings` | yes (happy path) | array of `Finding` objects; empty array valid |
| `load_bearing_findings_count` | yes (happy path) | integer; MUST equal the count of `findings[]` entries with `severity: "finding"` (cross-check integrity) |
| `verdict` | yes (happy path) | deterministic per FR-007: `no_drift` iff no non-info findings; `minor_drift` iff only `warn` findings; `load_bearing_drift` iff any `finding` severity |
| `status` | yes (blocked path) | literal string `"blocked"` |
| `reason` | yes (blocked path) | non-empty string describing the specific missing artifact |

**State**: immutable once committed. Amendments are follow-up commits (`session bundle amend: <session-id> — drift-audit ...`).

### `Finding`

One instance of observed drift in a session. Enters the `findings[]` array in the `Drift-Audit Output`.

**JSON shape**:

```json
{
  "category": "undeclared_emoji" | "undeclared_abbreviation" | "private_shorthand" | "hidden_channel_reference" | "off_palette_load_bearing" | "other",
  "severity": "info" | "warn" | "finding",
  "quote": "<exact text from transcript.md>",
  "turn_ref": "<ISO-8601 timestamp of the referenced turn>",
  "rationale": "<why this is drift; plain-prose reviewer note>"
}
```

**Validation rules**:

| Field | Required | Constraint |
|---|---|---|
| `category` | yes | enum (see FR-004); exactly one value |
| `severity` | yes | enum: `info`, `warn`, `finding` |
| `quote` | yes | exact text from `transcript.md`; preserves drift evidence for reviewer |
| `turn_ref` | yes | ISO-8601 timestamp matching a turn in `transcript.md` (canonical turn key per spec 001 FR-009) |
| `rationale` | yes | plain-prose; ≤280 chars recommended for reviewability |

**Relationships**:

- `Finding.turn_ref` → `transcript.md` turn timestamp (MUST resolve to a turn in the session's preserved transcript)
- `Finding.quote` → substring of the turn at `turn_ref` (integrity check for auditor-diligence)
- Findings with `severity: finding` → counted in `Drift-Audit Output.load_bearing_findings_count`

### `Rubric`

The procedure + category definitions + severity rules that govern Finding production. Lives at `observations/drift-audits/RUBRIC.md`; versioned via git commits.

**Not a JSON entity** — prose document. Referenced by `Drift-Audit Output.rubric_version` (commit hash of `RUBRIC.md` at audit time).

**Content contract** (what `RUBRIC.md` MUST contain per FR-013 and the content-scaffolding work in `/speckit.implement`):

- category definitions (one section per category in the enum)
- severity definitions (with disambiguation guidance, e.g., how to tell `warn` from `finding`)
- verdict logic (restating FR-007)
- manual-audit checklist (for FR-008 operator procedure)
- LLM-judge prompt template (for FR-009 automated procedure)
- agreement-tolerance rule (for FR-016 cross-auditor review)

### `Auditor`

The actor producing a `Drift-Audit Output`. Not a JSON entity; represented in the output via `audited_by` + `auditor` fields.

**Kinds**:

- **Manual auditor** (`audited_by: "manual"`): human or agent applying the RUBRIC.md procedure by hand from bundle content.
- **LLM-assisted auditor** (`audited_by: "llm_assisted"`): LLM-as-judge with the RUBRIC.md prompt template, operator may or may not have ratified.
- **Hybrid auditor** (`audited_by: "hybrid"`): LLM output with operator overrides / ratifications. Captured per FR-015.

**Relationships**:

- On hybrid audits, per FR-015, operator override judgment wins; `auditor` field records both identities (e.g., `"zoe+llm:claude-opus"`).

## Enum reference

| Field | Enum |
|---|---|
| `Finding.category` | `undeclared_emoji`, `undeclared_abbreviation`, `private_shorthand`, `hidden_channel_reference`, `off_palette_load_bearing`, `other` |
| `Finding.severity` | `info`, `warn`, `finding` |
| `Drift-Audit Output.verdict` | `no_drift`, `minor_drift`, `load_bearing_drift` |
| `Drift-Audit Output.audited_by` | `manual`, `llm_assisted`, `hybrid` |
| `Drift-Audit Output.status` (blocked-path) | `blocked` |

## Invariants across the model

- **Verdict ↔ findings consistency**: the `verdict` string and `findings[]` contents must agree per the FR-007 derivation rule. A well-formed `drift-audit.json` cannot have `verdict: no_drift` alongside any non-info finding.
- **Rubric version reachability**: `rubric_version` commit hash must resolve to a reachable commit in `main` (not a dangling reference). If inline snapshot is used, the inline content must be non-empty.
- **Turn-ref integrity**: every `Finding.turn_ref` must resolve to a turn in the session's `transcript.md`; every `Finding.quote` must be a substring of that turn's content.
- **Schema stability**: this data model evolves through rubric-version commits; each `Drift-Audit Output` references the rubric version that produced it, so old audits remain valid against their own rubric.
