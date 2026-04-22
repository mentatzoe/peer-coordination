#!/usr/bin/env bash
set -euo pipefail

# GitHub App Token Minting Helper
#
# Delegates to the Python implementation so JWT signing and base64url are
# handled correctly. The pure-bash version mis-handled base64url (stripping
# '+/=' instead of substituting) and produced invalid JWTs on GitHub.
#
# Usage:
#   eval "$(scripts/github-app-token-helper.sh <agent-name>)"
#
# Agents: vigil | dalgos | castor | echo | <your-agent>
# Profile lookup: ~/.config/peer-coordination/<agent>-app-profile

AGENT_NAME="${1:-}"
if [[ -z "$AGENT_NAME" ]]; then
  cat >&2 <<'USAGE'
Usage: github-app-token-helper.sh <agent-name>

Agents:
  vigil  | dalgos  | castor | echo
  <your-agent>  — any profile at ~/.config/peer-coordination/<name>-app-profile

To load tokens into the current shell:
  eval "$(scripts/github-app-token-helper.sh vigil)"
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
  echo "Error: token helper returned empty string for $AGENT_NAME" >&2
  exit 1
fi

# Emit shell-evalable exports on stdout. Any diagnostic noise must go to stderr.
printf 'export GH_TOKEN=%q\n' "$TOKEN"
printf 'export GITHUB_TOKEN=%q\n' "$TOKEN"
echo "# minted for $AGENT_NAME; expires in 60m" >&2
