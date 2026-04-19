# Session Bundles

Each directory under `observations/sessions/` is a **session bundle** — the canonical preserved record for one peer-coordination POC session, used for post-hoc review, KPI computation, and H1/H2 evaluation.

**Authoritative spec**: [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md).
**Design context**: [`design/poc.md`](../../design/poc.md) Layer 3 artifact bundle + Measurement model.

## Naming rule

Each session bundle lives at:

```
observations/sessions/<session-id>/
```

where `<session-id>` is:

- `YYYY-MM-DD-<short-slug>` — ISO date + hyphen + descriptive slug (lowercase kebab-case, ≤32 chars).
- If two sessions collide on date + slug, append `-NN` (two-digit counter): `2026-04-20-dry-run-one-02`.
- Directories prefixed with `_` or `.` are NOT session bundles (e.g., `_template/`). Downstream tooling (KPI rollup scripts, etc.) should filter those out.

Example: `2026-04-20-dry-run-one/`.

## Required files per bundle

Every committed session bundle must contain all five of:

| File | Purpose |
|---|---|
| `transcript.md` | Turn-by-turn conversation in chronological order, with at minimum timestamp + author per turn. Preferred source is Discord export via the native plugin's `fetch_messages`; re-authored markdown is an explicit fallback recorded in `meta.json.transcript_source`. |
| `meta.json` | Session metadata: `session_id`, `opened_at`, `closed_at`, `close_reason`, `participants`, `pinned_rules_ref`, `substrate`, `channel_id`, `transcript_source`. |
| `interventions.json` | Array of tagged operator interventions. Each entry has `at`, `type` (from the fixed taxonomy: `safety_stop`, `clarification`, `directive_redirect`, `drift_catch`, `close_or_resume`, `other`), `reason`, optional `target_turn`. Empty array is valid. |
| `summary.md` | Human-readable qualitative account: session goal, per-peer contribution, observed coordination patterns, notable drift, operator verdict on H1 stability / H1 complementarity / H2 fresh-reader KPIs per the POC's "Per-session clear definitions." |
| `drift-audit.json` | Output of the drift-audit rubric (rubric spec pending Phase 2). Placeholder `{"status": "pending-phase-2"}` is acceptable until that rubric lands. |

See [`_template/`](_template/) for copyable stubs of each file.

## Authoring discipline

- **One commit per session** when operationally feasible. All five required files land in one commit with message `session bundle: <session-id>`.
- **Streaming commits** during a long live session are allowed for operational reasons but SHOULD be squashed before the session is considered closed.
- **Corrections** after commit are follow-up commits (`session bundle amend: <session-id> — <reason>`). Never rewrite history.
- **Redaction** of unintended content is an amend commit marking the correction; the original stays in git history. Hard removal from history (e.g., BFG) is an operator-escalation event outside the normal bundle workflow.
- **No secrets**. Tokens, DMs, unrelated private content must not appear in a committed bundle.

## Creating a new session bundle

1. Copy `_template/` to `observations/sessions/<session-id>/` where `<session-id>` follows the naming rule above.
2. Fill `[FILL IN]` placeholders across the five files per the schemas documented in [`_template/README.md`](_template/README.md).
3. Commit per the authoring discipline above.
4. If corrections are needed later, amend with a follow-up commit (never rewrite history).

## Using a bundle for review

- **H1 intervention-rate** (count-based KPI): count entries in `interventions.json` by `type`; deterministic script can compute rate per turn.
- **H1 stability / H1 complementarity** (per-session clear-definitions): read `transcript.md` + `summary.md`; apply the per-KPI clear rules from `design/poc.md`.
- **H2 fresh-reader** (per-session clear-definitions): uninvolved human reviewer reads `transcript.md` + `meta.json` (for pinned-rules reference) + `summary.md`; reconstructs session goal, per-peer contribution, and resolution; operator judges materially correct.
- **Drift audit** (Phase 2+): `drift-audit.json` produced by the Phase 2 drift-audit workflow against `transcript.md` + pinned rules.
- **Fresh-agent pickup**: a new agent session can read `summary.md` + `interventions.json` and produce a next-step proposal without operator restitching. Direct test of the artifact-driven operating model.

## Related artifacts

- [`specs/001-session-bundle-skeleton/spec.md`](../../specs/001-session-bundle-skeleton/spec.md) — the authoritative spec.
- [`specs/001-session-bundle-skeleton/plan.md`](../../specs/001-session-bundle-skeleton/plan.md) — the implementation plan that produced this scaffolding.
- [`design/poc.md`](../../design/poc.md) — POC Layer 3 artifact bundle definition (parent authority).
- [`design/architecture.md`](../../design/architecture.md) — Layer 3 capabilities (evaluation of emergence and success).
- [`observations/harness-behaviors.md`](../harness-behaviors.md) — running cross-session field journal (separate from per-session bundles; tracks cross-cutting observations).
