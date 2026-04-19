from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.peer_session.test_bundle_init import InitializeBundleTest
from tools.peer_session.cli import main


class CliInitTest(unittest.TestCase):
    def test_main_returns_zero_for_successful_init(self) -> None:
        helper = InitializeBundleTest()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            helper._seed_template(repo_root)
            helper._seed_pinned_rules(repo_root)
            helper._write_defaults(repo_root)

            exit_code = main(
                ["init", "2026-04-20-dry-run-two", "--defaults", "observations/sessions/defaults.toml"],
                repo_root=repo_root,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((repo_root / "observations" / "sessions" / "2026-04-20-dry-run-two").is_dir())


if __name__ == "__main__":
    unittest.main()
