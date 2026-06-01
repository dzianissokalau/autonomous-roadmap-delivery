"""Stable command line interface for roadmap delivery workflows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from . import __version__
from .approval import (
    APPROVAL_MODES,
    approved_operation_names,
    default_approval_policy,
    parse_operation_assignments,
    read_approval_policy,
    validate_approval_policy,
)
from .paths import slug_forms
from .reports import inspect as inspect_state
from .state import JsonObjectError, load_json_object
from .validation import parse_allowed_warning_codes, print_text as print_validation_text, validate


CLI_SCHEMA_VERSION = 1


def _repo_root(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _status(report: Dict[str, Any]) -> str:
    if report.get("errors"):
        return "error"
    if report.get("warnings"):
        return "warning"
    return "ok"


def _with_cli_fields(report: Dict[str, Any], command: str) -> Dict[str, Any]:
    result = dict(report)
    result["cli_schema_version"] = CLI_SCHEMA_VERSION
    result["command"] = command
    result["status"] = _status(result)
    return result


def _strict_failed(report: Dict[str, Any], allowed: set[str]) -> bool:
    return any(str(item.get("code")) not in allowed for item in report.get("warnings", []))


def _print_json(report: Dict[str, Any]) -> None:
    print(json.dumps(report, indent=2, sort_keys=True))


def _print_key_values(report: Dict[str, Any], keys: Iterable[str]) -> None:
    for key in keys:
        print(f"{key}: {report.get(key)}")
    for section in ("errors", "warnings"):
        items = report.get(section) or []
        print(f"{section}: {len(items)}")
        for item in items:
            path = f" [{item['path']}]" if item.get("path") else ""
            print(f"- {item.get('code')}: {item.get('message')}{path}")


def _require_slug_or_automation(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if not args.roadmap_slug and not args.automation_id:
        parser.error("at least one of --roadmap-slug or --automation-id is required")


def run_version(args: argparse.Namespace) -> int:
    report = {
        "cli_schema_version": CLI_SCHEMA_VERSION,
        "command": "version",
        "status": "ok",
        "name": "roadmap-delivery",
        "version": __version__,
    }
    if args.json:
        _print_json(report)
    else:
        print(f"roadmap-delivery {__version__}")
    return 0


def run_inspect(args: argparse.Namespace) -> int:
    _require_slug_or_automation(args.parser, args)
    namespace = argparse.Namespace(
        repo_root=args.repo_root,
        roadmap_slug=args.roadmap_slug,
        automation_id=args.automation_id,
    )
    try:
        report = _with_cli_fields(inspect_state(namespace), "inspect")
    except RuntimeError as exc:
        report = _with_cli_fields(
            {
                "repo_root": str(_repo_root(args.repo_root)),
                "errors": [{"code": "inspect_failed", "message": str(exc)}],
                "warnings": [],
            },
            "inspect",
        )

    if args.json:
        _print_json(report)
    else:
        _print_key_values(
            report,
            (
                "command",
                "status",
                "automation_id",
                "automation_status",
                "roadmap_path",
                "state_file",
                "state_status",
                "current_phase",
                "required_model",
                "required_reasoning_effort",
                "configured_automation_model",
                "configured_automation_reasoning_effort",
                "current_branch",
                "worktree_dirty",
            ),
        )

    if report.get("errors"):
        return 1
    allowed = parse_allowed_warning_codes(args.allow_warning)
    if args.strict and _strict_failed(report, allowed):
        return 1
    return 0


def run_validate(args: argparse.Namespace) -> int:
    _require_slug_or_automation(args.parser, args)
    repo_root = _repo_root(args.repo_root)
    report = validate(repo_root, args.roadmap_slug, args.automation_id)
    attach_approval_policy_report(report, repo_root)
    report = _with_cli_fields(report, "validate")
    if args.json:
        _print_json(report)
    else:
        print_validation_text(report)

    if report.get("errors"):
        return 1
    allowed = parse_allowed_warning_codes(args.allow_warning)
    if args.strict and _strict_failed(report, allowed):
        return 1
    return 0


def attach_approval_policy_report(report: Dict[str, Any], repo_root: Path) -> None:
    if "approval_policy" in report:
        return
    state_file_value = report.get("state_file")
    if not isinstance(state_file_value, str) or not state_file_value:
        return
    state_file = Path(state_file_value)
    try:
        state = load_json_object(state_file)
    except JsonObjectError:
        return
    approval_report = read_approval_policy(repo_root, state_file, state)
    report["approval_policy"] = approval_report
    report.setdefault("errors", []).extend(approval_report.get("errors", []))


def build_approval_policy_from_args(args: argparse.Namespace) -> tuple[Dict[str, Any], List[Dict[str, str]]]:
    operations, errors = parse_operation_assignments(getattr(args, "approval_operation", None))
    mode = getattr(args, "approval_mode", "conservative")
    if mode != "custom" and operations:
        errors.append(
            {
                "code": "approval_operations_require_custom_mode",
                "message": "--approval-operation may only be used with --approval-mode custom.",
            }
        )
        operations = {}
    policy = default_approval_policy(mode, operations if mode == "custom" else None)
    errors.extend(validate_approval_policy(policy))
    return policy, errors


def build_scaffold_plan(args: argparse.Namespace) -> Dict[str, Any]:
    repo_root = _repo_root(args.repo_root)
    forms = slug_forms(args.roadmap_slug)
    slug_dir = forms["dir"] or args.roadmap_slug
    automation_id = args.automation_id or args.roadmap_slug
    automation_dir = repo_root / "automation" / slug_dir
    roadmap_path = repo_root / "roadmaps" / f"not_started_{slug_dir}_roadmap.md"
    approval_policy_path = automation_dir / "approval_policy.json"
    approval_policy, approval_errors = build_approval_policy_from_args(args)
    planned_paths = [
        {"kind": "file", "path": str(roadmap_path), "exists": roadmap_path.exists()},
        {"kind": "directory", "path": str(automation_dir), "exists": automation_dir.exists()},
        {"kind": "file", "path": str(automation_dir / "automation_guide.md"), "exists": (automation_dir / "automation_guide.md").exists()},
        {"kind": "file", "path": str(approval_policy_path), "exists": approval_policy_path.exists()},
        {"kind": "file", "path": str(automation_dir / "delivery_state.json"), "exists": (automation_dir / "delivery_state.json").exists()},
        {"kind": "file", "path": str(automation_dir / "delivery_log.md"), "exists": (automation_dir / "delivery_log.md").exists()},
        {"kind": "file", "path": str(automation_dir / "review_fix_state.json"), "exists": (automation_dir / "review_fix_state.json").exists()},
        {"kind": "file", "path": str(automation_dir / "review_fix_log.md"), "exists": (automation_dir / "review_fix_log.md").exists()},
        {"kind": "file", "path": str(automation_dir / "phase_model_policy.json"), "exists": (automation_dir / "phase_model_policy.json").exists()},
        {"kind": "file", "path": str(automation_dir / "automation_run_log.jsonl"), "exists": (automation_dir / "automation_run_log.jsonl").exists()},
        {"kind": "directory", "path": str(automation_dir / "reviews"), "exists": (automation_dir / "reviews").exists()},
        {"kind": "directory", "path": str(automation_dir / "alerts"), "exists": (automation_dir / "alerts").exists()},
    ]
    return {
        "cli_schema_version": CLI_SCHEMA_VERSION,
        "command": "scaffold",
        "status": "ok",
        "dry_run": bool(args.dry_run),
        "repo_root": str(repo_root),
        "roadmap_slug": args.roadmap_slug,
        "automation_id": automation_id,
        "approval_policy": {
            "path": str(approval_policy_path),
            "approval_mode": approval_policy["approval_mode"],
            "approved_operations": approved_operation_names(approval_policy["operations"]),
            "policy": approval_policy,
        },
        "planned_paths": planned_paths,
        "would_create": [item["path"] for item in planned_paths if not item["exists"]],
        "created": [],
        "errors": approval_errors,
        "warnings": [],
    }
    report["status"] = _status(report)
    return report


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_text_if_missing(path: Path, content: str, created: List[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(str(path))


def apply_scaffold_plan(report: Dict[str, Any]) -> None:
    repo_root = Path(str(report["repo_root"]))
    roadmap_slug = str(report["roadmap_slug"])
    automation_id = str(report["automation_id"])
    forms = slug_forms(roadmap_slug)
    slug_dir = forms["dir"] or roadmap_slug
    phase = "Phase 0 - Scope Confirmation"
    timestamp = _utc_now()
    automation_dir = repo_root / "automation" / slug_dir
    roadmap_path = repo_root / "roadmaps" / f"not_started_{slug_dir}_roadmap.md"
    approval_policy = report["approval_policy"]["policy"]
    approval_policy_rel = f"automation/{slug_dir}/approval_policy.json"
    created: List[str] = []

    for directory in (automation_dir, automation_dir / "reviews", automation_dir / "alerts"):
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(str(directory))

    _write_text_if_missing(
        roadmap_path,
        "\n".join(
            [
                f"# {roadmap_slug.replace('-', ' ').title()} Roadmap",
                "",
                "Status: Not Started",
                f"Current phase: {phase}",
                f"Last updated: {timestamp[:10]}",
                "Next action: Confirm scope and start Phase 0.",
                "Blocked by: None",
                "",
                f"## {phase}",
                "",
                "### Objective",
                "",
                "Confirm scope and delivery boundaries.",
                "",
            ]
        ),
        created,
    )
    _write_text_if_missing(
        automation_dir / "automation_guide.md",
        "\n".join(
            [
                f"# {roadmap_slug.replace('-', ' ').title()} Automation Guide",
                "",
                "Status: Draft",
                f"Roadmap: `roadmaps/not_started_{slug_dir}_roadmap.md`",
                f"Roadmap slug: `{roadmap_slug}`",
                f"Codex automation: `{automation_id}`",
                "",
            ]
        ),
        created,
    )
    _write_text_if_missing(
        automation_dir / "approval_policy.json",
        json.dumps(approval_policy, indent=2, sort_keys=False) + "\n",
        created,
    )
    state = {
        "schema_version": 1,
        "roadmap": f"roadmaps/not_started_{slug_dir}_roadmap.md",
        "roadmap_slug": roadmap_slug,
        "current_phase": phase,
        "branch": None,
        "status": "not_started",
        "review_iterations": 0,
        "max_review_iterations": 3,
        "last_verification": None,
        "last_review": None,
        "last_delivered_phase": None,
        "blocked_reason": None,
        "last_blocker_repair": None,
        "approval_policy_path": approval_policy_rel,
        "approval_mode": approval_policy["approval_mode"],
        "last_approval_policy_readback": {
            "read_at": timestamp,
            "path": approval_policy_rel,
            "status": "valid",
            "approval_mode": approval_policy["approval_mode"],
            "approved_operations": approved_operation_names(approval_policy["operations"]),
            "pause_automation_on_completion": approval_policy.get("pause_automation_on_completion", False),
            "pause_automation_on_stall": approval_policy.get("pause_automation_on_stall", False),
            "fallback_reason": None,
        },
        "run_count": 0,
        "stalled_run_count": 0,
        "max_stalled_runs": 3,
        "last_progress_signature": None,
        "last_progress_at": None,
        "last_operator_alert": None,
        "last_automation_pause": None,
        "last_run_quality": None,
        "last_adaptive_action": None,
        "model_history": [],
        "adaptive_escalation_count": 0,
        "adaptive_deescalation_count": 0,
        "adaptive_flawless_streak": 0,
        "auto_advance_after_delivered_review": True,
        "commit_delivered_phase_locally": True,
        "push_to_github": False,
        "all_phases_complete": False,
        "deep_review_prompt": None,
        "updated_at": timestamp,
    }
    _write_text_if_missing(automation_dir / "delivery_state.json", json.dumps(state, indent=2, sort_keys=False) + "\n", created)
    _write_text_if_missing(
        automation_dir / "delivery_log.md",
        f"# {roadmap_slug.replace('-', ' ').title()} Delivery Log\n\nStatus: Draft\nRoadmap: `roadmaps/not_started_{slug_dir}_roadmap.md`\n",
        created,
    )
    review_state = {
        "roadmap": f"roadmaps/not_started_{slug_dir}_roadmap.md",
        "roadmap_slug": roadmap_slug,
        "current_phase": phase,
        "status": "not_started",
        "review_iterations": 0,
        "max_review_iterations": 3,
        "active_review_file": None,
        "last_verdict": None,
        "last_review_file": None,
        "last_delivered_phase": None,
        "blocked_reason": None,
        "updated_at": timestamp,
    }
    _write_text_if_missing(automation_dir / "review_fix_state.json", json.dumps(review_state, indent=2) + "\n", created)
    _write_text_if_missing(automation_dir / "review_fix_log.md", f"# {roadmap_slug.replace('-', ' ').title()} Review/Fix Log\n", created)
    policy = {
        "schema_version": 1,
        "max_stalled_runs": 3,
        "notification": {"mode": "alert_file", "fallback": "alert_file"},
        "defaults": {"model": "gpt-5.5", "reasoning_effort": "xhigh"},
        "phases": {},
        "adaptive_model_policy": {
            "enabled": False,
            "escalate_on": [
                "delivered_with_fixes",
                "verification_failed",
                "review_needs_fix",
                "stalled",
                "retarget_failed",
            ],
            "human_gated_qualities": [
                "blocked_human_required",
                "completion_closeout_failed",
            ],
            "deescalate_after_flawless_runs": 0,
            "caps": {
                "allowed_models": ["gpt-5.5"],
                "max_reasoning_effort": "xhigh",
            },
        },
    }
    _write_text_if_missing(automation_dir / "phase_model_policy.json", json.dumps(policy, indent=2) + "\n", created)
    _write_text_if_missing(automation_dir / "automation_run_log.jsonl", "", created)
    report["created"] = created


def run_scaffold(args: argparse.Namespace) -> int:
    report = build_scaffold_plan(args)
    if report.get("errors"):
        if args.json:
            _print_json(report)
        else:
            _print_key_values(report, ("command", "status", "dry_run", "repo_root", "roadmap_slug", "automation_id"))
        return 1
    if not args.dry_run:
        apply_scaffold_plan(report)
    if args.json:
        _print_json(report)
    else:
        _print_key_values(report, ("command", "status", "dry_run", "repo_root", "roadmap_slug", "automation_id"))
        print("approved_operations:")
        for operation in report["approval_policy"]["approved_operations"]:
            print(f"- {operation}")
        print("would_create:")
        for path in report["would_create"]:
            print(f"- {path}")
    allowed = parse_allowed_warning_codes(args.allow_warning)
    if args.strict and _strict_failed(report, allowed):
        return 1
    return 0


def build_package_plan(args: argparse.Namespace) -> Dict[str, Any]:
    repo_root = _repo_root(args.repo_root)
    adapter = args.adapter
    core_paths = [
        repo_root / "core" / "references",
        repo_root / "core" / "templates",
        repo_root / "core" / "prompts",
    ]
    adapter_dir = repo_root / "adapters" / adapter
    output_dir = repo_root / "skill" / f"{adapter}-roadmap-delivery-skill"
    if adapter == "codex":
        output_dir = repo_root / "skill" / "roadmap-delivery-skill"

    required_paths = [*core_paths, output_dir]
    missing = [str(path) for path in required_paths if not path.exists()]
    warnings = []
    if missing:
        warnings.append(
            {
                "code": "package_sources_missing",
                "message": "Some package dry-run inputs are not present.",
                "paths": missing,
            }
        )
    return {
        "cli_schema_version": CLI_SCHEMA_VERSION,
        "command": "package",
        "status": "warning" if warnings else "ok",
        "dry_run": True,
        "repo_root": str(repo_root),
        "adapter": adapter,
        "dry_run_ready": not missing,
        "renderer_ready": adapter_dir.exists() and not missing,
        "adapter_overlay_present": adapter_dir.exists(),
        "planned_adapter_overlay": str(adapter_dir),
        "would_read": [str(path) for path in [*core_paths, adapter_dir]],
        "would_write": str(output_dir),
        "errors": [],
        "warnings": warnings,
    }


def run_package(args: argparse.Namespace) -> int:
    report = build_package_plan(args)
    if args.json:
        _print_json(report)
    else:
        _print_key_values(report, ("command", "status", "dry_run", "repo_root", "adapter", "renderer_ready", "would_write"))
        print("would_read:")
        for path in report["would_read"]:
            print(f"- {path}")
    allowed = parse_allowed_warning_codes(args.allow_warning)
    if args.strict and _strict_failed(report, allowed):
        return 1
    return 0


def add_common_flags(parser: argparse.ArgumentParser, *, require_repo_root: bool = True) -> None:
    parser.add_argument("--repo-root", required=require_repo_root, help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")


def add_state_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--roadmap-slug", help="Roadmap slug, accepting hyphen or underscore form.")
    parser.add_argument("--automation-id", help="Codex automation id under ~/.codex/automations.")


def add_strict_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--strict", action="store_true", help="Return non-zero when warnings are present.")
    parser.add_argument(
        "--allow-warning",
        action="append",
        default=[],
        metavar="CODE",
        help="Warning code to allow under --strict. May be repeated or comma-separated.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="roadmap-delivery", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    version_parser = subparsers.add_parser("version", help="Print the CLI version.")
    version_parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    version_parser.set_defaults(func=run_version, parser=version_parser)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect delivery state without mutating files.")
    add_common_flags(inspect_parser)
    add_state_flags(inspect_parser)
    add_strict_flags(inspect_parser)
    inspect_parser.set_defaults(func=run_inspect, parser=inspect_parser)

    validate_parser = subparsers.add_parser("validate", help="Validate roadmap delivery artifacts.")
    add_common_flags(validate_parser)
    add_state_flags(validate_parser)
    add_strict_flags(validate_parser)
    validate_parser.set_defaults(func=run_validate, parser=validate_parser)

    scaffold_parser = subparsers.add_parser("scaffold", help="Create or plan automation scaffolding.")
    add_common_flags(scaffold_parser)
    scaffold_parser.add_argument("--roadmap-slug", required=True, help="Roadmap slug for the planned automation.")
    scaffold_parser.add_argument("--automation-id", help="Automation id to include in the plan.")
    scaffold_parser.add_argument(
        "--approval-mode",
        default="conservative",
        choices=APPROVAL_MODES,
        help="Approval mode for the generated approval_policy.json.",
    )
    scaffold_parser.add_argument(
        "--approval-operation",
        action="append",
        default=[],
        metavar="OPERATION=allow|deny",
        help="Custom operation decision for --approval-mode custom. May be repeated.",
    )
    scaffold_parser.add_argument("--dry-run", action="store_true", help="Plan files without writing them.")
    add_strict_flags(scaffold_parser)
    scaffold_parser.set_defaults(func=run_scaffold, parser=scaffold_parser)

    package_parser = subparsers.add_parser("package", help="Plan host package rendering without writing files.")
    add_common_flags(package_parser)
    add_strict_flags(package_parser)
    package_parser.add_argument("--adapter", default="codex", choices=("codex",), help="Host adapter to plan.")
    package_parser.add_argument("--dry-run", action="store_true", help="Accepted for explicit dry-run plans.")
    package_parser.set_defaults(func=run_package, parser=package_parser)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
