"""Adaptive model policy helpers for roadmap delivery runs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence


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


def _normalized(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def is_run_quality(value: Any) -> bool:
    return _normalized(value) in {item.replace("_", "-") for item in RUN_QUALITIES}


def normalize_run_quality(value: Any) -> Optional[str]:
    normalized = _normalized(value)
    for quality in RUN_QUALITIES:
        if normalized == quality.replace("_", "-"):
            return quality
    return None


def classify_run_quality(
    *,
    verification_status: Any = None,
    review_verdict: Any = None,
    fix_iterations: Any = 0,
    blocker_class: Any = None,
    stalled: bool = False,
    retarget_status: Any = None,
    completion_closeout_failed: bool = False,
) -> str:
    """Classify a run outcome using the durable evidence collected by the gate."""

    retarget = _normalized(retarget_status)
    blocker = _normalized(blocker_class)
    verification = _normalized(verification_status)
    verdict = _normalized(review_verdict)

    if completion_closeout_failed:
        return "completion_closeout_failed"
    if retarget in {"failed", "retarget-failed", "retarget-failed-alert"}:
        return "retarget_failed"
    if stalled:
        return "stalled"
    if blocker in LOCAL_REPAIRABLE_BLOCKERS:
        return "blocked_local_repairable"
    if blocker in HUMAN_GATED_BLOCKERS:
        return "blocked_human_required"
    if verification in {"failed", "error", "failure"}:
        return "verification_failed"
    if verdict == "needs-fix":
        return "review_needs_fix"
    if verdict == "blocked":
        return "blocked_human_required"
    if verdict == "delivered":
        return "delivered_with_fixes" if _nonzero_int(fix_iterations) else "flawless"
    return "blocked_human_required" if blocker else "flawless"


def classify_run_quality_from_state(
    state: Dict[str, Any],
    *,
    stalled: Optional[bool] = None,
    retarget_status: Any = None,
    blocker_class: Any = None,
    completion_closeout_failed: bool = False,
) -> str:
    recorded = normalize_run_quality(state.get("last_run_quality"))
    if recorded:
        return recorded

    verification = state.get("last_verification") if isinstance(state.get("last_verification"), dict) else {}
    review = state.get("last_review") if isinstance(state.get("last_review"), dict) else {}
    if blocker_class is None:
        blocker_class = state.get("blocker_class") or state.get("last_blocker_class")
    if stalled is None:
        stalled_count = _nonzero_int(state.get("stalled_run_count"))
        max_stalled = _nonzero_int(state.get("max_stalled_runs"))
        stalled = bool(max_stalled and stalled_count >= max_stalled)
    fix_iterations = 0
    if _normalized(review.get("verdict")) == "delivered":
        fix_iterations = max(0, _nonzero_int(state.get("review_iterations")) - 1)
    return classify_run_quality(
        verification_status=verification.get("status"),
        review_verdict=review.get("verdict"),
        fix_iterations=fix_iterations,
        blocker_class=blocker_class,
        stalled=bool(stalled),
        retarget_status=retarget_status,
        completion_closeout_failed=completion_closeout_failed,
    )


def _nonzero_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and value > 0:
        return value
    return 0


def _policy_object(policy: Dict[str, Any]) -> Dict[str, Any]:
    value = policy.get("adaptive_model_policy")
    if isinstance(value, dict):
        return value
    value = policy.get("adaptive")
    return value if isinstance(value, dict) else {}


def _string_list(value: Any, default: Sequence[str]) -> List[str]:
    if not isinstance(value, list):
        return list(default)
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def _target_object(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _reasoning_index(value: Any) -> Optional[int]:
    text = str(value or "")
    try:
        return REASONING_ORDER.index(text)
    except ValueError:
        return None


def _next_reasoning(value: Any, max_reasoning: Any = None) -> Any:
    index = _reasoning_index(value)
    if index is None:
        return value
    cap_index = _reasoning_index(max_reasoning)
    if cap_index is None:
        cap_index = len(REASONING_ORDER) - 1
    return REASONING_ORDER[min(index + 1, cap_index)]


def _target_with_defaults(base_model: Any, base_reasoning: Any, target: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "model": target.get("model") or base_model,
        "reasoning_effort": target.get("reasoning_effort") or base_reasoning,
    }


def validate_adaptive_model_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    adaptive = _policy_object(policy)
    enabled = bool(adaptive.get("enabled")) if adaptive else False
    errors: List[Dict[str, str]] = []
    report: Dict[str, Any] = {
        "present": bool(adaptive),
        "enabled": enabled,
        "escalate_on": _string_list(adaptive.get("escalate_on"), DEFAULT_ESCALATE_ON),
        "human_gated_qualities": _string_list(adaptive.get("human_gated_qualities"), DEFAULT_HUMAN_GATED_QUALITIES),
        "deescalate_after_flawless_runs": adaptive.get("deescalate_after_flawless_runs", 0) if adaptive else 0,
        "errors": errors,
    }
    if not adaptive:
        return report

    for field in ("enabled",):
        if field in adaptive and not isinstance(adaptive[field], bool):
            errors.append({"code": "invalid_adaptive_policy", "message": f"adaptive_model_policy.{field} must be boolean."})

    for field in ("escalate_on", "human_gated_qualities"):
        value = adaptive.get(field)
        if value is not None and not isinstance(value, list):
            errors.append({"code": "invalid_adaptive_policy", "message": f"adaptive_model_policy.{field} must be an array."})
            continue
        for item in value or []:
            if normalize_run_quality(item) is None:
                errors.append({"code": "invalid_adaptive_run_quality", "message": f"Unknown run quality {item!r} in adaptive_model_policy.{field}."})

    deescalate_after = adaptive.get("deescalate_after_flawless_runs", 0)
    if not isinstance(deescalate_after, int) or isinstance(deescalate_after, bool) or deescalate_after < 0:
        errors.append({"code": "invalid_adaptive_policy", "message": "adaptive_model_policy.deescalate_after_flawless_runs must be a non-negative integer."})

    caps = adaptive.get("caps")
    if enabled and not isinstance(caps, dict):
        errors.append({"code": "missing_adaptive_caps", "message": "enabled adaptive_model_policy must define caps."})
        caps = {}
    elif not isinstance(caps, dict):
        caps = {}

    allowed_models = caps.get("allowed_models")
    if enabled:
        if not isinstance(allowed_models, list) or not allowed_models or not all(isinstance(item, str) and item.strip() for item in allowed_models):
            errors.append({"code": "invalid_adaptive_caps", "message": "adaptive_model_policy.caps.allowed_models must be a non-empty string array."})
        max_reasoning = caps.get("max_reasoning_effort")
        if max_reasoning not in REASONING_ORDER:
            errors.append({"code": "invalid_adaptive_caps", "message": "adaptive_model_policy.caps.max_reasoning_effort must be a known reasoning effort."})

    for field in ("escalation", "deescalation", "floors"):
        target = adaptive.get(field)
        if target is not None and not isinstance(target, dict):
            errors.append({"code": "invalid_adaptive_policy", "message": f"adaptive_model_policy.{field} must be an object."})
            continue
        if not isinstance(target, dict):
            continue
        model = target.get("model")
        reasoning = target.get("reasoning_effort") or target.get("min_reasoning_effort")
        if model is not None and (not isinstance(model, str) or not model.strip()):
            errors.append({"code": "invalid_adaptive_policy", "message": f"adaptive_model_policy.{field}.model must be a non-empty string."})
        if reasoning is not None and reasoning not in REASONING_ORDER:
            errors.append({"code": "invalid_adaptive_policy", "message": f"adaptive_model_policy.{field} reasoning must be a known effort."})
        if enabled and model is not None and isinstance(allowed_models, list) and model not in allowed_models:
            errors.append({"code": "adaptive_model_exceeds_caps", "message": f"adaptive_model_policy.{field}.model {model!r} is not allowed by caps.allowed_models."})
        max_reasoning = caps.get("max_reasoning_effort")
        if enabled and reasoning is not None and _reasoning_index(reasoning) is not None and _reasoning_index(max_reasoning) is not None:
            if _reasoning_index(reasoning) > _reasoning_index(max_reasoning):
                errors.append({"code": "adaptive_reasoning_exceeds_caps", "message": f"adaptive_model_policy.{field} reasoning {reasoning!r} exceeds caps.max_reasoning_effort."})

    return report


def resolve_adaptive_action(
    policy: Dict[str, Any],
    *,
    base_model: Any,
    base_reasoning_effort: Any,
    run_quality: Any,
    flawless_streak: Any = 0,
) -> Dict[str, Any]:
    adaptive = _policy_object(policy)
    quality = normalize_run_quality(run_quality) or "blocked_human_required"
    target = {"model": base_model, "reasoning_effort": base_reasoning_effort}
    result: Dict[str, Any] = {
        "enabled": bool(adaptive.get("enabled")) if adaptive else False,
        "run_quality": quality,
        "action": "disabled",
        "target": target,
        "target_changed": False,
        "reason": "Adaptive model policy is disabled or absent.",
        "errors": [],
        "next_flawless_streak": _nonzero_int(flawless_streak),
    }
    if not result["enabled"]:
        return result

    validation = validate_adaptive_model_policy(policy)
    if validation["errors"]:
        result["action"] = "blocked_by_policy"
        result["errors"] = validation["errors"]
        result["reason"] = "Adaptive model policy is invalid."
        return result

    escalate_on = {normalize_run_quality(item) for item in _string_list(adaptive.get("escalate_on"), DEFAULT_ESCALATE_ON)}
    human_gated = {normalize_run_quality(item) for item in _string_list(adaptive.get("human_gated_qualities"), DEFAULT_HUMAN_GATED_QUALITIES)}
    caps = adaptive.get("caps") if isinstance(adaptive.get("caps"), dict) else {}

    if quality in human_gated:
        result.update(
            {
                "action": "none_human_gated",
                "reason": "Human-gated blockers require the missing human action instead of model escalation.",
                "next_flawless_streak": 0,
            }
        )
        return result

    if quality in escalate_on:
        escalation = _target_object(adaptive.get("escalation"))
        candidate = _target_with_defaults(
            base_model,
            base_reasoning_effort,
            {
                "model": escalation.get("model"),
                "reasoning_effort": escalation.get("reasoning_effort") or _next_reasoning(base_reasoning_effort, caps.get("max_reasoning_effort")),
            },
        )
        result.update(
            {
                "action": "escalate" if candidate != target else "none_at_cap",
                "target": candidate,
                "target_changed": candidate != target,
                "reason": "Run quality triggers adaptive escalation." if candidate != target else "Run quality triggers escalation, but the target is already at the configured cap.",
                "next_flawless_streak": 0,
            }
        )
        return result

    if quality == "flawless":
        next_streak = _nonzero_int(flawless_streak) + 1
        threshold = adaptive.get("deescalate_after_flawless_runs", 0)
        if isinstance(threshold, int) and not isinstance(threshold, bool) and threshold > 0 and next_streak >= threshold:
            deescalation = _target_object(adaptive.get("deescalation"))
            candidate = _target_with_defaults(base_model, base_reasoning_effort, deescalation)
            result.update(
                {
                    "action": "deescalate" if candidate != target else "none",
                    "target": candidate,
                    "target_changed": candidate != target,
                    "reason": "Flawless run streak reached the configured de-escalation threshold.",
                    "next_flawless_streak": 0 if candidate != target else next_streak,
                }
            )
            return result
        result.update(
            {
                "action": "none",
                "reason": "Flawless run keeps the current model policy target.",
                "next_flawless_streak": next_streak,
            }
        )
        return result

    result.update(
        {
            "action": "none",
            "reason": "Run quality does not trigger an adaptive model change.",
            "next_flawless_streak": 0,
        }
    )
    return result


def adaptive_target_from_state(state: Dict[str, Any], current_phase: Any) -> Optional[Dict[str, Any]]:
    action = state.get("last_adaptive_action")
    if not isinstance(action, dict):
        return None
    target_phase = action.get("target_phase")
    if target_phase and str(target_phase) != str(current_phase):
        return None
    target = action.get("target")
    if not isinstance(target, dict):
        return None
    model = target.get("model")
    reasoning = target.get("reasoning_effort")
    if not model and not reasoning:
        return None
    return {
        "model": model,
        "reasoning_effort": reasoning,
        "source": "state.last_adaptive_action",
        "reason": action.get("reason") or action.get("status") or "Adaptive target recorded in delivery state.",
    }
