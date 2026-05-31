"""Claude adapter package metadata."""

from __future__ import annotations

from pathlib import Path

from roadmap_delivery.rendering import AdapterMetadata, FileSpec


ADAPTER = "claude"
CAPABILITY_FILE = "host-capabilities/claude.yaml"

README = """# Roadmap Delivery Claude Adapter

This is a minimal generated package used by the adapter build system.

It is not an installable Claude plugin yet. Later roadmap phases add the
Claude manifest, skill layout, hooks, and runtime smoke tests. The Phase 1
renderer proves that Claude output can be generated deterministically from the
same repository core and host capability contract as the Codex adapter.
"""


def adapter_metadata(repo_root: Path) -> AdapterMetadata:
    return AdapterMetadata(
        adapter=ADAPTER,
        output_dir="dist/claude",
        capability_file=CAPABILITY_FILE,
        output_committed=False,
        files=[
            FileSpec(output="README.md", literal=README),
            FileSpec(
                output="core/references/phase-loop.md",
                source="core/references/phase-loop.md",
                core_source="core/references/phase-loop.md",
            ),
            FileSpec(
                output="host-capabilities/claude.yaml",
                source=CAPABILITY_FILE,
            ),
        ],
    )
