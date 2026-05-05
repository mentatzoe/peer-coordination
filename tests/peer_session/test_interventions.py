from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.peer_session.test_support import seed_pinned_rules, seed_template, write_defaults
from tools.peer_session.bundle_init import initialize_bundle
from tools.peer_session.interventions import (
    InterventionValidationError,
    add_intervention,
    directive_signal_count,
    resolve_citation,
    validate_interventions_file,
)


class InterventionWorkflowTest(unittest.TestCase):
    def test_add_interventions_generates_ids_and_valid_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, session_id = self._seed_bundle(Path(tmp))

            first = add_intervention(
                repo_root,
                session_id,
                intervention_type="clarification",
                reason="Operator asked Vigil to restate the next step.",
                at="2026-05-05T17:00:45Z",
                actor="Zoe",
                attribution="operator_directed",
                target_turn="2026-05-05T17:00:30Z",
            )
            second = add_intervention(
                repo_root,
                session_id,
                intervention_type="directive_redirect",
                reason="Operator redirected both peers back to the seed after a loop.",
                at="2026-05-05T17:02:00Z",
                actor="Zoe",
                attribution="operator_directed",
                start_turn="2026-05-05T17:01:00Z",
                end_turn="2026-05-05T17:01:45Z",
            )

            self.assertEqual(first["id"], "iv-001")
            self.assertEqual(first["target"], {"kind": "turn", "turn_ref": "2026-05-05T17:00:30Z"})
            self.assertEqual(second["id"], "iv-002")
            self.assertEqual(second["target"]["kind"], "span")

            records = validate_interventions_file(
                repo_root / "observations" / "sessions" / session_id / "interventions.json",
                transcript_path=repo_root / "observations" / "sessions" / session_id / "transcript.md",
            )
            self.assertEqual(len(records), 2)
            self.assertEqual(resolve_citation(records, "interventions.json#iv-002"), second)
            self.assertEqual(directive_signal_count(records), 1)

    def test_add_intervention_rejects_invalid_type_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, session_id = self._seed_bundle(Path(tmp))
            log_path = repo_root / "observations" / "sessions" / session_id / "interventions.json"

            with self.assertRaisesRegex(InterventionValidationError, "type is not in the poc-v1 taxonomy"):
                add_intervention(
                    repo_root,
                    session_id,
                    intervention_type="nudge",
                    reason="Invalid taxonomy.",
                    at="2026-05-05T17:00:45Z",
                    actor="Zoe",
                    attribution="operator_directed",
                    target_turn="2026-05-05T17:00:30Z",
                )

            self.assertEqual(json.loads(log_path.read_text()), [])

    def test_add_intervention_rejects_target_not_in_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, session_id = self._seed_bundle(Path(tmp))

            with self.assertRaisesRegex(InterventionValidationError, "does not appear in transcript"):
                add_intervention(
                    repo_root,
                    session_id,
                    intervention_type="clarification",
                    reason="Operator asked for clarification.",
                    at="2026-05-05T17:00:45Z",
                    actor="Zoe",
                    attribution="operator_directed",
                    target_turn="2026-05-05T17:09:30Z",
                )

    def test_add_intervention_rejects_malformed_span(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, session_id = self._seed_bundle(Path(tmp))

            with self.assertRaisesRegex(InterventionValidationError, "start_turn must be <= end_turn"):
                add_intervention(
                    repo_root,
                    session_id,
                    intervention_type="directive_redirect",
                    reason="Operator redirected a loop.",
                    at="2026-05-05T17:02:00Z",
                    actor="Zoe",
                    attribution="operator_directed",
                    start_turn="2026-05-05T17:01:45Z",
                    end_turn="2026-05-05T17:01:00Z",
                )

    def _seed_bundle(self, repo_root: Path) -> tuple[Path, str]:
        seed_template(repo_root)
        seed_pinned_rules(repo_root)
        defaults_path = write_defaults(repo_root)
        session_id = "2026-05-05-intervention-test"
        bundle_dir = initialize_bundle(repo_root, session_id, defaults_path=defaults_path)
        (bundle_dir / "transcript.md").write_text(
            "# Transcript\n\n"
            "- 2026-05-05T17:00:30Z Vigil: I think we should split the review.\n"
            "- 2026-05-05T17:01:00Z Dalgos: Maybe we should revisit the whole roadmap.\n"
            "- 2026-05-05T17:01:45Z Vigil: Agreed, we are drifting from the seed.\n"
        )
        (bundle_dir / "interventions.json").write_text("[]\n")
        return repo_root, session_id


if __name__ == "__main__":
    unittest.main()
