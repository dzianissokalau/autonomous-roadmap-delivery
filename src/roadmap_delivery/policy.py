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


def paused_active_status_drift(reason: Any) -> bool:
    text = normalized(reason)
    return "paused" in text and "active" in text and (
        "automation" in text or "runner" in text or "saved" in text or "status" in text
    )


def manual_activation_reconciliation(
    state: Optional[dict[str, Any]],
    automation_status: Any,
    model_policy: Optional[dict[str, Any]],
    *,
    blocked_remediation_guard: bool,
    hard_stop_guard: bool,
    complete: bool,
) -> dict[str, Any]:
    blocked_reason = state.get("blocked_reason") if state else None
    model_mismatch = bool(model_policy and model_policy.get("model_mismatch"))
    reasoning_mismatch = bool(model_policy and model_policy.get("reasoning_mismatch"))
    model_unknown = bool(model_policy and model_policy.get("model_unknown"))
    reasoning_unknown = bool(model_policy and model_policy.get("reasoning_unknown"))
    model_policy_clean = not (model_mismatch or reasoning_mismatch or model_unknown or reasoning_unknown)
    active_readback = str(automation_status or "").upper() == "ACTIVE"
    blocked_state = normalized(state.get("status") if state else None) == "blocked"
    paused_active_drift = paused_active_status_drift(blocked_reason)
    available = (
        blocked_state
        and active_readback
        and paused_active_drift
        and model_policy_clean
        and blocked_remediation_guard
        and hard_stop_guard
        and not complete
    )
    return {
        "available": available,
        "classification": "automation-config" if paused_active_drift else None,
        "blocked_reason_indicates_paused_active_drift": paused_active_drift,
        "active_readback": active_readback,
        "blocked_state": blocked_state,
        "model_policy_clean": model_policy_clean,
        "blocked_remediation_guard": blocked_remediation_guard,
        "hard_stop_guard": hard_stop_guard,
        "complete": complete,
        "recommended_action": (
            "Record manual/operator activation acceptance, update durable status surfaces to ACTIVE, "
            "clear blocked_reason after validation, reset stalled counters, and resume the current phase."
            if available
            else None
        ),
    }
