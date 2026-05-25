"""Shared roadmap delivery framework helpers."""

from __future__ import annotations

from importlib import metadata as importlib_metadata
from pathlib import Path


__all__ = ["__version__"]


def _read_version() -> str:
    for parent in Path(__file__).resolve().parents:
        version_path = parent / "VERSION"
        if version_path.is_file():
            return version_path.read_text(encoding="utf-8").strip()
    try:
        return importlib_metadata.version("roadmap-delivery")
    except importlib_metadata.PackageNotFoundError:
        pass
    return "0.0.0"


__version__ = _read_version()
