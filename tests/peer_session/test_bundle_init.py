from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.peer_session.test_support import seed_pinned_rules, seed_template, write_defaults
from tools.peer_session.bundle_init import initialize_bundle


class InitializeBundleTest(unittest.TestCase):
    def test_initialize_bundle_creates_session_directory_and_fills_mechanical_meta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            seed_template(repo_root)
            seed_pinned_rules(repo_root)
            defaults_path = write_defaults(repo_root)

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
            self.assertEqual(meta["closed_at"], "[FILL IN: ISO-8601 timestamp or null]")
            self.assertEqual(
                meta["close_reason"],
                "[FILL IN: operator_close | pinned_rules_change | stop_no_resume]",
            )

    def test_initialize_bundle_cli_overrides_win_over_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            seed_template(repo_root)
            seed_pinned_rules(repo_root)
            defaults_path = write_defaults(repo_root)

            bundle_dir = initialize_bundle(
                repo_root,
                "2026-04-20-dry-run-overrides",
                defaults_path=defaults_path,
                peer_handles=["vigil", "dalgos"],
                operator_handle="station",
                channel_id="999999999999999999",
            )

            meta = json.loads((bundle_dir / "meta.json").read_text())
            self.assertEqual(meta["channel_id"], "999999999999999999")
            self.assertEqual(
                meta["participants"],
                [
                    {"handle": "vigil", "role": "peer"},
                    {"handle": "dalgos", "role": "peer"},
                    {"handle": "station", "role": "operator"},
                ],
            )

    def test_initialize_bundle_uses_inline_snapshot_when_pinned_rules_are_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            seed_template(repo_root)
            seed_pinned_rules(repo_root)
            defaults_path = write_defaults(repo_root)
            pinned_rules = repo_root / "pinned-rules" / "current.md"
            pinned_rules.write_text("# Rules\n\n- Dirty override.\n")

            bundle_dir = initialize_bundle(
                repo_root,
                "2026-04-20-dry-run-dirty-rules",
                defaults_path=defaults_path,
            )

            meta = json.loads((bundle_dir / "meta.json").read_text())
            self.assertEqual(meta["pinned_rules_ref"], {"inline": "# Rules\n\n- Dirty override.\n"})

    def test_initialize_bundle_fails_when_required_template_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            seed_template(repo_root)
            seed_pinned_rules(repo_root)
            defaults_path = write_defaults(repo_root)
            (repo_root / "observations" / "sessions" / "_template" / "summary.md").unlink()

            with self.assertRaisesRegex(FileNotFoundError, "template missing required files: summary.md"):
                initialize_bundle(
                    repo_root,
                    "2026-04-20-dry-run-missing-template",
                    defaults_path=defaults_path,
                )

if __name__ == "__main__":
    unittest.main()
