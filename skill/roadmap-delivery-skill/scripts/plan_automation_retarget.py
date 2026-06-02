#!/usr/bin/env python3
"""Plan a model-policy automation retarget without mutating files."""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_AUTOMATIONS_DIR = Path.home() / ".codex" / "automations"
AUTOMATIONS_DIR = Path(os.environ.get("AUTONOMOUS_ROADMAP_AUTOMATIONS_DIR", str(DEFAULT_AUTOMATIONS_DIR))).expanduser()

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

FORBIDDEN_NAMED_OPERATIONS = {
    "sync_installed_skill": "Installed skill or plugin synchronization is never automatic.",
    "publish_release_or_package": "Publication to release or package registries is never automatic.",
    "promote_to_main": "Merging or promoting work to main is never automatic.",
    "use_credentials": "Credential use requires explicit human approval and available credentials.",
    "destructive_git": "Destructive git operations are never automatic.",
}

RUN_QUALITIES = (
    "flawless",
    "delivered_with_fixes",
    "verification_failed",
    "review_needs_fix",
    "blocked_local_repairable",
    "blocked_human_required",
    "stalled",
    "retarget_failed",
    "completion_closeout_failed",
)

DEFAULT_ESCALATE_ON = (
    "delivered_with_fixes",
    "verification_failed",
    "review_needs_fix",
    "stalled",
    "retarget_failed",
)

DEFAULT_HUMAN_GATED_QUALITIES = (
    "blocked_human_required",
    "completion_closeout_failed",
)

LOCAL_REPAIRABLE_BLOCKERS = {"local-repairable", "local_repairable", "automation-config", "automation_config"}
HUMAN_GATED_BLOCKERS = {"permission-gated", "permission_gated", "external-decision", "external_decision", "destructive-risk", "destructive_risk"}
REASONING_ORDER = ("minimal", "low", "medium", "high", "xhigh")


def unique(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    out: List[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            out.append(path)
            seen.add(key)
    return out


def slug_forms(slug: str) -> Dict[str, str]:
    return {
        "input": slug,
        "dash": slug.replace("_", "-"),
        "dir": slug.replace("-", "_"),
    }


def resolve_repo_path(repo_root: Path, value: Optional[str]) -> Optional[Path]:
    if not value:
        return None
    path = Path(str(value)).expanduser()
    if path.is_absolute():
        return path
    return repo_root / path


def parse_minimal_toml(path: Path) -> Dict[str, Any]:
    try:
        import tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

    if tomllib is not None:
        with path.open("rb") as fh:
            return tomllib.load(fh)

    data: Dict[str, Any] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            continue
        if value.startswith("[") and value.endswith("]"):
            try:
                data[key] = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                data[key] = value
            continue
        if value.startswith(("'", '"')):
            try:
                data[key] = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                data[key] = value.strip("'\"")
            continue
        if value.lower() in ("true", "false"):
            data[key] = value.lower() == "true"
            continue
        try:
            data[key] = int(value)
        except ValueError:
            data[key] = value
    return data


def state_candidates(repo_root: Path, forms: Dict[str, str]) -> List[Path]:
    candidates: List[Path] = []
    for slug in unique([forms["dir"], forms["dash"]]):
        candidates.append(repo_root / "roadmaps" / "automation" / slug / "delivery_state.json")
        candidates.append(repo_root / "automation" / slug / "delivery_state.json")
    return unique_paths(candidates)


def automation_dir_candidates(repo_root: Path, forms: Dict[str, str]) -> List[Path]:
    candidates: List[Path] = []
    for slug in unique([forms["dir"], forms["dash"]]):
        candidates.append(repo_root / "roadmaps" / "automation" / slug)
        candidates.append(repo_root / "automation" / slug)
    return unique_paths(candidates)


def load_json(path: Path, errors: List[str]) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = json.load(fh)
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path}: JSON root is not an object")
        return None
    return value


def approved_operations_for_mode(mode: str, custom_operations: Optional[Dict[str, bool]] = None) -> Dict[str, bool]:
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


def approval_decision_for_operation(operations: Dict[str, bool], operation: str) -> Dict[str, Any]:
    if operation in FORBIDDEN_NAMED_OPERATIONS:
        return {
            "operation": operation,
            "decision": "forbidden",
            "reason": FORBIDDEN_NAMED_OPERATIONS[operation],
        }
    if operation not in OPERATIONS:
        return {
            "operation": operation,
            "decision": "forbidden",
            "reason": "Unknown operation cannot be classified safely.",
        }
    if operations.get(operation) is True:
        return {
            "operation": operation,
            "decision": "allowed",
            "reason": "Approval policy pre-approves this operation.",
        }
    return {
        "operation": operation,
        "decision": "ask",
        "reason": "Approval policy does not pre-approve this operation.",
    }


def normalized(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def normalize_run_quality(value: Any) -> Optional[str]:
    text = normalized(value)
    for quality in RUN_QUALITIES:
        if text == quality.replace("_", "-"):
            return quality
    return None


def nonzero_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value > 0:
        return value
    return 0


def reasoning_index(value: Any) -> Optional[int]:
    try:
        return REASONING_ORDER.index(str(value or ""))
    except ValueError:
        return None


def next_reasoning(value: Any, max_reasoning: Any = None) -> Any:
    index = reasoning_index(value)
    if index is None:
        return value
    cap_index = reasoning_index(max_reasoning)
    if cap_index is None:
        cap_index = len(REASONING_ORDER) - 1
    return REASONING_ORDER[min(index + 1, cap_index)]


def reasoning_satisfies(configured: Any, required: Any) -> bool:
    configured_index = reasoning_index(configured)
    required_index = reasoning_index(required)
    if configured_index is None or required_index is None:
        return False
    return configured_index >= required_index


def reasoning_exceeds(configured: Any, required: Any) -> bool:
    configured_index = reasoning_index(configured)
    required_index = reasoning_index(required)
    if configured_index is None or required_index is None:
        return False
    return configured_index > required_index


def string_list(value: Any, default: Iterable[str]) -> List[str]:
    if not isinstance(value, list):
        return list(default)
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def classify_run_quality(
    state: Dict[str, Any],
    *,
    retarget_status: Any = None,
    blocker_class: Any = None,
    stalled: Optional[bool] = None,
    completion_closeout_failed: bool = False,
) -> str:
    recorded = normalize_run_quality(state.get("last_run_quality"))
    if recorded:
        return recorded
    if completion_closeout_failed:
        return "completion_closeout_failed"
    if normalized(retarget_status) in {"failed", "retarget-failed", "retarget-failed-alert"}:
        return "retarget_failed"
    if stalled is None:
        stalled_count = nonzero_int(state.get("stalled_run_count"))
        max_stalled = nonzero_int(state.get("max_stalled_runs"))
        stalled = bool(max_stalled and stalled_count >= max_stalled)
    if stalled:
        return "stalled"
    blocker = normalized(blocker_class or state.get("blocker_class") or state.get("last_blocker_class"))
    if blocker in LOCAL_REPAIRABLE_BLOCKERS:
        return "blocked_local_repairable"
    if blocker in HUMAN_GATED_BLOCKERS:
        return "blocked_human_required"
    verification = state.get("last_verification") if isinstance(state.get("last_verification"), dict) else {}
    if normalized(verification.get("status")) in {"failed", "error", "failure"}:
        return "verification_failed"
    review = state.get("last_review") if isinstance(state.get("last_review"), dict) else {}
    verdict = normalized(review.get("verdict"))
    if verdict == "needs-fix":
        return "review_needs_fix"
    if verdict == "blocked":
        return "blocked_human_required"
    if verdict == "delivered":
        return "delivered_with_fixes" if nonzero_int(state.get("review_iterations")) > 1 else "flawless"
    return "blocked_human_required" if blocker else "flawless"


def validate_adaptive_policy(policy: Dict[str, Any]) -> List[str]:
    adaptive = policy.get("adaptive_model_policy")
    if not isinstance(adaptive, dict):
        return []
    errors: List[str] = []
    enabled = bool(adaptive.get("enabled"))
    for field in ("escalate_on", "human_gated_qualities"):
        value = adaptive.get(field)
        if value is not None and not isinstance(value, list):
            errors.append(f"adaptive_model_policy.{field} must be an array")
            continue
        for item in value or []:
            if normalize_run_quality(item) is None:
                errors.append(f"adaptive_model_policy.{field} contains unknown run quality {item!r}")
    caps = adaptive.get("caps")
    if enabled and not isinstance(caps, dict):
        errors.append("enabled adaptive_model_policy must define caps")
        caps = {}
    elif not isinstance(caps, dict):
        caps = {}
    allowed_models = caps.get("allowed_models")
    if enabled and (not isinstance(allowed_models, list) or not allowed_models or not all(isinstance(item, str) and item.strip() for item in allowed_models)):
        errors.append("adaptive_model_policy.caps.allowed_models must be a non-empty string array")
    max_reasoning = caps.get("max_reasoning_effort")
    if enabled and max_reasoning not in REASONING_ORDER:
        errors.append("adaptive_model_policy.caps.max_reasoning_effort must be a known reasoning effort")
    for field in ("escalation", "deescalation"):
        target = adaptive.get(field)
        if target is None:
            continue
        if not isinstance(target, dict):
            errors.append(f"adaptive_model_policy.{field} must be an object")
            continue
        model = target.get("model")
        reasoning = target.get("reasoning_effort")
        if enabled and model is not None and isinstance(allowed_models, list) and model not in allowed_models:
            errors.append(f"adaptive_model_policy.{field}.model {model!r} is not allowed by caps.allowed_models")
        if reasoning is not None and reasoning not in REASONING_ORDER:
            errors.append(f"adaptive_model_policy.{field}.reasoning_effort must be a known reasoning effort")
        if enabled and reasoning_index(reasoning) is not None and reasoning_index(max_reasoning) is not None and reasoning_index(reasoning) > reasoning_index(max_reasoning):
            errors.append(f"adaptive_model_policy.{field}.reasoning_effort exceeds caps.max_reasoning_effort")
    return errors


def resolve_adaptive_action(
    policy: Dict[str, Any],
    *,
    base_target: Dict[str, Any],
    run_quality: str,
    flawless_streak: Any,
) -> Dict[str, Any]:
    adaptive = policy.get("adaptive_model_policy")
    target = {
        "model": base_target.get("model"),
        "reasoning_effort": base_target.get("reasoning_effort"),
    }
    result = {
        "enabled": bool(isinstance(adaptive, dict) and adaptive.get("enabled")),
        "run_quality": run_quality,
        "action": "disabled",
        "target": target,
        "target_changed": False,
        "next_flawless_streak": nonzero_int(flawless_streak),
        "reason": "Adaptive model policy is disabled or absent.",
        "errors": [],
    }
    if not result["enabled"]:
        return result
    errors = validate_adaptive_policy(policy)
    if errors:
        result.update({"action": "blocked_by_policy", "reason": "Adaptive model policy is invalid.", "errors": errors})
        return result
    assert isinstance(adaptive, dict)
    caps = adaptive.get("caps") if isinstance(adaptive.get("caps"), dict) else {}
    human_gated = {normalize_run_quality(item) for item in string_list(adaptive.get("human_gated_qualities"), DEFAULT_HUMAN_GATED_QUALITIES)}
    escalate_on = {normalize_run_quality(item) for item in string_list(adaptive.get("escalate_on"), DEFAULT_ESCALATE_ON)}
    if run_quality in human_gated:
        result.update(
            {
                "action": "none_human_gated",
                "next_flawless_streak": 0,
                "reason": "Human-gated blockers require the missing human action instead of model escalation.",
            }
        )
        return result
    if run_quality in escalate_on:
        escalation = adaptive.get("escalation") if isinstance(adaptive.get("escalation"), dict) else {}
        candidate = {
            "model": escalation.get("model") or target["model"],
            "reasoning_effort": escalation.get("reasoning_effort") or next_reasoning(target["reasoning_effort"], caps.get("max_reasoning_effort")),
        }
        result.update(
            {
                "action": "escalate" if candidate != target else "none_at_cap",
                "target": candidate,
                "target_changed": candidate != target,
                "next_flawless_streak": 0,
                "reason": "Run quality triggers adaptive escalation." if candidate != target else "Run quality triggers escalation, but the target is already at the configured cap.",
            }
        )
        return result
    if run_quality == "flawless":
        next_streak = nonzero_int(flawless_streak) + 1
        threshold = adaptive.get("deescalate_after_flawless_runs", 0)
        if isinstance(threshold, int) and not isinstance(threshold, bool) and threshold > 0 and next_streak >= threshold:
            deescalation = adaptive.get("deescalation") if isinstance(adaptive.get("deescalation"), dict) else {}
            candidate = {
                "model": deescalation.get("model") or target["model"],
                "reasoning_effort": deescalation.get("reasoning_effort") or target["reasoning_effort"],
            }
            result.update(
                {
                    "action": "deescalate" if candidate != target else "none",
                    "target": candidate,
                    "target_changed": candidate != target,
                    "next_flawless_streak": 0 if candidate != target else next_streak,
                    "reason": "Flawless run streak reached the configured de-escalation threshold.",
                }
            )
            return result
        result.update(
            {
                "action": "none",
                "next_flawless_streak": next_streak,
                "reason": "Flawless run keeps the current model policy target.",
            }
        )
        return result
    result.update({"action": "none", "next_flawless_streak": 0, "reason": "Run quality does not trigger an adaptive model change."})
    return result


def read_approval_policy(repo_root: Path, state_path: Optional[Path], state: Dict[str, Any]) -> Dict[str, Any]:
    if state_path is not None and isinstance(state.get("approval_policy_path"), str) and state.get("approval_policy_path"):
        policy_path = resolve_repo_path(repo_root, str(state["approval_policy_path"]))
    elif state_path is not None:
        policy_path = state_path.parent / "approval_policy.json"
    else:
        policy_path = None

    operations = approved_operations_for_mode("conservative")
    if policy_path is None or not policy_path.exists():
        return {
            "path": str(policy_path) if policy_path else None,
            "present": False,
            "fallback": "conservative",
            "fallback_reason": "missing_policy",
            "approval_mode": "conservative",
            "approved_operations": approved_operation_names(operations),
            "operations": operations,
            "operation_decisions": {
                operation: approval_decision_for_operation(operations, operation)
                for operation in (*OPERATIONS, *FORBIDDEN_NAMED_OPERATIONS)
            },
            "errors": [],
        }

    policy = load_json(policy_path, [])
    if policy is None:
        return {
            "path": str(policy_path),
            "present": True,
            "fallback": "conservative",
            "fallback_reason": "invalid_policy",
            "approval_mode": "conservative",
            "approved_operations": approved_operation_names(operations),
            "operations": operations,
            "operation_decisions": {
                operation: approval_decision_for_operation(operations, operation)
                for operation in (*OPERATIONS, *FORBIDDEN_NAMED_OPERATIONS)
            },
            "errors": [f"{policy_path}: approval_policy.json could not be read as an object"],
        }

    mode = policy.get("approval_mode")
    raw_operations = policy.get("operations")
    if mode not in {"conservative", "delegated_local", "delegated_delivery", "custom"} or not isinstance(raw_operations, dict):
        return {
            "path": str(policy_path),
            "present": True,
            "fallback": "conservative",
            "fallback_reason": "invalid_policy",
            "approval_mode": "conservative",
            "approved_operations": approved_operation_names(operations),
            "operations": operations,
            "operation_decisions": {
                operation: approval_decision_for_operation(operations, operation)
                for operation in (*OPERATIONS, *FORBIDDEN_NAMED_OPERATIONS)
            },
            "errors": [f"{policy_path}: approval policy mode or operations map is invalid"],
        }

    if mode == "custom":
        operations = approved_operations_for_mode("custom", raw_operations)
    else:
        operations = approved_operations_for_mode(str(mode))
    return {
        "path": str(policy_path),
        "present": True,
        "fallback": None,
        "fallback_reason": None,
        "approval_mode": str(mode),
        "approved_operations": approved_operation_names(operations),
        "operations": operations,
        "operation_decisions": {
            operation: approval_decision_for_operation(operations, operation)
            for operation in (*OPERATIONS, *FORBIDDEN_NAMED_OPERATIONS)
        },
        "errors": [],
    }


def find_state(repo_root: Path, forms: Dict[str, str], errors: List[str]) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
    candidates = state_candidates(repo_root, forms)
    for candidate in candidates:
        if candidate.exists():
            return candidate, load_json(candidate, errors)
    errors.append("delivery_state.json not found; checked: " + ", ".join(str(path) for path in candidates))
    return (candidates[0] if candidates else None), None


def find_automation_dir(repo_root: Path, forms: Dict[str, str]) -> Optional[Path]:
    for candidate in automation_dir_candidates(repo_root, forms):
        if candidate.exists():
            return candidate
    return None


def find_automation_toml(automation_id: Optional[str], forms: Dict[str, str]) -> Optional[Path]:
    candidates: List[Path] = []
    if automation_id:
        candidates.append(AUTOMATIONS_DIR / automation_id / "automation.toml")
    candidates.extend(
        AUTOMATIONS_DIR / f"{slug}-delivery" / "automation.toml"
        for slug in unique([forms["dash"], forms["dir"]])
    )
    for candidate in unique_paths(candidates):
        if candidate.exists():
            return candidate
    return None


def phase_number(value: Any) -> Optional[int]:
    match = re.search(r"\bPhase\s+(\d+)\b", str(value or ""), re.IGNORECASE)
    return int(match.group(1)) if match else None


def parse_roadmap_phases(roadmap_path: Path, errors: List[str]) -> Dict[int, str]:
    try:
        text = roadmap_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{roadmap_path}: cannot read roadmap: {exc}")
        return {}

    phases: Dict[int, str] = {}
    for line in text.splitlines():
        match = re.match(r"^## Phase\s+(\d+)\s+-\s+(.+?)\s*$", line)
        if match:
            number = int(match.group(1))
            phases[number] = f"Phase {number} - {match.group(2)}"
    return dict(sorted(phases.items()))


def choose_delivered_phase(args: argparse.Namespace, state: Dict[str, Any], errors: List[str]) -> Optional[str]:
    if args.delivered_phase:
        return args.delivered_phase
    if state.get("status") == "delivered" and state.get("current_phase"):
        return str(state["current_phase"])
    errors.append("provide --delivered-phase unless delivery_state.json status is delivered")
    return None


def next_phase_for(delivered_phase: str, phases: Dict[int, str], errors: List[str]) -> Tuple[str, str]:
    delivered_number = phase_number(delivered_phase)
    if delivered_number is None:
        errors.append(f"cannot parse delivered phase number from: {delivered_phase}")
        return "unknown", "unknown"

    next_number = delivered_number + 1
    if next_number in phases:
        return str(next_number), phases[next_number]
    return "finalization", "finalization"


def resolve_policy_target(policy: Dict[str, Any], next_key: str, errors: List[str]) -> Dict[str, Any]:
    defaults = policy.get("defaults")
    if not isinstance(defaults, dict):
        errors.append("phase_model_policy.json is missing object defaults")
        defaults = {}
    phases = policy.get("phases")
    if not isinstance(phases, dict):
        errors.append("phase_model_policy.json is missing object phases")
        phases = {}

    override = phases.get(next_key)
    if override is not None and not isinstance(override, dict):
        errors.append(f"phase_model_policy.json phases.{next_key} is not an object")
        override = None

    source = f"phases.{next_key}" if isinstance(override, dict) else "defaults"
    model = (override or {}).get("model", defaults.get("model"))
    reasoning = (override or {}).get("reasoning_effort", defaults.get("reasoning_effort"))
    if not model:
        errors.append(f"no model could be resolved for next phase key {next_key}")
    if not reasoning:
        errors.append(f"no reasoning_effort could be resolved for next phase key {next_key}")

    return {
        "source": source,
        "model": model,
        "reasoning_effort": reasoning,
        "phase_policy_found": isinstance(override, dict),
    }


def build_plan(args: argparse.Namespace) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    repo_root = Path(args.repo_root).expanduser().resolve()
    forms = slug_forms(args.roadmap_slug)
    state_path, state = find_state(repo_root, forms, errors)
    state = state or {}
    approval_policy = read_approval_policy(repo_root, state_path, state)
    errors.extend(str(item) for item in approval_policy.get("errors", []))

    roadmap_path = resolve_repo_path(repo_root, state.get("roadmap"))
    if roadmap_path is None:
        errors.append("delivery_state.json does not define roadmap")
        roadmap_path = repo_root / "roadmaps" / f"{forms['dir']}_roadmap.md"
    phases = parse_roadmap_phases(roadmap_path, errors)

    delivered_phase = choose_delivered_phase(args, state, errors)
    next_key = "unknown"
    next_phase = "unknown"
    if delivered_phase:
        next_key, next_phase = next_phase_for(delivered_phase, phases, errors)

    automation_dir = find_automation_dir(repo_root, forms)
    policy_path = automation_dir / "phase_model_policy.json" if automation_dir else None
    policy = load_json(policy_path, errors) if policy_path and policy_path.exists() else None
    if policy is None:
        errors.append("phase_model_policy.json was not found or could not be read")
        policy = {}
    base_target = resolve_policy_target(policy, next_key, errors)
    run_quality = classify_run_quality(state)
    adaptive_action = resolve_adaptive_action(
        policy,
        base_target=base_target,
        run_quality=run_quality,
        flawless_streak=state.get("adaptive_flawless_streak", 0),
    )
    errors.extend(str(item) for item in adaptive_action.get("errors", []))
    target = dict(base_target)
    target["base_model"] = base_target.get("model")
    target["base_reasoning_effort"] = base_target.get("reasoning_effort")
    target["adaptive_action"] = adaptive_action.get("action")
    target["adaptive_run_quality"] = adaptive_action.get("run_quality")
    target["adaptive_reason"] = adaptive_action.get("reason")
    if adaptive_action.get("target_changed"):
        adaptive_target = adaptive_action.get("target") or {}
        target["model"] = adaptive_target.get("model")
        target["reasoning_effort"] = adaptive_target.get("reasoning_effort")
        target["source"] = f"{base_target.get('source')}+adaptive.{adaptive_action.get('action')}"

    automation_toml = find_automation_toml(args.automation_id, forms)
    automation_data = parse_minimal_toml(automation_toml) if automation_toml and automation_toml.exists() else {}
    configured_model = automation_data.get("model")
    configured_reasoning = automation_data.get("reasoning_effort")
    model_update_required = configured_model != target["model"]
    reasoning_satisfied = reasoning_satisfies(configured_reasoning, target["reasoning_effort"])
    reasoning_over_required = reasoning_exceeds(configured_reasoning, target["reasoning_effort"])
    reasoning_update_required = bool(target.get("reasoning_effort") and not reasoning_satisfied)
    update_required = model_update_required or reasoning_update_required
    retarget_decision = approval_decision_for_operation(
        approval_policy.get("operations", {}),
        "retarget_saved_automation",
    )

    retarget_status = "not_needed" if not update_required else "requires_approved_update"
    next_action = "advance state and leave automation config unchanged after readback"
    if update_required:
        if retarget_decision["decision"] == "allowed":
            retarget_status = "approved_update_available"
            next_action = "perform the pre-approved automation model/reasoning update, read back config, then stop"
        elif retarget_decision["decision"] == "forbidden":
            retarget_status = "forbidden_by_approval_policy"
            next_action = "record a blocker because approval policy forbids automation retarget"
        else:
            next_action = "request an approved automation model/reasoning update, read back config, then stop"
    if not automation_toml:
        retarget_status = "automation_config_missing"
        next_action = "stop for automation config readback before advancing"
    if args.simulate_update_failure:
        retarget_status = "failed"
        next_action = "write a retarget-failed alert, keep or set state blocked, and do not start the next phase"

    plan = {
        "repo_root": str(repo_root),
        "roadmap_slug": args.roadmap_slug,
        "state_file": str(state_path) if state_path else None,
        "roadmap": str(roadmap_path),
        "delivered_phase": delivered_phase,
        "next_phase_key": next_key,
        "next_phase": next_phase,
        "target": target,
        "run_quality": run_quality,
        "adaptive_action": adaptive_action,
        "automation": {
            "id": args.automation_id,
            "toml": str(automation_toml) if automation_toml else None,
            "status": automation_data.get("status"),
            "execution_environment": automation_data.get("execution_environment"),
            "configured_model": configured_model,
            "configured_reasoning_effort": configured_reasoning,
            "reasoning_satisfied": reasoning_satisfied,
            "reasoning_over_required": reasoning_over_required,
        },
        "approval_policy": approval_policy,
        "retarget": {
            "status": retarget_status,
            "update_required": update_required,
            "model_update_required": model_update_required,
            "reasoning_update_required": reasoning_update_required,
            "reasoning_downgrade_not_required": bool(reasoning_over_required and not reasoning_update_required),
            "approval_required": bool(update_required and retarget_decision["decision"] != "allowed"),
            "approval_decision": retarget_decision,
            "simulated_failure": args.simulate_update_failure,
            "readback_required": True,
        },
        "state_updates": {
            "current_phase": next_phase,
            "required_model": target["model"],
            "required_reasoning_effort": target["reasoning_effort"],
            "configured_automation_model": configured_model,
            "configured_automation_reasoning_effort": configured_reasoning,
            "last_run_quality": run_quality,
            "last_adaptive_action": {
                "action": adaptive_action.get("action"),
                "run_quality": adaptive_action.get("run_quality"),
                "target_phase": next_phase,
                "target": adaptive_action.get("target"),
                "reason": adaptive_action.get("reason"),
            },
            "adaptive_flawless_streak": adaptive_action.get("next_flawless_streak"),
        },
        "failure_path": {
            "state_status": "blocked",
            "alert_kind": "retarget-failed",
            "stop_before_next_phase": True,
        }
        if args.simulate_update_failure
        else None,
        "next_action": next_action,
        "errors": errors,
    }
    return plan, errors


def print_text(plan: Dict[str, Any]) -> None:
    print("Automation Retarget Plan")
    print(f"Roadmap: {plan['roadmap']}")
    print(f"Delivered phase: {plan['delivered_phase']}")
    print(f"Next phase: {plan['next_phase']}")
    print(
        "Target: "
        f"{plan['target']['model']} / {plan['target']['reasoning_effort']} "
        f"from {plan['target']['source']}"
    )
    automation = plan["automation"]
    print(
        "Configured automation: "
        f"{automation.get('configured_model')} / {automation.get('configured_reasoning_effort')}"
    )
    print(f"Retarget status: {plan['retarget']['status']}")
    print(f"Next action: {plan['next_action']}")
    if plan["errors"]:
        print("Errors:")
        for error in plan["errors"]:
            print(f"- {error}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--roadmap-slug", required=True)
    parser.add_argument("--automation-id")
    parser.add_argument("--delivered-phase", help="Delivered numbered phase to plan from, for dry-runs or review gates.")
    parser.add_argument("--simulate-update-failure", help="Return the retarget failure path without mutating files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    plan, errors = build_plan(args)
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print_text(plan)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
