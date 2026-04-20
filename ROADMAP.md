# Roadmap — Peer Coordination

| Field | Value |
|---|---|
| Status | Draft |
| Owner | Codex |
| Date | 2026-04-20 (refreshed by Claude to reflect PR #50/#52/#66 merges — spec 008 drift-audit workflow landed) |
| Primary inputs | [`VISION.md`](VISION.md), [`design/architecture.md`](design/architecture.md), [`design/poc.md`](design/poc.md) |
| Review thread | [discussion #39](https://github.com/mentatzoe/peer-coordination/discussions/39) |

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
- The roadmap names **stable area leads**. Task-level and per-session staffing updates live in [discussion #41](https://github.com/mentatzoe/peer-coordination/discussions/41), not in this document.

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

| Workstream | Kind | Derived from POC phase(s) | Status | Landed inputs | Missing outputs / decisions | Current owner |
|---|---|---|---|---|---|---|
| **Foundation artifacts** | Execution | 0 | Complete | `VISION.md`, `design/architecture.md`, `design/poc.md` | none inside this slice | Claude + Codex + Zoe |
| **Roadmap reset** | Maintenance | 0 | In progress | approved POC phases and artifact set | standalone roadmap artifact, review, closure | Codex |
| **Constitution cleanup** | Maintenance | adjacent maintenance | In progress | executive decision from discussion #32 | remove roadmap section from constitution and clean references | Claude |
| **Baseline substrate build** | Execution | 1 | In progress | session definition, transport/harness assumptions, L1/L2 requirements, contained `cc-connect/` workspace, pinned-rules authoring (spec 003), session-bundle skeleton (spec 001), Discord session controls (spec 004), transcript export (spec 006 merged via PR [#52](https://github.com/mentatzoe/peer-coordination/pull/52)) | session-bundle init CLI (spec 007, plan done), interrupt path | Codex (transport / substrate), Claude (session artifacts) |
| **Evaluation surface build** | Execution | 2 | In progress | draft drift-audit rubric (spec 005 landed via PR [#50](https://github.com/mentatzoe/peer-coordination/pull/50) + `observations/drift-audits/RUBRIC.md` v1), drift-audit workflow (spec 008 landed via PR [#66](https://github.com/mentatzoe/peer-coordination/pull/66) + `observations/drift-audits/WORKFLOW.md` + `COMMIT-TAXONOMY.md`) | intervention tagging mechanism, intervention log shape, KPI rollup logic / framing, session summary workflow | Claude (evaluation pipeline), Codex (schema / tagging), Zoe (summary UX design) |
| **Two-peer baseline run** | Execution | 3 | Blocked on 1–2 | baseline session count, H1/H2 evidence rules, operator model | runnable harness, preserved session bundles, completed baseline sessions | Zoe (operator), responder assigned per session |
| **Gemini extension** | Execution | 4 | Blocked on 3 | in-scope condition, preferred `cc-connect` adapter path | Gemini adapter decision and implementation, 1–2 extension sessions if baseline is credible | Gemini (adapter ownership after bootstrap), Codex (guidance), Zoe (dispatch) |
| **POC exit and handoff** | Execution | 5 | Blocked on 3–4 | exit criteria, required artifacts, hypothesis stance structure | KPI rollup, `observations/poc-exit.md`, operator ratification | Claude (first-pass synthesis), Codex (audit), Zoe (ratification) |

## What is still missing

The biggest missing pieces are not more design docs. They are implementation-facing artifacts and operational surfaces.

## Ownership and handover contracts

No single owner should quietly absorb the whole POC. Ownership in this roadmap
is meant to stay **slice-local** and **handoff-based**.

| Slice | Lead owner | Boundary | Handover contract |
|---|---|---|---|
| **Baseline substrate build** | Codex (transport / substrate), Claude (session artifacts) | Own the shared runtime surface only: bridge path, session controls, transcript export, pinned-rules support, and session-bundle skeleton. Does **not** own evaluation logic or hypothesis judgment. | Hand off a runnable dry-run-capable substrate to the Evaluation Surface and Two-Peer Baseline slices, with the required artifact outputs preserved. |
| **Evaluation surface build** | Claude (evaluation pipeline), Codex (schema / tagging), Zoe (summary UX design) | Own the review / measurement surfaces only: draft drift-audit rubric, intervention-tagging path, summary workflow, KPI computation path. Does **not** own transport or pilot-session execution. | Hand off a usable post-session review pipeline to the Two-Peer Baseline and POC Exit slices. |
| **Two-peer baseline run** | Zoe (operator), responder assigned per session | Own live session execution, operator intervention, and evidence capture for baseline sessions. Does **not** silently redesign the framework mid-run. | Hand off counted session bundles and operator observations to POC Exit / Handoff, and to Gemini Extension only if the credibility gate is met. |
| **Gemini extension** | Gemini (adapter ownership after bootstrap), Codex (guidance), Zoe (dispatch) | Own the incremental harness-diversity extension only if Phase 3 is credible enough to continue. Does **not** reopen already-settled baseline requirements. | Hand off extension-session bundles or a documented no-go / confounded-result decision to POC Exit / Handoff. |
| **POC exit and handoff** | Claude (first-pass synthesis), Codex (audit), Zoe (ratification) | Own final synthesis only: KPI rollup, hypothesis stances, next-step recommendation. Does **not** absorb unfinished implementation work back into the same slice. | Hand off `observations/poc-exit.md` and the resulting next-cut recommendation back into roadmap / spec planning. |

### Missing implementation-facing artifacts

| Needed artifact / deliverable | Why it is needed | Status |
|---|---|---|
| contained `cc-connect/` workspace | resolves where the probe implementation lives and how it is versioned against this repo | Landed |
| Session bundle skeleton under `observations/sessions/` | required before counted sessions can start | Landed (spec 001) |
| Pinned-rules authoring workflow | required before counted sessions can start | Landed (spec 003) |
| Discord session controls | required for operator-visible session open/close | Landed (spec 004) |
| Transcript export path | required for the canonical episode bundle | Landed (spec 006 merged via PR [#52](https://github.com/mentatzoe/peer-coordination/pull/52)) |
| Session-bundle init CLI | lets the operator materialize a bundle before the session starts | In progress (spec 007, plan complete — Codex owns) |
| Draft drift-audit rubric | required for Phase 2 to exit cleanly | Landed (spec 005 merged via PR [#50](https://github.com/mentatzoe/peer-coordination/pull/50) + `observations/drift-audits/RUBRIC.md` v1) |
| Drift-audit workflow | required to actually produce `drift-audit.json` from the rubric, first manually and later with LLM assistance | Landed (spec 008 merged via PR [#66](https://github.com/mentatzoe/peer-coordination/pull/66) + `observations/drift-audits/WORKFLOW.md` + `COMMIT-TAXONOMY.md` v1; LLM-assisted authoring deferred per FR-014 entry criteria) |
| Session-summary workflow | required so Phase 3 sessions produce a ratifiable post-session artifact | Open |
| Intervention tagging mechanism | required so the operator can capture intervention type/reason without ad hoc drift | Open |
| KPI rollup logic / framing | required for POC exit and hypothesis stance-taking | Open |

### Remaining staffing questions

| Slice | Current state |
|---|---|
| Gemini bootstrap path | Open: Gemini owns the adapter after bootstrap, but the initial bootstrap path still needs a concrete decision when Phase 4 approaches |
| Per-session responder assignment | Lives outside the roadmap; chosen by Zoe per session based on the slice currently under stress |

## Recommended next cuts

The next useful cuts should stay close to the roadmap and the POC phases:

1. Finish the remaining **Baseline substrate build** outputs on top of the landed `cc-connect/` workspace.
2. Cut the minimum implementation-facing artifact(s) needed for **Evaluation surface build**.
3. Only then start counted baseline sessions.

## Notes

- There are effectively **no active implementation specs on `main` yet** for the post-artifact phases. The roadmap is therefore mostly forward-planning, not back-cataloging.
- This is deliberate. The repo now has enough design convergence to cut the next specs and plans cleanly instead of guessing early.
