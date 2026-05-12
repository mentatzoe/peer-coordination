from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

TAXONOMY_VERSION = "poc-v1"
INTERVENTION_TYPES = {
    "safety_stop",
    "clarification",
    "directive_redirect",
    "drift_catch",
    "close_or_resume",
    "other",
}
ATTRIBUTIONS = {"operator_directed", "agent_self_flagged"}

INTERVENTION_ID_RE = re.compile(r"^iv-(\d{3})$")
RFC3339_UTC_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


class InterventionValidationError(ValueError):
    """Raised when an intervention log or record violates the v1 schema."""


def add_intervention(
    repo_root: Path,
    session_id: str,
    *,
    intervention_type: str,
    reason: str,
    at: str,
    actor: str,
    attribution: str,
    target_turn: str | None = None,
    start_turn: str | None = None,
    end_turn: str | None = None,
    intervention_id: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    bundle_dir = _bundle_dir(repo_root, session_id)
    if not bundle_dir.is_dir():
        raise FileNotFoundError(f"session bundle not found: {bundle_dir}")

    _validate_meta_session_id(bundle_dir, session_id)
    log_path = bundle_dir / "interventions.json"
    records = load_interventions(log_path)
    validate_interventions(records, transcript_path=bundle_dir / "transcript.md")

    record_id = intervention_id or next_intervention_id(records)
    record: dict[str, Any] = {
        "id": record_id,
        "taxonomy_version": TAXONOMY_VERSION,
        "at": at,
        "type": intervention_type,
        "reason": reason,
        "attribution": attribution,
        "actor": actor,
        "target": build_target(
            target_turn=target_turn,
            start_turn=start_turn,
            end_turn=end_turn,
        ),
    }
    if notes:
        record["notes"] = notes

    candidate = [*records, record]
    validate_interventions(candidate, transcript_path=bundle_dir / "transcript.md")
    write_interventions(log_path, candidate)
    return record


def validate_interventions_file(log_path: Path, *, transcript_path: Path | None = None) -> list[dict[str, Any]]:
    records = load_interventions(log_path)
    validate_interventions(records, transcript_path=transcript_path)
    return records


def load_interventions(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.is_file():
        raise FileNotFoundError(f"interventions log missing: {log_path}")
    raw = json.loads(log_path.read_text())
    if not isinstance(raw, list):
        raise InterventionValidationError("interventions.json must be a top-level array")
    if not all(isinstance(item, dict) for item in raw):
        raise InterventionValidationError("each intervention entry must be an object")
    return raw


def write_interventions(log_path: Path, records: list[dict[str, Any]]) -> None:
    log_path.write_text(json.dumps(records, indent=2) + "\n")


def validate_interventions(
    records: list[dict[str, Any]],
    *,
    transcript_path: Path | None = None,
) -> None:
    seen_ids: set[str] = set()
    turn_refs = extract_transcript_turn_refs(transcript_path) if transcript_path else None

    for index, record in enumerate(records):
        prefix = f"intervention[{index}]"
        _require_string(record, "id", prefix)
        match = INTERVENTION_ID_RE.match(record["id"])
        if not match:
            raise InterventionValidationError(f"{prefix}.id must match iv-###")
        if record["id"] in seen_ids:
            raise InterventionValidationError(f"duplicate intervention id: {record['id']}")
        seen_ids.add(record["id"])

        _require_string(record, "taxonomy_version", prefix)
        if record["taxonomy_version"] != TAXONOMY_VERSION:
            raise InterventionValidationError(
                f"{prefix}.taxonomy_version must be {TAXONOMY_VERSION}"
            )

        _require_string(record, "at", prefix)
        parse_rfc3339_utc(record["at"], f"{prefix}.at")

        _require_string(record, "type", prefix)
        if record["type"] not in INTERVENTION_TYPES:
            raise InterventionValidationError(f"{prefix}.type is not in the poc-v1 taxonomy")

        _require_string(record, "reason", prefix)
        if not record["reason"].strip():
            raise InterventionValidationError(f"{prefix}.reason must be non-empty")

        _require_string(record, "attribution", prefix)
        if record["attribution"] not in ATTRIBUTIONS:
            raise InterventionValidationError(f"{prefix}.attribution is invalid")

        _require_string(record, "actor", prefix)
        if not record["actor"].strip():
            raise InterventionValidationError(f"{prefix}.actor must be non-empty")

        if "target" not in record or not isinstance(record["target"], dict):
            raise InterventionValidationError(f"{prefix}.target must be an object")
        validate_target(record["target"], prefix=f"{prefix}.target", turn_refs=turn_refs)

        if "notes" in record and not isinstance(record["notes"], str):
            raise InterventionValidationError(f"{prefix}.notes must be a string when present")


def build_target(
    *,
    target_turn: str | None = None,
    start_turn: str | None = None,
    end_turn: str | None = None,
) -> dict[str, str]:
    if target_turn and (start_turn or end_turn):
        raise InterventionValidationError("use either --target-turn or --start-turn/--end-turn, not both")
    if target_turn:
        parse_rfc3339_utc(target_turn, "target_turn")
        return {"kind": "turn", "turn_ref": target_turn}

    if bool(start_turn) != bool(end_turn):
        raise InterventionValidationError("--start-turn and --end-turn must be provided together")
    if start_turn and end_turn:
        start = parse_rfc3339_utc(start_turn, "start_turn")
        end = parse_rfc3339_utc(end_turn, "end_turn")
        if start > end:
            raise InterventionValidationError("start_turn must be <= end_turn")
        return {"kind": "span", "start_turn_ref": start_turn, "end_turn_ref": end_turn}

    return {"kind": "session"}


def validate_target(
    target: dict[str, Any],
    *,
    prefix: str,
    turn_refs: set[str] | None = None,
) -> None:
    kind = target.get("kind")
    if kind == "turn":
        _only_keys(target, {"kind", "turn_ref"}, prefix)
        _require_string(target, "turn_ref", prefix)
        parse_rfc3339_utc(target["turn_ref"], f"{prefix}.turn_ref")
        _validate_turn_ref(target["turn_ref"], turn_refs, f"{prefix}.turn_ref")
        return

    if kind == "span":
        _only_keys(target, {"kind", "start_turn_ref", "end_turn_ref"}, prefix)
        _require_string(target, "start_turn_ref", prefix)
        _require_string(target, "end_turn_ref", prefix)
        start = parse_rfc3339_utc(target["start_turn_ref"], f"{prefix}.start_turn_ref")
        end = parse_rfc3339_utc(target["end_turn_ref"], f"{prefix}.end_turn_ref")
        if start > end:
            raise InterventionValidationError(f"{prefix}.start_turn_ref must be <= end_turn_ref")
        _validate_turn_ref(target["start_turn_ref"], turn_refs, f"{prefix}.start_turn_ref")
        _validate_turn_ref(target["end_turn_ref"], turn_refs, f"{prefix}.end_turn_ref")
        return

    if kind == "session":
        _only_keys(target, {"kind"}, prefix)
        return

    raise InterventionValidationError(f"{prefix}.kind must be turn, span, or session")


def next_intervention_id(records: list[dict[str, Any]]) -> str:
    max_seen = 0
    for record in records:
        record_id = record.get("id")
        if isinstance(record_id, str):
            match = INTERVENTION_ID_RE.match(record_id)
            if match:
                max_seen = max(max_seen, int(match.group(1)))
    return f"iv-{max_seen + 1:03d}"


def resolve_citation(records: list[dict[str, Any]], citation_key: str) -> dict[str, Any]:
    if "#" not in citation_key:
        raise InterventionValidationError("citation key must include #<intervention-id>")
    _, fragment = citation_key.rsplit("#", 1)
    matches = [record for record in records if record.get("id") == fragment]
    if len(matches) != 1:
        raise InterventionValidationError(f"citation key does not resolve exactly once: {citation_key}")
    return matches[0]


def directive_signal_count(records: list[dict[str, Any]]) -> int:
    return sum(
        1
        for record in records
        if record.get("type") == "directive_redirect"
        and record.get("attribution") == "operator_directed"
    )


def extract_transcript_turn_refs(transcript_path: Path | None) -> set[str]:
    if transcript_path is None or not transcript_path.is_file():
        return set()
    return set(RFC3339_UTC_RE.findall(transcript_path.read_text()))


def parse_rfc3339_utc(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not RFC3339_UTC_RE.fullmatch(value):
        raise InterventionValidationError(f"{field} must be RFC3339 UTC like 2026-05-05T17:00:00Z")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _bundle_dir(repo_root: Path, session_id: str) -> Path:
    return repo_root.resolve() / "observations" / "sessions" / session_id


def _validate_meta_session_id(bundle_dir: Path, session_id: str) -> None:
    meta_path = bundle_dir / "meta.json"
    if not meta_path.is_file():
        return
    meta = json.loads(meta_path.read_text())
    if isinstance(meta, dict) and meta.get("session_id") not in {None, session_id}:
        raise InterventionValidationError(
            f"meta.json session_id {meta.get('session_id')!r} does not match {session_id!r}"
        )


def _require_string(record: dict[str, Any], key: str, prefix: str) -> None:
    if key not in record or not isinstance(record[key], str):
        raise InterventionValidationError(f"{prefix}.{key} must be a string")


def _only_keys(record: dict[str, Any], expected: set[str], prefix: str) -> None:
    extra = sorted(set(record) - expected)
    missing = sorted(expected - set(record))
    if extra or missing:
        details: list[str] = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected: {', '.join(extra)}")
        raise InterventionValidationError(f"{prefix} has invalid keys ({'; '.join(details)})")


def _validate_turn_ref(turn_ref: str, turn_refs: set[str] | None, field: str) -> None:
    if turn_refs is not None and turn_ref not in turn_refs:
        raise InterventionValidationError(f"{field} does not appear in transcript.md")
