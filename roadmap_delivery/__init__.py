"""Source-tree import shim for ``python -m roadmap_delivery.cli``.

The installable package is defined under ``src/roadmap_delivery``. This small
shim lets repository-local verification run the module form before the package
has been installed.
"""

from __future__ import annotations

from pathlib import Path


_SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "roadmap_delivery"
if _SRC_PACKAGE.is_dir():
    __path__.append(str(_SRC_PACKAGE))  # type: ignore[name-defined]

__version__ = "0.0.0"
