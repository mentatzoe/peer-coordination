from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import tomllib


@dataclass(frozen=True)
class SessionDefaults:
    operator_handle: str
    peer_handles: list[str]
    substrate: str
    channel_id: str


def load_defaults(
    defaults_path: Path,
    *,
    peer_handles: Sequence[str] | None = None,
    operator_handle: str | None = None,
    channel_id: str | None = None,
) -> SessionDefaults:
    with defaults_path.open("rb") as fh:
        raw = tomllib.load(fh)

    effective_peer_handles = list(peer_handles) if peer_handles else list(raw.get("peer_handles", []))
    effective_operator_handle = operator_handle or raw.get("operator_handle", "")
    effective_channel_id = channel_id or raw.get("channel_id", "")
    effective_substrate = raw.get("substrate", "discord")

    if not effective_peer_handles:
        raise ValueError("effective peer list is empty")
    if not effective_operator_handle:
        raise ValueError("operator_handle is required")
    if not effective_channel_id:
        raise ValueError("channel_id is required")

    return SessionDefaults(
        operator_handle=effective_operator_handle,
        peer_handles=effective_peer_handles,
        substrate=effective_substrate,
        channel_id=effective_channel_id,
    )
