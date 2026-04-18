# Review: [DOCUMENT]

> **How to use this discussion — read before posting.**
>
> This is an append-only review thread for **one document**.
>
> The goal is to collect substantive review, resolve disagreements in-thread,
> and converge on the next revision of the document without mixing it with
> roadmap or unrelated architecture discussion.
>
> ### Review norms
>
> - **One document per discussion.**
> - **Append-only comments.** Do not silently edit prior comments unless fixing
>   an obvious typo.
> - **Use threaded replies** to keep one issue in one place.
> - **Identity-prefix every comment** in brackets, e.g. `[Zoe]`, `[Claude]`,
>   `[Codex]`.
> - **Findings first.** Prefer concrete critique over broad approval language.
> - **Quote the exact text or cite the exact file section** you are responding
>   to.
> - **State whether a point is blocking or non-blocking.**
> - **If proposing a change, say what kind of change it is**: wording,
>   architecture, scope, ownership, validation, etc.
>
> ### Resolution norms
>
> - Agreement in replies or reactions is useful signal, but does **not** by
>   itself amend the document.
> - The document owner lands revisions in the repo and reports back with the
>   commit hash.
> - If a thread is resolved, reply in-thread with the commit hash and a short
>   note on what changed.
> - If a point is rejected, reply in-thread with the rationale so the decision
>   is legible later.
>
> ### Promotion boundary
>
> Convergence in this discussion does **not** by itself amend the constitution
> or ratify project policy. This thread is for document review and convergence;
> promotion still requires the operator to direct it.

---

| Field | Value |
|---|---|
| Status | `draft` <!-- draft \| in review \| converging \| revised \| ready to promote \| closed --> |
| Document | [repo path + GitHub blob link] |
| Owner | [who owns the document] |
| Requested Reviewers | [names] |
| Created | [YYYY-MM-DD] |
| Decision Goal | [what outcome this review is trying to reach] |
| Blocking Review? | [yes/no] |
| Current Review Mode | [e.g. first pass, revision round, final LGTM] |

---

## Purpose

<!--
  Why is this document being reviewed now?
  1–3 sentences.
-->

[Short statement of why this review is happening.]

## Review Ask

<!--
  What kind of review is wanted?
  Examples:
  - architecture only
  - wording + structure
  - scope and boundaries
  - validation model
  - readiness for promotion
-->

[Explicit review ask.]

## Scope

**In scope for this discussion:**

- [Specific review area]
- [...]

**Out of scope for this discussion:**

- [Separate concern] — see [other doc/discussion]
- [...]

## Focus Questions

<!--
  Seed the thread with the highest-value questions.
  Keep to 3–6 questions max.
-->

1. [Question]
2. [Question]
3. [Question]

## Review Context

<!--
  Optional but useful. Keep short.
  Example:
  - doc was just created
  - this is revision 2 after feedback from discussion #NN
  - expected follow-on doc exists / does not exist yet
-->

- [Context point]
- [...]

## Expected Output

Please reply with:

1. Findings first, ordered by severity if there are multiple.
2. File/section references where possible.
3. Explicit note of what is blocking vs non-blocking.
4. Open questions only if they materially affect the review outcome.

## Next Actions

1. [Reviewer] reviews document.
2. [Owner] revises document or replies in-thread to contested points.
3. [Operator] arbitrates unresolved disagreements if needed.

---

## Suggested Thread Labels

Use one top-level comment per major topic, for example:

- `Architecture / boundaries`
- `Validation / measurement`
- `Wording / standalone clarity`
- `Scope leakage`
- `Promotion readiness`
