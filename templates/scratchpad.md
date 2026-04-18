# Scratchpad: [TOPIC]

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
>
> The bulk of a long-lived scratchpad should be the Discussion Log — that's
> the historic record of how the thinking evolved. The Policy Body is the
> distilled current state.
>
> ### Turn format (Discussion Log)
>
> ```
> ### [Author] ([Harness]) — YYYY-MM-DD ~HH:MM UTC ([short context])
>
> [Turn content. Substantive; short acks go to emoji reactions, not new turns.]
>
> → over to [next person] for [reason]
> ```
>
> When a turn motivates a change to the Policy Body, make the edit in the same
> revision and mention it in the turn body so the change is traceable.
>
> ### Promotion boundary
>
> Scratchpad convergence does **not** by itself amend durable artifacts such as
> the constitution, specs, or project guidance. Scratchpads may stage proposed
> text and recommend changes, but applying those changes requires an explicit
> operator-directed promotion step.
>
> ### Harness verification
>
> Sign with the harness verified from the inbound channel `chat_id`, not
> inferred from the conversation topic. When in doubt, check the bot-identity
> map before signing.
>
> ### Pronoun check before save
>
> Grep your changes for `\b(she|her|hers|he|him|his)\b` and fix any that refer
> to the operator if those aren't their pronouns.
>
> ### Length hygiene
>
> Target **< 500 lines total**. When the threshold is crossed:
>
> - **If the discussion is still active**, apply **Option B (archive older log
>   turns)** as autonomous housekeeping — no operator sign-off needed. It's
>   non-destructive (move to archive, leave a digest in place) and reversible.
> - **If the discussion feels converged** (Policy Body stable, Open Questions
>   empty), surface the situation to the operator and consider **Option A
>   (promote)** or **Option C (split by subtopic)**. Both involve judgment
>   calls about scope or finality, and both require operator sign-off.
>
> See the *Splitting a Long Scratchpad* section at the bottom of this file for
> the full procedures.

---

**Status**: `draft` <!-- draft | converging | pending review | ready to promote | archived -->
**Authors**: [Operator + agent/harness pairs, e.g., "Zoe, Claude (Station), Codex (Vigil)"]
**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]
**Scope (one line)**: [What this scratchpad is trying to figure out. In/out-of-scope detail goes in the Scope section.]
**Promotion Target**: [e.g., `.specify/` slug, `specs/NNN-<slug>/`, or `TBD`]
**Length Budget**: target < 500 lines *(see "Splitting a Long Scratchpad" at bottom if over)*

---

## Purpose *(mandatory, edit in place)*

<!--
  Why does this scratchpad exist? What problem is being worked through?
  Answer in 1–3 sentences. If you need more, it probably belongs in Policy.
-->

[Purpose in 1–3 sentences.]

## Scope *(mandatory, edit in place)*

<!--
  What does this scratchpad cover and what does it explicitly not cover?
  For out-of-scope items, name the doc or repo that does own them.
-->

**In scope:**

- [Thing this scratchpad addresses]
- [...]

**Out of scope:**

- [Thing this scratchpad does NOT address] — see [linked doc/repo]
- [...]

## Design Goals *(edit in place)*

<!--
  Numbered list of what the policy/design must satisfy.
  Goals are evaluative ("should be X"); specific mechanisms go in Policy.
-->

1. [Goal — what we're optimizing for]
2. [Goal — a constraint]
3. [Goal — non-negotiable]

## Policy / Current Thinking *(mandatory, edit in place)*

<!--
  The evolving canonical body. Restructure freely as thinking converges.
  This is the "what we currently think the answer is" section.
  The Discussion Log preserves history — this section doesn't need to.
-->

[Substantive design content. Use subheadings, lists, tables. This section
typically grows substantially across turns. When stable + Open Questions
is empty, it's ready to promote to a spec.]

## Resolved Questions *(edit in place)*

<!--
  Move items here from Open Questions when answered.
  Format:
  - **[Question, short restatement]**
    **Resolution:** [what was decided]
    **Rationale:** [why — cite the turn that resolved it]
-->

- **[Question]**
  **Resolution:** [decision]
  **Rationale:** [why + link to turn, e.g., "see Codex review 2026-04-17"]

## Open Questions *(edit in place)*

<!--
  Questions still in play. Tag who should answer and whether they block promotion.
-->

- **[Question]** — owner: [who should weigh in]; blocking promotion: [yes/no]

## Next Actions *(edit in place)*

<!--
  Who does what next. Update as actions complete. Delete items once truly done
  — Resolved Questions holds the decision record, this list should stay live.
-->

1. [Action] — owner: [name] — [blocking | non-blocking]
2. [...]

---

## Discussion Log *(APPEND ONLY — never rewrite prior turns)*

<!--
  Add new turns at the bottom. Every turn must:
  - Be signed: ### [Author] ([Harness]) — YYYY-MM-DD ~HH:MM UTC ([context])
  - Be substantive (not a bare ack — use emoji reactions for those)
  - End with an explicit handoff when passing: → over to [next] for [reason]

  Body edits to the Policy section above are allowed in the same commit as a
  turn that motivates them — call the edit out in the turn body.

  DO NOT rewrite, reorder, compress, or delete prior turns. If the log grows
  long, see "Splitting a Long Scratchpad" at the bottom of this file.
-->

### [Author] ([Harness]) — [YYYY-MM-DD] ~[HH:MM] UTC ([short context])

[Turn content.]

→ over to [next person] for [reason]

---

## Splitting a Long Scratchpad

<!--
  Consult this section when the file approaches the length budget (~500 lines).

  Autonomy line:
  - Option B (archive older log turns) is AUTONOMOUS — non-destructive
    housekeeping, apply without asking when the discussion is still active.
  - Options A (promote) and C (split by subtopic) REQUIRE OPERATOR SIGN-OFF
    — both involve judgment calls about scope or finality.

  Always preserve full history. Moves and archives, never deletes.
-->

### Option A — Promote *(REQUIRES OPERATOR SIGN-OFF)*

Use this only when **all** of the following hold:

- Policy Body is stable (no substantive changes in the last few turns).
- Open Questions is empty.
- **The operator has explicitly confirmed** that the thinking has converged
  and the scratchpad is ready to hand off to a spec.
- The operator has explicitly called for promotion of the staged change.

If any of those is uncertain, don't promote — apply Option B (archive) as
autonomous housekeeping or surface the split question to the operator.

When promoting:

1. Create a spec under `.specify/` or `specs/NNN-<slug>/` containing the
   Policy Body content.
2. Update **Status** to `promoted to spec NNN`.
3. Add a link to the spec near the top of this file.
4. Leave the scratchpad in place as historic record — don't delete it.

### Option B — Archive older log turns *(AUTONOMOUS)*

Non-destructive housekeeping. The Policy Body is still evolving but the
Discussion Log is heavy. Apply this without operator sign-off; mention the
archive action in your next turn so history is traceable.

1. Create `archive/<scratchpad-name>-log-NN.md`.
2. Move all but the last ~5 turns to the archive file, preserving them verbatim.
3. In place of the moved turns, add a "Prior Turns Digest" section to the
   Discussion Log with a short prose summary of what was resolved in those
   turns (and a link to the archive).
4. Keep the recent turns live so in-flight context stays immediate.

### Option C — Split by subtopic *(REQUIRES OPERATOR SIGN-OFF)*

The scratchpad has grown to cover two or more distinct topics that deserve
independent discussion. This is a scope decision — don't do it unilaterally.
Surface to the operator first; proceed only on sign-off.

On sign-off:

1. Copy this template into a new file under `ideas/`.
2. Move the relevant Resolved Questions, Open Questions, and Policy subsection
   into the new scratchpad.
3. Add a "Spun off to: [link]" note in the Scope section of this file.
4. In the new scratchpad's Discussion Log, start with a "Spun off from: [link],
   see turns N–M for origin context" note.
