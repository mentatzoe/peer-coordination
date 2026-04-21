# Phase 0 Research: KPI Rollup

**Feature**: KPI Rollup
**Branch**: `010-kpi-rollup`
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

Phase 0 consolidates the research decisions needed to harden the spec-010 plan. Each section names a decision, rationale, and the alternatives considered.

---

## 1. Inputs-hash algorithm for staleness detection

**Decision**: `kpi.json.inputs_hash` is a SHA-256 hex digest computed over a deterministic byte concatenation of the tally's input files. For JSON inputs (`interventions.json`, `drift-audit.json`, `fresh-reader-audit.json` when present), the file is parsed and re-dumped with `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')` to normalize whitespace and key ordering. For markdown/text inputs (`summary.md`, `transcript.md`, `meta.json` — meta.json included here as raw bytes because its whitespace signifies operator edits), raw bytes are used. Files are concatenated in a fixed order separated by a null byte (`\x00`), and the hash is computed over that concatenation.

**Rationale**:
- SHA-256 is stdlib (`hashlib.sha256`), fast enough for small files, and collision-free for this use.
- Canonicalizing JSON with sorted keys avoids false-positive staleness when a JSON re-save reorders keys or reflows whitespace (common when operators edit via different tools).
- Using raw bytes for markdown preserves operator intent (whitespace, trailing newlines) as semantically load-bearing.
- A fixed concatenation order with a null-byte separator makes the hash deterministic and prevents ambiguity between file boundaries.

**Alternatives considered**:
- **Per-file hash list stored as a JSON map** (e.g., `{"interventions.json": "<sha>", ...}`): more diffable, but adds surface area and complicates the staleness check without buying audit value beyond a single combined digest.
- **mtime-based staleness**: rejected — filesystem mtimes are unreliable across git clones and worktree copies, and can regress on re-checkouts.
- **BLAKE2 or xxh3**: not stdlib; SHA-256 is sufficient and available.

---

## 2. Per-run file timestamp format

**Decision**: Per-run rollup files use UTC ISO-8601 basic-format with a `Z` suffix and no colons: `poc-exit-YYYYMMDDTHHMMSSZ.md`. Example: `poc-exit-20260421T143022Z.md`. Seconds precision matches spec-001 FR-009's ISO-8601 minimum-precision convention.

**Rationale**:
- Basic format (no colons) is filesystem-safe on macOS and Linux; avoids shell-quoting surprises.
- UTC + `Z` eliminates timezone ambiguity for a governance-track artifact likely consumed across timezones.
- Lexical sorting of filenames yields chronological order — useful for `ls observations/poc-exit-*.md` in scripts and reviews.
- Seconds precision is sufficient for distinguishing any plausible back-to-back re-run cadence.

**Alternatives considered**:
- **Extended ISO-8601 with colons** (`2026-04-21T14:30:22Z`): readable but colon-sensitive on some filesystems; unnecessary risk.
- **Unix epoch seconds**: sorts the same way lexically (for any reasonable post-1970 window) but loses human readability entirely.
- **Millisecond precision**: overkill — re-runs cannot plausibly race inside the same second for this workflow.

---

## 3. `poc-exit.md` pointer mechanism

**Decision**: `observations/poc-exit.md` is a POSIX symlink (`os.symlink`) whose target is the most recent `poc-exit-<timestamp>.md` file in the same directory. On each successful rollup run, the symlink is removed (`os.unlink`) and re-created pointing to the newly written per-run file. The operation is sequenced to minimize the window where the symlink is broken.

**Rationale**:
- Symlinks are stdlib-accessible and git-trackable on macOS/Linux.
- `git` preserves symlinks as blobs pointing to the target path, so commits capture pointer state reliably.
- The alternative (a pointer markdown file) would either require an extra parse step for readers or duplicate content, defeating the per-run-files model's "no duplication" property.

**Alternatives considered**:
- **Pointer markdown file** (`poc-exit.md` contains `See [poc-exit-<latest>.md](...).`): platform-portable and handles the Windows case, but introduces a second source of truth (the pointer file's internal link vs. the filesystem presence of the target file).
- **Copy-latest**: rewrite `poc-exit.md` as a byte-copy of the latest per-run file on each run. Loses the pointer semantics (readers can't distinguish "this is the canonical file" from "this is a copy").
- **Git annotated tag per rollup run**: overkill; introduces a ref-level artifact for a file-level concern.

**Windows non-support rationale**: Technical Context in `plan.md` scopes the target platform to macOS/Linux; `cc-connect` and the operator workstations in scope run on those. Adding a Windows-compatible fallback before the concrete need emerges would be pre-optimization.

---

## 4. `per_session_clear` composite judgment

**Decision**: `kpi.json.per_session_clear` is a derived composite field; `kpi.json` additionally carries a `per_session_clear_breakdown` object with six sub-judgments drawn directly from `design/poc.md`'s "Per-session clear definitions" table:

| Sub-judgment | Source | Type |
|---|---|---|
| `h1_stable_coordination` | transcript.md turn-level analysis + interventions.json + summary.md | Composite: count-derivable and operator-authored |
| `h1_intervention_load` | interventions.json + transcript.md | Count-derivable: `directive_redirect_count / substantive_turn_count <= 0.5` |
| `h1_complementarity` | summary.md | Operator-authored narrative check (per poc.md: "session summary can point to at least one distinct useful contribution from each peer") |
| `h2_fresh_reader` | fresh-reader-audit.json | Direct: `verdict == "pass"` |
| `h2_drift` | drift-audit.json | Direct: drift-audit verdict indicates zero load-bearing undeclared conventions |
| `h2_episode_record` | bundle file set | Count-derivable: all spec-001 required files present and non-empty per FR-001..FR-011 |

Each sub-judgment is one of `cleared`, `not-cleared`, or `ambiguous`. The top-level `per_session_clear` is:
- `cleared` iff all applicable sub-judgments are `cleared`,
- `not-cleared` iff any sub-judgment is `not-cleared`,
- `ambiguous` otherwise (any sub-judgment is `ambiguous` and none are `not-cleared`).

**Rationale**:
- The poc.md clear definitions are already composite — tally should surface each sub-claim so reviewers can audit the judgment instead of trusting a single opaque label.
- Separating count-derivable sub-judgments from operator-authored ones makes the "which parts need human input?" question mechanically clear.
- Top-level precedence (`not-cleared` > `ambiguous` > `cleared`) avoids accidental upgrade: a single clear failure can't be outvoted by a few clears.

**Alternatives considered**:
- **Single flat `cleared | not-cleared | ambiguous` field** without breakdown: opaque; forces reviewers to re-derive the judgment to audit it.
- **Boolean per sub-judgment**: loses the `ambiguous` third state, which is load-bearing for the FR-013 split.
- **Numerical score (0–6)**: forces a totalization where the POC's framing is categorical.

---

## 5. Intervention-rate computation

**Decision**: `kpi.json.intervention_rate_per_turn` is `directive_redirect_count / substantive_turn_count`, where:
- `directive_redirect_count` = number of entries in `interventions.json` with `type == "directive_redirect"`
- `substantive_turn_count` = number of turns in `transcript.md` whose author is a peer (not the operator) — per the poc.md measurement model which focuses intervention load on peer-turns, not operator turns

When `substantive_turn_count == 0`, the rate is `null` and `kpi.json.zero_turn_session` is `true` per FR-009.

**Rationale**:
- `directive_redirect` is the type poc.md names as the intervention-load signal ("Coordination only works because the operator is effectively orchestrating it").
- Dividing by peer-turn count (not total turns) avoids deflating the rate by including operator turns in the denominator, which would misleadingly make a heavily operator-orchestrated session look light on intervention.
- Null with indicator (not zero) honors the "don't silently pretend the session cleared" rule — a zero-turn session has no intervention-load signal at all.

**Alternatives considered**:
- **Total intervention count / total turns**: dilutes the directive-redirect signal; poc.md is specifically about directive intervention load.
- **Per-type rate map**: useful for rollup surfacing but overloads the per-session-clear judgment.

---

## 6. Drift-audit placeholder detection

**Decision**: Tally detects the spec-001 placeholder by loading `drift-audit.json` as JSON and comparing the parsed object equality to `{"status": "pending-phase-2"}`. When the placeholder is detected, `per_session_clear_breakdown.h2_drift` is set to `ambiguous` with a human-readable `reason` field ("drift-audit.json is still the spec-001 Phase-2-pending placeholder; no audit has run yet"). `peer-session tally` does NOT fail; `peer-session rollup` treats this like any other `ambiguous` operator-judgment gap per FR-013.

**Rationale**:
- Exact-equality check on the parsed object avoids false positives from whitespace or key ordering.
- Ambiguous (not not-cleared) because the absence of drift evidence is not affirmative evidence of drift — it's evidence that the drift-audit workflow hasn't been run.
- Non-failure in tally keeps the tally re-runnable without operator intervention during pre-drift-audit phases.

**Alternatives considered**:
- **Hard-fail**: forces drift-audit to be run before any tally run. Too strict — operators may want to tally early for intervention-load visibility before completing the drift audit.
- **Silently treat placeholder as "cleared"**: explicitly rejected by FR-008.

---

## 7. Tally vs. missing `fresh-reader-audit.json`

**Decision**: `peer-session tally` does NOT require `fresh-reader-audit.json` to exist. When absent, tally still produces `kpi.json` but sets `per_session_clear_breakdown.h2_fresh_reader = "ambiguous"` with `reason: "fresh-reader-audit.json not yet authored"`. The top-level `per_session_clear` will therefore be `ambiguous` at minimum. When the operator later authors `fresh-reader-audit.json` (via `observations/kpi-rollup/WORKFLOW.md`), re-running tally refreshes `kpi.json` with the new verdict.

`peer-session rollup`, by contrast, DOES refuse to produce `poc-exit-<timestamp>.md` when any counted session is missing `fresh-reader-audit.json` — this is a hard data gap per FR-013.

**Rationale**:
- This split separates "bundle is complete per spec 001" (tally's hard gate — FR-006) from "counted-session-ready per spec 010" (rollup's hard gate).
- Operators can tally immediately after session close to see intervention-load and drift results before doing the fresh-reader work; they then author fresh-reader-audit.json and re-tally.
- Matches the FR-013 clarify-session resolution: hard data gaps refuse at rollup time; judgment gaps are visible per-session and roll up as ambiguous.

**Alternatives considered**:
- **Tally requires fresh-reader-audit.json**: forces a serialization of operator work that the split-flow above avoids.
- **Tally writes a partial `kpi.json` with missing fields**: contradicts FR-006's "fail loudly or produce complete output" stance.

---

## 8. Counted-session discovery in rollup

**Decision**: `peer-session rollup` discovers counted sessions by iterating `observations/sessions/` and accepting every subdirectory whose name does not start with `_` or `.`, then verifying each accepted directory contains the spec-001 required files AND a committed `kpi.json` AND a committed `fresh-reader-audit.json`. Session-id collisions (two sessions with the same `meta.json.session_id`) are detected by reading each `meta.json` and checking uniqueness; collision causes a refuse with exit code.

**Rationale**:
- Matches spec-001 FR-017's `_`-prefix and hidden-file exclusion convention.
- Requiring BOTH `kpi.json` and `fresh-reader-audit.json` as hard gates aligns with FR-013's "hard data gaps refuse" branch.
- Checking session-id uniqueness from `meta.json` (not directory name) catches the spec-001 FR-002 collision edge case even when directory names happen to differ.

**Alternatives considered**:
- **Accept any directory with `kpi.json`**: skips the bundle-completeness check, reintroducing the silent-partial-KPI risk.
- **Use directory name as session-id**: matches spec-001 FR-002's requirement but doesn't catch the case where an operator renames a directory without updating `meta.json.session_id`.

---

## 9. H1 decision-rule application

**Decision**: `peer-session rollup` counts sessions where `per_session_clear == "cleared"` (call this `C`) and sessions where `per_session_clear != "ambiguous"` (the "decidable" total `T`, i.e., counted sessions that are either cleared or not-cleared). The H1 pass/fail for each H1 KPI is computed against the decidable total `T`:
- `T == 3`: pass iff `C == 3`
- `T == 4`: pass iff `C >= 3`
- `T == 5`: pass iff `C >= 4`
- `T < 3` or `T > 5`: surface an "out-of-range" flag in `poc-exit-<timestamp>.md`; do NOT attempt to apply the decision rule.

Ambiguous sessions are enumerated in the draft-marked `poc-exit-<timestamp>.md` so the operator can resolve via the workflow.

**Rationale**:
- Directly mirrors poc.md's KPI summary table's decision rule.
- Using the "decidable total" (cleared + not-cleared only) avoids double-penalizing a session that is ambiguous — it's held out, not counted against.
- The out-of-range branch satisfies FR-014 explicitly.

**Alternatives considered**:
- **Apply the rule to the raw counted-session total regardless of ambiguity**: would unfairly penalize ambiguous sessions as "not-cleared" when the operator's judgment is still pending.
- **Refuse any rollup with ambiguous sessions**: too strict; contradicts FR-013's judgment-gap draft branch.

---

## 10. Testing approach

**Decision**: Unit tests cover each pure function in `tally`, `rollup`, `bundle_io`, and `per_session_clear` with synthetic session-bundle fixtures under `tests/peer_session/fixtures/`. Each spec-010 edge case has a dedicated fixture:
- `session_minimal/` — complete bundle, all fields populated, passes tally cleanly.
- `session_missing_fra/` — exercises the "tally tolerates, rollup refuses" split.
- `session_placeholder_drift/` — exercises the drift-audit placeholder branch.
- `session_zero_turns/` — exercises the divide-by-zero guard.
- `session_unclosed/` — exercises the `closed_at: null` refuse branch.
- `session_ambiguous/` — exercises composite per-session-clear rolling up to `ambiguous`.
- `rollup_counted_set/` — full set of 3 complete bundles for end-to-end rollup testing.

End-to-end CLI tests invoke `python3 -m unittest` over `tools.peer_session.cli.main` with temp-directory target paths, matching spec 007's test posture.

**Rationale**:
- Per the user memory note "Interactive CLIs require manual testing": unit tests are necessary but NOT sufficient. Manual smoke tests are documented in `quickstart.md` and expected before declaring the slice complete.
- Per the user memory note "Test-driven quality validation — tests must verify real behavior, not just pass": fixtures are actual directory trees on disk, not dict-level mocks, so the tests exercise real filesystem reads.
- Per the user memory note "Skip markers are shortcuts, not fixes": the fixture infrastructure is built on stdlib + `tempfile`, requiring no external services, so no skip-on-missing-infra shortcuts are needed.

**Alternatives considered**:
- **Mocked-filesystem unittest**: rejected — masks the actual IO path where most bugs live.
- **Integration-only tests**: would be slower per run and wouldn't isolate the per-function logic for easy debugging.
