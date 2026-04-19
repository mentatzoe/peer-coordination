from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from tests.peer_session.test_support import seed_pinned_rules, seed_template, write_defaults
from tools.peer_session.cli import build_parser, main


class CliInitTest(unittest.TestCase):
    def test_main_returns_zero_for_successful_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            seed_template(repo_root)
            seed_pinned_rules(repo_root)
            write_defaults(repo_root)

            exit_code = main(
                ["init", "2026-04-20-dry-run-two", "--defaults", "observations/sessions/defaults.toml"],
                repo_root=repo_root,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((repo_root / "observations" / "sessions" / "2026-04-20-dry-run-two").is_dir())

    def test_main_returns_one_for_existing_directory_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            seed_template(repo_root)
            seed_pinned_rules(repo_root)
            write_defaults(repo_root)
            (repo_root / "observations" / "sessions" / "2026-04-20-dry-run-two").mkdir(parents=True)

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = main(
                    ["init", "2026-04-20-dry-run-two", "--defaults", "observations/sessions/defaults.toml"],
                    repo_root=repo_root,
                )

            self.assertEqual(exit_code, 1)
            self.assertIn("session bundle already exists", stderr.getvalue())

    def test_help_surface_exposes_init_only(self) -> None:
        help_text = build_parser().format_help()

        self.assertIn("{init}", help_text)
        self.assertNotIn("validate", help_text)


if __name__ == "__main__":
    unittest.main()
