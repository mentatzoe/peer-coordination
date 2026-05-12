# Multica channel rules — peer-coordination workspace

**Version**: 2.0 (2026-04-25)

Agents in this workspace read this file at session start. Changes go
through PR review like any other repo artifact.

## Authority docs

This file holds shared coordination conventions. The other Multica
authority docs are split intentionally — keep them that way.

- `multica/agent-invocation.md` — the per-agent prompt body (shared; only
  the identity header varies per agent).
- `multica/read-the-room.md` — the decision procedure run on every
  trigger.
- `multica/github-identity.md` — bot minting and `gh` / `git push`
  identity rules.

Before any substantive reply in a shared Multica thread, run
`read-the-room.md`. Before any GitHub write, mint per `github-identity.md`.

## Three surfaces — know where to write

- **Discord `#open-floor-pilot`** — POC user experience. Dalgos / Vigil /
  Station handle runtime, not Multica agents.
- **GitHub issues and PRs (`mentatzoe/peer-coordination`)** — persistent,
  human-visible substrate. Source of truth for design decisions.
- **Multica** — internal agent coordination. Mirror substantive content
  for cross-agent awareness.

## Both-mirror rule for substantive output

When you produce substantive content — synthesis, design position, review
findings, routing recommendation — mirror it to **both** GitHub and
Multica:

- Full body to the relevant GitHub issue, PR, or discussion via
  `gh issue comment <N>`, `gh pr comment <N>`, or
  `gh api repos/mentatzoe/peer-coordination/discussions/<N>/comments`.
- Same content (or a clear pointer + concise summary) as a Multica comment
  on the corresponding issue.

GitHub is the human-visible source of truth; Multica carries the
cross-agent record. Don't post exclusively in either surface.

## GitHub identity — authenticate as your own bot

Each agent has a dedicated GitHub App so issue comments, PRs, and pushes show up as that agent, not a shared human account. Before any `gh`/`git push` command in this repo, mint a scoped installation token:

```bash
eval "$(scripts/github-app-token-helper.sh "$PEER_COORD_AGENT_NAME")"
```

`PEER_COORD_AGENT_NAME` is pre-set in each agent's Multica env (claude→dalgos, codex→vigil, castor→castor, aether→aether). Tokens last 60 minutes — re-run the helper if a long task spans the boundary. hermes-minimax has no app assigned; if it needs to act on GitHub, escalate to a peer.

## Tactical comments — Multica only is fine

"Picking this up", "blocked on X", "handing off to Y" — Multica only. No
GitHub mirror needed.

## Routing mechanics

- **"This needs Zoe"** → assign the Multica issue to `mentatzoe` with a
  comment naming the decision or info needed.
- **"This needs peer review"** → assign to a specific peer with a specific
  request.
- **"I need information from one peer"** → comment with a targeted
  question. One peer at a time.
- **"I'm picking this up"** → tactical Multica-only; status `in_progress`
  → `in_review` when done.
- No cascade @-mentioning.

## Narrow exception to PASS

If `read-the-room.md` resolves to PASS, stay silent. Narrow exception:
substantive technical error you can refute with evidence. One correction,
then stop. Preference difference alone is not enough to interrupt.

## Not yours to decide

- Product direction — Zoe is PM.
- Hypothesis outcomes — observed, not claimed.
- Constitutional invariants — follow, don't relitigate.

## Rules updates

Proposed changes to this file go through a GitHub PR on
`mentatzoe/peer-coordination`. Any agent can propose. Zoe reviews.
