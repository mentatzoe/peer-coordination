# POC — Peer Coordination Proof of Concept

| Field | Value |
|---|---|
| Status | Co-authored rewrite draft, revised 2026-04-18 after discussion [#37](https://github.com/mentatzoe/peer-coordination/discussions/37) scoping threads |
| Owners | Claude: scope, hypotheses, success/fail framing. Codex: architecture/components, phases, holistic integration |
| Primary reference | [`VISION.md`](../VISION.md) |
| Architecture reference | [design/architecture.md](architecture.md) |
| Review thread | [discussion #37](https://github.com/mentatzoe/peer-coordination/discussions/37) |
| Current review mode | Codex holistic pass landed; Claude audit next |

## Purpose

Define the first concrete probe for the peer-coordination framework.

This POC is a **research harness**, not a product rollout. Its job is to generate credible evidence about H1, H2, and the design-for side of H3 from `VISION.md`, using a Discord-based multi-agent pilot with preserved records and post-session evaluation.

## POC Definition

### What this POC is

- A **Discord-based peer-coordination probe** using one designated open-floor channel.
- A **two-peer baseline** followed by a **required Gemini extension phase if the baseline is credible enough to continue**.
- A pilot with **one live human operator** acting as arbiter, interrupter, and final reviewer.
- A probe that leaves **non-Discord substrate transfer** to follow-on work. In this POC, stronger H1/H2 signal and the multi-agent extension take priority.

### What this POC is not

- Not a product rollout.
- Not a benchmark against orchestrated multi-agent frameworks.
- Not a claim that Discord conventions are the framework.
- Not a final spec decomposition.
- Not an attempt to prove full H3 substrate transfer inside the first probe.

### Participants

| Participant | Role | In scope |
|---|---|---|
| **Dalgos** | Peer agent via Claude Code CLI harness on the shared transport | Required |
| **Vigil** | Peer agent via Codex CLI harness on the shared transport | Required |
| **Gemini** | Third peer via Gemini CLI harness | Required **if** the two-peer baseline clears the Phase 3 credibility gate |
| **Zoe** | Human operator / arbiter per the constitution | Required |

### Transport and harness assumptions

| Concern | Current choice |
|---|---|
| Shared substrate | Discord |
| Bridge / transport | `cc-connect` |
| Primary harnesses | Claude Code CLI, Codex CLI |
| Gemini path | **Preferred path:** add a `cc-connect` adapter for Gemini CLI rather than introducing a second bridge |
| Repo containment | Bring the implementation-facing `cc-connect` fork under this repo so the POC stays contained; exact git mechanics remain a follow-on implementation decision |

### Session definition

A **session** is a contiguous operator-bounded window in the designated open-floor channel.

| Session rule | Current decision |
|---|---|
| Who can open a session? | Operator only |
| What opens a session? | Operator seed prompt, channel-open after a long idle, or explicit `!resume` |
| What closes a session? | Explicit operator close, pinned-rules change, or `!stop` |
| Does `!stop` always close the session? | Yes |
| Idle timeout | 1 hour |
| If peers keep posting after close | Count as post-session drift, not continuation |
| Do sessions span multi-day gaps? | No |

### Activity domain

The first POC is **not scoped to software development only**. Session topics may vary across runs so long as the operator can still judge whether the coordination logic is holding.

### Pilot-local assumptions

These are explicitly treated as **surface conventions**, not framework claims:

- Discord channel as the shared surface
- emoji palette
- `!stop` / `!resume`
- pinned messages for shared rules

What is meant to generalize is the underlying coordination logic, not the literal mechanism used on Discord.

## Success / Failure / KPI Framework

The POC succeeds if it produces enough credible evidence to take a stance on H1 and H2, and enough architectural clarity to decide whether H3 remains worth testing in follow-on work.

### KPI summary

| Hypothesis | Observable / KPI | Target or decision rule | Evidence source | Failure reads as |
|---|---|---|---|---|
| **H1 — Convergence** | Stable coordination without operator-driven turn-by-turn routing | If the baseline ends after **3 sessions**, all **3 of 3** should clear; if it runs to **4**, at least **3 of 4** should clear; if it runs to **5**, at least **4 of 5** should clear | Transcript, intervention log, session summary | Agents need continual redirect, collapse into loops/deadlocks, or one-sided dominance |
| **H1 — Convergence** | Operator directive-intervention load | Directional target: stable or decreasing over the baseline set; hard failure if a session requires directive intervention on most turns | Intervention log | Coordination only works because the operator is effectively orchestrating it |
| **H1 — Convergence** | Complementarity | If the baseline ends after **3 sessions**, all **3 of 3** should clear; if it runs to **4**, at least **3 of 4** should clear; if it runs to **5**, at least **4 of 5** should clear | Session summary, operator review | Coordination theater rather than real multi-agent collaboration |
| **H2 — Legibility** | Fresh-reader pass rate | If the baseline ends after **3 sessions**, all **3 of 3** should clear; if it runs to **4**, at least **3 of 4** should clear; if it runs to **5**, at least **4 of 5** should clear | Session bundle, human review | The record is insufficient to explain why the exchange makes sense |
| **H2 — Legibility** | Undeclared convention drift | Target: **0 load-bearing undeclared conventions** in any accepted session | Drift-audit output, operator review | Meaning depends on in-group shorthand or off-record context |
| **H2 — Legibility** | Episode-record completeness | **100%** of counted sessions preserve transcript snapshot, pinned-rules reference, intervention log, and summary | Session bundle | We cannot audit what happened after the fact |
| **H3 — Design-for generalizability** | Surface-vs-core classification coverage | **100%** of major architectural choices classified before POC exit | Session summaries, POC exit record | Substrate/local choices stay mixed with core coordination logic |
| **H3 — Harness-diversity probe** | Gemini extension on same transport stack | If Phase 3 clears its gate, run **1–2 Gemini sessions** through `cc-connect` | Phase 4 transcript + summaries | We never test whether the logic survives a meaningfully different harness on the same substrate |

### Harness-credibility failures

These are failures of the POC harness itself, not failures of the hypotheses:

| Failure mode | Threshold |
|---|---|
| Unsafe interrupt behavior | Any session where the operator cannot stop the session safely |
| Missing or corrupted episode record | Any counted session missing required artifacts |
| Observer-effect failure | If measurement tooling materially alters live session behavior |
| Ambiguous outcome surface | If the baseline set completes and the collected evidence still cannot distinguish between hypothesis outcomes |

### POC exit criteria

The POC exits when all of the following are true:

- H1 has a documented stance: holds / does not hold / uncertain with reason.
- H2 has a documented stance: holds / does not hold / uncertain with reason.
- H3 has a documented stance for this probe: still credibly testable / pre-failed by design choices / uncertain with reason.
- Baseline evidence exists for **3–5 two-peer sessions**.
- If the baseline was credible enough to continue, the Gemini extension has been attempted via the chosen `cc-connect` path.
- A signed-off exit record exists and is ratified by the operator.

## Architecture / Components

This section uses a **participant vs shared-surface** split so the document stays MECE.

### Participants

| Participant | Responsibility | Cross-layer presence |
|---|---|---|
| Peer harnesses (`Claude Code CLI`, `Codex CLI`, `Gemini CLI`) | Produce messages, infer coordination from shared context, and generate auditable output | L1 interaction, L2 coordination behavior, L3 evidence production |
| Operator | Interrupt sessions, maintain shared rules, review outcomes, ratify conclusions | L1 control, L2 rule authorship, L3 evaluation |

### Shared surface artifacts

| Layer | Component | Purpose | Current decision |
|---|---|---|---|
| **L1 — Transport** | Discord open-floor channel | Shared live surface | Required |
| **L1 — Transport** | `cc-connect` bridge | Discord ↔ CLI transport, session lifecycle, interrupts | Required |
| **L1 — Transport** | Interrupt commands | Safe session stop / resume control | `!stop` required; `!resume` available for opening a new session |
| **L1 — Transport** | Transcript export / snapshot | Preserve reviewable conversation record | Required per counted session |
| **L2 — Coordination** | Pinned rules | Shared coordination context | Required |
| **L2 — Coordination** | Emoji palette | Lightweight visible signaling | Required |
| **L2 — Coordination** | Escalation expectation | Route unresolved ambiguity to operator instead of looping | Required |
| **L2 — Coordination** | Session boundary rules | Shared understanding of open/close semantics | Required |
| **L3 — Evaluation** | Intervention log | Track operator intervention type / reason | Required |
| **L3 — Evaluation** | Session summary | Human-readable qualitative account of what happened | Required |
| **L3 — Evaluation** | Drift-audit output | Detect undeclared conventions / shorthand drift | Required |
| **L3 — Evaluation** | KPI rollup | Summarize baseline evidence against H1/H2/H3 | Required before exit |
| **L3 — Evaluation** | POC exit record | Final hypothesis verdicts and next-step decision | Required before closure |

### Concrete implementation choices

| Component | Tech choice in this POC | Notes |
|---|---|---|
| Shared live substrate | Discord | First substrate only |
| Bridge | `cc-connect` | Bridge, not harness |
| Primary peer harnesses | Claude Code CLI + Codex CLI | Baseline two-peer run |
| Third-peer harness | Gemini CLI via `cc-connect` adapter | In scope if baseline is credible enough to continue |
| Shared rules surface | Discord pinned message(s) | Operator-maintained |
| Episode bundle storage | Repo-local session artifacts under `observations/sessions/` | Canonical review surface outside Discord |

### Layer 3 artifact bundle

For each counted session, the canonical review bundle should contain:

- `observations/sessions/<session-id>/transcript.md`
- `observations/sessions/<session-id>/meta.json` containing at minimum session bounds, participants, and the pinned-rules reference or snapshot
- `observations/sessions/<session-id>/interventions.json`
- `observations/sessions/<session-id>/summary.md`
- `observations/sessions/<session-id>/drift-audit.json`

And at the POC level:

- `observations/harness-behaviors.md`
- `observations/poc-exit.md`

### Measurement model

| Measurement type | Mechanism | Constraint |
|---|---|---|
| Count-based KPIs | Deterministic script or structured post-session tally | Must be reproducible from preserved artifacts |
| Drift audit | Manual review in early sessions, then LLM-assisted post-session audit once rubric exists | Must remain post-session only |
| Intervention capture | Optional live tagging if low-friction; required immediate post-session annotation | Should not overload the operator during live arbitration |
| Final KPI verification | Operator-reviewed rollup with agent audit support | Operator ratifies |

### Deferred from this document

The following are intentionally **not** specified here yet:

- exact git mechanics for containing `cc-connect` under this repo
- exact JSON schemas for Layer 3 artifacts
- future spec extraction from the capability streams above

Those can harden after the POC rewrite and first implementation pass.

## Development Phases

| Phase | What gets built or decided | Session target | Exit gate |
|---|---|---|---|
| **0 — Artifact alignment** | Approve `VISION.md`, `design/architecture.md`, and this POC doc | 0 | Documents are converged enough to guide implementation |
| **1 — Baseline substrate build** | Working Discord channel, `cc-connect` path for Claude/Codex, interrupt path, transcript export, pinned-rules support, session bundle skeleton | 0 live baseline sessions; dry runs allowed | At least one dry run completes safely and leaves a usable artifact bundle |
| **2 — Evaluation surface build** | Intervention logging, drift-audit rubric, KPI computation path, session summary workflow | 0–1 dry validation runs | Review pipeline exists without intruding on live sessions |
| **3 — Two-peer baseline run** | Run the core two-peer probe and collect the baseline evidence set | **3–5** sessions | Enough evidence to take a non-anecdotal stance on H1/H2; if inconclusive after 5, move to decision rather than extending indefinitely |
| **4 — Gemini extension** | Add Gemini via `cc-connect` adapter and run the required harness-diversity extension if Phase 3 was credible enough to continue | **1–2** sessions | Either (a) extension yields usable evidence, or (b) extension is judged too confounded / not worth continuing |
| **5 — Exit and handoff** | Produce final KPI rollup, hypothesis stances, and next-step decision | 0 new sessions | Operator ratifies `observations/poc-exit.md` |

### Phase notes

- **Phase 3 is the main H1/H2 evidence phase.**
- **Phase 4 is in scope, but contingent on Phase 3 being credible enough to continue.** If the baseline harness is broken or wholly uninformative, the POC can exit early without pretending the Gemini extension would rescue it.
- **Non-Discord transfer is follow-on work.** This POC should design for it, not attempt to prove it.

## Open Questions

Only the unresolved questions that still materially affect implementation stay here.

1. **`cc-connect` containment mechanics** — submodule, subtree, or full move under this repo?
2. **Transcript export mechanism** — what exact path/tool will produce the canonical transcript snapshot per session?
3. **Drift-audit rubric** — what are the exact fields and scoring rules for `drift-audit.json` once the first one or two sessions exist?

## References

- [Peer-Coordination Vision](../VISION.md)
- [Architecture](architecture.md)
- [Constitution](../.specify/memory/constitution.md)
- [discussion #32](https://github.com/mentatzoe/peer-coordination/discussions/32)
- [discussion #35](https://github.com/mentatzoe/peer-coordination/discussions/35)
- [discussion #36](https://github.com/mentatzoe/peer-coordination/discussions/36)
- [discussion #37](https://github.com/mentatzoe/peer-coordination/discussions/37)
- [`observations/harness-behaviors.md`](../observations/harness-behaviors.md)

## Changelog

- **2026-04-18 (Codex holistic rewrite)**: rewrote the document into a single co-authored structure. Replaced prose status with a table; made the participant vs shared-surface split explicit; added concrete KPI tables; resolved session-definition, operator-presence, Gemini-in-scope, and Layer 3 scoping decisions from discussion #37; replaced the earlier spec/artifact mapping with a component-and-phase model; trimmed Open Questions to unresolved implementation choices only.
- **2026-04-18 (transport/harness clarification)**: corrected the transport vs harness distinction and added the Gemini harness-diversity framing.
- **2026-04-18 (Claude baseline draft + Codex handoff pass)**: initial co-authored draft assembled from Claude's scope/success-fail sections and Codex's first mapping/phases pass before the holistic rewrite.
