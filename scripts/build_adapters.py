#!/usr/bin/env python3
"""Render or check host adapter packages."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Dict, List, Optional, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from roadmap_delivery.rendering import (  # noqa: E402
    AdapterMetadata,
    AdapterRenderError,
    RenderedPackage,
    aggregate_status,
    build_adapter_report,
    compare_output,
    render_package,
    write_output,
)


DEFAULT_ADAPTERS = ("codex", "claude")
AVAILABLE_ADAPTERS = (*DEFAULT_ADAPTERS, "generic")


def load_adapter_metadata(repo_root: Path, adapter: str) -> AdapterMetadata:
    package_path = repo_root / "adapters" / adapter / "package.py"
    if not package_path.is_file():
        raise AdapterRenderError(f"Adapter package metadata is missing: {package_path}")
    spec = importlib.util.spec_from_file_location(f"roadmap_delivery_adapter_{adapter}", package_path)
    if spec is None or spec.loader is None:
        raise AdapterRenderError(f"Cannot load adapter package metadata: {package_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    metadata_factory = getattr(module, "adapter_metadata", None)
    if not callable(metadata_factory):
        raise AdapterRenderError(f"Adapter metadata module must define adapter_metadata(repo_root): {package_path}")
    metadata = metadata_factory(repo_root)
    if not isinstance(metadata, AdapterMetadata):
        raise AdapterRenderError(f"adapter_metadata(repo_root) did not return AdapterMetadata: {package_path}")
    if metadata.adapter != adapter:
        raise AdapterRenderError(f"Adapter metadata returned {metadata.adapter!r}, expected {adapter!r}")
    return metadata


def adapter_output_dir(repo_root: Path, adapter: str, metadata: AdapterMetadata, output_root: Optional[Path]) -> Path:
    if output_root is not None:
        return output_root / adapter
    return repo_root / metadata.output_dir


def run_adapter(
    *,
    repo_root: Path,
    adapter: str,
    check: bool,
    write: bool,
    output_root: Optional[Path],
) -> Dict[str, Any]:
    errors: List[str] = []
    diffs: List[Dict[str, str]] = []
    wrote = False
    checked_output = False

    try:
        metadata = load_adapter_metadata(repo_root, adapter)
        output_dir = adapter_output_dir(repo_root, adapter, metadata, output_root)
        package = render_package(repo_root, metadata, output_dir=output_dir)
        if write:
            write_output(package.output_dir, package.files)
            wrote = True
        checked_output = bool(check and (metadata.output_committed or output_root is not None or package.output_dir.exists()))
        if checked_output:
            diffs = compare_output(package.output_dir, package.files)
    except AdapterRenderError as exc:
        errors.append(str(exc))
        metadata = AdapterMetadata(adapter=adapter, output_dir="", files=[])
        package = RenderedPackage(metadata=metadata, output_dir=Path(""), files=[])
    except OSError as exc:
        errors.append(str(exc))
        metadata = AdapterMetadata(adapter=adapter, output_dir="", files=[])
        package = RenderedPackage(metadata=metadata, output_dir=Path(""), files=[])

    return build_adapter_report(
        package,
        diffs=diffs,
        errors=errors,
        wrote=wrote,
        checked_output=checked_output,
    )


def build_report(
    *,
    repo_root: Path,
    adapters: Sequence[str],
    check: bool,
    write: bool,
    output_root: Optional[Path],
) -> Dict[str, Any]:
    reports = [
        run_adapter(
            repo_root=repo_root,
            adapter=adapter,
            check=check,
            write=write,
            output_root=output_root,
        )
        for adapter in adapters
    ]
    return {
        "schema_version": 1,
        "status": aggregate_status(reports),
        "repo_root": str(repo_root),
        "adapters": list(adapters),
        "check": check,
        "write": write,
        "output_root": str(output_root) if output_root is not None else None,
        "reports": reports,
    }


def print_text(report: Dict[str, Any]) -> None:
    print(f"status: {report['status']}")
    print(f"repo_root: {report['repo_root']}")
    for adapter_report in report["reports"]:
        print(f"adapter: {adapter_report['adapter']}")
        print(f"  status: {adapter_report['status']}")
        print(f"  output_dir: {adapter_report['output_dir']}")
        print(f"  check_mode: {adapter_report['check_mode']}")
        print(f"  files: {adapter_report['file_count']}")
        print(f"  diffs: {len(adapter_report['diffs'])}")
        for diff in adapter_report["diffs"]:
            print(f"  - {diff['kind']}: {diff['path']}: {diff['message']}")
        print(f"  errors: {len(adapter_report['errors'])}")
        for error in adapter_report["errors"]:
            print(f"  - {error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument(
        "--adapter",
        action="append",
        choices=AVAILABLE_ADAPTERS,
        help="Adapter to render. May be repeated. Defaults to supported runtime adapters.",
    )
    parser.add_argument("--check", action="store_true", help="Check generated output when the adapter has committed output.")
    parser.add_argument("--write", action="store_true", help="Write rendered output to each adapter output directory.")
    parser.add_argument(
        "--output-root",
        help="Override adapter output directories with <output-root>/<adapter>; useful for snapshot checks.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.check and args.write:
        parser.error("--check and --write cannot be used together")

    repo_root = Path(args.repo_root).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve() if args.output_root else None
    adapters = args.adapter or list(DEFAULT_ADAPTERS)
    report = build_report(
        repo_root=repo_root,
        adapters=adapters,
        check=args.check,
        write=args.write,
        output_root=output_root,
    )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)

    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
