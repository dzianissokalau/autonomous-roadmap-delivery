"""Source-tree import shim for ``python -m roadmap_delivery.cli``.

The installable package is defined under ``src/roadmap_delivery``. This small
shim lets repository-local verification run the module form before the package
has been installed.
"""

from __future__ import annotations

from importlib import metadata as importlib_metadata
from pathlib import Path


_SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "roadmap_delivery"
if _SRC_PACKAGE.is_dir():
    __path__.append(str(_SRC_PACKAGE))  # type: ignore[name-defined]


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
