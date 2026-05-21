from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tests.peer_session.test_support import install_fixture_bundle
from tools.peer_session.bundle_io import compute_inputs_hash, read_bundle
from tools.peer_session.rollup import EXIT_HARD_GAP, EXIT_OK, run_rollup
from tools.peer_session.tally import run_tally


def _stable_now(offset_hours: int = 0) -> datetime:
    return datetime(2026, 4, 22, 17, 0, 0, tzinfo=timezone.utc) + timedelta(hours=offset_hours)


def _seed_counted_set(
    repo_root: Path,
    *,
    session_ids: list[str],
    fixture_per_session: dict[str, str] | None = None,
) -> None:
    fixture_per_session = fixture_per_session or {}
    for sid in session_ids:
        fixture = fixture_per_session.get(sid, "session_minimal")
        install_fixture_bundle(repo_root, fixture, session_id=sid)


def _tally_all(repo_root: Path, session_ids: list[str]) -> None:
    sessions_root = repo_root / "observations" / "sessions"
    for sid in session_ids:
        rc = run_tally(sid, sessions_root=sessions_root, now=_stable_now(offset_hours=-1))
        assert rc == 0, f"tally failed for {sid}: exit={rc}"


class RollupContractTest(unittest.TestCase):
    def _run(self, repo_root: Path, *, now: datetime | None = None) -> int:
        return run_rollup(
            observations_root=repo_root / "observations",
            now=now or _stable_now(),
        )

    def test_happy_path_three_cleared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(repo_root, session_ids=ids)
            _tally_all(repo_root, ids)
            exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_OK)
            obs = repo_root / "observations"
            artifact = next(obs.glob("poc-exit-*.md"))
            content = artifact.read_text()
            self.assertIn("Ratifiability**: ratifiable", content)
            self.assertIn("Cleared count**: 3/3 (threshold 3/3)", content)
            self.assertTrue((obs / "poc-exit.md").is_symlink())
            self.assertEqual((obs / "poc-exit.md").resolve().name, artifact.name)

    def test_happy_path_four_sessions_three_cleared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c", "sess-d"]
            _seed_counted_set(repo_root, session_ids=ids)
            # Flip session-d's summary verdict to fail to make it not-cleared.
            bundle_d = repo_root / "observations" / "sessions" / "sess-d"
            summary = (bundle_d / "summary.md").read_text()
            (bundle_d / "summary.md").write_text(
                summary.replace("**H1 stability**: `clear`", "**H1 stability**: `fail`")
            )
            _tally_all(repo_root, ids)
            exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_OK)
            artifact = next((repo_root / "observations").glob("poc-exit-*.md"))
            content = artifact.read_text()
            self.assertIn("Cleared count**: 3/4 (threshold 3/4)", content)
            self.assertIn("Ratifiability**: ratifiable", content)
            self.assertIn("H1 verdict**: pass", content)

    def test_ambiguous_session_yields_draft_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(
                repo_root,
                session_ids=ids,
                fixture_per_session={"sess-c": "session_ambiguous"},
            )
            _tally_all(repo_root, ids)
            exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_OK)
            artifact = next((repo_root / "observations").glob("poc-exit-*.md"))
            content = artifact.read_text()
            self.assertIn("Ratifiability**: draft, not ratifiable", content)
            self.assertIn("`sess-c`", content)
            self.assertIn("Ambiguous sessions", content)
            # FR-014 regression: 3 counted sessions is in-range; do NOT report
            # out-of-range based on the decidable count.
            self.assertNotIn("Out-of-range", content)
            self.assertNotIn("Out of range", content)

    def test_fresh_reader_pass_rate_denominator_is_counted_total(self) -> None:
        """Spec FR-012: denominator must equal counted_session_total — 2 pass + 1
        ambiguous reports 2/3, not 2/2."""
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(
                repo_root,
                session_ids=ids,
                fixture_per_session={"sess-c": "session_ambiguous"},
            )
            _tally_all(repo_root, ids)
            self._run(repo_root)
            content = next((repo_root / "observations").glob("poc-exit-*.md")).read_text()
            self.assertIn("Fresh-reader pass-rate**: 2/3", content)

    def test_missing_kpi_json_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(repo_root, session_ids=ids)
            _tally_all(repo_root, ids)
            (repo_root / "observations" / "sessions" / "sess-c" / "kpi.json").unlink()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_HARD_GAP)
            self.assertIn("kpi.json missing", stderr.getvalue())
            self.assertFalse((repo_root / "observations" / "poc-exit.md").exists())

    def test_missing_fresh_reader_audit_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(repo_root, session_ids=ids)
            _tally_all(repo_root, ids)
            (
                repo_root
                / "observations"
                / "sessions"
                / "sess-c"
                / "fresh-reader-audit.json"
            ).unlink()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_HARD_GAP)
            self.assertIn("fresh-reader-audit.json missing", stderr.getvalue())

    def test_stale_kpi_json_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(repo_root, session_ids=ids)
            _tally_all(repo_root, ids)
            bundle_c = repo_root / "observations" / "sessions" / "sess-c"
            (bundle_c / "interventions.json").write_text("[]\n")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_HARD_GAP)
            self.assertIn("stale", stderr.getvalue())

    def test_session_id_collision_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(repo_root, session_ids=ids)
            _tally_all(repo_root, ids)
            # Force session_id collision: rewrite sess-b/meta.json.session_id to
            # "sess-a" AND refresh sess-b/kpi.json.inputs_hash so the stale-hash
            # gate does not fire ahead of the collision gate.
            bundle_b = repo_root / "observations" / "sessions" / "sess-b"
            meta = json.loads((bundle_b / "meta.json").read_text())
            meta["session_id"] = "sess-a"
            (bundle_b / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
            kpi = json.loads((bundle_b / "kpi.json").read_text())
            kpi["inputs_hash"] = compute_inputs_hash(read_bundle(bundle_b))
            (bundle_b / "kpi.json").write_text(json.dumps(kpi, indent=2) + "\n")

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_HARD_GAP)
            self.assertIn("collision", stderr.getvalue())

    def test_out_of_range_two_sessions_marks_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b"]
            _seed_counted_set(repo_root, session_ids=ids)
            _tally_all(repo_root, ids)
            exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_OK)
            artifact = next((repo_root / "observations").glob("poc-exit-*.md"))
            content = artifact.read_text()
            self.assertIn("Ratifiability**: draft, not ratifiable", content)
            self.assertIn("Out of range", content)
            self.assertIn("counted_session_total=2", content)

    def test_template_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(repo_root, session_ids=ids)
            # Seed a _template/ directory that would break the rollup if discovered.
            template_dir = repo_root / "observations" / "sessions" / "_template"
            template_dir.mkdir(parents=True)
            (template_dir / "meta.json").write_text("{\"this\": \"is invalid\"}")
            _tally_all(repo_root, ids)
            exit_code = self._run(repo_root)
            self.assertEqual(exit_code, EXIT_OK)
            artifact = next((repo_root / "observations").glob("poc-exit-*.md"))
            content = artifact.read_text()
            self.assertIn("Counted-session total**: 3", content)

    def test_second_rollup_updates_pointer_preserves_prior_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            ids = ["sess-a", "sess-b", "sess-c"]
            _seed_counted_set(repo_root, session_ids=ids)
            _tally_all(repo_root, ids)
            self._run(repo_root, now=_stable_now())
            first_artifact = next((repo_root / "observations").glob("poc-exit-*.md"))
            first_name = first_artifact.name

            self._run(repo_root, now=_stable_now(offset_hours=1))
            artifacts = sorted(
                p.name for p in (repo_root / "observations").glob("poc-exit-*.md")
            )
            self.assertEqual(len(artifacts), 2)
            self.assertIn(first_name, artifacts)
            self.assertNotEqual(first_name, artifacts[-1])
            pointer = repo_root / "observations" / "poc-exit.md"
            self.assertTrue(pointer.is_symlink())
            self.assertEqual(pointer.resolve().name, artifacts[-1])


if __name__ == "__main__":
    unittest.main()
