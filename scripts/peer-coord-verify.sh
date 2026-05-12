#!/usr/bin/env bash
# peer-coord-verify.sh — falsifiable smoke for the PC-62 identity fix.
#
# Bootstraps the agent's App identity (idempotent), then asks GitHub who the
# token belongs to. Exits 0 only if the active identity is pc-<agent>[bot].
#
# This is the smoke harness the acceptance criteria call for: an agent runs
# this before any GH write or `git push` and gets a hard fail rather than a
# silent leak. Designed to be wired into CI, harness boot scripts, or a
# pre-write check inside agent loops.
#
# Usage:
#     scripts/peer-coord-verify.sh <agent-name>
#
# Exit codes:
#     0  identity matches pc-<agent>[bot]
#     1  identity mismatch (leak — mentatzoe or other)
#     2  bootstrap or API failure
#
# See PC-62 and multica/github-identity.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_NAME="${1:-${PEER_COORD_AGENT_NAME:-}}"

if [[ -z "$AGENT_NAME" ]]; then
  echo "Usage: peer-coord-verify.sh <agent-name>" >&2
  exit 2
fi

# Bootstrap (sourced) — sets GH_TOKEN/GITHUB_TOKEN in this shell.
# shellcheck disable=SC1091
source "$SCRIPT_DIR/peer-coord-bootstrap.sh" "$AGENT_NAME"

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "FAIL: GH_TOKEN not set after bootstrap (mint or source failed)" >&2
  exit 2
fi

# Direct API call — no `gh` dependency, no PATH-skip exposure. Header carries
# the bytes; the response carries the identity. App installation tokens can't
# hit /user (that's a user-token endpoint), but GraphQL `viewer.login`
# resolves correctly under installation auth and returns `pc-<agent>[bot]`.
RESPONSE_FILE="$(mktemp -t peer-coord-verify.XXXXXX)"
trap 'rm -f "$RESPONSE_FILE"' EXIT

HTTP_CODE=$(curl -sS -o "$RESPONSE_FILE" -w '%{http_code}' \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -X POST \
  -d '{"query":"query { viewer { login __typename } }"}' \
  https://api.github.com/graphql)

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "FAIL: GitHub graphql returned HTTP $HTTP_CODE" >&2
  cat "$RESPONSE_FILE" >&2
  exit 2
fi

LOGIN=$(python3 -c '
import json, sys
data = json.load(open(sys.argv[1])).get("data", {}).get("viewer") or {}
print(data.get("login", ""))
' "$RESPONSE_FILE")

EXPECTED="pc-${AGENT_NAME}[bot]"
if [[ "$LOGIN" == "$EXPECTED" ]]; then
  printf 'OK: identity=%s\n' "$LOGIN"
  exit 0
fi

printf 'FAIL: expected login=%s, got login=%s\n' "$EXPECTED" "$LOGIN" >&2
exit 1
