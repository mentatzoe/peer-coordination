# GitHub identity for peer-coordination agents

**Version**: 1.0 (2026-04-25)

Each peer-coordination agent has a dedicated GitHub App so issue comments,
PRs, and pushes show up under that agent — not under a shared human
account. This file is the single authority on minting and using those
tokens. `multica/rules.md` and `multica/read-the-room.md` point here
instead of inlining the rules.

## Mint before any `gh` or `git push` write

```bash
eval "$(scripts/github-app-token-helper.sh "$PEER_COORD_AGENT_NAME")"
```

`PEER_COORD_AGENT_NAME` is pre-set in each agent's Multica environment
(see `multica/agent-invocation.md` for the canonical mapping).

Tokens last 60 minutes. Re-run the helper if a long task spans the
boundary.

If the helper, the local profile, or the app credential is missing, stop
and file the gap as a dependency. **Do not fall back to a
human-authenticated write path** — that defeats the per-agent identity
pattern and erases attribution.

`hermes-minimax` has no app assigned. If it needs to act on GitHub,
escalate to a peer.

## `GH_TOKEN` is shell-local

If your client starts a fresh shell for each command, a token exported in
one invocation will not survive into the next one. Two safe patterns:

- run the helper in the same shell as each `gh` or `git push` write, OR
- re-run the helper immediately before every separate write command.

This is the failure mode behind the dismissed-and-re-posted review noted
in PR #83's history (mint succeeded, second `gh` invocation ran under a
different shell with `GH_TOKEN` unset, defaulting to the user). Treat it
as a per-shell concern.

## Helper script and ownership

The minting helper lives in `scripts/github-app-token-helper.sh` (with a
Python sibling at `scripts/github-app-token-helper.py`). The helper itself
is maintained on the GitHub-app patch train (PR #73). Treat the helper as
a forward dependency of this rule — once that PR lands on `main`, the rule
above is enforceable.

## Updates

Proposed changes go through a PR on `mentatzoe/peer-coordination`. Any
agent can propose. Zoe reviews.
