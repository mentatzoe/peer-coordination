"""CLI surface for repo-owned session bundle tooling."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from tools.peer_session.bundle_init import initialize_bundle
from tools.peer_session.interventions import add_intervention, validate_interventions_file
from tools.peer_session.rollup import run_rollup
from tools.peer_session.tally import run_tally


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

    intervention_parser = subparsers.add_parser(
        "intervention",
        help="Add or validate intervention tags in a session bundle.",
    )
    intervention_subparsers = intervention_parser.add_subparsers(dest="intervention_command")

    add_parser = intervention_subparsers.add_parser(
        "add",
        help="Append one intervention record to observations/sessions/<session-id>/interventions.json.",
    )
    add_parser.add_argument("session_id", help="Target session bundle ID")
    add_parser.add_argument("--id", dest="intervention_id", default=None, help="Optional stable id, e.g. iv-003.")
    add_parser.add_argument("--type", dest="intervention_type", required=True, help="Intervention taxonomy type.")
    add_parser.add_argument("--reason", required=True, help="Operator-readable reason for the intervention.")
    add_parser.add_argument("--at", required=True, help="RFC3339 UTC timestamp when the intervention occurred.")
    add_parser.add_argument("--actor", required=True, help="Human or peer that made/requested the intervention.")
    add_parser.add_argument(
        "--attribution",
        required=True,
        choices=["operator_directed", "agent_self_flagged"],
        help="Attribution class for the intervention.",
    )
    add_parser.add_argument("--target-turn", default=None, help="Single transcript turn timestamp target.")
    add_parser.add_argument("--start-turn", default=None, help="Span start transcript turn timestamp.")
    add_parser.add_argument("--end-turn", default=None, help="Span end transcript turn timestamp.")
    add_parser.add_argument("--notes", default=None, help="Optional extra context for reviewers.")

    validate_parser = intervention_subparsers.add_parser(
        "validate",
        help="Validate a session bundle intervention log.",
    )
    validate_parser.add_argument("session_id", help="Target session bundle ID")

    tally_parser = subparsers.add_parser(
        "tally",
        help="Compute per-session KPIs from a closed bundle (writes kpi.json).",
    )
    tally_parser.add_argument("session_id", help="Target session bundle ID")

    subparsers.add_parser(
        "rollup",
        help="Aggregate counted-session KPIs into observations/poc-exit-<timestamp>.md.",
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

    if args.command == "intervention":
        effective_repo_root = repo_root or Path.cwd()
        bundle_dir = effective_repo_root / "observations" / "sessions" / args.session_id
        try:
            if args.intervention_command == "add":
                record = add_intervention(
                    effective_repo_root,
                    args.session_id,
                    intervention_type=args.intervention_type,
                    reason=args.reason,
                    at=args.at,
                    actor=args.actor,
                    attribution=args.attribution,
                    target_turn=args.target_turn,
                    start_turn=args.start_turn,
                    end_turn=args.end_turn,
                    intervention_id=args.intervention_id,
                    notes=args.notes,
                )
                print(f"Added intervention {record['id']} to {bundle_dir / 'interventions.json'}")
                return 0

            if args.intervention_command == "validate":
                records = validate_interventions_file(
                    bundle_dir / "interventions.json",
                    transcript_path=bundle_dir / "transcript.md",
                )
                print(f"Validated {len(records)} intervention record(s)")
                return 0
        except Exception as exc:  # pragma: no cover - exact paths will be expanded in tests
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    if args.command == "tally":
        effective_repo_root = repo_root or Path.cwd()
        sessions_root = effective_repo_root / "observations" / "sessions"
        return run_tally(args.session_id, sessions_root=sessions_root)

    if args.command == "rollup":
        effective_repo_root = repo_root or Path.cwd()
        observations_root = effective_repo_root / "observations"
        return run_rollup(observations_root=observations_root)

    parser.print_help()
    return 1
