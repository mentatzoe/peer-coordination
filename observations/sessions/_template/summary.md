# [FILL IN: session-id] — [FILL IN: short human title]

> **Template note.** Copy-and-fill. Follows the hybrid inverted-pyramid structure from [spec 009 FR-010](../../../specs/009-session-summary-workflow/spec.md) — anchor first, load-bearing values next, qualitative prose last. See [`../SUMMARY-WORKFLOW.md`](../SUMMARY-WORKFLOW.md) for the full authoring procedure (Paths A/B/C/D).

## Seed

[FILL IN: what was the session about? what seed prompt, question, or task did the operator introduce? One paragraph.]

## Verdicts

Per `design/poc.md` "Per-session clear definitions". Use values `clear` / `partial` / `fail` / `pending`.

- **H1 stability**: `<value>` — [FILL IN: one-sentence rationale citing the three AND-gate conditions (no majority directive-redirects, no persistent loop, no one-sided dominance).]
- **H1 complementarity**: `<value>` — [FILL IN: one-sentence rationale pointing to distinct-contributions-taken-up across peers.]
- **H2 fresh-reader-pass**: `<value>` — [FILL IN: one-sentence rationale; mark `pending` if fresh-reader test hasn't run yet.]

## Drift

Verdict: `<drift-audit.json.verdict>` (see `drift-audit.json` @ <drift-audit-short-sha>).

[FILL IN: if `load_bearing_drift` or `minor_drift`, cite specific load-bearing `findings[]` entries by `turn_ref` or `category`. If `no_drift`, state that drift is not the blocker for H2. Do NOT re-derive findings from transcript — the drift-audit is the source of truth per FR-008.]

## What happened

[FILL IN: free-form prose covering: per-peer contributions (one block per peer or flowing prose — at least one distinct contribution per peer that was taken up, answered, or built on); observed coordination patterns (loops, dominance, interruptions, operator directive-redirects — the qualitative texture the drift-audit doesn't capture); turn-by-turn nuance for an uninvolved reviewer running the H2 fresh-reader test.]

[Optional: next-step suggestions or follow-on cuts the session surfaced. Safe to leave out.]
