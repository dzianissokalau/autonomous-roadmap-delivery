"""Generic documentation-only adapter package metadata."""

from __future__ import annotations

from pathlib import Path

from roadmap_delivery.rendering import AdapterMetadata, FileSpec


ADAPTER = "generic"
CAPABILITY_FILE = "host-capabilities/generic.yaml"
TEMPLATE_DIR = "adapters/generic/templates"

CORE_REFERENCES = (
    "finalization-and-promotion.md",
    "model-policy-and-stall-control.md",
    "phase-loop.md",
    "review-and-fix.md",
    "setup-automation.md",
    "state-log-and-branches.md",
    "troubleshooting.md",
)

SCHEMA_FILES = (
    "automation_run_log.schema.json",
    "delivery_state.schema.json",
    "phase_model_policy.schema.json",
    "provider_config.schema.json",
    "review_artifact.schema.json",
)


def adapter_metadata(repo_root: Path) -> AdapterMetadata:
    workflow_files = [
        FileSpec(
            output=f"workflow/{name}",
            source=f"core/references/{name}",
            core_source=f"core/references/{name}",
        )
        for name in CORE_REFERENCES
    ]
    schema_files = [
        FileSpec(output=f"schemas/{name}", source=f"schemas/{name}")
        for name in SCHEMA_FILES
    ]
    return AdapterMetadata(
        adapter=ADAPTER,
        output_dir="dist/generic",
        template_dir=TEMPLATE_DIR,
        capability_file=CAPABILITY_FILE,
        output_committed=False,
        files=[
            FileSpec(output="README.md", template="README.md"),
            FileSpec(output="cli/install.md", template="cli/install.md"),
            FileSpec(output="checklists/future-adapter.md", template="future-adapter.md"),
            FileSpec(output="capabilities/generic.yaml", source=CAPABILITY_FILE),
            *workflow_files,
            *schema_files,
        ],
    )
