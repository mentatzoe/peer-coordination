from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.peer_session.test_support import install_fixture_bundle
from tools.peer_session.bundle_io import read_bundle
from tools.peer_session.per_session_clear import (
    AMBIGUOUS,
    CLEARED,
    NOT_CLEARED,
    compute_per_session_clear,
    derive_intervention_load,
)


def _judge(result: dict, key: str) -> str:
    return result["breakdown"][key]["judgment"]


class ComputePerSessionClearTest(unittest.TestCase):
    def test_cleared_bundle_resolves_to_cleared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_minimal")
            inputs = read_bundle(bundle)
            rate, load_pass, reason = derive_intervention_load(inputs)
            result = compute_per_session_clear(
                inputs, intervention_load_pass=load_pass, intervention_load_reason=reason
            )
            self.assertEqual(result["per_session_clear"], CLEARED)
            for sub in result["breakdown"].values():
                self.assertEqual(sub["judgment"], CLEARED)
            self.assertIsNotNone(rate)
            self.assertEqual(load_pass, True)

    def test_missing_fra_marks_h2_fresh_reader_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_missing_fra")
            inputs = read_bundle(bundle)
            _, load_pass, reason = derive_intervention_load(inputs)
            result = compute_per_session_clear(
                inputs, intervention_load_pass=load_pass, intervention_load_reason=reason
            )
            self.assertEqual(_judge(result, "h2_fresh_reader"), AMBIGUOUS)
            self.assertEqual(result["per_session_clear"], AMBIGUOUS)

    def test_inconclusive_fra_marks_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_ambiguous")
            inputs = read_bundle(bundle)
            _, load_pass, reason = derive_intervention_load(inputs)
            result = compute_per_session_clear(
                inputs, intervention_load_pass=load_pass, intervention_load_reason=reason
            )
            self.assertEqual(_judge(result, "h2_fresh_reader"), AMBIGUOUS)
            self.assertEqual(result["per_session_clear"], AMBIGUOUS)

    def test_drift_placeholder_marks_h2_drift_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_placeholder_drift")
            inputs = read_bundle(bundle)
            _, load_pass, reason = derive_intervention_load(inputs)
            result = compute_per_session_clear(
                inputs, intervention_load_pass=load_pass, intervention_load_reason=reason
            )
            self.assertEqual(_judge(result, "h2_drift"), AMBIGUOUS)
            self.assertEqual(result["per_session_clear"], AMBIGUOUS)

    def test_zero_turn_session_makes_intervention_load_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_zero_turns")
            inputs = read_bundle(bundle)
            rate, load_pass, reason = derive_intervention_load(inputs)
            self.assertIsNone(rate)
            self.assertIsNone(load_pass)
            self.assertIn("zero peer turns", reason or "")
            result = compute_per_session_clear(
                inputs, intervention_load_pass=load_pass, intervention_load_reason=reason
            )
            self.assertEqual(_judge(result, "h1_intervention_load"), AMBIGUOUS)

    def test_not_cleared_summary_verdict_yields_not_cleared_composite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_minimal")
            summary = (bundle / "summary.md").read_text()
            (bundle / "summary.md").write_text(
                summary.replace("**H1 stability**: `clear`", "**H1 stability**: `fail`")
            )
            inputs = read_bundle(bundle)
            _, load_pass, reason = derive_intervention_load(inputs)
            result = compute_per_session_clear(
                inputs, intervention_load_pass=load_pass, intervention_load_reason=reason
            )
            self.assertEqual(_judge(result, "h1_stable_coordination"), NOT_CLEARED)
            self.assertEqual(result["per_session_clear"], NOT_CLEARED)

    def test_composite_precedence_not_cleared_beats_ambiguous(self) -> None:
        """If any sub-judgment is `not-cleared`, the composite is `not-cleared`."""
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_missing_fra")
            summary = (bundle / "summary.md").read_text()
            (bundle / "summary.md").write_text(
                summary.replace(
                    "**H1 complementarity**: `clear`", "**H1 complementarity**: `fail`"
                )
            )
            inputs = read_bundle(bundle)
            _, load_pass, reason = derive_intervention_load(inputs)
            result = compute_per_session_clear(
                inputs, intervention_load_pass=load_pass, intervention_load_reason=reason
            )
            self.assertEqual(_judge(result, "h2_fresh_reader"), AMBIGUOUS)
            self.assertEqual(_judge(result, "h1_complementarity"), NOT_CLEARED)
            self.assertEqual(result["per_session_clear"], NOT_CLEARED)


class InterventionLoadTest(unittest.TestCase):
    def test_load_below_threshold_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_minimal")
            inputs = read_bundle(bundle)
            rate, load_pass, _ = derive_intervention_load(inputs)
            self.assertEqual(load_pass, True)
            self.assertLessEqual(rate, 0.5)

    def test_load_above_threshold_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = install_fixture_bundle(Path(tmp), "session_minimal")
            interventions = json.loads((bundle / "interventions.json").read_text())
            for n in range(3):
                interventions.append(
                    {
                        "id": f"iv-{n + 2:03d}",
                        "taxonomy_version": "poc-v1",
                        "at": f"2026-04-21T15:{n + 20}:00Z",
                        "type": "directive_redirect",
                        "reason": "test load",
                        "attribution": "operator_directed",
                        "actor": "zoe",
                        "target": {"kind": "session"},
                    }
                )
            (bundle / "interventions.json").write_text(json.dumps(interventions, indent=2) + "\n")
            inputs = read_bundle(bundle)
            rate, load_pass, _ = derive_intervention_load(inputs)
            self.assertGreater(rate, 0.5)
            self.assertEqual(load_pass, False)


if __name__ == "__main__":
    unittest.main()
