"""State file loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class JsonObjectError(RuntimeError):
    """Raised when a JSON file cannot be read as an object."""


def load_json_object(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            value = json.load(fh)
    except json.JSONDecodeError as exc:
        raise JsonObjectError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise JsonObjectError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise JsonObjectError(f"JSON root is not an object: {path}")
    return value


def write_json_object(path: Path, value: Dict[str, Any]) -> None:
    try:
        path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    except OSError as exc:
        raise JsonObjectError(f"Cannot write {path}: {exc}") from exc
