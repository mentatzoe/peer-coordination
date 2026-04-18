# Roadmap — Peer Coordination

| Field | Value |
|---|---|
| Status | Draft |
| Owner | Codex |
| Date | 2026-04-19 |
| Primary inputs | [`VISION.md`](VISION.md), [`design/architecture.md`](design/architecture.md), [`design/poc.md`](design/poc.md) |
| Review thread | TBD |

## Purpose

This document is the current source of truth for what comes next after the main design artifacts landed.

It uses the approved development phases in [`design/poc.md`](design/poc.md) as the sequencing backbone, but it does **not** copy them verbatim. Its job is to show:

- what is already landed
- what still needs to be built
- what is still underspecified
- who currently owns each chunk

## Roadmap posture

- This roadmap is a **planning artifact**, not a constitutional section.
- This roadmap is a **normalized work view**, not a restatement of the POC doc.
- This roadmap tracks real repo state. Right now, most of the work on `main` is design-level, not implementation-spec complete.
- Ownership should be explicit. Where no owner is confirmed yet, the roadmap says `Open`.

## Current state

The following foundation artifacts are landed:

- [`VISION.md`](VISION.md)
- [`design/architecture.md`](design/architecture.md)
- [`design/poc.md`](design/poc.md)
- research spikes in [`docs/research/`](docs/research/)

The following immediate maintenance work is in flight outside this roadmap artifact:

- constitution cleanup to remove the old roadmap section

The main gap is that the repo now has the **design and evaluation shape**, but not yet the implementation-facing specs / plans for actually running the first probe.

## Workstreams

| Workstream | Derived from POC phase(s) | Status | Landed inputs | Missing outputs / decisions | Current owner |
|---|---|---|---|---|---|
| **Foundation artifacts** | 0 | Complete | `VISION.md`, `design/architecture.md`, `design/poc.md` | none inside this slice | Claude + Codex + Zoe |
| **Roadmap reset** | 0 | In progress | approved POC phases and artifact set | standalone roadmap artifact, review, closure | Codex |
| **Constitution cleanup** | adjacent maintenance | In progress | executive decision from discussion #32 | remove roadmap section from constitution and clean references | Claude |
| **Baseline substrate build** | 1 | Not started | session definition, transport/harness assumptions, L1/L2 requirements | `cc-connect` containment decision, Discord channel binding, interrupt path, transcript export, pinned-rules support, session bundle skeleton | Open |
| **Evaluation surface build** | 2 | Not started | KPI framework, artifact bundle, intervention taxonomy, exit criteria | draft drift-audit rubric, intervention log shape, KPI computation path, session summary workflow | Open |
| **Two-peer baseline run** | 3 | Blocked on 1–2 | baseline session count, H1/H2 evidence rules, operator model | runnable harness, preserved session bundles, completed baseline sessions | Zoe + Open implementation support |
| **Gemini extension** | 4 | Blocked on 3 | in-scope condition, preferred `cc-connect` adapter path | Gemini adapter decision and implementation, 1–2 extension sessions if baseline is credible | Open |
| **POC exit and handoff** | 5 | Blocked on 3–4 | exit criteria, required artifacts, hypothesis stance structure | KPI rollup, `observations/poc-exit.md`, operator ratification | Zoe + Open analysis support |

## What is still missing

The biggest missing pieces are not more design docs. They are implementation-facing artifacts and operational surfaces.

### Missing implementation-facing artifacts

| Needed artifact / deliverable | Why it is needed | Status |
|---|---|---|
| `cc-connect` containment decision | determines where the probe implementation lives and how it is versioned against this repo | Open |
| Transcript export path | required for the canonical episode bundle | Open |
| Session bundle skeleton under `observations/sessions/` | required before counted sessions can start | Open |
| Draft drift-audit rubric | required for Phase 2 to exit cleanly | Open |
| KPI rollup path | required for POC exit and hypothesis stance-taking | Open |

### Missing ownership decisions

| Slice | Current state |
|---|---|
| Transport / bridge implementation | Open |
| Evaluation-surface implementation | Open |
| Session operations / runtime support | Zoe operates the pilot; implementation support still Open |

## Recommended next cuts

The next useful cuts should stay close to the roadmap and the POC phases:

1. Confirm where the runnable probe work lives relative to `cc-connect`.
2. Cut the minimum implementation-facing artifact(s) needed for **Baseline substrate build**.
3. Cut the minimum evaluation artifact(s) needed for **Evaluation surface build**.
4. Only then start counted baseline sessions.

## Notes

- There are effectively **no active implementation specs on `main` yet** for the post-artifact phases. The roadmap is therefore mostly forward-planning, not back-cataloging.
- This is deliberate. The repo now has enough design convergence to cut the next specs and plans cleanly instead of guessing early.
