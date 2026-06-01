"""Approval policy helpers for roadmap automation setup and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .paths import resolve_repo_path


APPROVAL_MODES = ("conservative", "delegated_local", "delegated_delivery", "custom")

OPERATIONS = (
    "edit_phase_owned_files",
    "write_state_log_review_artifacts",
    "create_or_switch_phase_branch",
    "run_verification",
    "commit_delivered_phase_locally",
    "retarget_saved_automation",
    "pause_saved_automation",
    "push_current_phase_branch",
)

BASE_LOCAL_OPERATIONS = frozenset(
    {
        "edit_phase_owned_files",
        "write_state_log_review_artifacts",
        "create_or_switch_phase_branch",
        "run_verification",
    }
)

LOCAL_DELEGATED_OPERATIONS = frozenset(
    {
        "commit_delivered_phase_locally",
        "retarget_saved_automation",
        "pause_saved_automation",
    }
)

DELIVERY_DELEGATED_OPERATIONS = frozenset({"push_current_phase_branch"})

NEVER_AUTO_OPERATIONS = (
    "force_push",
    "git_reset_hard",
    "delete_branches_or_tags",
    "merge_or_promote_to_main",
    "publish_releases_or_packages",
    "use_unavailable_credentials",
    "change_repository_security_or_billing",
    "install_or_sync_global_tools",
    "destructive_filesystem_outside_phase_scope",
)


def approved_operations_for_mode(
    mode: str,
    custom_operations: Optional[Dict[str, bool]] = None,
) -> Dict[str, bool]:
    """Return the effective operation map for an approval mode."""

    if mode == "conservative":
        allowed = set(BASE_LOCAL_OPERATIONS)
    elif mode == "delegated_local":
        allowed = set(BASE_LOCAL_OPERATIONS | LOCAL_DELEGATED_OPERATIONS)
    elif mode == "delegated_delivery":
        allowed = set(BASE_LOCAL_OPERATIONS | LOCAL_DELEGATED_OPERATIONS | DELIVERY_DELEGATED_OPERATIONS)
    elif mode == "custom":
        custom_operations = custom_operations or {}
        return {operation: bool(custom_operations.get(operation, False)) for operation in OPERATIONS}
    else:
        allowed = set()
    return {operation: operation in allowed for operation in OPERATIONS}


def approved_operation_names(operations: Dict[str, bool]) -> List[str]:
    return [operation for operation in OPERATIONS if operations.get(operation) is True]


def default_approval_policy(
    mode: str = "conservative",
    custom_operations: Optional[Dict[str, bool]] = None,
) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "approval_mode": mode,
        "operations": approved_operations_for_mode(mode, custom_operations),
        "never_auto": list(NEVER_AUTO_OPERATIONS),
    }


def parse_operation_assignments(values: Optional[Iterable[str]]) -> Tuple[Dict[str, bool], List[Dict[str, str]]]:
    """Parse CLI values shaped as operation=allow|deny|true|false."""

    operations: Dict[str, bool] = {}
    errors: List[Dict[str, str]] = []
    for value in values or []:
        if "=" not in value:
            errors.append(
                {
                    "code": "invalid_approval_operation_flag",
                    "message": f"Approval operation {value!r} must use operation=allow or operation=deny.",
                }
            )
            continue
        key, raw_decision = [part.strip() for part in value.split("=", 1)]
        if key not in OPERATIONS:
            errors.append(
                {
                    "code": "unknown_approval_operation",
                    "message": f"Approval operation {key!r} is not one of {list(OPERATIONS)!r}.",
                }
            )
            continue
        decision = raw_decision.lower()
        if decision in {"allow", "allowed", "true", "yes", "1"}:
            operations[key] = True
        elif decision in {"deny", "denied", "false", "no", "0"}:
            operations[key] = False
        else:
            errors.append(
                {
                    "code": "invalid_approval_operation_decision",
                    "message": f"Approval operation {key!r} has unsupported decision {raw_decision!r}.",
                }
            )
    return operations, errors


def _finding(code: str, message: str, path: Optional[Path] = None) -> Dict[str, str]:
    result = {"code": code, "message": message}
    if path is not None:
        result["path"] = str(path)
    return result


def validate_approval_policy(policy: Any, path: Optional[Path] = None) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []
    if not isinstance(policy, dict):
        return [_finding("invalid_approval_policy_shape", "Approval policy root must be an object.", path)]

    if policy.get("schema_version") != 1:
        errors.append(_finding("invalid_approval_policy_schema_version", "Approval policy schema_version must be 1.", path))

    mode = policy.get("approval_mode")
    if mode not in APPROVAL_MODES:
        errors.append(_finding("invalid_approval_mode", f"approval_mode must be one of {list(APPROVAL_MODES)!r}.", path))

    raw_operations = policy.get("operations")
    if not isinstance(raw_operations, dict):
        errors.append(_finding("invalid_approval_operations", "operations must be an object.", path))
        raw_operations = {}

    custom_operations: Dict[str, bool] = {}
    for operation, decision in raw_operations.items():
        if operation not in OPERATIONS:
            errors.append(_finding("unknown_approval_operation", f"Unknown approval operation {operation!r}.", path))
            continue
        if not isinstance(decision, bool):
            errors.append(_finding("invalid_approval_operation_decision", f"Operation {operation!r} must be boolean.", path))
            continue
        custom_operations[operation] = decision

    if mode == "custom":
        if not raw_operations:
            errors.append(_finding("custom_approval_operations_required", "custom approval mode requires an operations map.", path))
    elif mode in APPROVAL_MODES and mode != "custom" and raw_operations:
        expected = approved_operations_for_mode(str(mode))
        for operation in OPERATIONS:
            if operation in raw_operations and raw_operations.get(operation) != expected[operation]:
                errors.append(
                    _finding(
                        "approval_policy_operations_mismatch",
                        f"Operation {operation!r} does not match the {mode!r} approval mode.",
                        path,
                    )
                )

    raw_never_auto = policy.get("never_auto")
    if not isinstance(raw_never_auto, list):
        errors.append(_finding("invalid_never_auto_operations", "never_auto must be an array.", path))
    else:
        for operation in raw_never_auto:
            if operation not in NEVER_AUTO_OPERATIONS:
                errors.append(_finding("unknown_never_auto_operation", f"Unknown never-auto operation {operation!r}.", path))

    return errors


def approval_policy_path(repo_root: Path, state_file: Path, state: Dict[str, Any]) -> Path:
    value = state.get("approval_policy_path")
    if isinstance(value, str) and value.strip():
        resolved = resolve_repo_path(repo_root, value)
        if resolved is not None:
            return resolved
    return state_file.parent / "approval_policy.json"


def read_approval_policy(repo_root: Path, state_file: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    path = approval_policy_path(repo_root, state_file, state)
    if not path.exists():
        policy = default_approval_policy("conservative")
        return {
            "path": str(path),
            "present": False,
            "fallback": "conservative",
            "fallback_reason": "missing_policy",
            "approval_mode": "conservative",
            "approved_operations": approved_operation_names(policy["operations"]),
            "operations": policy["operations"],
            "errors": [],
        }

    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "path": str(path),
            "present": True,
            "fallback": "conservative",
            "fallback_reason": "invalid_json",
            "approval_mode": "conservative",
            "approved_operations": approved_operation_names(approved_operations_for_mode("conservative")),
            "operations": approved_operations_for_mode("conservative"),
            "errors": [_finding("invalid_approval_policy_json", f"Approval policy is invalid JSON: {exc}", path)],
        }
    except OSError as exc:
        return {
            "path": str(path),
            "present": True,
            "fallback": "conservative",
            "fallback_reason": "unreadable",
            "approval_mode": "conservative",
            "approved_operations": approved_operation_names(approved_operations_for_mode("conservative")),
            "operations": approved_operations_for_mode("conservative"),
            "errors": [_finding("approval_policy_unreadable", f"Cannot read approval policy: {exc}", path)],
        }

    errors = validate_approval_policy(policy, path)
    if errors:
        operations = approved_operations_for_mode("conservative")
        return {
            "path": str(path),
            "present": True,
            "fallback": "conservative",
            "fallback_reason": "invalid_policy",
            "approval_mode": "conservative",
            "approved_operations": approved_operation_names(operations),
            "operations": operations,
            "errors": errors,
        }

    mode = str(policy["approval_mode"])
    operations = approved_operations_for_mode(mode, policy.get("operations") if isinstance(policy.get("operations"), dict) else None)
    return {
        "path": str(path),
        "present": True,
        "fallback": None,
        "fallback_reason": None,
        "approval_mode": mode,
        "approved_operations": approved_operation_names(operations),
        "operations": operations,
        "errors": [],
    }
