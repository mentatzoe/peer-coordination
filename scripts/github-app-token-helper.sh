#!/usr/bin/env bash
set -euo pipefail

# Mint a GitHub App installation token for the requested peer bot and emit
# shell-export lines that can be eval'd into the current session.

AGENT_NAME="${1:-}"
if [[ -z "$AGENT_NAME" ]]; then
  cat >&2 <<'USAGE'
Usage: scripts/github-app-token-helper.sh <agent-name>

Examples:
  eval "$(scripts/github-app-token-helper.sh vigil)"
  eval "$(scripts/github-app-token-helper.sh dalgos)"
USAGE
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Error: venv missing at $SCRIPT_DIR/.venv" >&2
  echo "Create it with: python3 -m venv $SCRIPT_DIR/.venv && $SCRIPT_DIR/.venv/bin/pip install -r $SCRIPT_DIR/requirements.txt" >&2
  exit 1
fi

TOKEN="$("$PY" "$SCRIPT_DIR/github-app-token-helper.py" "$AGENT_NAME" --token-only)"
if [[ -z "$TOKEN" ]]; then
  echo "Error: token helper returned an empty token for $AGENT_NAME" >&2
  exit 1
fi

printf 'export GH_TOKEN=%q\n' "$TOKEN"
printf 'export GITHUB_TOKEN=%q\n' "$TOKEN"
echo "# minted for $AGENT_NAME; expires in 60m" >&2
