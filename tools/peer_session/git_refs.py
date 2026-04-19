from __future__ import annotations

from pathlib import Path
import subprocess


def resolve_pinned_rules_ref(repo_root: Path) -> str | dict[str, str]:
    rules_path = repo_root / "pinned-rules" / "current.md"
    if not rules_path.is_file():
        raise FileNotFoundError(f"pinned rules file missing: {rules_path}")

    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--", "pinned-rules/current.md"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return {"inline": rules_path.read_text()}

    if status.stdout.strip():
        return {"inline": rules_path.read_text()}

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return commit.stdout.strip()
