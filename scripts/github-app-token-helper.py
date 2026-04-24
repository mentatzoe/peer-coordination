#!/usr/bin/env python3
"""
GitHub App token minting helper.

Usage:
    python scripts/github-app-token-helper.py <agent-name>
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    import jwt
except ImportError:
    print("Error: PyJWT not installed", file=sys.stderr)
    print("Install with: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
except ImportError:
    print("Error: cryptography not installed", file=sys.stderr)
    print("Install with: pip install -r scripts/requirements.txt", file=sys.stderr)
    sys.exit(1)


def load_profile(agent_name: str) -> dict[str, str]:
    profile_path = Path.home() / ".config" / "peer-coordination" / f"{agent_name}-app-profile"
    if not profile_path.exists():
        print(f"Error: profile not found at {profile_path}", file=sys.stderr)
        print(
            "Create it from config/app-profile.template before minting a token.",
            file=sys.stderr,
        )
        sys.exit(1)

    profile: dict[str, str] = {}
    for raw_line in profile_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        profile[key.strip()] = value

    required = ["APP_ID", "INSTALLATION_ID", "PRIVATE_KEY_PATH"]
    missing = [key for key in required if not profile.get(key)]
    if missing:
        print(
            "Error: missing required profile keys: " + ", ".join(missing),
            file=sys.stderr,
        )
        sys.exit(1)
    return profile


def mint_token(profile: dict[str, str]) -> str:
    key_path = Path(profile["PRIVATE_KEY_PATH"]).expanduser()
    if not key_path.exists():
        print(f"Error: private key not found at {key_path}", file=sys.stderr)
        sys.exit(1)

    private_key = load_pem_private_key(
        key_path.read_bytes(),
        password=None,
        backend=default_backend(),
    )

    now = int(time.time())
    app_jwt = jwt.encode(
        {
            "iat": now,
            "exp": now + 600,
            "iss": profile["APP_ID"],
        },
        private_key,
        algorithm="RS256",
    )

    req = urllib.request.Request(
        f"https://api.github.com/app/installations/{profile['INSTALLATION_ID']}/access_tokens",
        method="POST",
        headers={
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        print(f"Error: GitHub token mint failed (HTTP {exc.code})", file=sys.stderr)
        print(exc.read().decode(), file=sys.stderr)
        sys.exit(1)

    token = payload.get("token", "")
    if not token:
        print("Error: GitHub response did not include a token", file=sys.stderr)
        sys.exit(1)
    return token


def main() -> None:
    parser = argparse.ArgumentParser(description="Mint a GitHub App installation token")
    parser.add_argument("agent", help="Agent profile name, e.g. vigil or dalgos")
    parser.add_argument(
        "--token-only",
        action="store_true",
        help="Print only the token for shell wrappers",
    )
    args = parser.parse_args()

    token = mint_token(load_profile(args.agent))
    if args.token_only:
        print(token)
        return

    print(f"Minted installation token for {args.agent}")
    print(f'export GH_TOKEN="{token}"')
    print(f'export GITHUB_TOKEN="{token}"')


if __name__ == "__main__":
    main()
