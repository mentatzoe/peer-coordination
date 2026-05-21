from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def seed_template(repo_root: Path) -> None:
    template_src = Path(__file__).resolve().parents[2] / "observations" / "sessions" / "_template"
    template_dst = repo_root / "observations" / "sessions" / "_template"
    template_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_src, template_dst)


def fixture_path(fixture_name: str) -> Path:
    return FIXTURES_DIR / fixture_name


def install_fixture_bundle(
    repo_root: Path,
    fixture_name: str,
    *,
    session_id: str | None = None,
) -> Path:
    """Copy a fixture bundle into <repo_root>/observations/sessions/<session_id>/.

    When `session_id` is provided (or inferred from the fixture name), the
    bundle's `meta.json.session_id` is rewritten to match so tally's session-id
    consistency check passes.
    """
    src = fixture_path(fixture_name)
    if not src.is_dir():
        raise FileNotFoundError(f"fixture missing: {src}")

    bundle_session_id = session_id or fixture_name.replace("_", "-")
    bundle_dir = repo_root / "observations" / "sessions" / bundle_session_id
    bundle_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, bundle_dir)

    meta_path = bundle_dir / "meta.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        if isinstance(meta, dict):
            meta["session_id"] = bundle_session_id
            meta_path.write_text(json.dumps(meta, indent=2) + "\n")

    drift_audit_path = bundle_dir / "drift-audit.json"
    if drift_audit_path.is_file():
        try:
            drift = json.loads(drift_audit_path.read_text())
        except json.JSONDecodeError:
            drift = None
        if isinstance(drift, dict) and "session_id" in drift:
            drift["session_id"] = bundle_session_id
            drift_audit_path.write_text(json.dumps(drift, indent=2) + "\n")

    fra_path = bundle_dir / "fresh-reader-audit.json"
    if fra_path.is_file():
        try:
            fra = json.loads(fra_path.read_text())
        except json.JSONDecodeError:
            fra = None
        if isinstance(fra, dict) and "session_id" in fra:
            fra["session_id"] = bundle_session_id
            fra_path.write_text(json.dumps(fra, indent=2) + "\n")

    return bundle_dir


def seed_pinned_rules(repo_root: Path) -> None:
    rules_dir = repo_root / "pinned-rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "current.md").write_text("# Rules\n\n- Keep it legible.\n")

    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", "pinned-rules/current.md"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "seed pinned rules"], cwd=repo_root, check=True, capture_output=True)


def write_defaults(repo_root: Path) -> Path:
    defaults_path = repo_root / "observations" / "sessions" / "defaults.toml"
    defaults_path.write_text(
        'operator_handle = "zoe"\n'
        'peer_handles = ["codex", "claude"]\n'
        'substrate = "discord"\n'
        'channel_id = "123456789012345678"\n'
    )
    return defaults_path
