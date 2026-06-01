#!/usr/bin/env python3
"""Compatibility wrapper for roadmap_delivery.alerts."""

from __future__ import annotations

from pathlib import Path
import sys


def _add_repo_src_to_path() -> None:
    script_path = Path(__file__).resolve()
    for parent in script_path.parents:
        src = parent / "src"
        if (src / "roadmap_delivery").is_dir():
            sys.path.insert(0, str(src))
            return


_add_repo_src_to_path()

try:
    from roadmap_delivery.alerts import main
except ModuleNotFoundError as exc:
    if exc.name == "roadmap_delivery":
        print(
            "roadmap_delivery package is not importable. Run this script from "
            "the repository checkout or install the roadmap-delivery package.",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    raise


if __name__ == "__main__":
    raise SystemExit(main())
