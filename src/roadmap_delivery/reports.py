"""Inspect phase-gated roadmap delivery state without mutating files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional

from .git import run_git
from .paths import (
    automation_dir_candidates,
    extract_roadmap_references,
    resolve_repo_path,
    slug_forms,
    state_candidates,
    unique,
)
from .policy import (
    ACTIVE_STATUSES,
    ALLOWED_REASONING_EFFORTS,
    COMPLETED_STATUSES,
    has_hard_stop_guard,
    has_blocked_remediation_guard,
    manual_activation_reconciliation,
    normalized,
    phase_number,
)
from .progress import ProgressSignatureError, build_run_result
from .state import JsonObjectError, load_json_object
from .toml import parse_minimal_toml


AUTOMATIONS_DIR = Path.home() / ".codex" / "automations"
DEEP_REVIEW_FILENAMES = (
    "deep_review_prompt.md",
    "deep_review_prompt.txt",
    "final_deep_review_prompt.md",
    "final-deep-review-prompt.md",
    "final_review_prompt.md",
    "final-review-prompt.md",
    "final_deep_review.md",
    "final-deep-review.md",
    "review_fixes_prompt.md",
    "deep_review.md",
)
DEEP_REVIEW_STATE_KEYS = (
    "deep_review_prompt",
    "deep_review_prompt_path",
    "deep_review",
    "deep_review_path",
    "final_deep_review_prompt_file",
    "final_deep_review_prompt",
    "final_deep_review_review_file",
    "final_deep_review_artifact",
    "final_review_prompt",
    "final_review_artifact",
)
FINAL_DEEP_REVIEW_STATUSES = {"prompt-prepared", "review-complete", "waived-by-human"}
FINAL_DEEP_REVIEW_STATUS_KEYS = ("final_deep_review_status", "deep_review_status", "final_review_status")
FINAL_DEEP_REVIEW_PREPARED_KEYS = ("final_deep_review_prompt_prepared", "deep_review_prompt_prepared")
FINAL_DEEP_REVIEW_WAIVER_REASON_KEYS = (
    "final_deep_review_waiver_reason",
    "final_review_waiver_reason",
    "deep_review_waiver_reason",
)
LIFECYCLE_ACTIVE_STATE_STATUSES = {"active", "in progress", "in-progress"}


def add_warning(warnings: List[Dict[str, str]], code: str, message: str) -> None:
    warnings.append({"code": code, "message": message})


def first_finalization_value(state: Optional[Dict[str, Any]], keys: tuple[str, ...]) -> Any:
    if not state:
        return None
    finalization = state.get("finalization")
    containers: List[Dict[str, Any]] = []
    if isinstance(finalization, dict):
        containers.append(finalization)
    containers.append(state)
    for container in containers:
        for key in keys:
            value = container.get(key)
            if value not in (None, ""):
                return value
    return None


def final_deep_review_status(state: Optional[Dict[str, Any]]) -> Optional[str]:
    value = first_finalization_value(state, FINAL_DEEP_REVIEW_STATUS_KEYS)
    if value is None:
        return None
    return normalized(value)


def final_deep_review_prompt_prepared(state: Optional[Dict[str, Any]]) -> Optional[bool]:
    value = first_finalization_value(state, FINAL_DEEP_REVIEW_PREPARED_KEYS)
    if isinstance(value, bool):
        return value
    return None


def final_deep_review_waiver_reason(state: Optional[Dict[str, Any]]) -> Optional[str]:
    value = first_finalization_value(state, FINAL_DEEP_REVIEW_WAIVER_REASON_KEYS)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def load_json(path: Path, warnings: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    if not path.exists():
        add_warning(warnings, "missing_state_file", f"State file does not exist: {path}")
        return None
    try:
        return load_json_object(path)
    except JsonObjectError as exc:
        message = str(exc)
        if message.startswith("Invalid JSON"):
            add_warning(warnings, "invalid_state_json", f"State file is invalid JSON: {path}: {message}")
        elif message.startswith("JSON root"):
            add_warning(warnings, "invalid_state_shape", f"State file root is not an object: {path}")
        else:
            raise RuntimeError(f"Cannot read state file {path}: {exc}") from exc
        return None


def load_state_from_candidates(
    repo_root: Path,
    forms: Dict[str, Optional[str]],
    warnings: List[Dict[str, str]],
) -> tuple[Optional[Path], Optional[Dict[str, Any]]]:
    candidates = state_candidates(repo_root, forms)
    for candidate in candidates:
        if candidate.exists():
            return candidate, load_json(candidate, warnings)
    if candidates:
        add_warning(
            warnings,
            "missing_state_file",
            "State file does not exist. Checked: " + ", ".join(str(path) for path in candidates),
        )
        return candidates[0], None
    return None, None


def find_automation_id(forms: Dict[str, Optional[str]], warnings: List[Dict[str, str]]) -> Optional[str]:
    dash = forms["dash"]
    directory = forms["dir"]
    if not dash and not directory:
        return None

    preferred = []
    if dash:
        preferred.append(f"{dash}-delivery")
    if directory:
        preferred.append(f"{directory}-delivery")
    for candidate in preferred:
        if (AUTOMATIONS_DIR / candidate / "automation.toml").exists():
            return candidate

    matches: List[str] = []
    if AUTOMATIONS_DIR.exists():
        needles = [item for item in (dash, directory) if item]
        for toml in AUTOMATIONS_DIR.glob("*/automation.toml"):
            try:
                text = toml.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if any(needle in text or needle in toml.parent.name for needle in needles):
                matches.append(toml.parent.name)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        add_warning(
            warnings,
            "multiple_automation_matches",
            "Multiple automation configs match the slug: " + ", ".join(sorted(matches)),
        )
    return None


def warn_lifecycle_filename_drift(
    roadmap_path: Optional[Path],
    state_status: Any,
    current_phase: Any,
    roadmap_status: Any,
    warnings: List[Dict[str, str]],
) -> None:
    if not roadmap_path or not roadmap_path.name.startswith("not_started_"):
        return
    phase = phase_number(current_phase)
    phase_started = phase is not None and int(phase) >= 1
    if normalized(state_status) in LIFECYCLE_ACTIVE_STATE_STATUSES or normalized(roadmap_status) in ACTIVE_STATUSES or phase_started:
        add_warning(
            warnings,
            "roadmap_lifecycle_filename_mismatch",
            f"Active roadmap or Phase 1+ roadmap still uses a not_started_ lifecycle filename: {roadmap_path}",
        )


def read_roadmap_header(roadmap_path: Optional[Path], warnings: List[Dict[str, str]]) -> Dict[str, str]:
    if not roadmap_path or not roadmap_path.exists() or not roadmap_path.is_file():
        return {}
    try:
        text = roadmap_path.read_text(encoding="utf-8")
    except OSError as exc:
        add_warning(warnings, "roadmap_unreadable", f"Cannot read roadmap file: {roadmap_path}: {exc}")
        return {}
    header: Dict[str, str] = {}
    for line in text.splitlines()[:80]:
        match = re.match(r"^(Status|Current phase|Last completed phase|Next action):\s*(.+?)\s*$", line)
        if match:
            header[match.group(1).lower()] = match.group(2)
    return header


def is_complete_state(state: Optional[Dict[str, Any]]) -> bool:
    if not state:
        return False
    state_status = normalized(state.get("status"))
    current_phase = normalized(state.get("current_phase"))
    return (
        bool(state.get("all_phases_complete"))
        or state_status in COMPLETED_STATUSES
        or current_phase in {"complete", "completed", "all-phases-complete"}
    )


def inspect_completion_alert(
    repo_root: Path,
    state: Optional[Dict[str, Any]],
    warnings: List[Dict[str, str]],
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "completion_alert_present": False,
        "completion_alert_kind": None,
        "completion_alert_file": None,
    }
    if not state or not is_complete_state(state):
        return result

    last_alert = state.get("last_operator_alert")
    if not isinstance(last_alert, dict):
        add_warning(
            warnings,
            "completed_state_missing_completed_alert",
            "Completed state does not record a completed operator alert.",
        )
        return result

    kind = last_alert.get("kind")
    result["completion_alert_kind"] = kind
    file_value = last_alert.get("file")
    if isinstance(file_value, str) and file_value.strip():
        alert_path = resolve_repo_path(repo_root, file_value)
        result["completion_alert_file"] = str(alert_path) if alert_path else None
    else:
        alert_path = None

    if kind != "completed":
        add_warning(
            warnings,
            "completed_state_missing_completed_alert",
            f"Completed state records alert kind {kind!r}, not 'completed'.",
        )
    elif alert_path and alert_path.exists() and alert_path.is_file():
        result["completion_alert_present"] = True
    else:
        add_warning(
            warnings,
            "completed_state_missing_completed_alert",
            "Completed state records a completed alert, but the alert file is missing.",
        )
    return result


def find_deep_review_artifact(
    repo_root: Path,
    state_file: Optional[Path],
    forms: Dict[str, Optional[str]],
    state: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if state:
        for key in DEEP_REVIEW_STATE_KEYS:
            value = first_finalization_value(state, (key,))
            if value:
                path = resolve_repo_path(repo_root, str(value))
                return {
                    "path": str(path) if path else str(value),
                    "exists": bool(path and path.exists() and path.is_file()),
                }
        last_verification = state.get("last_verification")
        if isinstance(last_verification, dict) and last_verification.get("deep_review_prompt"):
            value = str(last_verification["deep_review_prompt"])
            path = resolve_repo_path(repo_root, value)
            return {
                "path": str(path) if path else value,
                "exists": bool(path and path.exists() and path.is_file()),
            }

    deep_review_dirs: List[Path] = []
    if state_file is not None:
        deep_review_dirs.append(state_file.parent)
    deep_review_dirs.extend(path for path in automation_dir_candidates(repo_root, forms) if path not in deep_review_dirs)
    for automation_dir in deep_review_dirs:
        review_dir = automation_dir / "reviews"
        if review_dir.is_dir():
            for pattern in ("*deep-review-prompt.md", "*final-deep-review*.md"):
                for path in review_dir.glob(pattern):
                    return {"path": str(path), "exists": path.is_file()}
        for name in DEEP_REVIEW_FILENAMES:
            path = automation_dir / name
            if path.exists():
                return {"path": str(path), "exists": path.is_file()}
    return {"path": None, "exists": False}


def inspect_final_deep_review(
    repo_root: Path,
    state_file: Optional[Path],
    forms: Dict[str, Optional[str]],
    state: Optional[Dict[str, Any]],
    complete: bool,
    warnings: List[Dict[str, str]],
) -> Dict[str, Any]:
    status = final_deep_review_status(state)
    prompt_prepared = final_deep_review_prompt_prepared(state)
    waiver_reason = final_deep_review_waiver_reason(state)
    artifact = find_deep_review_artifact(repo_root, state_file, forms, state)
    result: Dict[str, Any] = {
        "status": status,
        "prompt_prepared": prompt_prepared,
        "prompt": artifact["path"],
        "prompt_exists": artifact["exists"],
        "waived": status == "waived-by-human",
        "waiver_reason": waiver_reason,
    }
    if not complete:
        return result

    if status is not None and status not in FINAL_DEEP_REVIEW_STATUSES:
        add_warning(
            warnings,
            "invalid_final_deep_review_status",
            f"Final deep-review status {status!r} is not one of {sorted(FINAL_DEEP_REVIEW_STATUSES)}.",
        )
    if status == "waived-by-human":
        if not waiver_reason:
            add_warning(
                warnings,
                "final_deep_review_waiver_missing_reason",
                "Final deep review was waived, but no human waiver reason is recorded.",
            )
        return result
    if not artifact["exists"]:
        add_warning(
            warnings,
            "completed_state_missing_final_deep_review_prompt",
            "Completed state does not record an existing final deep-review prompt/review artifact or a human waiver.",
        )
    elif prompt_prepared is None:
        add_warning(
            warnings,
            "final_deep_review_metadata_missing",
            "Completed state has a final deep-review prompt, but does not record final_deep_review_prompt_prepared.",
        )
    if artifact["exists"] and status is None:
        add_warning(
            warnings,
            "final_deep_review_status_missing",
            "Completed state has a final deep-review prompt, but does not record final_deep_review_status.",
        )
    return result


def inspect_model_policy(
    policy_path: Optional[Path],
    state: Optional[Dict[str, Any]],
    automation_data: Dict[str, Any],
    warnings: List[Dict[str, str]],
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "policy_path": str(policy_path) if policy_path else None,
        "present": False,
        "required_model": None,
        "required_reasoning_effort": None,
        "configured_model": automation_data.get("model") if automation_data else None,
        "configured_reasoning_effort": automation_data.get("reasoning_effort") if automation_data else None,
        "model_mismatch": False,
        "reasoning_mismatch": False,
    }
    if not policy_path or not policy_path.exists() or not state:
        return result
    result["present"] = True
    try:
        with policy_path.open("r", encoding="utf-8") as fh:
            policy = json.load(fh)
    except json.JSONDecodeError as exc:
        add_warning(warnings, "invalid_model_policy_json", f"Policy file is invalid JSON: {policy_path}: {exc}")
        return result
    except OSError as exc:
        add_warning(warnings, "model_policy_unreadable", f"Cannot read policy file: {policy_path}: {exc}")
        return result
    if not isinstance(policy, dict):
        add_warning(warnings, "invalid_model_policy_shape", f"Policy file root is not an object: {policy_path}")
        return result
    result["schema_version"] = policy.get("schema_version")
    if policy.get("schema_version") != 1:
        add_warning(warnings, "unsupported_model_policy_schema", f"Policy schema_version must be 1: {policy_path}")
    defaults = policy.get("defaults") if isinstance(policy.get("defaults"), dict) else {}
    phases = policy.get("phases") if isinstance(policy.get("phases"), dict) else {}
    phase_key = phase_number(state.get("current_phase"))
    if not phase_key and normalized(state.get("current_phase")) in {"complete", "completed", "finalization"}:
        phase_key = "finalization"
    phase_policy = phases.get(phase_key, {}) if phase_key else {}
    if not isinstance(phase_policy, dict):
        phase_policy = {}
    required_model = phase_policy.get("model") or defaults.get("model")
    required_reasoning = phase_policy.get("reasoning_effort") or defaults.get("reasoning_effort")
    configured_model = automation_data.get("model") or state.get("configured_automation_model")
    configured_reasoning = automation_data.get("reasoning_effort") or state.get("configured_automation_reasoning_effort")
    result.update(
        {
            "required_model": required_model,
            "required_reasoning_effort": required_reasoning,
            "configured_model": configured_model,
            "configured_reasoning_effort": configured_reasoning,
            "model_mismatch": bool(required_model and configured_model and str(required_model) != str(configured_model)),
            "reasoning_mismatch": bool(required_reasoning and configured_reasoning and str(required_reasoning) != str(configured_reasoning)),
        }
    )
    if required_reasoning and str(required_reasoning) not in ALLOWED_REASONING_EFFORTS:
        add_warning(warnings, "invalid_required_reasoning_effort", f"Required reasoning effort {required_reasoning!r} is not known.")
    if result["model_mismatch"]:
        add_warning(warnings, "automation_model_mismatch", f"Required model {required_model!r} differs from configured model {configured_model!r}.")
    if result["reasoning_mismatch"]:
        add_warning(warnings, "automation_reasoning_mismatch", f"Required reasoning {required_reasoning!r} differs from configured reasoning {configured_reasoning!r}.")
    return result


def lifecycle_matches(repo_root: Path, forms: Dict[str, Optional[str]]) -> List[str]:
    roadmaps_dir = repo_root / "roadmaps"
    if not roadmaps_dir.is_dir():
        return []
    needles = {item for item in (forms["dash"], forms["dir"]) if item}
    matches: List[str] = []
    for path in roadmaps_dir.glob("*.md"):
        normalized_name = path.name.replace("_", "-")
        if any(needle and needle in normalized_name for needle in needles):
            matches.append(str(path))
    return sorted(matches)


def normalize_branch_line(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("* "):
        stripped = stripped[2:].strip()
    return stripped


def inspect(args: argparse.Namespace) -> Dict[str, Any]:
    repo_root = Path(args.repo_root).expanduser().resolve()
    if not repo_root.is_dir():
        raise RuntimeError(f"--repo-root is not a directory: {repo_root}")

    warnings: List[Dict[str, str]] = []
    forms = slug_forms(args.roadmap_slug)
    automation_id = args.automation_id
    if not automation_id:
        automation_id = find_automation_id(forms, warnings)

    automation_status = None
    automation_prompt = ""
    automation_toml = None
    automation_roadmap_references: List[str] = []
    automation_data: Dict[str, Any] = {}
    blocked_remediation_guard = False
    hard_stop_guard = False
    if automation_id:
        automation_toml = AUTOMATIONS_DIR / automation_id / "automation.toml"
        if not automation_toml.exists():
            add_warning(warnings, "missing_automation_config", f"Automation config does not exist: {automation_toml}")
        else:
            automation_data = parse_minimal_toml(automation_toml)
            automation_status = automation_data.get("status")
            automation_prompt = str(automation_data.get("prompt") or "")
            hard_stop_guard = has_hard_stop_guard(automation_prompt)
            blocked_remediation_guard = has_blocked_remediation_guard(automation_prompt)
            automation_roadmap_references = [
                str(path)
                for path in extract_roadmap_references(
                    automation_prompt,
                    repo_root,
                    require_roadmap_suffix=True,
                )
            ]
            if args.roadmap_slug and forms["dash"] and forms["dir"]:
                if forms["dash"] not in automation_prompt and forms["dir"] not in automation_prompt and forms["dash"] not in automation_id and forms["dir"] not in automation_id:
                    add_warning(
                        warnings,
                        "automation_slug_mismatch",
                        f"Automation {automation_id!r} does not appear to reference roadmap slug {args.roadmap_slug!r}.",
                    )

    if not args.roadmap_slug and automation_prompt:
        match = re.search(r"(?:roadmaps/)?automation/([A-Za-z0-9_-]+)/delivery_state\.json", automation_prompt)
        if match:
            forms = slug_forms(match.group(1))

    state_file = None
    state = None
    if forms["dir"] or forms["dash"]:
        state_file, state = load_state_from_candidates(repo_root, forms, warnings)

    state_slug = state.get("roadmap_slug") if state else None
    if args.roadmap_slug and state_slug:
        requested = args.roadmap_slug.replace("_", "-")
        actual = str(state_slug).replace("_", "-")
        if requested != actual:
            add_warning(
                warnings,
                "roadmap_slug_mismatch",
                f"Requested slug {args.roadmap_slug!r} differs from state roadmap_slug {state_slug!r}",
            )

    state_roadmap = state.get("roadmap") if state else None
    roadmap_path = resolve_repo_path(repo_root, str(state_roadmap)) if state_roadmap else None
    if roadmap_path and not roadmap_path.exists():
        add_warning(warnings, "missing_roadmap_file", f"Roadmap file does not exist: {roadmap_path}")

    for ref in automation_roadmap_references:
        ref_path = Path(ref)
        if roadmap_path and ref_path != roadmap_path and not ref_path.exists():
            add_warning(
                warnings,
                "stale_automation_roadmap_path",
                f"Automation prompt references missing roadmap path {ref_path}; state points to {roadmap_path}",
            )
        elif roadmap_path and ref_path != roadmap_path:
            add_warning(
                warnings,
                "automation_roadmap_path_mismatch",
                f"Automation prompt references {ref_path}; state points to {roadmap_path}",
            )

    matches = lifecycle_matches(repo_root, forms)
    if len(matches) > 1:
        add_warning(
            warnings,
            "multiple_matching_roadmap_files",
            "Multiple roadmap lifecycle files match the slug: " + ", ".join(matches),
        )

    branch_proc = run_git(repo_root, ["branch", "--show-current"])
    current_branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else None
    if branch_proc.returncode != 0:
        add_warning(warnings, "git_branch_failed", branch_proc.stderr.strip() or "git branch --show-current failed")

    branch_patterns = []
    if forms["dash"]:
        branch_patterns.append(f"codex/{forms['dash']}*")
    if forms["dir"]:
        branch_patterns.append(f"codex/{forms['dir']}*")
    matching_branches: List[str] = []
    for pattern in unique(branch_patterns):
        proc = run_git(repo_root, ["branch", "--list", pattern])
        if proc.returncode == 0:
            matching_branches.extend(normalize_branch_line(line) for line in proc.stdout.splitlines() if line.strip())
        else:
            add_warning(warnings, "git_branch_list_failed", proc.stderr.strip() or f"git branch --list {pattern} failed")
    matching_branches = sorted(unique(matching_branches))

    status_proc = run_git(repo_root, ["status", "--short"])
    worktree_dirty = False
    if status_proc.returncode == 0:
        worktree_dirty = bool(status_proc.stdout.strip())
        if worktree_dirty:
            add_warning(warnings, "worktree_dirty", "Repository has uncommitted changes.")
    else:
        add_warning(warnings, "git_status_failed", status_proc.stderr.strip() or "git status --short failed")

    state_branch = state.get("branch") if state else None
    if state_branch and current_branch and state_branch != current_branch:
        add_warning(
            warnings,
            "current_branch_mismatch",
            f"Current branch {current_branch!r} differs from state branch {state_branch!r}.",
        )

    state_status = state.get("status") if state else None
    current_phase = state.get("current_phase") if state else None
    state_schema_version = state.get("schema_version") if state else None
    if state is not None and state_schema_version is None:
        add_warning(
            warnings,
            "legacy_delivery_state_schema_version",
            "Delivery state has no schema_version; accepted in legacy compatibility mode.",
        )
    elif state_schema_version not in (None, 1):
        add_warning(warnings, "invalid_delivery_state_schema_version", "Delivery state schema_version must be 1.")
    last_delivered_phase = state.get("last_delivered_phase") if state else None
    blocked_reason = state.get("blocked_reason") if state else None
    roadmap_header = read_roadmap_header(roadmap_path, warnings)
    roadmap_status = roadmap_header.get("status")
    warn_lifecycle_filename_drift(roadmap_path, state_status, current_phase, roadmap_status, warnings)
    state_dir = state_file.parent if state_file else None
    policy_path = state_dir / "phase_model_policy.json" if state_dir else None
    model_policy = inspect_model_policy(policy_path, state, automation_data, warnings)
    progress_report: Dict[str, Any] = {}
    if state_file is not None and state is not None:
        try:
            progress_report = build_run_result(repo_root, state_file, state)
        except ProgressSignatureError as exc:
            add_warning(warnings, "progress_signature_failed", str(exc))
        else:
            for item in progress_report.get("run_log_errors", []):
                line = item.get("line")
                suffix = f" line {line}" if line is not None else ""
                add_warning(warnings, "invalid_run_log_jsonl", f"{item.get('path')}{suffix}: {item.get('message')}")
    blocked_remediation_required = normalized(state_status) == "blocked"
    if automation_prompt and not blocked_remediation_guard:
        add_warning(warnings, "automation_prompt_missing_blocked_remediation_guard", "Automation prompt does not include Blocked Remediation Mode.")
    all_phases_complete = is_complete_state(state)
    completion_alert = inspect_completion_alert(repo_root, state, warnings)
    final_deep_review = inspect_final_deep_review(repo_root, state_file, forms, state, all_phases_complete, warnings)
    activation_reconciliation = manual_activation_reconciliation(
        state,
        automation_status,
        model_policy,
        blocked_remediation_guard=blocked_remediation_guard,
        hard_stop_guard=hard_stop_guard,
        complete=all_phases_complete,
    )
    completion_pause_required = all_phases_complete and str(automation_status).upper() == "ACTIVE"
    automation_should_be_paused = all_phases_complete and str(automation_status).upper() != "PAUSED"
    if all_phases_complete and str(automation_status).upper() == "ACTIVE":
        add_warning(
            warnings,
            "completed_state_active_automation",
            "State appears complete but the automation is ACTIVE.",
        )

    return {
        "automation_id": automation_id,
        "automation_status": automation_status,
        "automation_toml": str(automation_toml) if automation_toml else None,
        "automation_roadmap_references": automation_roadmap_references,
        "roadmap_path": str(roadmap_path) if roadmap_path else None,
        "state_file": str(state_file) if state_file else None,
        "state_status": state_status,
        "roadmap_status": roadmap_status,
        "state_schema_version": state_schema_version,
        "current_phase": current_phase,
        "last_delivered_phase": last_delivered_phase,
        "blocked_reason": blocked_reason,
        "last_blocker_repair": state.get("last_blocker_repair") if state else None,
        "blocked_remediation_required": blocked_remediation_required,
        "blocked_remediation_guard": blocked_remediation_guard,
        "hard_stop_guard": hard_stop_guard,
        "activation_reconciliation": activation_reconciliation,
        "required_model": model_policy.get("required_model"),
        "required_reasoning_effort": model_policy.get("required_reasoning_effort"),
        "configured_automation_model": model_policy.get("configured_model"),
        "configured_automation_reasoning_effort": model_policy.get("configured_reasoning_effort"),
        "model_mismatch": model_policy.get("model_mismatch"),
        "reasoning_mismatch": model_policy.get("reasoning_mismatch"),
        "run_count": state.get("run_count") if state else None,
        "next_run_count": progress_report.get("run_count"),
        "stalled_run_count": state.get("stalled_run_count") if state else None,
        "next_stalled_run_count": progress_report.get("stalled_run_count"),
        "max_stalled_runs": state.get("max_stalled_runs") if state else None,
        "policy_max_stalled_runs": progress_report.get("max_stalled_runs"),
        "progress_signature": progress_report.get("progress_signature"),
        "previous_progress_signature": progress_report.get("previous_progress_signature"),
        "progress_detected": progress_report.get("progress_detected"),
        "stall_threshold_reached": progress_report.get("threshold_reached"),
        "phase_6_alert_required": progress_report.get("phase_6_alert_required"),
        "run_log_path": progress_report.get("run_log_path"),
        "run_log_entries": progress_report.get("run_log_entries"),
        "run_log_valid": not bool(progress_report.get("run_log_errors")) if progress_report else None,
        "model_policy": model_policy,
        "model_policy_schema_version": model_policy.get("schema_version"),
        "all_phases_complete": all_phases_complete,
        "completion_alert_present": completion_alert["completion_alert_present"],
        "completion_alert_kind": completion_alert["completion_alert_kind"],
        "completion_alert_file": completion_alert["completion_alert_file"],
        "completion_pause_required": completion_pause_required,
        "automation_should_be_paused": automation_should_be_paused,
        "final_deep_review_status": final_deep_review["status"],
        "final_deep_review_prompt": final_deep_review["prompt"],
        "final_deep_review_prompt_prepared": final_deep_review["prompt_prepared"],
        "final_deep_review_waived": final_deep_review["waived"],
        "current_branch": current_branch,
        "matching_branches": matching_branches,
        "worktree_dirty": worktree_dirty,
        "deep_review_prompt_exists": final_deep_review["prompt_exists"],
        "warnings": warnings,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect phase-gated roadmap delivery state without mutating files.")
    parser.add_argument("--repo-root", required=True, help="Repository root to inspect.")
    parser.add_argument("--roadmap-slug", help="Roadmap slug, accepting hyphen or underscore form.")
    parser.add_argument("--automation-id", help="Codex automation id under ~/.codex/automations.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    if not args.roadmap_slug and not args.automation_id:
        parser.error("at least one of --roadmap-slug or --automation-id is required")

    try:
        result = inspect(args)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for key in (
            "automation_id",
            "automation_status",
            "roadmap_path",
            "state_file",
            "roadmap_status",
            "state_status",
            "state_schema_version",
            "current_phase",
            "last_delivered_phase",
            "blocked_reason",
            "blocked_remediation_required",
            "blocked_remediation_guard",
            "hard_stop_guard",
            "activation_reconciliation",
            "required_model",
            "required_reasoning_effort",
            "configured_automation_model",
            "configured_automation_reasoning_effort",
            "model_mismatch",
            "reasoning_mismatch",
            "run_count",
            "next_run_count",
            "stalled_run_count",
            "next_stalled_run_count",
            "max_stalled_runs",
            "policy_max_stalled_runs",
            "progress_signature",
            "previous_progress_signature",
            "progress_detected",
            "stall_threshold_reached",
            "phase_6_alert_required",
            "run_log_path",
            "run_log_entries",
            "run_log_valid",
            "model_policy_schema_version",
            "all_phases_complete",
            "completion_alert_present",
            "completion_pause_required",
            "automation_should_be_paused",
            "final_deep_review_status",
            "final_deep_review_prompt",
            "final_deep_review_prompt_prepared",
            "final_deep_review_waived",
            "current_branch",
            "worktree_dirty",
            "deep_review_prompt_exists",
        ):
            print(f"{key}: {result.get(key)}")
        if result["warnings"]:
            print("warnings:")
            for warning in result["warnings"]:
                print(f"- {warning['code']}: {warning['message']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
