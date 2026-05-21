from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tests.peer_session.test_support import install_fixture_bundle
from tools.peer_session.tally import (
    EXIT_INCOMPLETE,
    EXIT_INVALID,
    EXIT_OK,
    EXIT_UNCLOSED,
    run_tally,
)


def _stable_now() -> datetime:
    return datetime(2026, 4, 21, 17, 0, 0, tzinfo=timezone.utc)


class TallyContractTest(unittest.TestCase):
    def _run(self, repo_root: Path, session_id: str, *, now: datetime | None = None) -> int:
        sessions_root = repo_root / "observations" / "sessions"
        return run_tally(session_id, sessions_root=sessions_root, now=now or _stable_now())

    def test_happy_path_writes_kpi_with_cleared_judgment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_minimal")
            exit_code = self._run(repo_root, "session-minimal")
            self.assertEqual(exit_code, EXIT_OK)
            kpi_path = repo_root / "observations" / "sessions" / "session-minimal" / "kpi.json"
            self.assertTrue(kpi_path.is_file())
            kpi = json.loads(kpi_path.read_text())
            self.assertEqual(kpi["session_id"], "session-minimal")
            self.assertEqual(kpi["per_session_clear"], "cleared")
            self.assertEqual(kpi["intervention_count"], 1)
            self.assertEqual(kpi["drift_audit_verdict"], "no_drift")
            self.assertEqual(kpi["zero_turn_session"], False)
            self.assertEqual(
                sorted(kpi["intervention_type_tally"].keys()),
                [
                    "clarification",
                    "close_or_resume",
                    "directive_redirect",
                    "drift_catch",
                    "other",
                    "safety_stop",
                ],
            )
            self.assertEqual(kpi["intervention_type_tally"]["clarification"], 1)

    def test_idempotent_re_run_modulo_tallied_at(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_minimal")
            self._run(repo_root, "session-minimal", now=_stable_now())
            kpi_path = repo_root / "observations" / "sessions" / "session-minimal" / "kpi.json"
            first = json.loads(kpi_path.read_text())
            later = datetime(2026, 4, 21, 18, 0, 0, tzinfo=timezone.utc)
            self._run(repo_root, "session-minimal", now=later)
            second = json.loads(kpi_path.read_text())
            first.pop("tallied_at")
            second.pop("tallied_at")
            self.assertEqual(first, second)

    def test_inputs_hash_changes_when_inputs_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            self._run(repo_root, "session-minimal")
            kpi_path = bundle / "kpi.json"
            first = json.loads(kpi_path.read_text())["inputs_hash"]

            interventions = json.loads((bundle / "interventions.json").read_text())
            interventions.append(
                {
                    "id": "iv-002",
                    "taxonomy_version": "poc-v1",
                    "at": "2026-04-21T15:25:00Z",
                    "type": "drift_catch",
                    "reason": "operator note",
                    "attribution": "operator_directed",
                    "actor": "zoe",
                    "target": {"kind": "session"},
                }
            )
            (bundle / "interventions.json").write_text(json.dumps(interventions, indent=2) + "\n")
            self._run(repo_root, "session-minimal")
            second = json.loads(kpi_path.read_text())["inputs_hash"]
            self.assertNotEqual(first, second)

    def test_missing_fresh_reader_audit_yields_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_missing_fra")
            exit_code = self._run(repo_root, "session-missing-fra")
            self.assertEqual(exit_code, EXIT_OK)
            kpi = json.loads(
                (
                    repo_root
                    / "observations"
                    / "sessions"
                    / "session-missing-fra"
                    / "kpi.json"
                ).read_text()
            )
            self.assertEqual(kpi["per_session_clear"], "ambiguous")
            self.assertEqual(
                kpi["per_session_clear_breakdown"]["h2_fresh_reader"]["judgment"],
                "ambiguous",
            )

    def test_drift_placeholder_yields_ambiguous_h2_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_placeholder_drift")
            exit_code = self._run(repo_root, "session-placeholder-drift")
            self.assertEqual(exit_code, EXIT_OK)
            kpi = json.loads(
                (
                    repo_root
                    / "observations"
                    / "sessions"
                    / "session-placeholder-drift"
                    / "kpi.json"
                ).read_text()
            )
            self.assertEqual(
                kpi["per_session_clear_breakdown"]["h2_drift"]["judgment"],
                "ambiguous",
            )
            self.assertIsNone(kpi["drift_audit_verdict"])
            self.assertIn(
                "drift-audit.json is the spec-001 Phase-2-pending placeholder",
                kpi["notes"],
            )

    def test_zero_turns_yields_null_rate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_zero_turns")
            exit_code = self._run(repo_root, "session-zero-turns")
            self.assertEqual(exit_code, EXIT_OK)
            kpi = json.loads(
                (
                    repo_root
                    / "observations"
                    / "sessions"
                    / "session-zero-turns"
                    / "kpi.json"
                ).read_text()
            )
            self.assertIsNone(kpi["intervention_rate_per_turn"])
            self.assertEqual(kpi["zero_turn_session"], True)

    def test_bundle_incomplete_refuses_with_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            (bundle / "interventions.json").unlink()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self._run(repo_root, "session-minimal")
            self.assertEqual(exit_code, EXIT_INCOMPLETE)
            self.assertIn("interventions.json", stderr.getvalue())
            self.assertFalse((bundle / "kpi.json").exists())

    def test_unclosed_session_refuses_with_exit_three(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_unclosed")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self._run(repo_root, "session-unclosed")
            self.assertEqual(exit_code, EXIT_UNCLOSED)
            self.assertIn("unclosed", stderr.getvalue())

    def test_invalid_intervention_type_refuses_with_exit_four(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            install_fixture_bundle(repo_root, "session_bad_intervention")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self._run(repo_root, "session-bad-intervention")
            self.assertEqual(exit_code, EXIT_INVALID)
            self.assertIn("interventions.json", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
