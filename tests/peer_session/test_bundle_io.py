from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tests.peer_session.test_support import install_fixture_bundle
from tools.peer_session.bundle_io import (
    BundleIncompleteError,
    compute_inputs_hash,
    count_peer_turns,
    format_iso8601_field,
    format_iso8601_filename,
    is_drift_audit_placeholder,
    peer_handles_from_meta,
    read_bundle,
)


class ReadBundleTest(unittest.TestCase):
    def test_read_bundle_succeeds_on_complete_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            inputs = read_bundle(bundle)

            self.assertEqual(inputs.session_id, "session-minimal")
            self.assertEqual(inputs.meta["session_id"], "session-minimal")
            self.assertEqual(inputs.meta["closed_at"], "2026-04-21T15:30:00Z")
            self.assertEqual(len(inputs.interventions), 1)
            self.assertEqual(inputs.drift_audit["verdict"], "no_drift")
            self.assertIn("Verdicts", inputs.summary_text)
            self.assertIsNotNone(inputs.fresh_reader_audit)
            self.assertEqual(inputs.fresh_reader_audit["verdict"], "pass")

    def test_read_bundle_tolerates_missing_fresh_reader_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_missing_fra")
            inputs = read_bundle(bundle)
            self.assertIsNone(inputs.fresh_reader_audit)

    def test_read_bundle_refuses_when_required_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            (bundle / "interventions.json").unlink()
            with self.assertRaises(BundleIncompleteError) as ctx:
                read_bundle(bundle)
            self.assertIn("interventions.json", str(ctx.exception))

    def test_read_bundle_refuses_on_empty_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            (bundle / "summary.md").write_text("\n")
            with self.assertRaises(BundleIncompleteError):
                read_bundle(bundle)


class InputsHashTest(unittest.TestCase):
    def test_inputs_hash_is_deterministic_for_unchanged_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            inputs_a = read_bundle(bundle)
            inputs_b = read_bundle(bundle)
            self.assertEqual(compute_inputs_hash(inputs_a), compute_inputs_hash(inputs_b))

    def test_inputs_hash_changes_when_interventions_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            before = compute_inputs_hash(read_bundle(bundle))

            interventions = json.loads((bundle / "interventions.json").read_text())
            interventions.append(
                {
                    "id": "iv-002",
                    "taxonomy_version": "poc-v1",
                    "at": "2026-04-21T15:20:00Z",
                    "type": "drift_catch",
                    "reason": "operator flagged a drift episode",
                    "attribution": "operator_directed",
                    "actor": "zoe",
                    "target": {"kind": "session"},
                }
            )
            (bundle / "interventions.json").write_text(json.dumps(interventions, indent=2) + "\n")
            after = compute_inputs_hash(read_bundle(bundle))
            self.assertNotEqual(before, after)

    def test_inputs_hash_changes_when_summary_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            bundle = install_fixture_bundle(repo_root, "session_minimal")
            before = compute_inputs_hash(read_bundle(bundle))
            (bundle / "summary.md").write_text(
                (bundle / "summary.md").read_text() + "\n\n## Addendum\n\nlate edit\n"
            )
            after = compute_inputs_hash(read_bundle(bundle))
            self.assertNotEqual(before, after)


class TimestampFormatTest(unittest.TestCase):
    def test_format_iso8601_field_seconds_precision(self) -> None:
        dt = datetime(2026, 4, 21, 14, 30, 22, 123456, tzinfo=timezone.utc)
        self.assertEqual(format_iso8601_field(dt), "2026-04-21T14:30:22Z")

    def test_format_iso8601_filename_no_colons(self) -> None:
        dt = datetime(2026, 4, 21, 14, 30, 22, tzinfo=timezone.utc)
        self.assertEqual(format_iso8601_filename(dt), "20260421T143022Z")


class HelperFunctionsTest(unittest.TestCase):
    def test_is_drift_audit_placeholder(self) -> None:
        self.assertTrue(is_drift_audit_placeholder({"status": "pending-phase-2"}))
        self.assertFalse(is_drift_audit_placeholder({"verdict": "no_drift"}))

    def test_peer_handles_from_meta_skips_operator_and_fill_ins(self) -> None:
        meta = {
            "participants": [
                {"handle": "alpha", "role": "peer"},
                {"handle": "beta", "role": "peer"},
                {"handle": "zoe", "role": "operator"},
                {"handle": "[FILL IN: peer-3 handle]", "role": "peer"},
            ]
        }
        self.assertEqual(peer_handles_from_meta(meta), {"alpha", "beta"})

    def test_count_peer_turns_matches_template_format(self) -> None:
        transcript = (
            "# Session transcript — s\n\n"
            "## 2026-04-21T15:01:00Z · alpha\n\nFirst turn.\n\n"
            "## 2026-04-21T15:03:00Z · beta\n\nSecond turn.\n\n"
            "## 2026-04-21T15:05:00Z · zoe\n\nOperator turn.\n\n"
            "## 2026-04-21T15:07:00Z · alpha\n\nThird peer turn.\n"
        )
        self.assertEqual(count_peer_turns(transcript, {"alpha", "beta"}), 3)
        self.assertEqual(count_peer_turns(transcript, set()), 0)


if __name__ == "__main__":
    unittest.main()
