"""Composite per-session-clear judgment per spec 010 research §4."""

from __future__ import annotations

import re
from typing import Any

from tools.peer_session.bundle_io import (
    BundleInputs,
    count_intervention_type,
    count_peer_turns,
    is_drift_audit_placeholder,
    peer_handles_from_meta,
)

SUB_JUDGMENTS = (
    "h1_stable_coordination",
    "h1_intervention_load",
    "h1_complementarity",
    "h2_fresh_reader",
    "h2_drift",
    "h2_episode_record",
)

CLEARED = "cleared"
NOT_CLEARED = "not-cleared"
AMBIGUOUS = "ambiguous"

SUMMARY_VERDICT_MAP = {
    "clear": CLEARED,
    "fail": NOT_CLEARED,
    "partial": AMBIGUOUS,
    "pending": AMBIGUOUS,
}

DRIFT_VERDICT_MAP = {
    "no_drift": CLEARED,
    "minor_drift": CLEARED,
    "load_bearing_drift": NOT_CLEARED,
}

FRA_VERDICT_MAP = {
    "pass": CLEARED,
    "fail": NOT_CLEARED,
    "inconclusive": AMBIGUOUS,
}

INTERVENTION_LOAD_THRESHOLD = 0.5

H1_STABILITY_RE = re.compile(
    r"^\s*-\s*\*\*H1\s+stability\*\*\s*:\s*`?(\w+)`?",
    re.IGNORECASE | re.MULTILINE,
)
H1_COMPLEMENTARITY_RE = re.compile(
    r"^\s*-\s*\*\*H1\s+complementarity\*\*\s*:\s*`?(\w+)`?",
    re.IGNORECASE | re.MULTILINE,
)


def compute_per_session_clear(
    inputs: BundleInputs,
    *,
    intervention_load_pass: bool | None,
    intervention_load_reason: str | None = None,
) -> dict[str, Any]:
    """Return the six sub-judgments plus a top-level composite.

    `intervention_load_pass` is computed in `tally.py` (where the rate lives) and
    passed in so this function stays a pure mapping over already-parsed inputs.
    Pass `None` when the rate is undefined (zero-turn session).
    """

    breakdown: dict[str, dict[str, str]] = {}

    breakdown["h1_stable_coordination"] = _from_summary_verdict(
        inputs.summary_text,
        H1_STABILITY_RE,
        field_name="H1 stability",
    )

    breakdown["h1_intervention_load"] = _intervention_load_judgment(
        intervention_load_pass, intervention_load_reason
    )

    breakdown["h1_complementarity"] = _from_summary_verdict(
        inputs.summary_text,
        H1_COMPLEMENTARITY_RE,
        field_name="H1 complementarity",
    )

    breakdown["h2_fresh_reader"] = _fresh_reader_judgment(inputs.fresh_reader_audit)

    breakdown["h2_drift"] = _drift_judgment(inputs.drift_audit)

    breakdown["h2_episode_record"] = {
        "judgment": CLEARED,
        "reason": "all spec-001 required files present and non-empty",
    }

    composite = _compose(breakdown)
    return {"per_session_clear": composite, "breakdown": breakdown}


def derive_intervention_load(
    inputs: BundleInputs,
) -> tuple[float | None, bool | None, str | None]:
    """Return (rate, pass-flag, reason).

    Rate uses `directive_redirect` count divided by peer-turn count per
    research §5. When there are zero peer turns, rate is `None` and the pass
    flag is `None` with a documented reason; otherwise the pass flag is the
    rate ≤ 0.5 threshold per research §4.
    """
    peer_handles = peer_handles_from_meta(inputs.meta)
    peer_turns = count_peer_turns(inputs.transcript_text, peer_handles)
    if peer_turns == 0:
        return None, None, "zero peer turns; intervention load undefined"
    directive_count = count_intervention_type(inputs.interventions, "directive_redirect")
    rate = directive_count / peer_turns
    passed = rate <= INTERVENTION_LOAD_THRESHOLD
    return rate, passed, None


def _intervention_load_judgment(
    intervention_load_pass: bool | None,
    reason: str | None,
) -> dict[str, str]:
    if intervention_load_pass is None:
        return {
            "judgment": AMBIGUOUS,
            "reason": reason or "intervention load undefined",
        }
    return {
        "judgment": CLEARED if intervention_load_pass else NOT_CLEARED,
        "reason": (
            "directive_redirect rate within threshold (<= 0.5)"
            if intervention_load_pass
            else "directive_redirect rate exceeds threshold (> 0.5)"
        ),
    }


def _fresh_reader_judgment(audit: dict[str, Any] | None) -> dict[str, str]:
    if audit is None:
        return {
            "judgment": AMBIGUOUS,
            "reason": "fresh-reader-audit.json not yet authored",
        }
    verdict = audit.get("verdict")
    if not isinstance(verdict, str) or verdict not in FRA_VERDICT_MAP:
        return {
            "judgment": AMBIGUOUS,
            "reason": f"fresh-reader-audit.json verdict missing or invalid: {verdict!r}",
        }
    judgment = FRA_VERDICT_MAP[verdict]
    if judgment == AMBIGUOUS:
        reasoning = audit.get("reasoning")
        return {
            "judgment": judgment,
            "reason": (
                reasoning
                if isinstance(reasoning, str) and reasoning
                else "fresh-reader-audit.json verdict is inconclusive"
            ),
        }
    return {
        "judgment": judgment,
        "reason": f"fresh-reader-audit.json verdict is {verdict!r}",
    }


def _drift_judgment(drift_audit: dict[str, Any]) -> dict[str, str]:
    if is_drift_audit_placeholder(drift_audit):
        return {
            "judgment": AMBIGUOUS,
            "reason": (
                "drift-audit.json is still the spec-001 Phase-2-pending "
                "placeholder; no audit has run yet"
            ),
        }
    if drift_audit.get("status") == "blocked":
        return {
            "judgment": AMBIGUOUS,
            "reason": (
                f"drift-audit.json is blocked: {drift_audit.get('reason') or 'unspecified'}"
            ),
        }
    verdict = drift_audit.get("verdict")
    if not isinstance(verdict, str) or verdict not in DRIFT_VERDICT_MAP:
        return {
            "judgment": AMBIGUOUS,
            "reason": f"drift-audit.json verdict missing or invalid: {verdict!r}",
        }
    return {
        "judgment": DRIFT_VERDICT_MAP[verdict],
        "reason": f"drift-audit.json verdict is {verdict!r}",
    }


def _from_summary_verdict(
    summary_text: str,
    pattern: re.Pattern[str],
    *,
    field_name: str,
) -> dict[str, str]:
    match = pattern.search(summary_text)
    if not match:
        return {
            "judgment": AMBIGUOUS,
            "reason": f"{field_name} verdict not captured in summary.md",
        }
    raw = match.group(1).strip().lower()
    if raw not in SUMMARY_VERDICT_MAP:
        return {
            "judgment": AMBIGUOUS,
            "reason": f"{field_name} verdict not recognised: {raw!r}",
        }
    judgment = SUMMARY_VERDICT_MAP[raw]
    return {
        "judgment": judgment,
        "reason": f"{field_name} verdict in summary.md is {raw!r}",
    }


def _compose(breakdown: dict[str, dict[str, str]]) -> str:
    judgments = [entry["judgment"] for entry in breakdown.values()]
    if any(j == NOT_CLEARED for j in judgments):
        return NOT_CLEARED
    if any(j == AMBIGUOUS for j in judgments):
        return AMBIGUOUS
    return CLEARED
