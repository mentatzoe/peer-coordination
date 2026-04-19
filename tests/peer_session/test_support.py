from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def seed_template(repo_root: Path) -> None:
    template_src = Path(__file__).resolve().parents[2] / "observations" / "sessions" / "_template"
    template_dst = repo_root / "observations" / "sessions" / "_template"
    template_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template_src, template_dst)


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
