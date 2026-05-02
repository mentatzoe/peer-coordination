# GitHub identity for peer-coordination agents

**Version**: 2.0 (2026-05-02)

Each peer-coordination agent has a dedicated GitHub App so issue comments,
PRs, and pushes show up under that agent — not under a shared human
account. This file is the single authority on minting and using those
tokens. `multica/rules.md` and `multica/read-the-room.md` point here
instead of inlining the rules.

## Bootstrap before any `gh` or `git push` write

```bash
# shellcheck disable=SC1091
source scripts/peer-coord-bootstrap.sh "$PEER_COORD_AGENT_NAME"
gh issue comment ...                   # authored as pc-<agent>[bot]

# git push over HTTPS — choose one (git doesn't read $GH_TOKEN itself):
gh auth setup-git && git push fork <branch>           # via gh credential helper
git push "https://x-access-token:${GH_TOKEN}@github.com/<owner>/<repo>.git" <branch>  # URL form
```

`PEER_COORD_AGENT_NAME` is pre-set in each agent's Multica environment
(see `multica/agent-invocation.md` for the canonical mapping).

The bootstrap mints a fresh App installation token and:

1. Writes it to a 0600 env file at `${XDG_RUNTIME_DIR:-/tmp}/peer-coord-env-<agent>` —
   token bytes never traverse a redacted display layer.
2. Exports `GH_TOKEN` / `GITHUB_TOKEN` into the current shell when sourced —
   `gh`, `git push` (HTTPS), and any in-process Octokit client all read these.

Tokens last 60 minutes; the bootstrap re-mints automatically if the env
file is older than 55 minutes.

If the bootstrap, the local profile, or the app credential is missing, stop
and file the gap as a dependency. **Do not fall back to a
human-authenticated write path** — that defeats the per-agent identity
pattern and erases attribution.

`hermes-minimax` has no app assigned. If it needs to act on GitHub,
escalate to a peer.

## Verifying identity before a write

`scripts/peer-coord-verify.sh <agent>` bootstraps then asks GraphQL
`viewer.login`. Exits 0 only if the active identity is `pc-<agent>[bot]`.
Wire it into harness boot scripts or run it manually before a long-running
task that includes GitHub writes.

```bash
scripts/peer-coord-verify.sh "$PEER_COORD_AGENT_NAME"  # OK: identity=pc-<agent>[bot]
```

## Why the bootstrap (PC-62)

Three observed bypass paths broke the previous `eval "$(...)"` pattern:

- **Display redactor** — some harnesses redact `ghs_*` substrings on
  subprocess streams. `eval "$(helper.sh ...)"` then sets `GH_TOKEN=***`,
  the call hits 401, and `gh` falls back to whatever stored credential the
  shell carries (often the operator's PAT).
- **Bundled Octokit** — opencode and similar harnesses ship an in-process
  HTTP client that reads `GITHUB_TOKEN` from process env directly,
  bypassing any `gh` wrapper.
- **Runtime PATH skip** — the per-host `~/.peer-coord-bin/gh` wrapper is
  reached only when its directory sits ahead of the system `gh` on PATH.
  Multica agent runtimes don't inherit the prefix.

The bootstrap addresses all three: token bytes go straight to a file
(no redacted stream), the env-var path covers Octokit, and shell-local
exports work regardless of any wrapper or PATH state.

## `GH_TOKEN` is shell-local

When sourced, the bootstrap exports `GH_TOKEN` / `GITHUB_TOKEN` only into
the calling shell. Clients that spawn a fresh shell per write must either:

- source the bootstrap in the same shell as the write, OR
- read the env file: `set -a; . "${XDG_RUNTIME_DIR:-/tmp}/peer-coord-env-<agent>"; set +a`

The env-file path is stable across shells and survives 55 minutes per
mint, so subsequent shells can pick it up without re-minting.

## Commit author/committer

`gh` writes and HTTPS pushes attribute the *push event* to the App once
`GH_TOKEN`/`GITHUB_TOKEN` is set. Commit author/committer are read from
local git config, not from the token. Set them per-session before
committing if you need the commit itself to attribute to the bot:

```bash
git config user.name  "pc-${PEER_COORD_AGENT_NAME}[bot]"
git config user.email "<app-id>+pc-${PEER_COORD_AGENT_NAME}[bot]@users.noreply.github.com"
```

App IDs are listed in `docs/github-apps-setup.md`. Or use the
`createCommitOnBranch` GraphQL mutation, which attributes solely from the
token and ignores local git config.

## Helper script and ownership

The minting helper lives in `scripts/github-app-token-helper.sh` (with a
Python sibling at `scripts/github-app-token-helper.py`) and bootstraps
its venv on first run — if `scripts/.venv/` is missing, the wrapper
provisions it and installs `scripts/requirements.txt` automatically. The
top-level `scripts/peer-coord-bootstrap.sh` and
`scripts/peer-coord-verify.sh` wrap it. See `docs/github-apps-setup.md`
for the full host-setup contract.

## Deprecated: `eval "$(github-app-token-helper.sh <agent>)"`

The previous documented pattern emitted `export GH_TOKEN=...` on stdout
for `eval`. This is fragile under harness display redactors (PC-62
Mechanism A) and is **deprecated**. The helper still supports it for
back-compat but new code should use `peer-coord-bootstrap.sh`. The
back-compat path is scheduled for removal once all four agents are off
it.

## Updates

Proposed changes go through a PR on `mentatzoe/peer-coordination`. Any
agent can propose. Zoe reviews.
