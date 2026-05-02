# Per-Bot GitHub Apps Setup

Each agent in the peer-coordination workspace has a dedicated GitHub App so issue comments, PRs, and pushes are attributed to the right bot instead of a shared human account.

## Current apps

| App | Agent (Multica) | Identity purpose | App ID | Install ID |
| --- | --- | --- | --- | --- |
| `pc-vigil`  | `codex`  | Codex-powered implementation bot   | 3468724 | 126210542 |
| `pc-dalgos` | `claude` | Claude-powered generalist/reviewer | 3468744 | 126210902 |
| `pc-castor` | `castor` | Gemini 3.1 Pro Preview             | 3468752 | 126211266 |
| `pc-aether` | `aether` | Hermes harness + Grok-4 via xAI    | 3468766 | 126211615 |

All four are installed on `mentatzoe/peer-coordination` with Contents/Issues/PRs/Discussions write + Metadata read. `hermes-minimax` has no app — it operates as a worker that escalates GitHub-side actions to a peer.

Profiles live at `~/.config/peer-coordination/<agent>-app-profile` and private keys at `~/.config/peer-coordination/peer-coordination-<agent>.pem` (mode 600, never committed).

## Token minting

```bash
# shellcheck disable=SC1091
source scripts/peer-coord-bootstrap.sh "$PEER_COORD_AGENT_NAME"
```

`PEER_COORD_AGENT_NAME` is pre-set per agent in Multica (claude→dalgos,
codex→vigil, castor→castor, aether→aether). The bootstrap mints a fresh
App installation token via `github-app-token-helper.py`, writes it to a
0600 env file at `${XDG_RUNTIME_DIR:-/tmp}/peer-coord-env-<agent>`, and
when sourced exports `GH_TOKEN`/`GITHUB_TOKEN` into the current shell.
Tokens last 60 minutes; the bootstrap auto re-mints after 55 minutes.

`scripts/peer-coord-verify.sh <agent>` bootstraps and then asks GraphQL
`viewer.login` — exits 0 only if the active identity is
`pc-<agent>[bot]`. Use it as a pre-write smoke before any long-running
task that includes GitHub writes.

The previous documented pattern (`eval "$(github-app-token-helper.sh ...)"`)
is **deprecated** — display redactors silently set `GH_TOKEN=***`, the
call hits 401, and `gh` falls back to whatever stored credential the
shell carries. The helper still supports it for back-compat; new code
should use the bootstrap.

## Host setup

The helper depends on a Python venv at `scripts/.venv/` containing `pyjwt` and `cryptography`. **It bootstraps itself on first run** — if the venv doesn't exist, the bash wrapper creates it and installs `scripts/requirements.txt` automatically. All bootstrap noise stays on stderr; stdout remains shell-evalable.

This means agent runtimes hitting a fresh ephemeral worktree, a fresh checkout, or a new host see one slow first call (~10–20 s for venv + pip install) and zero-cost calls thereafter. Manual provisioning is supported but unnecessary:

```bash
# Optional — pre-warm the venv before first agent run
python3 -m venv scripts/.venv
scripts/.venv/bin/pip install -r scripts/requirements.txt
```

If bootstrap fails (no `python3` in PATH, network blocked, etc.), the wrapper exits non-zero with a clear stderr message and `gh`/`git push` fall through to whatever ambient credentials the shell carries — usually the user's PAT, which is what we want to avoid. Audit any commit attributed to your personal user instead of `pc-<agent>[bot]` and re-mint.

## Using the token

`gh`, `git push` (HTTPS), and any in-process Octokit client all honor
`GH_TOKEN`/`GITHUB_TOKEN`. After `source scripts/peer-coord-bootstrap.sh
<agent>`, commands run as the agent's app:

```bash
gh pr comment 123 --body "Handing off to dalgos for review."
gh api repos/mentatzoe/peer-coordination/issues -f title='...' -f body='...'
git push origin claude-pc-62-gh-identity-fix
```

HTTPS push works because git treats `GITHUB_TOKEN` as the password for
`x-access-token`. For SSH-based remotes, the token does not replace the
key — use HTTPS remotes when you want push attribution to flow through
the app.

## Per-harness install steps

`PEER_COORD_AGENT_NAME` and the bootstrap-source pattern are sufficient on
any harness whose agent code can run a shell command before a GitHub
write. Per-harness boot-script entries:

| Harness                | Pre-write hook |
|------------------------|----------------|
| Claude Code (Multica)  | `source scripts/peer-coord-bootstrap.sh "$PEER_COORD_AGENT_NAME"` at task-start. |
| Codex (Multica)        | Same. |
| opencode / aether      | Same — sourced before opencode boots so its bundled Octokit reads `GITHUB_TOKEN` from process env. |
| Hermes                 | Same — and run `scripts/peer-coord-verify.sh "$PEER_COORD_AGENT_NAME"` after, since the redactor previously corrupted the eval pattern silently. |

The legacy `~/.peer-coord-bin/gh` shell wrapper is no longer required.
It still works on hosts where it's installed and on PATH, but the
bootstrap covers all three previously-observed bypasses (display
redactor, bundled Octokit, runtime-PATH skip — see PC-62 and
`multica/github-identity.md`).

## Adding a new agent

1. Create the app via GitHub UI at `https://github.com/settings/apps/new`. Name must be globally unique (use the `pc-<name>` prefix).
2. Generate a private key, save to `~/.config/peer-coordination/peer-coordination-<name>.pem` (mode 600).
3. Install on `mentatzoe/peer-coordination` (Only select repositories → peer-coordination). Permissions: Contents/Issues/PRs/Discussions write, Metadata read.
4. Write the profile (only these three fields are parsed — anything else is
   ignored):
   ```ini
   # ~/.config/peer-coordination/<name>-app-profile
   APP_ID=<numeric-app-id>
   INSTALLATION_ID=<numeric-install-id>
   PRIVATE_KEY_PATH=~/.config/peer-coordination/peer-coordination-<name>.pem
   ```
5. Set `PEER_COORD_AGENT_NAME=<name>` on the Multica agent via the workspace API.
6. Verify: `scripts/.venv/bin/python scripts/github-app-token-helper.py <name> --token-only`.

## Commit / push attribution (important)

`gh` comments, PRs, and issue operations via `gh api` attribute correctly to
the app bot once `GH_TOKEN` is set. **`git push` attribution is a separate
concern**: the commit author and committer are read from local git config,
not from the token. HTTPS push succeeds with `GITHUB_TOKEN`, but the commits
will show whatever `user.name` / `user.email` are configured in the shell
(often `mentatzoe`).

To make commits attribute to the bot, set per-session identity before committing:

```bash
# After eval'ing the token helper:
git config user.name  "pc-${PEER_COORD_AGENT_NAME}[bot]"
git config user.email "<app-id>+pc-${PEER_COORD_AGENT_NAME}[bot]@users.noreply.github.com"
```

The `<app-id>` is the numeric App ID from the table above (not the install
ID). Alternatively, commit via the `createCommitOnBranch` GraphQL mutation,
which attributes solely from the token and ignores local git config — use
that when you need guaranteed bot authorship without trusting the shell
state.

## Troubleshooting

- **`Profile not found`** — path typo or the helper is running under a different HOME.
- **`Failed to obtain installation token (HTTP 404)`** — install ID is wrong or the app isn't installed on this repo.
- **`HTTP 401`** — private key doesn't match the app, or system clock is skewed (JWT `iat`/`exp` drift).
- **`gh` still posts as @mentatzoe** — `GH_TOKEN` wasn't exported into the subshell. Use `eval "$(scripts/github-app-token-helper.sh …)"`, not `./scripts/…`.
