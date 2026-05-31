#!/usr/bin/env python3
"""Claude hook helpers for Roadmap Delivery safety checks."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


PHASE_PROMPT_TERMS = (
    "run the next safe phase-gated delivery step",
    "phase-gated delivery",
    "deliver phase",
    "roadmap delivery",
)

RELEASE_PROMPT_TERMS = (
    "publish",
    "release",
    "promote",
    "promotion",
    "package",
)

COMPLETION_CLAIM_PATTERNS = (
    re.compile(r"\bphase\s+\d+\s+(?:is\s+)?delivered\b", re.IGNORECASE),
    re.compile(r"\bdelivered\s+phase\s+\d+\b", re.IGNORECASE),
)

BROAD_STAGING_PATTERNS = (
    re.compile(r"(?<![\w-])git\s+add\s+(?:\.|-A|--all|--\s+\.|:/|\*)(?:\s|$|&&|;)", re.IGNORECASE),
    re.compile(r"(?<![\w-])git\s+commit\s+(?:-[^\s]*a[^\s]*|--all)(?:\s|$)", re.IGNORECASE),
)

PROTECTED_COMMAND_PATTERNS = (
    (
        re.compile(r"(?<![\w-])git\s+reset\s+--hard\b", re.IGNORECASE),
        "destructive git reset",
    ),
    (
        re.compile(r"(?<![\w-])git\s+clean\s+-[^\n;|&]*[dfx]", re.IGNORECASE),
        "destructive git clean",
    ),
    (
        re.compile(r"(?<![\w-])git\s+checkout\s+--\s+\S+", re.IGNORECASE),
        "destructive git checkout",
    ),
    (
        re.compile(r"(?<![\w-])git\s+restore\b", re.IGNORECASE),
        "destructive git restore",
    ),
    (
        re.compile(r"(?<![\w-])git\s+branch\s+-D\b", re.IGNORECASE),
        "branch deletion",
    ),
    (
        re.compile(r"(?<![\w-])git\s+push\b", re.IGNORECASE),
        "publication or remote mutation",
    ),
    (
        re.compile(r"(?<![\w-])git\s+(?:merge|rebase)\b", re.IGNORECASE),
        "branch promotion or history rewrite",
    ),
    (
        re.compile(r"(?<![\w-])gh\s+release\s+create\b", re.IGNORECASE),
        "release publication",
    ),
    (
        re.compile(r"(?<![\w-])(?:npm|pnpm|yarn)\s+publish\b", re.IGNORECASE),
        "package publication",
    ),
    (
        re.compile(r"(?<![\w-])twine\s+upload\b", re.IGNORECASE),
        "package publication",
    ),
)


def main(argv: List[str]) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    payload = read_hook_input()
    if mode == "guard-bash":
        return guard_bash(payload)
    if mode == "remind-prompt":
        return remind_prompt(payload)
    if mode == "guard-stop":
        return guard_stop(payload)
    return 0


def read_hook_input() -> Dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def emit_json(value: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(value, sort_keys=True))
    sys.stdout.write("\n")


def guard_bash(payload: Dict[str, Any]) -> int:
    if payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str) or not command.strip():
        return 0

    for pattern in BROAD_STAGING_PATTERNS:
        if pattern.search(command):
            return ask_pretool(
                "Roadmap Delivery guard: broad git staging can hide unrelated work. "
                "Stage explicit phase-owned paths, or confirm this broad staging command was approved."
            )

    for pattern, label in PROTECTED_COMMAND_PATTERNS:
        if pattern.search(command):
            return ask_pretool(
                "Roadmap Delivery guard: this command looks like "
                f"{label}. Protected operations require explicit human approval and, "
                "for release or publication paths, a completed privacy/release check."
            )

    return 0


def ask_pretool(reason: str) -> int:
    emit_json(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": reason,
            }
        }
    )
    return 0


def remind_prompt(payload: Dict[str, Any]) -> int:
    prompt = str(payload.get("prompt") or "")
    prompt_lower = prompt.lower()
    cwd = Path(str(payload.get("cwd") or ".")).expanduser()
    states = list(read_delivery_states(cwd))
    contexts: List[str] = []

    for state in states:
        if not prompt_targets_state(prompt_lower, state, states):
            continue
        status = str(state.get("status") or "")
        slug = str(state.get("roadmap_slug") or "roadmap")
        if state.get("all_phases_complete") is True or status in {"completed", "completed_pending_pause"}:
            emit_json(
                {
                    "decision": "block",
                    "reason": (
                        f"Roadmap Delivery hard stop: {slug} is {status or 'complete'} "
                        "or all phases are complete. Do not start phase work; confirm/pause automation instead."
                    ),
                    "hookSpecificOutput": {"hookEventName": "UserPromptSubmit"},
                }
            )
            return 0
        if status == "blocked":
            blocked_reason = state.get("blocked_reason") or "not recorded"
            contexts.append(
                "Blocked Remediation Mode applies before phase delivery for "
                f"{slug}. Classify the blocker as local-repairable, automation-config, "
                "permission-gated, external-decision, or destructive-risk before advancing. "
                f"blocked_reason: {blocked_reason}"
            )

    if any(term in prompt_lower for term in RELEASE_PROMPT_TERMS):
        contexts.append(
            "Roadmap Delivery privacy reminder: publication, promotion, package release, "
            "or credential use requires explicit human approval and the release/privacy checks."
        )

    if contexts:
        emit_json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "\n\n".join(contexts),
                }
            }
        )
    return 0


def guard_stop(payload: Dict[str, Any]) -> int:
    if payload.get("stop_hook_active") is True:
        return 0
    message = str(payload.get("last_assistant_message") or "")
    if not any(pattern.search(message) for pattern in COMPLETION_CLAIM_PATTERNS):
        return 0
    lower = message.lower()
    has_review = "review" in lower and "delivered" in lower
    has_verification = "verification" in lower or "tests" in lower or "passed" in lower
    if has_review and has_verification:
        return 0
    emit_json(
        {
            "decision": "block",
            "reason": (
                "Roadmap Delivery completion guard: before stopping after a delivered-phase "
                "claim, include verification evidence and the delivered review verdict, or keep working."
            ),
        }
    )
    return 0


def read_delivery_states(cwd: Path) -> Iterable[Dict[str, Any]]:
    root = cwd.resolve() if cwd.exists() else Path.cwd()
    automation_root = root / "automation"
    if not automation_root.is_dir():
        return []
    states: List[Dict[str, Any]] = []
    for path in sorted(automation_root.glob("*/delivery_state.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data["_state_path"] = path.as_posix()
            states.append(data)
    return states


def prompt_targets_state(prompt_lower: str, state: Dict[str, Any], states: List[Dict[str, Any]]) -> bool:
    roadmap = str(state.get("roadmap") or "").lower()
    slug = str(state.get("roadmap_slug") or "").lower()
    if roadmap and roadmap in prompt_lower:
        return True
    if slug and slug in prompt_lower:
        return True
    return len(states) == 1 and any(term in prompt_lower for term in PHASE_PROMPT_TERMS)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
