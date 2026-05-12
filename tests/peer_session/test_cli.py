from __future__ import annotations

import contextlib
import io
import json
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

    def test_intervention_add_and_validate_return_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            seed_template(repo_root)
            seed_pinned_rules(repo_root)
            write_defaults(repo_root)
            main(
                ["init", "2026-05-05-cli-interventions", "--defaults", "observations/sessions/defaults.toml"],
                repo_root=repo_root,
            )
            bundle_dir = repo_root / "observations" / "sessions" / "2026-05-05-cli-interventions"
            (bundle_dir / "transcript.md").write_text(
                "- 2026-05-05T17:00:30Z Vigil: First turn.\n"
            )

            exit_code = main(
                [
                    "intervention",
                    "add",
                    "2026-05-05-cli-interventions",
                    "--type",
                    "clarification",
                    "--reason",
                    "Operator asked for a restatement.",
                    "--at",
                    "2026-05-05T17:00:45Z",
                    "--actor",
                    "Zoe",
                    "--attribution",
                    "operator_directed",
                    "--target-turn",
                    "2026-05-05T17:00:30Z",
                ],
                repo_root=repo_root,
            )

            self.assertEqual(exit_code, 0)
            records = json.loads((bundle_dir / "interventions.json").read_text())
            self.assertEqual(records[0]["id"], "iv-001")

            self.assertEqual(
                main(["intervention", "validate", "2026-05-05-cli-interventions"], repo_root=repo_root),
                0,
            )

    def test_help_surface_exposes_init_intervention_tally_rollup(self) -> None:
        help_text = build_parser().format_help()

        self.assertIn("init", help_text)
        self.assertIn("intervention", help_text)
        self.assertIn("tally", help_text)
        self.assertIn("rollup", help_text)


class CliTallyDispatchTest(unittest.TestCase):
    def test_tally_dispatch_writes_kpi_and_returns_zero(self) -> None:
        from tests.peer_session.test_support import install_fixture_bundle

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_minimal")
            exit_code = main(["tally", "session-minimal"], repo_root=repo_root)
            self.assertEqual(exit_code, 0)
            kpi_path = repo_root / "observations" / "sessions" / "session-minimal" / "kpi.json"
            self.assertTrue(kpi_path.is_file())


class CliRollupDispatchTest(unittest.TestCase):
    def test_rollup_dispatch_writes_artifact_and_pointer(self) -> None:
        from tests.peer_session.test_support import install_fixture_bundle

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            for sid in ("sess-a", "sess-b", "sess-c"):
                install_fixture_bundle(repo_root, "session_minimal", session_id=sid)
                self.assertEqual(main(["tally", sid], repo_root=repo_root), 0)

            exit_code = main(["rollup"], repo_root=repo_root)
            self.assertEqual(exit_code, 0)
            artifacts = list((repo_root / "observations").glob("poc-exit-*.md"))
            self.assertEqual(len(artifacts), 1)
            pointer = repo_root / "observations" / "poc-exit.md"
            self.assertTrue(pointer.is_symlink())


if __name__ == "__main__":
    unittest.main()
