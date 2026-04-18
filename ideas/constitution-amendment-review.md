# Scratchpad: Constitution Amendment Review

> **How to use this scratchpad — read before editing.**
>
> A scratchpad is a living design log shared between the operator and two or
> more agents. It has **two zones with different edit rules**.
>
> ### Zone 1 — Policy Body *(EDIT IN PLACE)*
>
> Everything from the metadata header through **Next Actions**. When consensus
> shifts, overwrite this content freely. Prior versions are **not** preserved
> here — the Discussion Log is the history.
>
> ### Zone 2 — Discussion Log *(APPEND ONLY)*
>
> Everything below the `## Discussion Log` heading. **Never** rewrite, reorder,
> or delete prior turns. Add new turns at the bottom, signed and dated.

---

**Status**: `draft`
**Authors**: Zoe, Claude (Station), Codex
**Created**: 2026-04-18
**Last Updated**: 2026-04-18
**Scope (one line)**: Decide whether the proposed `1.1.0` constitution amendment keeps the right governance/spec boundary.
**Promotion Target**: `.specify/memory/constitution.md`
**Length Budget**: target < 500 lines

---

## Purpose *(mandatory, edit in place)*

This scratchpad exists to resolve whether the current constitution amendment is
correctly constitutional in scope, or whether it pulls operational coordination
rules up out of the future Transport MVP / policy specs too early.

## Scope *(mandatory, edit in place)*

**In scope:**

- Whether Principle VI belongs in the constitution at all
- Whether the 7 coordination heuristics belong in the constitution or a follow-on spec
- Whether the Transport MVP roadmap language is too prescriptive for constitutional text
- What minimal amendment, if any, should land in the constitution now

**Out of scope:**

- Implementing any `cc-connect` transport behavior
- Rewriting the full Transport MVP spec here
- Re-opening settled constitutional principles unrelated to this amendment

## Design Goals *(edit in place)*

1. Preserve a clean boundary between governance and operational policy.
2. Make the constitution strong enough to guide future specs without becoming one.
3. Leave Claude and Codex with one concrete, reviewable path to resolution.

## Policy / Current Thinking *(mandatory, edit in place)*

### Current review position from Codex

Codex does **not** approve the amendment as currently written.

The blocking concern is abstraction level:

- A constitution should define durable governing principles.
- A spec should define operational heuristics and behavior rules.
- The current amendment appears to move several operational rules into the
  constitution:
  - the 7 coordination heuristics
  - the explicit "react-driven" loop-prevention choice
  - the specific prohibition on transport blocking inter-agent replies
- That seems to conflict with the prior review note in
  `ideas/peer-coordination.md`, which explicitly said those items were
  **correctly not in the constitution** and belonged in the Transport MVP Spec
  or a future heuristics spec.

### Narrowest plausible constitutional version

A narrower Principle VI could still be constitutional if it stays at the level
of governance, for example:

- multi-agent coordination should remain human-legible
- governance should prefer heuristic, operator-legible coordination over brittle
  protocolization where possible
- specific channel heuristics, ack behavior, and loop-management rules belong in
  follow-on specs

### Decision to make

Claude and Codex need to decide which of these is correct:

**Option A — Keep Principle VI, trim hard**

Keep only the constitutional idea:

coordination should remain heuristic, legible, and operator-centered rather than
over-protocolized.

**Option B — Move Principle VI out**

Remove Principle VI entirely from the constitution and keep the whole topic for
the Transport MVP Spec or a future coordination-policy spec.

**Option C — Keep Principle VI as written**

Accept that these heuristics are now load-bearing enough to be constitutional.

### Codex lean

Codex leans to **Option A**.

That preserves the useful constitutional insight without collapsing the
governance/spec boundary.

## Resolved Questions *(edit in place)*

- **Should Principle III's scratchpad language be expanded?**
  **Resolution:** Yes.
  **Rationale:** It now matches the scratchpad template materially better.

## Open Questions *(edit in place)*

- **Are the 7 coordination heuristics constitutional or operational?**
  — owner: Claude; blocking promotion: yes
- **Should "react-driven loop prevention" be a constitutional rule or only a
  Transport MVP design choice?**
  — owner: Claude; blocking promotion: yes
- **Does the roadmap section currently over-specify the Transport MVP from the
  constitutional layer?**
  — owner: Claude; blocking promotion: yes
- **Which option should replace the current amendment: A, B, or C?**
  — owner: Zoe + Claude + Codex; blocking promotion: yes

## Next Actions *(edit in place)*

1. Claude reviews the blocking concern against the current constitution text and
   the prior scratchpad note at `ideas/peer-coordination.md:503`.
   — owner: Claude — blocking
2. Claude states whether they agree that the amendment crossed the constitutional
   boundary, and if not, why not.
   — owner: Claude — blocking
3. Zoe chooses between trimming Principle VI, moving it to a follow-on spec, or
   keeping it as written after both reviews are on record.
   — owner: Zoe — blocking

---

## Discussion Log *(APPEND ONLY — never rewrite prior turns)*

### Codex (terminal) — 2026-04-18 ~00:27 UTC (constitution amendment review)

Reviewed the current `.specify/memory/constitution.md` amendment and found one
blocking issue before approval.

The issue is not the general idea behind the amendment; it is the layer it now
occupies. The amendment promotes the 7 coordination heuristics and the
react-driven loop-prevention choice into constitutional text. That appears to
conflict with the earlier alignment review in `ideas/peer-coordination.md`,
which explicitly said those items were correctly kept out of the constitution
and should live in the Transport MVP Spec or a future heuristics spec.

My current position is:

- expanding Principle III was a good amendment
- adding a narrower constitutional principle about human-legible,
  non-over-protocolized coordination could be correct
- embedding the operational heuristics themselves in the constitution is too far

Open question for Claude:

Do you think Principle VI can be salvaged by trimming it to the governance
principle only, or do you think the whole topic should stay out of the
constitution for now?

→ over to Claude for review of the abstraction boundary
