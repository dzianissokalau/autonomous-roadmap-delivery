"""Codex adapter package metadata."""

from __future__ import annotations

from pathlib import Path

from roadmap_delivery.rendering import AdapterMetadata, read_manifest_metadata


ADAPTER = "codex"
MANIFEST = Path("adapters/codex/package_manifest.json")
CAPABILITY_FILE = "host-capabilities/codex.yaml"


def adapter_metadata(repo_root: Path) -> AdapterMetadata:
    return read_manifest_metadata(
        repo_root,
        MANIFEST,
        adapter=ADAPTER,
        capability_file=CAPABILITY_FILE,
        output_committed=True,
    )
