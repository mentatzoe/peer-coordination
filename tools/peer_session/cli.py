"""CLI surface for repo-owned session bundle tooling."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from tools.peer_session.bundle_init import initialize_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="peer-session",
        description="Repo-owned session bundle tooling.",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new session bundle from observations/sessions/_template/.",
    )
    init_parser.add_argument("session_id", help="Target session bundle ID")
    init_parser.add_argument(
        "--defaults",
        default="observations/sessions/defaults.toml",
        help="Path to the operator-local defaults file.",
    )
    init_parser.add_argument(
        "--peer",
        action="append",
        dest="peer_handles",
        default=None,
        help="Override peer handle (repeatable).",
    )
    init_parser.add_argument(
        "--operator",
        dest="operator_handle",
        default=None,
        help="Override operator handle.",
    )
    init_parser.add_argument(
        "--channel-id",
        dest="channel_id",
        default=None,
        help="Override Discord channel snowflake.",
    )

    return parser


def main(argv: Sequence[str] | None = None, *, repo_root: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        try:
            effective_repo_root = repo_root or Path.cwd()
            defaults_path = Path(args.defaults)
            if not defaults_path.is_absolute():
                defaults_path = effective_repo_root / defaults_path
            initialize_bundle(
                effective_repo_root,
                args.session_id,
                defaults_path=defaults_path,
                peer_handles=args.peer_handles,
                operator_handle=args.operator_handle,
                channel_id=args.channel_id,
            )
        except Exception as exc:  # pragma: no cover - exact paths will be expanded in later tests
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 1
