"""Cross-session POC-exit rollup — `peer-session rollup`."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.peer_session.bundle_io import (
    BundleIncompleteError,
    BundleSchemaError,
    compute_inputs_hash,
    format_iso8601_field,
    format_iso8601_filename,
    read_bundle,
)

EXIT_OK = 0
EXIT_UNEXPECTED = 1
EXIT_HARD_GAP = 2


@dataclass
class _SessionRecord:
    session_id: str
    bundle_dir: Path
    kpi: dict[str, Any]
    fresh_reader_audit: dict[str, Any]


@dataclass
class _RollupResult:
    timestamp: datetime
    counted_session_total: int
    cleared_count: int
    not_cleared_count: int
    ambiguous_count: int
    sessions: list[_SessionRecord]
    h2_fresh_reader_pass_count: int
    drift_verdicts: list[tuple[str, Any]]
    ambiguous_sessions: list[str] = field(default_factory=list)
    out_of_range: bool = False
    ratifiability: str = "ratifiable"


def run_rollup(
    *,
    observations_root: Path,
    now: datetime | None = None,
) -> int:
    sessions_root = observations_root / "sessions"
    try:
        records, errors = _discover_sessions(sessions_root)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED

    if errors:
        print("rollup refused: hard data gap(s) found:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return EXIT_HARD_GAP

    collision_error = _detect_session_id_collisions(records)
    if collision_error:
        print(f"rollup refused: {collision_error}", file=sys.stderr)
        return EXIT_HARD_GAP

    now = now or datetime.now(UTC)
    result = _aggregate(records, now=now)

    artifact_text = _render_artifact(result)
    filename = f"poc-exit-{format_iso8601_filename(result.timestamp)}.md"
    artifact_path = observations_root / filename
    artifact_path.write_text(artifact_text)

    pointer_path = observations_root / "poc-exit.md"
    _update_pointer(pointer_path, filename)

    print(f"wrote {artifact_path}")
    print(f"ratifiability: {result.ratifiability}")
    if result.out_of_range:
        print(f"out-of-range: counted_session_total={result.counted_session_total}")
    elif result.counted_session_total > 0:
        threshold = _h1_threshold(result.counted_session_total)
        if threshold is not None:
            print(
                f"H1 cleared {result.cleared_count}/{result.counted_session_total} "
                f"(threshold: {threshold})"
            )
    if result.ambiguous_sessions:
        print(f"ambiguous sessions: {', '.join(result.ambiguous_sessions)}")
    return EXIT_OK


def _discover_sessions(sessions_root: Path) -> tuple[list[_SessionRecord], list[str]]:
    if not sessions_root.is_dir():
        return [], [f"observations/sessions/ does not exist at {sessions_root}"]

    records: list[_SessionRecord] = []
    errors: list[str] = []

    for entry in sorted(sessions_root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(("_", ".")):
            continue
        session_id = entry.name

        try:
            inputs = read_bundle(entry)
        except (BundleIncompleteError, BundleSchemaError) as exc:
            errors.append(f"{session_id}: bundle invalid: {exc}")
            continue

        kpi_path = entry / "kpi.json"
        if not kpi_path.is_file():
            errors.append(f"{session_id}: kpi.json missing")
            continue
        try:
            kpi = json.loads(kpi_path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{session_id}: kpi.json is not valid JSON: {exc}")
            continue
        if not isinstance(kpi, dict):
            errors.append(f"{session_id}: kpi.json must be a top-level object")
            continue

        if inputs.fresh_reader_audit is None:
            errors.append(f"{session_id}: fresh-reader-audit.json missing")
            continue

        recorded_hash = kpi.get("inputs_hash")
        current_hash = compute_inputs_hash(inputs)
        if recorded_hash != current_hash:
            errors.append(
                f"{session_id}: kpi.json is stale "
                f"(recorded inputs_hash {recorded_hash!r} does not match current {current_hash!r})"
            )
            continue

        records.append(
            _SessionRecord(
                session_id=session_id,
                bundle_dir=entry,
                kpi=kpi,
                fresh_reader_audit=inputs.fresh_reader_audit,
            )
        )

    return records, errors


def _detect_session_id_collisions(records: list[_SessionRecord]) -> str | None:
    seen: dict[str, str] = {}
    for record in records:
        meta_path = record.bundle_dir / "meta.json"
        try:
            meta = json.loads(meta_path.read_text())
        except json.JSONDecodeError as exc:
            return f"{record.session_id}: meta.json unreadable: {exc}"
        meta_sid = meta.get("session_id") if isinstance(meta, dict) else None
        if not isinstance(meta_sid, str):
            return f"{record.session_id}: meta.json.session_id missing/invalid"
        if meta_sid in seen:
            return (
                f"session_id collision: directories {seen[meta_sid]!r} and "
                f"{record.session_id!r} share meta.json.session_id {meta_sid!r}"
            )
        seen[meta_sid] = record.session_id
    return None


def _aggregate(records: list[_SessionRecord], *, now: datetime) -> _RollupResult:
    cleared = 0
    not_cleared = 0
    ambiguous = 0
    ambiguous_sessions: list[str] = []
    fra_pass = 0
    drift_verdicts: list[tuple[str, Any]] = []

    for record in records:
        psc = record.kpi.get("per_session_clear")
        if psc == "cleared":
            cleared += 1
        elif psc == "not-cleared":
            not_cleared += 1
        else:
            ambiguous += 1
            ambiguous_sessions.append(record.session_id)

        fra_verdict = record.fresh_reader_audit.get("verdict")
        if fra_verdict == "pass":
            fra_pass += 1

        drift_verdicts.append((record.session_id, record.kpi.get("drift_audit_verdict")))

    total = len(records)
    out_of_range = total < 3 or total > 5

    if ambiguous_sessions or out_of_range:
        ratifiability = "draft, not ratifiable"
    else:
        ratifiability = "ratifiable"

    return _RollupResult(
        timestamp=now,
        counted_session_total=total,
        cleared_count=cleared,
        not_cleared_count=not_cleared,
        ambiguous_count=ambiguous,
        sessions=records,
        h2_fresh_reader_pass_count=fra_pass,
        drift_verdicts=drift_verdicts,
        ambiguous_sessions=ambiguous_sessions,
        out_of_range=out_of_range,
        ratifiability=ratifiability,
    )


def _h1_threshold(total: int) -> str | None:
    if total == 3:
        return "3/3"
    if total == 4:
        return "3/4"
    if total == 5:
        return "4/5"
    return None


def _h1_pass(total: int, cleared: int) -> bool | None:
    if total == 3:
        return cleared == 3
    if total == 4:
        return cleared >= 3
    if total == 5:
        return cleared >= 4
    return None


def _render_artifact(result: _RollupResult) -> str:
    timestamp = format_iso8601_field(result.timestamp)
    lines: list[str] = []
    lines.append(f"# POC-exit rollup — {timestamp}")
    lines.append("")
    lines.append(f"- **Ratifiability**: {result.ratifiability}")
    lines.append(f"- **Counted-session total**: {result.counted_session_total}")
    lines.append("")

    lines.append("## H1 decision rule")
    lines.append("")
    if result.out_of_range:
        lines.append(
            f"- **Out of range**: counted_session_total={result.counted_session_total}; "
            f"H1 decision rule (3/3, 3/4, 4/5) does not apply."
        )
    else:
        threshold = _h1_threshold(result.counted_session_total) or "n/a"
        pass_flag = _h1_pass(result.counted_session_total, result.cleared_count)
        if result.ambiguous_count > 0:
            verdict = "pending (ambiguous sessions present)"
        elif pass_flag is True:
            verdict = "pass"
        elif pass_flag is False:
            verdict = "fail"
        else:
            verdict = "n/a"
        lines.append(
            f"- **Cleared count**: {result.cleared_count}/{result.counted_session_total} "
            f"(threshold {threshold})"
        )
        lines.append(f"- **H1 verdict**: {verdict}")
    lines.append("")

    lines.append("## H2 observations")
    lines.append("")
    if result.counted_session_total > 0:
        rate = result.h2_fresh_reader_pass_count / result.counted_session_total
        lines.append(
            f"- **Fresh-reader pass-rate**: "
            f"{result.h2_fresh_reader_pass_count}/{result.counted_session_total} "
            f"({rate:.2%})"
        )
    else:
        lines.append("- **Fresh-reader pass-rate**: n/a (no counted sessions)")
    lines.append("- **Drift verdicts**:")
    for sid, verdict in result.drift_verdicts:
        verdict_display = verdict if verdict is not None else "placeholder/absent"
        lines.append(f"    - `{sid}`: `{verdict_display}`")
    lines.append(
        "- **Episode-record completeness**: 100% (hard gate per FR-013 — "
        "any incomplete bundle would have refused the rollup)."
    )
    lines.append("")

    lines.append("## Per-session table")
    lines.append("")
    lines.append("| session_id | per_session_clear | breakdown |")
    lines.append("|---|---|---|")
    for record in result.sessions:
        breakdown = record.kpi.get("per_session_clear_breakdown", {})
        parts = []
        for key, abbrev in (
            ("h1_stable_coordination", "h1_sc"),
            ("h1_intervention_load", "h1_il"),
            ("h1_complementarity", "h1_cp"),
            ("h2_fresh_reader", "h2_fr"),
            ("h2_drift", "h2_d"),
            ("h2_episode_record", "h2_er"),
        ):
            entry = breakdown.get(key) or {}
            parts.append(f"{abbrev}={entry.get('judgment', '?')}")
        psc = record.kpi.get("per_session_clear", "?")
        lines.append(
            f"| `{record.session_id}` | `{psc}` | {', '.join(parts)} |"
        )
    lines.append("")

    if result.ambiguous_sessions:
        lines.append("## Ambiguous sessions")
        lines.append("")
        for record in result.sessions:
            if record.session_id not in result.ambiguous_sessions:
                continue
            lines.append(f"### `{record.session_id}`")
            lines.append("")
            breakdown = record.kpi.get("per_session_clear_breakdown", {}) or {}
            for key, entry in breakdown.items():
                if not isinstance(entry, dict):
                    continue
                if entry.get("judgment") == "ambiguous":
                    lines.append(
                        f"- `{key}` — {entry.get('reason') or 'no reason given'}"
                    )
            lines.append("")

    if result.out_of_range:
        lines.append("## Out-of-range note")
        lines.append("")
        if result.counted_session_total < 3:
            lines.append(
                f"- Only {result.counted_session_total} counted session(s) found; "
                "the H1 decision rule requires at least 3."
            )
        else:
            lines.append(
                f"- {result.counted_session_total} counted sessions found; "
                "the H1 decision rule applies only up to 5. Investigate whether the "
                "counted-session set has grown beyond its window."
            )
        lines.append("")

    lines.append("## Ratification gate")
    lines.append("")
    lines.append("> Operator fills this section on ratification per "
                 "`observations/kpi-rollup/WORKFLOW.md` §D.")
    lines.append("")
    lines.append("- **Ratified**: [ ] (mark `[x]` and add commit metadata)")
    lines.append("- **Ratifier**: [FILL IN: operator handle]")
    lines.append("- **Ratified at**: [FILL IN: ISO-8601 timestamp]")
    lines.append("- **Notes**: [FILL IN: free-text]")
    lines.append("")

    return "\n".join(lines) + "\n"


def _update_pointer(pointer_path: Path, target_name: str) -> None:
    if pointer_path.exists() or pointer_path.is_symlink():
        pointer_path.unlink()
    os.symlink(target_name, pointer_path)
