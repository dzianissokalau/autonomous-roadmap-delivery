"""Saved automation config helpers for approved local runner updates."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import re
from typing import Any, Dict, Optional

from .toml import parse_minimal_toml


DEFAULT_AUTOMATIONS_DIR = Path.home() / ".codex" / "automations"
AUTOMATIONS_DIR_ENV = "AUTONOMOUS_ROADMAP_AUTOMATIONS_DIR"


class AutomationConfigError(RuntimeError):
    """Raised when a saved automation config cannot be read or updated."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def automations_dir(path: Optional[Path] = None) -> Path:
    if path is not None:
        return path.expanduser()
    return Path(os.environ.get(AUTOMATIONS_DIR_ENV, str(DEFAULT_AUTOMATIONS_DIR))).expanduser()


def automation_config_path(automation_id: str, *, root: Optional[Path] = None) -> Path:
    return automations_dir(root) / automation_id / "automation.toml"


def read_automation_config(path: Path) -> Dict[str, Any]:
    try:
        return parse_minimal_toml(path)
    except OSError as exc:
        raise AutomationConfigError(f"Cannot read automation config {path}: {exc}") from exc


def _replace_status(text: str, status: str) -> str:
    replacement = f'status = "{status}"'
    pattern = re.compile(r'(?m)^status\s*=\s*["\'][^"\']*["\']\s*$')
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    suffix = "" if text.endswith("\n") or not text else "\n"
    return f"{text}{suffix}{replacement}\n"


def _status(data: Dict[str, Any]) -> Optional[str]:
    value = data.get("status")
    if value is None:
        return None
    return str(value)


def pause_saved_automation(
    automation_id: Optional[str],
    *,
    root: Optional[Path] = None,
    timestamp: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Set a saved automation's status to PAUSED and verify readback.

    The helper mutates only the `status` line in the selected automation's
    `automation.toml`. It does not create automations, alter prompts, retarget
    models, or touch unrelated runner config.
    """

    timestamp = timestamp or utc_now()
    if not automation_id:
        return {
            "attempted": False,
            "paused": False,
            "status": "missing_automation_id",
            "reason": "Automation id is required before pausing a saved automation.",
            "paused_at": timestamp,
        }

    path = automation_config_path(automation_id, root=root)
    result: Dict[str, Any] = {
        "automation_id": automation_id,
        "config_path": str(path),
        "attempted": False,
        "paused": False,
        "status": None,
        "previous_status": None,
        "readback_status": None,
        "paused_at": timestamp,
        "reason": reason,
    }
    if not path.exists():
        result.update(
            {
                "status": "missing_config",
                "reason": reason or f"Automation config does not exist: {path}",
            }
        )
        return result

    try:
        original_text = path.read_text(encoding="utf-8")
        original_data = read_automation_config(path)
    except (OSError, AutomationConfigError) as exc:
        result.update({"status": "read_failed", "reason": str(exc)})
        return result

    previous_status = _status(original_data)
    result["previous_status"] = previous_status
    if str(previous_status or "").upper() == "PAUSED":
        result.update({"status": "already_paused", "readback_status": previous_status, "paused": True})
        return result

    result["attempted"] = True
    try:
        path.write_text(_replace_status(original_text, "PAUSED"), encoding="utf-8")
        readback = read_automation_config(path)
    except (OSError, AutomationConfigError) as exc:
        result.update({"status": "write_failed", "reason": str(exc)})
        return result

    readback_status = _status(readback)
    result["readback_status"] = readback_status
    if str(readback_status or "").upper() == "PAUSED":
        result.update({"status": "paused", "paused": True})
    else:
        result.update(
            {
                "status": "readback_failed",
                "reason": reason or "Pause update did not read back status PAUSED.",
            }
        )
    return result


def automation_id_from_state(state: Dict[str, Any]) -> Optional[str]:
    automation = state.get("automation")
    if isinstance(automation, dict) and automation.get("id"):
        return str(automation["id"])
    value = state.get("automation_id")
    if value:
        return str(value)
    return None
