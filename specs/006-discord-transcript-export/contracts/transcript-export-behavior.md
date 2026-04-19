# Contract: Discord Transcript Export Behavior

**Feature**: `006-discord-transcript-export`
**Consumers**: operator producing session bundles, cross-reviewers reading
`transcript.md`, downstream bundle artifacts that reference transcript turns.

## Contract guarantees

### Guarantee 1 — Bundle-compatible transcript shape

A successful preferred export produces `observations/sessions/<session-id>/transcript.md`
in chronological order with author + timestamp per turn, compatible with spec
`001` FR-009.

### Guarantee 2 — Stable turn references

The rendered transcript preserves a unique canonical timestamp per turn, so
other bundle artifacts can reference turns without ambiguity.

### Guarantee 3 — Truthful provenance

The bundle metadata records `transcript_source` truthfully as `export`,
`reauthored`, or `hybrid`. The export path must not claim pure export when the
operator materially repaired the artifact.

### Guarantee 4 — Explicit failure

If the preferred export path cannot produce a trustworthy transcript, the
workflow fails explicitly and directs the operator to fallback rather than
silently writing an unreliable `export` transcript.

### Guarantee 5 — Session-window boundedness

The preferred export path targets the intended session window rather than
blindly dumping unrelated channel history into the bundle.

## Non-guarantees

- This slice does not guarantee perfect author naming or formatting parity with
  native Discord UI.
- This slice does not define intervention logging, summary generation, or
  drift-audit behavior.
- This slice does not make transcript export cross-platform.

## Consumer responsibilities

- The operator must verify that the exported or repaired transcript actually
  reflects the intended session window.
- Cross-reviewers should rely on `transcript_source` when judging transcript
  confidence.
- Downstream tools should treat duplicate or unresolved turn references as a
  bundle integrity failure, not something to guess through.
