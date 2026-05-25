"""Small TOML reader used when stdlib tomllib is unavailable."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict


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
