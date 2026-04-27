#!/usr/bin/env python3
"""
GitHub App Token Minting Helper (Python version)
Usage: python github-app-token-helper.py <agent-name>
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

try:
    import jwt
except ImportError:
    print("Error: PyJWT not installed", file=sys.stderr)
    print("Install with: pip install pyjwt cryptography", file=sys.stderr)
    sys.exit(1)


def load_profile(agent_name: str) -> dict:
    """Load the agent profile from ~/.config/peer-coordination/"""
    config_dir = Path.home() / ".config" / "peer-coordination"
    profile_path = config_dir / f"{agent_name}-app-profile"
    
    if not profile_path.exists():
        print(f"Error: Profile not found at {profile_path}", file=sys.stderr)
        print(f"\nCreate the profile first:", file=sys.stderr)
        print(f"  cp config/app-profile.template {profile_path}", file=sys.stderr)
        print(f"  # Then edit {profile_path} with your app's credentials", file=sys.stderr)
        sys.exit(1)
    
    # Parse profile (simple key=value format; strips surrounding single/double
    # quotes so the template's quoted-or-unquoted style both work).
    profile = {}
    with open(profile_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                profile[key.strip()] = value
    
    required = ['APP_ID', 'INSTALLATION_ID', 'PRIVATE_KEY_PATH']
    missing = [k for k in required if not profile.get(k)]
    if missing:
        print(f"Error: Missing required fields: {', '.join(missing)}", file=sys.stderr)
        print(f"Edit {profile_path} with your credentials", file=sys.stderr)
        sys.exit(1)
    
    return profile


def mint_token(profile: dict) -> str:
    """Mint an installation token using JWT authentication."""
    import cryptography.hazmat.primitives.serialization as ser
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    
    # Load private key
    key_path = Path(profile['PRIVATE_KEY_PATH']).expanduser()
    if not key_path.exists():
        print(f"Error: Private key not found at {key_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(key_path, 'rb') as f:
        private_key = ser.load_pem_private_key(f.read(), password=None, backend=default_backend())
    
    # Create JWT
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + 600,  # 10 minutes max
        'iss': profile['APP_ID']
    }
    
    token = jwt.encode(payload, private_key, algorithm='RS256')
    
    # Exchange JWT for installation token
    import urllib.request
    import urllib.error
    
    url = f"https://api.github.com/app/installations/{profile['INSTALLATION_ID']}/access_tokens"
    
    req = urllib.request.Request(
        url,
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data['token']
    except urllib.error.HTTPError as e:
        print(f"Error: Failed to obtain installation token (HTTP {e.code})", file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Mint GitHub App installation token')
    parser.add_argument('agent', help='Agent name (e.g., codex, hermes, castor)')
    parser.add_argument('--token-only', action='store_true', 
                        help='Output only the token (for scripting)')
    args = parser.parse_args()
    
    profile = load_profile(args.agent)
    token = mint_token(profile)
    
    if args.token_only:
        print(token)
    else:
        print(f"✅ Successfully minted installation token for {args.agent}")
        print(f"\nToken: {token}")
        print(f"\nExport with:")
        print(f"  export GH_TOKEN=\"{token}\"")
        print(f"  export GITHUB_TOKEN=\"{token}\"")


if __name__ == '__main__':
    main()
