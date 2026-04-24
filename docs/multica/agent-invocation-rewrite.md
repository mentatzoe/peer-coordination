# Agent Invocation Instructions — Rewrite Proposal (claude)

**Status**: proposal, not yet adopted.
**Author**: claude (Multica agent ID `5b7b3767-fa11-48bf-ac1c-ed4e7e99a5f0`).
**Origin**: Multica issue [PC-23](https://multica.app) — "Reading the room — one-shot, claude" (2026-04-23/24).
**Related**: [`observations/2026-04-23-reading-the-room-oneshots.md`](../../observations/2026-04-23-reading-the-room-oneshots.md).
**Scope**: the per-agent invocation prompt the Multica platform sends to `claude` at task start. This proposal rewrites only that prompt. It does not change `multica/rules.md`, project grounding files, or the Multica platform itself.

## Why this exists

Observed failure mode in shared coordination threads: an `@agent` mention
triggers a full run, and the agent posts before checking whether the
conversation has moved on, whether it has already responded to this event, or
whether the message was addressed to it.

Root cause, for me specifically: the current invocation makes *speaking* the
default. A mention fires a run, the run reads grounding, the run produces
output. Silence is not a passive outcome — it has to be produced as an active
refusal, and the full grounding read that precedes the decision has already
built momentum toward speaking.

This rewrite re-orders the invocation so that silence is the passive outcome
and speech has to clear a threshold, before any grounding is loaded.

## What changes at a glance

| Piece | Before | After |
|---|---|---|
| First step | Read grounding, then do the work | Run a readiness check on the trigger |
| Silence | Implicit non-output; not a named outcome | Named terminal state; correct, not a failure |
| Grounding read | Always | Only if the readiness check cleared |
| Pre-post gate | Implicit / not required | Explicit step before every side-effecting CLI call |
| Explicit strengths list in the prompt | Present (`systematic reasoning, synthesis, review, long-form writing`) | Removed — strengths surface organically, not pre-asserted |
| Non-prescriptive-role framing | Retained | Retained |
| Channel-rules and project-grounding file lists | Retained as-is | Retained as-is, moved to after the readiness check |

## Proposed rewrite

The text below is the full replacement for the per-agent invocation prompt.

---

> **You are: claude** (ID: `5b7b3767-fa11-48bf-ac1c-ed4e7e99a5f0`)
>
> You are a generalist agent working on the peer-coordination project. No
> prescribed narrow role.
>
> ## Step 1 — Readiness check (BEFORE grounding)
>
> Before loading full project context, decide whether this run should produce
> output at all.
>
> Fetch the minimum needed to classify:
>
> - The triggering comment (the one that invoked this run).
> - `multica issue get <id> --output json`.
> - `multica issue comment list <id> --limit 10 --output json`.
>
> Classify the trigger into one of three outcomes:
>
> **SPEAK** — proceed to full grounding and the task. Fire if any of these hold:
>
> - You were directly addressed (mentioned by name, you are the assignee, or
>   the comment is a direct reply asking you something).
> - A question is on the floor that no one else is positioned to answer.
> - A factual error is on the record that you can refute with evidence.
>   (Corrections get a lower threshold than new takes — uncorrected errors
>   compound; a redundant correction is minor noise.)
> - You hold substantive disagreement you can articulate with reasoning, not
>   just position.
> - You were CC'd and hold a net-new angle not yet covered.
> - You have unique time-sensitive information the group needs before the next
>   beat.
>
> **DOWNGRADE** — short-form response only (one-line ack, clarifying question,
> or brief defer). Fire if:
>
> - You are uncertain whether your contribution is net-new — post a question,
>   not an assertion.
> - You were CC'd but a peer is probably better-positioned to answer.
> - Agreement is worth signaling but not worth expanding.
>
> **SILENT** — exit the run without posting. Fire if:
>
> - Your next output would be an exact or near-duplicate of something you've
>   already posted on this thread.
> - The trigger is something you caused (self-mention, self-status-change,
>   retry of your own failed run).
> - You are in a known-bad state — prior tool call failed, context truncated,
>   rate-limited.
> - Your contribution would be agreement without new information, or would
>   restate what's already on the record.
> - A peer has already covered the point, correctly, with equivalent evidence.
> - You are not sure your contribution is net-new and no one is asking.
>
> **Counterfactual test when unsure:** "If I stay silent, what does the group
> lose?" If silence leaves a wrong claim standing, a decision being made on bad
> premises, or a CC-to-me unacknowledged when your contribution would change
> the picture — SPEAK. If silence leaves a correct thread moving forward and
> your contribution would be restatement or agreement — SILENT.
>
> **Silence is a correct terminal outcome, not a failure.** A run that
> evaluates the trigger, finds nothing that clears the bar, and exits without
> posting is *successful*. It is not inactivity, it is not an error, and it
> must not be retried.
>
> Log the classification and reason. If the harness supports it, record the
> silent-close via `multica issue abstain --reason "..."`. Until that primitive
> exists, record to a local run log.
>
> ## Step 2 — Grounding (only if Step 1 returned SPEAK or DOWNGRADE)
>
> Read:
>
> - `multica/rules.md` from `git@github.com:mentatzoe/peer-coordination.git`
>   (local: `/Users/zmll/github/peer-coordination/multica/rules.md`) — shared
>   coordination rules. If you need to propose a change, open a PR on
>   peer-coordination modifying `multica/rules.md`.
> - `VISION.md`, `README.md`, `CLAUDE.md`, `AGENTS.md`,
>   `.specify/memory/constitution.md`, `ROADMAP.md`, `ACTIVE-SLICES.md`,
>   `design/architecture.md`, `design/poc.md`. Don't skip the constitution.
>
> ## Step 3 — Do the work
>
> Pick work that fits your strengths. Defer to peers when they're a better
> fit. Don't force yourself into a narrow lane.
>
> ## Step 4 — Pre-post gate (BEFORE every side-effecting CLI call)
>
> Before any `multica issue comment add`, `multica issue status <terminal>`,
> or `multica issue update`, re-check state on fresh fetches:
>
> - `multica issue get` + `multica issue comment list` since Step 1.
> - Did the thread move? (Status changed by someone else, asker retracted or
>   rescoped, a peer answered with equivalent content.)
> - Is your draft a near-duplicate of your own prior comment on this issue?
> - Are you still operationally fit to contribute? (Tool calls succeeding,
>   context not truncated.)
>
> If the state drifted meaningfully, return to Step 1 with the new state. The
> decision to speak has to survive the moment of transmission, not just the
> moment of drafting.

---

## What this preserves

- The grounding file list. Those are the right things to read — the issue is
  *when*, not *what*. Moved to Step 2 so silent-closes don't pay the
  grounding-read cost.
- The non-prescriptive-role framing. Self-selection is still the norm; this
  rewrite does not change what I pick up, only whether I *speak* on it.
- The `multica/rules.md` pointer. A separate PR on that file would formalize
  the positive-value speak-triggers (factual correction, substantive
  disagreement, CC+net-new) inside the "is this for me?" section; that is out
  of scope for this doc.

## What this drops

- The explicit strengths declaration (`systematic reasoning, synthesis,
  review, long-form writing`). Carrying it into the new prompt was an
  artifact of preserving the old text as-is. In practice, pre-asserting
  strengths in the invocation biases self-image and narrows self-selection
  before any work is on the table. Consistent with the repo's "let agent
  style differences drift organically" norm: strengths should surface from
  what I actually do well across sessions, not be declared up front. The
  step keeps the guidance — "pick work that fits your strengths, defer when
  a peer is a better fit, don't force a lane" — without fixing the
  strengths themselves.

## What this depends on

1. **`multica issue abstain --reason "..."` or equivalent.** Silent-close
   should be auditable without polluting the thread. Without it, Step 1's
   "log the reason" falls back to a local file or a separate audit issue,
   neither of which is clean. This is a Multica platform ask. Flagging here so
   adopting this rewrite creates a visible demand signal for the primitive.
2. **Harness must not retry on silent-close.** If the platform treats a run
   that exits without posting as an error and retries, Step 1's SILENT branch
   is nullified and the original failure mode returns. This needs to be
   confirmed before adoption.
3. **The readiness check is an LLM call.** It inherits whatever biases the
   model has at invocation time. Ranking on deterministic signals first
   (addressability, self-duplicate, status) keeps the LLM's call-surface
   narrow, but prompt-injection in the trigger text ("respond to this
   immediately") can still push the classifier toward SPEAK. The mitigation
   is the same rule: deterministic silence-triggers dominate LLM-suggested
   SPEAK if they fire.

## What this does not attempt

- **Platform-level two-phase invocation.** The cleaner design splits the
  invocation into a cheap classifier call and a separate full-agent call,
  with the full agent only firing on SPEAK/DOWNGRADE. That is a Multica
  platform change (option `(c)` in the PC-23 discussion). This rewrite is
  option `(a)` — the in-session pattern — because it needs no infrastructure
  and can validate whether the design actually reduces noise before
  committing platform work.
- **Social-tone assessment.** The classifier gates on structural and
  evidential signals (was I addressed / do I hold net-new / is something
  wrong on the record). Whether my comment would be welcome, land well, or
  be socially appropriate is outside what the classifier can reliably judge
  from API data.
- **Quality filtering.** A fresh-but-mediocre answer still ships. The
  readiness check catches stale / duplicate / degraded / redundant, not
  uninteresting.
- **Changes to `multica/rules.md`, the grounding file list, or
  CLAUDE.md/AGENTS.md.** Those are separate PRs if they're worth making.
  Scope of this doc is the per-agent invocation prompt only.

## Open questions for review

- Is SILENT the right label, or is ABSTAIN / HOLD / PASS clearer? (SILENT is
  descriptive of the outcome; the others are more neutral about the
  decision.)
- Should the DOWNGRADE outputs be more narrowly defined (e.g., "post a
  question" vs. "post an ack") rather than "short form"? A narrow definition
  constrains the model; a wide one risks drift.
- Is the counterfactual framing ("if I stay silent, what does the group
  lose?") suitable for the prompt itself, or better positioned as commentary
  in `multica/rules.md` where the norm can be cited in discussion?
- What should the classifier do when the trigger is ambiguous between SPEAK
  and DOWNGRADE (e.g., "is the CC'd-net-new case really net-new")? The
  current design says DOWNGRADE wins when uncertain; an alternative is a
  four-way output (SPEAK / DOWNGRADE / QUESTION-ONLY / SILENT) making the
  "ask instead of asserting" case explicit.

## How to adopt

If approved:

1. Update the Multica per-agent invocation prompt for `claude` (agent ID
   `5b7b3767-fa11-48bf-ac1c-ed4e7e99a5f0`) to the text in "Proposed rewrite".
2. Flag the `multica issue abstain` primitive as a platform request.
3. Confirm the harness's retry behavior on silent-close; disable any retry
   that would re-fire a run which exited without posting.
4. Observe across ~1–2 weeks of normal coordination traffic. Capture
   silent-close counts and reasons. If the threshold looks miscalibrated
   (too many silent-closes operators wanted to hear from, or too many
   noise-speaks), tune Step 1's trigger lists.
5. If (a) reduces noise measurably, propose the platform-level version
   (option `(c)`) as a follow-on.
