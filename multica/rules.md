# Multica channel rules — peer-coordination workspace

**Version**: 1.0 (2026-04-22)

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

## GitHub identity — authenticate as your own bot

Each agent has a dedicated GitHub App so issue comments, PRs, and pushes show up as that agent, not a shared human account. Before any `gh`/`git push` command in this repo, mint a scoped installation token:

```bash
eval "$(scripts/github-app-token-helper.sh "$PEER_COORD_AGENT_NAME")"
```

`PEER_COORD_AGENT_NAME` is pre-set in each agent's Multica env (claude→dalgos, codex→vigil, castor→castor, echo→echo). Tokens last 60 minutes — re-run the helper if a long task spans the boundary. hermes-minimax has no app assigned; if it needs to act on GitHub, escalate to a peer.

## Tactical comments — Multica only is fine

"Picking this up", "blocked on X", "handing off to Y" — stays in Multica. No GitHub mirror needed.

## Routing mechanics

- **"This needs Zoe"** → assign the Multica issue to `mentatzoe` with a comment naming the decision or info needed.
- **"This needs peer review"** → assign to the specific peer agent with a specific request.
- **"I need information from one peer"** → comment with a targeted question. One peer at a time.
- **"I'm picking this up"** → tactical Multica-only; status `in_progress` → `in_review` when done.
- No cascade-@-mentioning.

## The "is this for me?" check — before every reply

A new comment triggers every agent that's been active on an issue. Before replying:
1. Directly addressed to you (by name or assignee)?
2. Direct reply to your last comment asking you a question?
3. Advances work you actively own?

If none — **stay silent**. Narrow exception: substantive technical error you can refute with evidence. One correction, then stop.

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
