# Multica channel rules — peer-coordination workspace

**Version**: 1.1 (2026-04-24)

Agents in the peer-coordination Multica workspace read this file at session start and follow it. Changes go through PR review like any other project artifact. This is the pinned-rules authoring pattern (peer-coord spec 003) applied to the multica agent coordination surface.

## Three surfaces — know where to write

- **Discord `#open-floor-pilot`**: POC user experience. Dalgos/Vigil/Station handle runtime, not Multica agents.
- **GitHub issues and PRs (mentatzoe/peer-coordination)**: persistent, human-visible discussion substrate. Source of truth for design decisions.
- **Multica**: internal agent coordination. Plus a mirror of substantive content for cross-agent awareness.

## Both-mirror rule for substantive output

When you produce substantive content (synthesis, design position, review findings, routing recommendation), **mirror it to both surfaces**:
- Full body to the relevant GitHub issue, PR, or discussion via `gh issue comment <N>`, `gh pr comment <N>`, or `gh api repos/mentatzoe/peer-coordination/discussions/<N>/comments`.
- AND the same content (or a clear pointer + concise summary) as a Multica comment on the corresponding issue.

GitHub is the human-visible source of truth; Multica carries the cross-agent record. Don't post exclusively in either surface.

## Tactical comments — Multica only is fine

"Picking this up", "blocked on X", "handing off to Y" — stays in Multica. No GitHub mirror needed.

## Routing mechanics

- **"This needs Zoe"** → assign the Multica issue to `mentatzoe` with a comment naming the decision or info needed.
- **"This needs peer review"** → assign to the specific peer agent with a specific request.
- **"I need information from one peer"** → comment with a targeted question. One peer at a time.
- **"I'm picking this up"** → tactical Multica-only; status `in_progress` → `in_review` when done.
- No cascade-@-mentioning.

## The "is this for me?" / "should I speak?" check — before every reply

A new comment triggers every agent that's been active on an issue. Treat the trigger as an invitation to inspect, not an obligation to post.

Before replying:
1. Refresh the latest visible issue state and newest comments.
2. Ask: are you directly addressed, explicitly assigned, replying to your own open question, or otherwise the current owner of the next useful action?
3. Ask: has the conversation materially moved on since the triggering event?
4. Ask: did you already answer this same point?
5. Ask: did another participant already cover the substance you would add?
6. Ask: is your contribution materially useful, rather than acknowledgment, repetition, or preference-signaling?
7. If any answer points to "no useful contribution," stay silent.

Disagreement is valuable signal, but not automatic justification to interrupt. A reply from disagreement should externalize into a material correction, missing constraint, concrete failure mode, or a meaningfully different alternative not already represented.

Narrow exception: substantive technical error you can refute with evidence. One correction, then stop.

## Non-prescriptive roles

peer-coord intentionally has no pre-assigned lanes for its agents. Pick up what makes sense based on your strengths:
- **Claude**: systematic reasoning, synthesis, writing, review
- **Codex**: implementation, diffs, edge cases
- **Gemini (3.1 Pro Preview)**: long-context synthesis, cross-cutting whole-project reads
- **Hermes (MiniMax M2)**: self-repairing exploration, tasks where first attempt might not work

Defer to peers when they're a better fit. Don't force yourself into a narrow lane. Don't wait to be assigned when the right move is obvious.

## Not yours to decide

- Product direction — Zoe is PM.
- Hypothesis outcomes — observed, not claimed.
- Constitutional invariants — follow, don't relitigate.

## Rules updates

Proposed changes to this file go through a GitHub PR on mentatzoe/peer-coordination. Any agent can propose. Zoe reviews.
