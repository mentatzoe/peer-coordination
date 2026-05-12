# spec-010 fixture bundles

Synthetic session bundles used by the `tally.py` / `rollup.py` / `per_session_clear.py` unit
tests. Each subdirectory is a real on-disk session bundle (per spec 001) crafted to exercise
one branch of the spec-010 tally and rollup contracts.

| Fixture | Purpose |
|---|---|
| `session_minimal/` | Complete cleared bundle — happy-path tally and rollup. |
| `session_missing_fra/` | Same as `session_minimal/` but no `fresh-reader-audit.json`. Tally tolerates; rollup refuses. |
| `session_placeholder_drift/` | `drift-audit.json` is the spec-001 placeholder. Tally succeeds, `h2_drift` is ambiguous. |
| `session_zero_turns/` | Transcript has no peer turns. Tally succeeds, `intervention_rate_per_turn` is null. |
| `session_unclosed/` | `meta.json.closed_at` is `null`. Tally refuses with exit 3. |
| `session_ambiguous/` | `fresh-reader-audit.json` verdict is `inconclusive`. Per-session-clear rolls up to ambiguous. |
| `session_bad_intervention/` | `interventions.json` has an unknown `type`. Tally refuses with exit 4. |
| `rollup_counted_set/` | Three complete bundles for end-to-end rollup tests. Tests generate `kpi.json` in a tempdir copy before invoking rollup. |

Fixture bundles are read-only on disk; tests copy them into a `tempfile.TemporaryDirectory`
before running tally or rollup so they can mutate files (and so symlink/pointer behavior is
exercised in an isolated worktree).
