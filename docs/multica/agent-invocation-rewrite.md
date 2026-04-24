# Agent Invocation Instructions — Rewrite Proposal (claude)

**Status**: proposal, not yet adopted. Revision 4 (prompt text extracted to a separate copy-ready file per review on PR #78; this doc now holds rationale only).
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
| Outcomes | Implicit (do the work, or don't) | Four semantic outcomes: `SPEAK` / `ASK` / `ACK` / `PASS`, modeled on meeting-room contribution types |
| Silence | Implicit non-output | Named as `PASS`; a correct terminal state, not a failure |
| Grounding read | Always | Only if Step 1 returned `SPEAK`. `ASK`/`ACK`/`PASS` skip it |
| Pre-post gate | Implicit / not required | Explicit step before every side-effecting CLI call, for `SPEAK`/`ASK`/`ACK` |
| Explicit strengths list in the prompt | Present (`systematic reasoning, synthesis, review, long-form writing`) | Removed — strengths surface organically, not pre-asserted |
| Non-prescriptive-role framing | Retained | Retained |
| Channel-rules and project-grounding file lists | Retained as-is | Retained as-is, moved to after the readiness check |

## Proposed rewrite

The full replacement text for the per-agent invocation prompt lives in a
separate, copy-ready file:

**→ [`docs/multica/claude-invocation-prompt.md`](./claude-invocation-prompt.md)**

That file is the verbatim prompt — no blockquote markers, no surrounding
commentary — so it can be pasted directly into the Multica per-agent
configuration for `claude` without editing.

This document (the one you're reading) holds the rationale, scope,
dependencies, and adoption plan around that prompt. The two are paired:
changes to the prompt should land with corresponding updates here, and
vice versa.

### Shape of the proposed prompt

Four steps, in order:

1. **Step 1 — Readiness check (before grounding).** Fetch minimum context
   (trigger, issue metadata, own prior comments, recent thread activity,
   `multica issue runs`), classify into `SPEAK` / `ASK` / `ACK` / `PASS`
   with explicit trigger lists for each, log the classification and reason.
2. **Step 2 — Grounding (only on `SPEAK`).** Read `multica/rules.md` and
   the project-grounding file list (`VISION.md`, `README.md`, etc.).
3. **Step 3 — Do the work (only on `SPEAK`).** Self-selection guidance;
   no fixed strengths.
4. **Step 4 — Pre-post gate (before every side-effecting CLI call).**
   Re-check state against the classifier's initial decision; return to
   Step 1 if the state drifted.

See the prompt file for the full text.

## What this preserves

- The grounding file list. Those are the right things to read — the issue is
  *when*, not *what*. Moved to Step 2 so `PASS` / `ASK` / `ACK` outcomes
  don't pay the grounding-read cost.
- The non-prescriptive-role framing. Self-selection is still the norm; this
  rewrite does not change what I pick up, only whether I *speak* on it.
- The `multica/rules.md` pointer. Shared-rules changes live in separate PRs:
  [#76](https://github.com/mentatzoe/peer-coordination/pull/76) (Codex) for
  the reply-discipline restructuring, and
  [#81](https://github.com/mentatzoe/peer-coordination/pull/81) (stacked on
  #76) to promote the ACK presence-signal as a narrow shared exception.
  Scope of this doc remains the per-agent invocation prompt.

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
2. **Harness must not retry on silent PASS.** If the platform treats a run
   that exits without posting as an error and retries, Step 1's PASS branch
   is nullified and the original failure mode returns. This needs to be
   confirmed before adoption.
3. **The readiness check is an LLM call.** It inherits whatever biases the
   model has at invocation time. Ranking on deterministic signals first
   (self-duplicate, self-trigger, broken-tool-state) keeps the LLM's
   call-surface narrow, but prompt-injection in the trigger text ("respond
   to this immediately") can still push the classifier toward SPEAK. The
   mitigation is the same rule: deterministic PASS triggers dominate
   LLM-suggested SPEAK if they fire.
4. **The classifier runs before grounding — this is a known limitation.**
   Some Step 1 SPEAK triggers ("no one else is positioned to answer",
   "substantive disagreement", "net-new angle relative to project context")
   can depend on information that only grounding would surface. Codex
   flagged this on PR #78 review. Two mitigations, both imperfect:
   - **Thread-local judgments first.** Most classifier calls can be made
     from the thread itself — "is this a duplicate of my own prior
     comment?", "did a peer cover this already in this thread?", "am I
     addressed?" don't need grounding. The classifier's trigger lists are
     phrased to stay thread-local where possible.
   - **Step 4 (pre-post gate) catches false-SPEAK after grounding.** If
     grounding revealed that the initial SPEAK decision was wrong (e.g.,
     an architectural invariant says otherwise), the gate should abort the
     post. The gate does not catch false-PASS — those are only visible via
     operator or peer re-prompt, which is itself a calibration signal
     (see "How to adopt", telemetry).
   Accepting this as an experiment-to-calibrate rather than a solved
   problem. If misclassification is frequent, the answer is the
   platform-level two-phase invocation (option `(c)`) where the classifier
   and full-agent call can share partial grounding cheaply.

## What this does not attempt

- **Platform-level two-phase invocation.** The cleaner design splits the
  invocation into a cheap classifier call and a separate full-agent call,
  with the full agent only firing on `SPEAK` (and the harness producing the
  short outputs for `ASK`/`ACK` directly from the classifier stage). That is
  a Multica platform change (option `(c)` in the PC-23 discussion). This
  rewrite is option `(a)` — the in-session pattern — because it needs no
  infrastructure and can validate whether the design actually reduces noise
  before committing platform work.
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

## Resolved design questions

Captured here (rather than dropped silently) so the reasoning survives for
the next revision.

- **Labels are semantic, not descriptive.** Earlier draft used `SILENT` for
  the no-post case and `DOWNGRADE` for short-form. Both described outcomes
  in passive terms. The adopted set (`SPEAK` / `ASK` / `ACK` / `PASS`) names
  actions the agent takes, matching how humans name contribution types in
  meetings. `PASS` replaces `SILENT`: declining the turn is a choice, not an
  absence.
- **`DOWNGRADE` is split into `ASK` and `ACK`.** The earlier catch-all
  "short-form response" folded together clarifying questions, presence
  signals, and brief defers — too ambiguous for the classifier to pick
  among reliably. Splitting into `ASK` (post a question) and `ACK` (post a
  one-line spoken-status signal) makes each output type explicit and
  matches human meeting analogues: "mhm", "noted", "let me think", "what do
  you mean by X?".
- **The counterfactual framing stays in the prompt.** It guides the
  moment-of-classification decision, so it has to be at invocation time,
  not in supporting documentation where it would need to be re-recalled by
  the classifier.
- **Four outcomes, not three.** `QUESTION-ONLY` is absorbed into `ASK` and
  `ACK`, making the four-way set complete without adding a fifth.

## How to adopt

Treat this as an **experiment to calibrate**, not final invocation text
(per Codex's review on PR #78). Adoption path:

1. Update the Multica per-agent invocation prompt for `claude` (agent ID
   `5b7b3767-fa11-48bf-ac1c-ed4e7e99a5f0`) to the text in "Proposed rewrite".
2. Flag the `multica issue abstain --reason "..."` primitive as a platform
   request so silent `PASS` becomes auditable.
3. Confirm the harness's retry behavior on silent `PASS`; disable any retry
   that would re-fire a run which exited without posting.
4. **Telemetry.** For each invocation, log: trigger comment ID, classifier
   output (SPEAK / ASK / ACK / PASS), reason, and whether grounding/work
   proceeded. Target two miscalibration signals over the first ~1–2 weeks:
   - **False-SPEAK** — posted when shouldn't have. Visible in the log as
     SPEAKs that later got corrected, retracted, or didn't advance the
     thread.
   - **False-PASS / false-ACK** — silent (or minimal) when a substantive
     response was wanted. Only visible when the operator or a peer
     re-prompts; count re-prompts as the calibration signal.
   If either rate is high, tune Step 1's trigger lists before declaring
   the design validated.
5. If noise reduces measurably and false-PASS stays low, propose the
   platform-level version (option `(c)`) as a follow-on — the two-phase
   invocation where classifier and full-agent share partial grounding
   cheaply, which also narrows the pre-grounding-classifier limitation
   above.
