"""Policy normalization helpers shared by inspection and validation."""

from __future__ import annotations

import re
from typing import Any, Optional


ALLOWED_REASONING_EFFORTS = {"minimal", "low", "medium", "high", "xhigh"}
COMPLETED_STATUSES = {
    "complete",
    "completed",
    "delivered",
    "completed-pending-pause",
    "completed_pending_pause",
    "all-phases-complete",
    "all_phases_complete",
}
ACTIVE_STATUSES = {
    "in progress",
    "in-progress",
    "active",
    "not-started",
    "delivering",
    "verifying",
    "reviewing",
    "fixing",
    "blocked",
}


def normalized(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def phase_number(value: Any) -> Optional[str]:
    match = re.search(r"\bPhase\s+(\d+)\b", str(value or ""), re.IGNORECASE)
    return match.group(1) if match else None


def has_hard_stop_guard(prompt: str) -> bool:
    lowered = prompt.lower()
    complete_marker = "completed_pending_pause" in lowered or "all_phases_complete" in lowered
    stop_marker = "do not start" in lowered or "hard-stop" in lowered or "hard stop" in lowered
    return complete_marker and stop_marker


def has_blocked_remediation_guard(prompt: str) -> bool:
    lowered = prompt.lower()
    blocked_marker = "status: blocked" in lowered or "status is `blocked`" in lowered or "status is blocked" in lowered
    remediation_marker = "blocked remediation" in lowered or "blocker remediation" in lowered
    repair_marker = "repair" in lowered and "advance" in lowered
    return blocked_marker and remediation_marker and repair_marker
