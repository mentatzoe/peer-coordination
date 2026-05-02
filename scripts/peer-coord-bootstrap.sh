#!/usr/bin/env bash
# peer-coord-bootstrap.sh — pre-task GitHub identity bootstrap.
#
# Mints a fresh App installation token for the agent and exposes it as
# GH_TOKEN/GITHUB_TOKEN, both via:
#   - a 0600 env file at $PEER_COORD_ENV_FILE
#     (default: ${XDG_RUNTIME_DIR:-/tmp}/peer-coord-env-<agent>), and
#   - direct environment-variable export when this script is *sourced*.
#
# Designed to address all three known wrapper-bypass paths from PC-62:
#   - display-layer redactor (token never round-trips through stdout)
#   - bundled Octokit clients (read GITHUB_TOKEN from process env directly)
#   - runtime-PATH skip (no dependence on ~/.peer-coord-bin being on PATH)
#
# Usage (sourced — preferred for shell flows):
#     # shellcheck disable=SC1091
#     source scripts/peer-coord-bootstrap.sh dalgos
#     gh issue comment ...                 # authored as pc-dalgos[bot]
#     git push origin <branch>             # via HTTPS, authored as pc-dalgos
#
# Usage (executed — for harnesses that bootstrap subprocess env via a file):
#     scripts/peer-coord-bootstrap.sh dalgos
#     set -a; . "$(scripts/peer-coord-bootstrap.sh dalgos --print-env-file)"; set +a
#
# Agent profiles live at ~/.config/peer-coordination/<agent>-app-profile.
# See multica/github-identity.md and docs/github-apps-setup.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_NAME=""
PRINT_ENV_FILE=0

usage() {
  cat >&2 <<'USAGE'
Usage: peer-coord-bootstrap.sh <agent-name> [--print-env-file]

Mints a GitHub App installation token for <agent-name> and writes it to a
0600 env file (default: ${XDG_RUNTIME_DIR:-/tmp}/peer-coord-env-<agent-name>;
override via $PEER_COORD_ENV_FILE).

When sourced, exports GH_TOKEN and GITHUB_TOKEN into the current shell.

Flags:
  --print-env-file   Print the env-file path on stdout (and exit 0 without
                     re-minting if a non-stale file already exists). Useful
                     for callers that want the path without sourcing.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --print-env-file)
      PRINT_ENV_FILE=1
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Error: unknown flag: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [[ -z "$AGENT_NAME" ]]; then
        AGENT_NAME="$1"
      else
        echo "Error: unexpected argument: $1" >&2
        exit 2
      fi
      shift
      ;;
  esac
done

AGENT_NAME="${AGENT_NAME:-${PEER_COORD_AGENT_NAME:-}}"
if [[ -z "$AGENT_NAME" ]]; then
  echo "Error: agent name required (positional arg or PEER_COORD_AGENT_NAME)" >&2
  usage
  exit 2
fi

ENV_FILE="${PEER_COORD_ENV_FILE:-${XDG_RUNTIME_DIR:-/tmp}/peer-coord-env-$AGENT_NAME}"

# Re-mint if the file is missing, empty, or older than 55m (tokens live 60m).
needs_refresh() {
  [[ ! -s "$ENV_FILE" ]] && return 0
  local age
  age=$(( $(date +%s) - $(stat -f %m "$ENV_FILE" 2>/dev/null || stat -c %Y "$ENV_FILE" 2>/dev/null || echo 0) ))
  (( age >= 3300 ))
}

if needs_refresh; then
  "$SCRIPT_DIR/github-app-token-helper.sh" "$AGENT_NAME" --write-env-file "$ENV_FILE"
fi

if (( PRINT_ENV_FILE )); then
  printf '%s\n' "$ENV_FILE"
  exit 0
fi

# Sourced detection: when the file is sourced, BASH_SOURCE[0] differs from $0.
_sourced=0
if [[ "${BASH_SOURCE[0]:-}" != "${0:-}" ]]; then
  _sourced=1
fi

if (( _sourced )); then
  set -a
  # shellcheck source=/dev/null
  . "$ENV_FILE"
  set +a
  # Tell the caller where the file lives, redaction-safe (no token bytes).
  printf '# peer-coord identity bootstrapped: agent=%s env_file=%s\n' "$AGENT_NAME" "$ENV_FILE" >&2
else
  # Executed (not sourced): the parent shell can't inherit our exports, so
  # tell it where the env file is. This single line is the entire stdout.
  printf 'PEER_COORD_ENV_FILE=%s\n' "$ENV_FILE"
  printf '# peer-coord identity ready for agent=%s; source the env file with: set -a; . %s; set +a\n' \
    "$AGENT_NAME" "$ENV_FILE" >&2
fi
