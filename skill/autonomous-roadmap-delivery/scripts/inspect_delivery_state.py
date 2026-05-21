#!/usr/bin/env python3
"""Inspect phase-gated roadmap delivery state without mutating files."""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Optional


AUTOMATIONS_DIR = Path.home() / ".codex" / "automations"
DEEP_REVIEW_CANDIDATES = (
    "deep_review_prompt.md",
    "deep_review_prompt.txt",
    "review_fixes_prompt.md",
    "deep_review.md",
)


def add_warning(warnings: List[Dict[str, str]], code: str, message: str) -> None:
    warnings.append({"code": code, "message": message})


def slug_forms(slug: Optional[str]) -> Dict[str, Optional[str]]:
    if not slug:
        return {"input": None, "dash": None, "dir": None}
    return {
        "input": slug,
        "dash": slug.replace("_", "-"),
        "dir": slug.replace("-", "_"),
    }


def resolve_repo_path(repo_root: Path, path_value: Optional[str]) -> Optional[Path]:
    if not path_value:
        return None
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return repo_root / path


def run_git(repo_root: Path, args: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git"] + args,
        cwd=str(repo_root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


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


def load_json(path: Path, warnings: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    if not path.exists():
        add_warning(warnings, "missing_state_file", f"State file does not exist: {path}")
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = json.load(fh)
    except json.JSONDecodeError as exc:
        add_warning(warnings, "invalid_state_json", f"State file is invalid JSON: {path}: {exc}")
        return None
    except OSError as exc:
        raise RuntimeError(f"Cannot read state file {path}: {exc}") from exc
    if not isinstance(value, dict):
        add_warning(warnings, "invalid_state_shape", f"State file root is not an object: {path}")
        return None
    return value


def unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    out: List[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            out.append(path)
            seen.add(key)
    return out


def state_candidates(repo_root: Path, forms: Dict[str, Optional[str]]) -> List[Path]:
    candidates: List[Path] = []
    for slug in unique([item for item in (forms["dir"], forms["dash"]) if item]):
        candidates.append(repo_root / "roadmaps" / "automation" / slug / "delivery_state.json")
        candidates.append(repo_root / "automation" / slug / "delivery_state.json")
    return unique_paths(candidates)


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


def automation_dir_candidates(repo_root: Path, forms: Dict[str, Optional[str]]) -> List[Path]:
    candidates: List[Path] = []
    for slug in unique([item for item in (forms["dir"], forms["dash"]) if item]):
        candidates.append(repo_root / "roadmaps" / "automation" / slug)
        candidates.append(repo_root / "automation" / slug)
    return unique_paths(candidates)


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


def extract_roadmap_references(prompt: str, repo_root: Path) -> List[str]:
    refs: List[str] = []
    patterns = (
        r"/Users/[^`'\"\s]+?\.md",
        r"roadmaps/[^`'\"\s]+?\.md",
    )
    for pattern in patterns:
        for match in re.findall(pattern, prompt):
            path = Path(match)
            if not (path.name == "roadmap.md" or path.name.endswith("_roadmap.md")):
                continue
            if not path.is_absolute():
                path = repo_root / path
            normalized = str(path)
            if normalized not in refs:
                refs.append(normalized)
    return refs


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


def unique(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


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
    if automation_id:
        automation_toml = AUTOMATIONS_DIR / automation_id / "automation.toml"
        if not automation_toml.exists():
            raise RuntimeError(f"Automation config does not exist: {automation_toml}")
        automation_data = parse_minimal_toml(automation_toml)
        automation_status = automation_data.get("status")
        automation_prompt = str(automation_data.get("prompt") or "")
        automation_roadmap_references = extract_roadmap_references(automation_prompt, repo_root)
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
    last_delivered_phase = state.get("last_delivered_phase") if state else None
    blocked_reason = state.get("blocked_reason") if state else None
    all_phases_complete = str(current_phase).lower() in {"complete", "completed", "all_phases_complete"} if current_phase is not None else False
    if str(state_status).lower() in {"complete", "completed", "all_phases_complete"}:
        all_phases_complete = True
    if all_phases_complete and str(automation_status).upper() == "ACTIVE":
        add_warning(
            warnings,
            "completed_state_active_automation",
            "State appears complete but the automation is ACTIVE.",
        )

    deep_review_prompt_exists = False
    deep_review_dirs: List[Path] = []
    if state_file is not None:
        deep_review_dirs.append(state_file.parent)
    deep_review_dirs.extend(path for path in automation_dir_candidates(repo_root, forms) if path not in deep_review_dirs)
    deep_review_prompt_exists = any(
        (automation_dir / name).exists()
        for automation_dir in deep_review_dirs
        for name in DEEP_REVIEW_CANDIDATES
    )

    return {
        "automation_id": automation_id,
        "automation_status": automation_status,
        "automation_toml": str(automation_toml) if automation_toml else None,
        "automation_roadmap_references": automation_roadmap_references,
        "roadmap_path": str(roadmap_path) if roadmap_path else None,
        "state_file": str(state_file) if state_file else None,
        "state_status": state_status,
        "current_phase": current_phase,
        "last_delivered_phase": last_delivered_phase,
        "blocked_reason": blocked_reason,
        "all_phases_complete": all_phases_complete,
        "current_branch": current_branch,
        "matching_branches": matching_branches,
        "worktree_dirty": worktree_dirty,
        "deep_review_prompt_exists": deep_review_prompt_exists,
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
            "state_status",
            "current_phase",
            "last_delivered_phase",
            "blocked_reason",
            "all_phases_complete",
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
