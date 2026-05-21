#!/usr/bin/env python3
"""Compute and optionally record durable roadmap delivery progress."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_MAX_STALLED_RUNS = 3
RUN_LOG_FILENAME = "automation_run_log.jsonl"
SIGNATURE_VERSION = 1


class ProgressSignatureError(RuntimeError):
    """Raised when progress cannot be computed or recorded safely."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug_forms(slug: Optional[str]) -> Dict[str, Optional[str]]:
    if not slug:
        return {"input": None, "dash": None, "dir": None}
    return {
        "input": slug,
        "dash": slug.replace("_", "-"),
        "dir": slug.replace("-", "_"),
    }


def unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    out: List[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            out.append(path)
            seen.add(key)
    return out


def state_candidates(repo_root: Path, roadmap_slug: str) -> List[Path]:
    forms = slug_forms(roadmap_slug)
    candidates: List[Path] = []
    for slug in [item for item in (forms["dir"], forms["dash"]) if item]:
        candidates.append(repo_root / "roadmaps" / "automation" / slug / "delivery_state.json")
        candidates.append(repo_root / "automation" / slug / "delivery_state.json")
    return unique_paths(candidates)


def find_state_file(repo_root: Path, roadmap_slug: str) -> Path:
    candidates = state_candidates(repo_root, roadmap_slug)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    checked = ", ".join(str(path) for path in candidates) or "<none>"
    raise ProgressSignatureError(f"State file does not exist. Checked: {checked}")


def load_json_object(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ProgressSignatureError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise ProgressSignatureError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProgressSignatureError(f"JSON root is not an object: {path}")
    return value


def write_json_object(path: Path, value: Dict[str, Any]) -> None:
    try:
        path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ProgressSignatureError(f"Cannot write {path}: {exc}") from exc


def relative_or_absolute(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def non_negative_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int) and value >= 0:
        return value
    return default


def positive_int(value: Any, default: int = DEFAULT_MAX_STALLED_RUNS) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int) and value > 0:
        return value
    return default


def git_head(repo_root: Path) -> Optional[str]:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def file_fingerprint(repo_root: Path, path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "path": relative_or_absolute(repo_root, path),
            "exists": False,
            "size": None,
            "sha256": None,
        }
    digest = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        stat = path.stat()
    except OSError as exc:
        raise ProgressSignatureError(f"Cannot fingerprint {path}: {exc}") from exc
    return {
        "path": relative_or_absolute(repo_root, path),
        "exists": True,
        "size": stat.st_size,
        "sha256": digest.hexdigest(),
    }


def progress_signature_input(repo_root: Path, state_file: Path, state: Dict[str, Any]) -> Dict[str, Any]:
    delivery_log = state_file.parent / "delivery_log.md"
    return {
        "signature_version": SIGNATURE_VERSION,
        "current_phase": state.get("current_phase"),
        "status": state.get("status"),
        "last_delivered_phase": state.get("last_delivered_phase"),
        "review_iterations": state.get("review_iterations"),
        "last_verification": state.get("last_verification"),
        "last_review": state.get("last_review"),
        "git_head": git_head(repo_root),
        "delivery_log": file_fingerprint(repo_root, delivery_log),
        "blocked_reason": state.get("blocked_reason"),
    }


def compute_progress_signature(repo_root: Path, state_file: Path, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    state = state if state is not None else load_json_object(state_file)
    signature_input = progress_signature_input(repo_root, state_file, state)
    digest = hashlib.sha256(canonical_json(signature_input).encode("utf-8")).hexdigest()
    return {
        "progress_signature": f"sha256:{digest}",
        "signature_input": signature_input,
    }


def policy_max_stalled_runs(policy_path: Path) -> Tuple[int, str]:
    if not policy_path.exists():
        return DEFAULT_MAX_STALLED_RUNS, "default"
    try:
        policy = load_json_object(policy_path)
    except ProgressSignatureError:
        return DEFAULT_MAX_STALLED_RUNS, "default"
    value = policy.get("max_stalled_runs")
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value, "phase_model_policy"
    return DEFAULT_MAX_STALLED_RUNS, "default"


def parse_run_log(run_log_path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    entries: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    if not run_log_path.exists():
        return entries, errors
    try:
        lines = run_log_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return entries, [{"line": None, "message": f"Cannot read run log: {exc}", "path": str(run_log_path)}]
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append({"line": number, "message": f"Invalid JSONL entry: {exc}", "path": str(run_log_path)})
            continue
        if not isinstance(value, dict):
            errors.append({"line": number, "message": "Run log entry is not a JSON object.", "path": str(run_log_path)})
            continue
        entries.append(value)
    return entries, errors


def build_run_result(
    repo_root: Path,
    state_file: Path,
    state: Optional[Dict[str, Any]] = None,
    *,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    state = state if state is not None else load_json_object(state_file)
    timestamp = timestamp or utc_now()
    signature = compute_progress_signature(repo_root, state_file, state)
    previous_signature = state.get("last_progress_signature")
    progress_detected = not previous_signature or previous_signature != signature["progress_signature"]
    previous_run_count = non_negative_int(state.get("run_count"))
    previous_stalled_run_count = non_negative_int(state.get("stalled_run_count"))
    max_stalled_runs, max_stalled_runs_source = policy_max_stalled_runs(state_file.parent / "phase_model_policy.json")
    run_count = previous_run_count + 1
    stalled_run_count = 0 if progress_detected else previous_stalled_run_count + 1
    threshold_reached = stalled_run_count >= max_stalled_runs
    run_log_path = state_file.parent / RUN_LOG_FILENAME
    run_log_entries, run_log_errors = parse_run_log(run_log_path)
    result = {
        "timestamp": timestamp,
        "state_file": str(state_file),
        "run_log_path": str(run_log_path),
        "previous_progress_signature": previous_signature,
        "progress_signature": signature["progress_signature"],
        "progress_detected": progress_detected,
        "previous_run_count": previous_run_count,
        "run_count": run_count,
        "previous_stalled_run_count": previous_stalled_run_count,
        "stalled_run_count": stalled_run_count,
        "max_stalled_runs": max_stalled_runs,
        "max_stalled_runs_source": max_stalled_runs_source,
        "threshold_reached": threshold_reached,
        "phase_6_alert_required": threshold_reached,
        "status_before": state.get("status"),
        "status_after": "blocked" if threshold_reached else state.get("status"),
        "blocked_reason_after": (
            f"Stalled after {stalled_run_count} consecutive runs without durable progress "
            f"(threshold {max_stalled_runs})."
            if threshold_reached
            else state.get("blocked_reason")
        ),
        "run_log_entries": len(run_log_entries),
        "run_log_errors": run_log_errors,
        "signature_input": signature["signature_input"],
    }
    return result


def append_run_log(run_log_path: Path, entry: Dict[str, Any]) -> None:
    try:
        with run_log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n")
    except OSError as exc:
        raise ProgressSignatureError(f"Cannot append run log {run_log_path}: {exc}") from exc


def record_run_result(repo_root: Path, state_file: Path, *, timestamp: Optional[str] = None) -> Dict[str, Any]:
    state = load_json_object(state_file)
    result = build_run_result(repo_root, state_file, state, timestamp=timestamp)
    if result["run_log_errors"]:
        first = result["run_log_errors"][0]
        raise ProgressSignatureError(f"Run log is corrupt at line {first.get('line')}: {first.get('message')}")

    state["run_count"] = result["run_count"]
    state["stalled_run_count"] = result["stalled_run_count"]
    state["max_stalled_runs"] = result["max_stalled_runs"]
    state["last_progress_signature"] = result["progress_signature"]
    if result["progress_detected"]:
        state["last_progress_at"] = result["timestamp"]
    if result["threshold_reached"]:
        state["status"] = "blocked"
        state["blocked_reason"] = result["blocked_reason_after"]
    state["updated_at"] = result["timestamp"]
    write_json_object(state_file, state)

    log_entry = {
        "timestamp": result["timestamp"],
        "current_phase": state.get("current_phase"),
        "status": state.get("status"),
        "last_delivered_phase": state.get("last_delivered_phase"),
        "progress_signature": result["progress_signature"],
        "previous_progress_signature": result["previous_progress_signature"],
        "progress_detected": result["progress_detected"],
        "run_count": result["run_count"],
        "stalled_run_count": result["stalled_run_count"],
        "max_stalled_runs": result["max_stalled_runs"],
        "threshold_reached": result["threshold_reached"],
        "phase_6_alert_required": result["phase_6_alert_required"],
    }
    append_run_log(Path(result["run_log_path"]), log_entry)
    result["recorded"] = True
    return result


def print_text(result: Dict[str, Any]) -> None:
    for key in (
        "state_file",
        "progress_signature",
        "previous_progress_signature",
        "progress_detected",
        "run_count",
        "stalled_run_count",
        "max_stalled_runs",
        "threshold_reached",
        "phase_6_alert_required",
        "run_log_path",
    ):
        print(f"{key}: {result.get(key)}")
    if result.get("run_log_errors"):
        print("run_log_errors:")
        for item in result["run_log_errors"]:
            print(f"- line {item.get('line')}: {item.get('message')}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compute and optionally record durable roadmap progress.")
    parser.add_argument("--repo-root", required=True, help="Repository root.")
    parser.add_argument("--roadmap-slug", help="Roadmap slug, accepting hyphen or underscore form.")
    parser.add_argument("--state-file", help="Explicit delivery_state.json path.")
    parser.add_argument("--record-run", action="store_true", help="Update delivery_state.json and append automation_run_log.jsonl.")
    parser.add_argument("--timestamp", help="Timestamp to write when recording, mainly for deterministic tests.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve()
    if args.state_file:
        state_file = Path(args.state_file).expanduser()
        if not state_file.is_absolute():
            state_file = repo_root / state_file
    elif args.roadmap_slug:
        state_file = find_state_file(repo_root, args.roadmap_slug)
    else:
        parser.error("one of --roadmap-slug or --state-file is required")

    try:
        if args.record_run:
            result = record_run_result(repo_root, state_file, timestamp=args.timestamp)
        else:
            result = build_run_result(repo_root, state_file, timestamp=args.timestamp)
            result["recorded"] = False
    except ProgressSignatureError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
