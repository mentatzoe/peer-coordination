"""Shared bundle-IO helpers for the spec-010 tally + rollup commands."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SPEC_001_REQUIRED_FILES = (
    "meta.json",
    "interventions.json",
    "drift-audit.json",
    "summary.md",
    "transcript.md",
)

DRIFT_AUDIT_PLACEHOLDER = {"status": "pending-phase-2"}

TURN_HEADING_RE = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+·\s+(\S+)\s*$",
    re.MULTILINE,
)

FILL_IN_RE = re.compile(r"\[FILL IN[^\]]*\]")


class BundleIncompleteError(ValueError):
    """Raised when a bundle does not satisfy spec-001 FR-001..FR-011."""


class BundleSchemaError(ValueError):
    """Raised when a bundle file violates its documented schema."""


@dataclass(frozen=True)
class BundleInputs:
    session_id: str
    bundle_dir: Path
    meta_raw: bytes
    meta: dict[str, Any]
    interventions_raw: bytes
    interventions: list[dict[str, Any]]
    drift_audit_raw: bytes
    drift_audit: dict[str, Any]
    summary_raw: bytes
    summary_text: str
    transcript_raw: bytes
    transcript_text: str
    fresh_reader_audit_raw: bytes | None
    fresh_reader_audit: dict[str, Any] | None


def read_bundle(session_dir: Path) -> BundleInputs:
    if not session_dir.is_dir():
        raise BundleIncompleteError(f"session bundle directory missing: {session_dir}")

    missing = sorted(
        name for name in SPEC_001_REQUIRED_FILES if not (session_dir / name).is_file()
    )
    if missing:
        raise BundleIncompleteError(
            f"bundle missing required spec-001 files: {', '.join(missing)}"
        )

    meta_raw = (session_dir / "meta.json").read_bytes()
    meta = _load_json("meta.json", meta_raw)
    if not isinstance(meta, dict):
        raise BundleSchemaError("meta.json must be a top-level object")
    session_id_value = meta.get("session_id")
    if not isinstance(session_id_value, str) or not session_id_value:
        raise BundleSchemaError("meta.json.session_id is missing or not a string")

    interventions_raw = (session_dir / "interventions.json").read_bytes()
    interventions = _load_json("interventions.json", interventions_raw)
    if not isinstance(interventions, list):
        raise BundleSchemaError("interventions.json must be a top-level array")

    drift_audit_raw = (session_dir / "drift-audit.json").read_bytes()
    drift_audit = _load_json("drift-audit.json", drift_audit_raw)
    if not isinstance(drift_audit, dict):
        raise BundleSchemaError("drift-audit.json must be a top-level object")

    summary_raw = (session_dir / "summary.md").read_bytes()
    transcript_raw = (session_dir / "transcript.md").read_bytes()

    if not summary_raw.strip():
        raise BundleIncompleteError("summary.md is present but empty")
    if not transcript_raw.strip():
        raise BundleIncompleteError("transcript.md is present but empty")

    fresh_reader_path = session_dir / "fresh-reader-audit.json"
    fresh_reader_raw: bytes | None = None
    fresh_reader: dict[str, Any] | None = None
    if fresh_reader_path.is_file():
        fresh_reader_raw = fresh_reader_path.read_bytes()
        loaded = _load_json("fresh-reader-audit.json", fresh_reader_raw)
        if not isinstance(loaded, dict):
            raise BundleSchemaError("fresh-reader-audit.json must be a top-level object")
        fresh_reader = loaded

    return BundleInputs(
        session_id=session_id_value,
        bundle_dir=session_dir,
        meta_raw=meta_raw,
        meta=meta,
        interventions_raw=interventions_raw,
        interventions=interventions,
        drift_audit_raw=drift_audit_raw,
        drift_audit=drift_audit,
        summary_raw=summary_raw,
        summary_text=summary_raw.decode("utf-8"),
        transcript_raw=transcript_raw,
        transcript_text=transcript_raw.decode("utf-8"),
        fresh_reader_audit_raw=fresh_reader_raw,
        fresh_reader_audit=fresh_reader,
    )


def compute_inputs_hash(inputs: BundleInputs) -> str:
    parts: list[bytes] = [
        inputs.meta_raw,
        _canonical_json(inputs.interventions),
        _canonical_json(inputs.drift_audit),
        inputs.summary_raw,
        inputs.transcript_raw,
        _canonical_json(inputs.fresh_reader_audit) if inputs.fresh_reader_audit is not None else b"",
    ]
    digest = hashlib.sha256()
    for i, part in enumerate(parts):
        if i > 0:
            digest.update(b"\x00")
        digest.update(part)
    return digest.hexdigest()


def format_iso8601_field(dt: datetime) -> str:
    """Return an ISO-8601 UTC timestamp with seconds precision and `Z` suffix."""
    return dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_iso8601_filename(dt: datetime) -> str:
    """Return a filesystem-safe basic-format UTC timestamp (no colons, `Z` suffix)."""
    return dt.replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")


def is_drift_audit_placeholder(drift_audit: dict[str, Any]) -> bool:
    return drift_audit == DRIFT_AUDIT_PLACEHOLDER


def peer_handles_from_meta(meta: dict[str, Any]) -> set[str]:
    participants = meta.get("participants")
    if not isinstance(participants, list):
        return set()
    handles: set[str] = set()
    for entry in participants:
        if not isinstance(entry, dict):
            continue
        if entry.get("role") != "peer":
            continue
        handle = entry.get("handle")
        if isinstance(handle, str) and handle and not FILL_IN_RE.search(handle):
            handles.add(handle)
    return handles


def count_peer_turns(transcript_text: str, peer_handles: set[str]) -> int:
    if not peer_handles:
        return 0
    count = 0
    for match in TURN_HEADING_RE.finditer(transcript_text):
        handle = match.group(2).strip()
        if handle in peer_handles:
            count += 1
    return count


def count_intervention_type(records: list[dict[str, Any]], intervention_type: str) -> int:
    return sum(1 for record in records if record.get("type") == intervention_type)


def write_text_atomic(path: Path, text: str) -> None:
    """Write text atomically via a tmp file + rename."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    tmp.replace(path)


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _load_json(name: str, raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise BundleSchemaError(f"{name} is not valid JSON: {exc}") from exc
