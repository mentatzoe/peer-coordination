from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, UTC
from pathlib import Path
from typing import Sequence

from tools.peer_session.defaults import load_defaults
from tools.peer_session.git_refs import resolve_pinned_rules_ref

SESSION_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*(?:-\d{2})?$")
REQUIRED_TEMPLATE_FILES = {
    "README.md",
    "meta.json",
    "transcript.md",
    "interventions.json",
    "summary.md",
    "drift-audit.json",
}


def initialize_bundle(
    repo_root: Path,
    session_id: str,
    *,
    defaults_path: Path | None = None,
    peer_handles: Sequence[str] | None = None,
    operator_handle: str | None = None,
    channel_id: str | None = None,
) -> Path:
    repo_root = repo_root.resolve()
    validate_session_id(session_id)

    template_dir = repo_root / "observations" / "sessions" / "_template"
    validate_template_dir(template_dir)

    bundle_dir = repo_root / "observations" / "sessions" / session_id
    if bundle_dir.exists():
        raise FileExistsError(f"session bundle already exists: {bundle_dir}")

    defaults = load_defaults(
        defaults_path or repo_root / "observations" / "sessions" / "defaults.toml",
        peer_handles=peer_handles,
        operator_handle=operator_handle,
        channel_id=channel_id,
    )

    shutil.copytree(template_dir, bundle_dir)

    meta_path = bundle_dir / "meta.json"
    meta = json.loads(meta_path.read_text())
    meta["session_id"] = session_id
    meta["opened_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    meta["participants"] = [
        *({"handle": handle, "role": "peer"} for handle in defaults.peer_handles),
        {"handle": defaults.operator_handle, "role": "operator"},
    ]
    meta["pinned_rules_ref"] = resolve_pinned_rules_ref(repo_root)
    meta["substrate"] = defaults.substrate
    meta["channel_id"] = defaults.channel_id
    meta.pop("transcript_source", None)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")

    return bundle_dir


def validate_session_id(session_id: str) -> None:
    if not SESSION_ID_RE.match(session_id):
        raise ValueError(f"invalid session_id: {session_id}")


def validate_template_dir(template_dir: Path) -> None:
    if not template_dir.is_dir():
        raise FileNotFoundError(f"template directory missing: {template_dir}")

    missing = sorted(name for name in REQUIRED_TEMPLATE_FILES if not (template_dir / name).is_file())
    if missing:
        raise FileNotFoundError(f"template missing required files: {', '.join(missing)}")
