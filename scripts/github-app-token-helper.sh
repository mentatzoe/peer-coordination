#!/usr/bin/env bash
set -euo pipefail

# GitHub App Token Minting Helper
#
# Delegates to the Python implementation so JWT signing and base64url are
# handled correctly. The pure-bash version mis-handled base64url (stripping
# '+/=' instead of substituting) and produced invalid JWTs on GitHub.
#
# Two modes:
#
#   1. Redactor-safe (preferred — PC-62):
#        scripts/github-app-token-helper.sh <agent-name> --write-env-file <path>
#      Mints token, writes GH_TOKEN=/GITHUB_TOKEN= to <path> (mode 0600). Token
#      bytes never touch stdout/stderr — safe under harness display redactors.
#
#   2. Eval-stream (DEPRECATED):
#        eval "$(scripts/github-app-token-helper.sh <agent-name>)"
#      Emits `export GH_TOKEN=...` on stdout. Some agent harnesses redact
#      `ghs_*` substrings on subprocess streams, which silently sets
#      GH_TOKEN to `***`. See multica/github-identity.md.
#
# Agents: vigil | dalgos | castor | echo | <your-agent>
# Profile lookup: ~/.config/peer-coordination/<agent>-app-profile

WRITE_ENV_FILE=""
POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --write-env-file)
      WRITE_ENV_FILE="${2:-}"
      if [[ -z "$WRITE_ENV_FILE" ]]; then
        echo "Error: --write-env-file requires a path argument" >&2
        exit 2
      fi
      shift 2
      ;;
    --write-env-file=*)
      WRITE_ENV_FILE="${1#*=}"
      shift
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done
AGENT_NAME="${POSITIONAL[0]:-}"

if [[ -z "$AGENT_NAME" ]]; then
  cat >&2 <<'USAGE'
Usage: github-app-token-helper.sh <agent-name> [--write-env-file <path>]

Agents:
  vigil  | dalgos  | castor | aether
  <your-agent>  — any profile at ~/.config/peer-coordination/<name>-app-profile

Preferred (redactor-safe):
  scripts/github-app-token-helper.sh vigil --write-env-file "$XDG_RUNTIME_DIR/peer-coord-env-vigil"
  set -a; . "$XDG_RUNTIME_DIR/peer-coord-env-vigil"; set +a

Or use scripts/peer-coord-bootstrap.sh, which wraps this helper with sane
defaults (PC-62).

DEPRECATED eval-stream form:
  eval "$(scripts/github-app-token-helper.sh vigil)"
USAGE
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/.venv/bin/python"

# Auto-bootstrap the venv if missing. Agents and ephemeral worktrees hit this
# on first run; rather than erroring out, we provision quietly to stderr so
# subsequent calls are zero-cost. All bootstrap noise stays on stderr — stdout
# is reserved for shell-evalable exports.
if [[ ! -x "$PY" ]]; then
  echo "# bootstrapping $SCRIPT_DIR/.venv (first-run on this host)" >&2
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 not found in PATH; cannot bootstrap venv" >&2
    exit 1
  fi
  if ! python3 -m venv "$SCRIPT_DIR/.venv" >&2; then
    echo "Error: failed to create venv at $SCRIPT_DIR/.venv" >&2
    exit 1
  fi
  if ! "$SCRIPT_DIR/.venv/bin/pip" install --quiet --disable-pip-version-check \
       -r "$SCRIPT_DIR/requirements.txt" >&2; then
    echo "Error: failed to install requirements into $SCRIPT_DIR/.venv" >&2
    echo "Inspect: $SCRIPT_DIR/.venv/bin/pip install -r $SCRIPT_DIR/requirements.txt" >&2
    exit 1
  fi
  if [[ ! -x "$PY" ]]; then
    echo "Error: bootstrap completed but $PY is still not executable" >&2
    exit 1
  fi
fi

if [[ -n "$WRITE_ENV_FILE" ]]; then
  # Redactor-safe path: token bytes go straight to disk, never touch stdout.
  exec "$PY" "$SCRIPT_DIR/github-app-token-helper.py" "$AGENT_NAME" --write-env-file "$WRITE_ENV_FILE"
fi

TOKEN="$("$PY" "$SCRIPT_DIR/github-app-token-helper.py" "$AGENT_NAME" --token-only)"
if [[ -z "$TOKEN" ]]; then
  echo "Error: token helper returned empty string for $AGENT_NAME" >&2
  exit 1
fi

# Emit shell-evalable exports on stdout. Any diagnostic noise must go to stderr.
# DEPRECATED: see multica/github-identity.md (PC-62). Prefer --write-env-file.
printf 'export GH_TOKEN=%q\n' "$TOKEN"
printf 'export GITHUB_TOKEN=%q\n' "$TOKEN"
echo "# minted for $AGENT_NAME; expires in 60m" >&2
