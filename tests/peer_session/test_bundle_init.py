from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.peer_session.bundle_init import initialize_bundle


class InitializeBundleTest(unittest.TestCase):
    def test_initialize_bundle_creates_session_directory_and_fills_mechanical_meta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            self._seed_template(repo_root)
            self._seed_pinned_rules(repo_root)
            defaults_path = self._write_defaults(repo_root)

            bundle_dir = initialize_bundle(
                repo_root,
                "2026-04-20-dry-run-one",
                defaults_path=defaults_path,
            )

            self.assertTrue(bundle_dir.is_dir())
            self.assertTrue((bundle_dir / "meta.json").is_file())
            self.assertTrue((bundle_dir / "transcript.md").is_file())
            self.assertTrue((bundle_dir / "interventions.json").is_file())
            self.assertTrue((bundle_dir / "summary.md").is_file())
            self.assertTrue((bundle_dir / "drift-audit.json").is_file())
            self.assertTrue((bundle_dir / "README.md").is_file())

            meta = json.loads((bundle_dir / "meta.json").read_text())
            self.assertEqual(meta["session_id"], "2026-04-20-dry-run-one")
            self.assertEqual(meta["substrate"], "discord")
            self.assertEqual(meta["channel_id"], "123456789012345678")
            self.assertEqual(
                meta["participants"],
                [
                    {"handle": "codex", "role": "peer"},
                    {"handle": "claude", "role": "peer"},
                    {"handle": "zoe", "role": "operator"},
                ],
            )
            self.assertIn("opened_at", meta)
            self.assertIn("pinned_rules_ref", meta)
            self.assertNotIn("transcript_source", meta)

    def _seed_template(self, repo_root: Path) -> None:
        template_src = Path(__file__).resolve().parents[2] / "observations" / "sessions" / "_template"
        template_dst = repo_root / "observations" / "sessions" / "_template"
        template_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(template_src, template_dst)

    def _seed_pinned_rules(self, repo_root: Path) -> None:
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

    def _write_defaults(self, repo_root: Path) -> Path:
        defaults_path = repo_root / "observations" / "sessions" / "defaults.toml"
        defaults_path.write_text(
            'operator_handle = "zoe"\n'
            'peer_handles = ["codex", "claude"]\n'
            'substrate = "discord"\n'
            'channel_id = "123456789012345678"\n'
        )
        return defaults_path


if __name__ == "__main__":
    unittest.main()
