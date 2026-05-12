"""Per-session KPI tally — `peer-session tally <session-id>`."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.peer_session.bundle_io import (
    BundleIncompleteError,
    BundleSchemaError,
    compute_inputs_hash,
    count_intervention_type,
    format_iso8601_field,
    is_drift_audit_placeholder,
    read_bundle,
)
from tools.peer_session.interventions import INTERVENTION_TYPES, validate_interventions
from tools.peer_session.per_session_clear import (
    compute_per_session_clear,
    derive_intervention_load,
)

EXIT_OK = 0
EXIT_UNEXPECTED = 1
EXIT_INCOMPLETE = 2
EXIT_UNCLOSED = 3
EXIT_INVALID = 4


class TallyError(Exception):
    """Base class for tally-specific errors with documented exit codes."""

    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def run_tally(
    session_id: str,
    *,
    sessions_root: Path,
    now: datetime | None = None,
) -> int:
    try:
        kpi = compute_tally(session_id, sessions_root=sessions_root, now=now)
    except TallyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return exc.exit_code
    except BundleIncompleteError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_INCOMPLETE
    except BundleSchemaError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_INVALID
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED

    kpi_path = sessions_root / session_id / "kpi.json"
    kpi_path.write_text(json.dumps(kpi, indent=2) + "\n")
    print(f"wrote {kpi_path}")
    print(f"per_session_clear: {kpi['per_session_clear']}")
    ambiguous = [
        name
        for name, entry in kpi["per_session_clear_breakdown"].items()
        if entry["judgment"] == "ambiguous"
    ]
    if ambiguous:
        print(f"ambiguous sub-judgments: {', '.join(ambiguous)}")
    return EXIT_OK


def compute_tally(
    session_id: str,
    *,
    sessions_root: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    if session_id.startswith(("_", ".")):
        raise TallyError(
            f"refusing to tally template/hidden session_id: {session_id!r}",
            EXIT_INVALID,
        )
    session_dir = sessions_root / session_id
    inputs = read_bundle(session_dir)

    if inputs.meta.get("session_id") != session_id:
        raise TallyError(
            f"meta.json session_id ({inputs.meta.get('session_id')!r}) does not match "
            f"directory name ({session_id!r})",
            EXIT_INVALID,
        )

    if inputs.meta.get("closed_at") is None:
        raise TallyError(
            f"session {session_id!r} is unclosed (meta.json.closed_at is null)",
            EXIT_UNCLOSED,
        )

    try:
        validate_interventions(inputs.interventions, transcript_path=None)
    except Exception as exc:  # InterventionValidationError or similar
        raise TallyError(
            f"interventions.json fails spec-001 FR-011 validation: {exc}",
            EXIT_INVALID,
        ) from exc

    intervention_count = len(inputs.interventions)
    intervention_type_tally = {
        type_name: count_intervention_type(inputs.interventions, type_name)
        for type_name in sorted(INTERVENTION_TYPES)
    }

    rate, load_pass, load_reason = derive_intervention_load(inputs)
    zero_turn = rate is None

    per_session_clear_result = compute_per_session_clear(
        inputs,
        intervention_load_pass=load_pass,
        intervention_load_reason=load_reason,
    )

    notes: list[str] = []
    if is_drift_audit_placeholder(inputs.drift_audit):
        notes.append("drift-audit.json is the spec-001 Phase-2-pending placeholder")
    if inputs.fresh_reader_audit is None:
        notes.append("fresh-reader-audit.json absent; h2_fresh_reader marked ambiguous")
    if zero_turn:
        notes.append("transcript has zero peer turns; intervention_rate_per_turn is null")

    drift_verdict_snapshot: Any
    if is_drift_audit_placeholder(inputs.drift_audit):
        drift_verdict_snapshot = None
    else:
        drift_verdict_snapshot = inputs.drift_audit.get("verdict")

    now = now or datetime.now(UTC)

    return {
        "session_id": session_id,
        "tallied_at": format_iso8601_field(now),
        "inputs_hash": compute_inputs_hash(inputs),
        "intervention_count": intervention_count,
        "intervention_type_tally": intervention_type_tally,
        "intervention_rate_per_turn": rate,
        "zero_turn_session": zero_turn,
        "drift_audit_verdict": drift_verdict_snapshot,
        "per_session_clear": per_session_clear_result["per_session_clear"],
        "per_session_clear_breakdown": per_session_clear_result["breakdown"],
        "notes": notes,
    }
