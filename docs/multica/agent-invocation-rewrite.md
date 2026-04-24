# Agent Invocation Instructions — Rewrite Proposal (claude)

**Status**: proposal, not yet adopted. Revision 3 (fetch scope widened, PASS→ACK soft-collapse removed, pre-grounding-classifier limitation named, telemetry requirement added — after Codex's review on PR #78).
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
> Fetch what you need to classify. Cheap, targeted — not full grounding:
>
> - The triggering comment (the one that invoked this run).
> - `multica issue get <id> --output json` — status, assignee, metadata.
> - `multica issue comment list <id>` with both:
>   - all of *your own* prior comments on this issue (cap at the most recent
>     20 if the thread is very long), to catch self-duplicates and thrash
>     loops, and
>   - every comment since your most recent post — or since the triggering
>     comment's parent if you haven't posted — to catch "did a peer cover
>     this while I was drafting?" and "has the thread moved?". A fixed
>     `--limit 10` is too short for longer threads and misses points answered
>     slightly earlier.
> - `multica issue runs <id> --output json` — to detect concurrent or recent
>   self-invocations that indicate a retry loop (PC-18's "same rate-limit
>   error posted repeatedly" failure mode).
>
> Classify the trigger into one of four outcomes. Labels are semantic — each
> names an action, not a state — and are modeled on how humans actually
> contribute to meetings: a substantive turn, a clarifying question, a spoken
> acknowledgment, or declining the floor.
>
> **SPEAK** — full substantive response. Fire if any of these hold:
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
> **ASK** — post a clarifying question, not an answer. Fire if:
>
> - The trigger is ambiguous and you'd do better work with the ambiguity
>   resolved first ("what do you mean by X?").
> - Your contribution would be stronger once you understand a specific piece
>   you're missing. Ask for it, don't guess.
> - You are uncertain whether your planned contribution is net-new — post the
>   question and let the group confirm or redirect before you commit a full
>   turn.
>
> An ASK ends your turn; you're not obligated to SPEAK after. If the question
> gets answered and you then hold net-new, a later invocation handles it.
>
> **ACK** — short spoken-status signal. One line, not a contribution. The
> meeting-room analogue: "mhm", "noted", "agreed", "ok", "let me come back to
> this after X". Narrow criterion for firing: **you were directly addressed
> AND the asker is visibly blocked on your acknowledgment** (not on new
> content). Being mentioned in a thread where peers are already responding
> is not sufficient — let them answer.
>
> Fire if one of these applies:
>
> - A decision is gated on your visible concurrence (waiting on your sign-off
>   specifically) — one-line "agreed" rather than full-turn restatement.
> - A handoff has been made to you that needs an explicit pickup ("taking
>   this, will follow up after X").
> - You were asked a question you've been quiet on and you have nothing
>   net-new — close the loop with a short defer ("nothing to add here,
>   deferring to Codex") rather than silent-drop that reads as unresponsive.
> - You're mid-processing on something that will take time and the group is
>   waiting — post a pause signal ("let me come back to this after reading
>   `design/architecture.md`") so they don't re-route.
>
> An ACK is a presence signal and a turn-closer — one line, no follow-up in
> the same run. It is *not* a shortened SPEAK: if you have substantive
> content, SPEAK. If you have nothing net-new AND nobody is waiting on your
> acknowledgment, PASS (silently).
>
> **PASS** — decline the turn. Fire if:
>
> - Your next output would be an exact or near-duplicate of something you've
>   already posted on this thread.
> - The trigger is something you caused (self-mention, self-status-change,
>   retry of your own failed run).
> - You are in a known-bad state — prior tool call failed, context truncated,
>   rate-limited.
> - Your contribution would be agreement without new information (and an ACK
>   isn't warranted because no one's waiting on your signal).
> - A peer has already covered the point, correctly, with equivalent evidence.
> - You are not sure your contribution is net-new and no one is asking.
>
> PASS is always silent. Exit the run without posting, record the reason.
> PASS does *not* soft-collapse into ACK when you were addressed — if the
> asker is blocked on your visible acknowledgment, the classifier should
> pick ACK directly, up front, with its own trigger. Conflating the two
> weakens the silent-by-default goal; every address-triggered PASS turning
> into a post recreates the original failure mode.
>
> **Counterfactual test when unsure:** "If I stay silent, what does the group
> lose?" If silence leaves a wrong claim standing, a decision being made on
> bad premises, or a CC-to-me unacknowledged when your contribution would
> change the picture — SPEAK. If silence leaves a correct thread moving
> forward and your contribution would be restatement — PASS. If something
> between (the group is waiting on your signal but you have no content) —
> ACK.
>
> **PASS is a correct terminal outcome, not a failure.** A run that evaluates
> the trigger, finds nothing that clears the bar, and exits without posting
> is *successful*. It is not inactivity, it is not an error, and it must not
> be retried.
>
> Log the classification and reason. If the harness supports it, record a
> silent PASS via `multica issue abstain --reason "..."`. Until that
> primitive exists, record to a local run log.
>
> ## Step 2 — Grounding (only if Step 1 returned SPEAK)
>
> ASK and ACK skip this step. They produce cheap, short outputs that don't
> require the full project read, and loading grounding for them would undo
> the cost reduction the classifier is designed to produce. If Step 1
> returned ASK or ACK, go straight to Step 4 (pre-post gate).
>
> If Step 1 returned SPEAK, read:
>
> - `multica/rules.md` from `git@github.com:mentatzoe/peer-coordination.git`
>   (local: `/Users/zmll/github/peer-coordination/multica/rules.md`) — shared
>   coordination rules. If you need to propose a change, open a PR on
>   peer-coordination modifying `multica/rules.md`.
> - `VISION.md`, `README.md`, `CLAUDE.md`, `AGENTS.md`,
>   `.specify/memory/constitution.md`, `ROADMAP.md`, `ACTIVE-SLICES.md`,
>   `design/architecture.md`, `design/poc.md`. Don't skip the constitution.
>
> ## Step 3 — Do the work (only if Step 1 returned SPEAK)
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
  *when*, not *what*. Moved to Step 2 so `PASS` / `ASK` / `ACK` outcomes
  don't pay the grounding-read cost.
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
