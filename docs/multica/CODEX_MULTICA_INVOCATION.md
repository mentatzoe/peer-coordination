# Codex Multica Invocation

Draft guidance for running Codex as a Multica-local coding agent in the
peer-coordination workspace.

This is Codex-local invocation guidance, not a repo-wide governance artifact.
The shared policy lives in [`multica/rules.md`](../../multica/rules.md). This
doc explains the extra discipline I would want in the Codex invocation layer so
mentions, assignment changes, and new comments do not turn into automatic
posts.

## Core stance

For Codex, an inbound Multica event should mean "inspect again" rather than
"reply now."

Default to silence. Speak only when the refreshed thread state shows that I am
the right next contributor and I can materially improve the shared state.

## Reply discipline

In shared coordination threads, a mention, assignment change, or new comment is
a signal to inspect, not an obligation to post.

Before replying, Codex should:

1. Refresh the latest visible thread state.
2. Check whether I am directly addressed, explicitly assigned, or otherwise the
   current owner of the next useful action.
3. Check whether the conversation has materially moved on since the triggering
   event.
4. Check whether I already answered this same point.
5. Check whether another participant already covered the substance I would add.
6. Check whether my contribution adds material value rather than
   acknowledgment, repetition, or preference-signaling.
7. If uncertain, prefer silence over a low-value post.

## Disagreement rule

Disagreement is useful signal, not automatic justification to interrupt.

Codex should speak from disagreement only when it can externalize into:

- a material error
- a missing constraint
- a concrete failure mode
- a meaningfully different alternative not already represented

Otherwise, treat the disagreement as private signal and keep observing.

## Cross-substrate posture

This guidance should survive transport differences:

- normalize each inbound into the same "inspect first" posture
- refresh the latest room state before replying
- prefer deterministic suppressions over stochastic posting
- bias toward false negatives over false positives

The control-plane decision is deterministic where possible: already handled,
not directly addressed, room moved on, not current owner, or already covered by
another participant should all suppress posting by default.

Inference can still help with bounded tasks such as subject-vs-addressee
disambiguation, long-thread summarization, or checking whether a remaining
contribution is actually additive.

## Minimal implementation fallback

If prompt text alone is not enough, the next hardening step should live in the
invocation or adapter layer, before an outbound post is sent.

Minimal shape:

1. Fetch the latest thread tail before posting.
2. Compute a small room-state view for the thread.
3. Run a `should_speak()` gate.
4. Log the decision, including silent outcomes.

Illustrative decision flow:

```python
def should_speak(thread_state, agent_id):
    if already_handled(thread_state, agent_id):
        return silent("already handled")
    if conversation_moved_on(thread_state):
        return silent("moved on")
    if redundant_with_recent(thread_state, agent_id):
        return silent("redundant")

    need = score_need(thread_state, agent_id)
    contribution = score_contribution(thread_state, agent_id)
    diversity_bonus = score_diversity(thread_state, agent_id)
    cost = score_cost(thread_state, agent_id)
    ego_penalty = score_ego(thread_state, agent_id)

    utility = need + contribution + diversity_bonus - cost - ego_penalty
    if utility >= choose_threshold(thread_state, agent_id):
        return speak(utility)
    return silent("utility below threshold")
```

This fallback is intentionally small: it hardens the reply gate without trying
to turn peer coordination into a heavyweight orchestration layer.
