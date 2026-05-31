"""Claude adapter package metadata."""

from __future__ import annotations

from pathlib import Path

from roadmap_delivery.rendering import AdapterMetadata, FileSpec


ADAPTER = "claude"
CAPABILITY_FILE = "host-capabilities/claude.yaml"
TEMPLATE_DIR = "adapters/claude"

SKILL_ROOT = "skills/roadmap-delivery-skill"
CORE_REFERENCES = (
    "finalization-and-promotion.md",
    "model-policy-and-stall-control.md",
    "phase-loop.md",
    "review-and-fix.md",
    "setup-automation.md",
    "state-log-and-branches.md",
    "troubleshooting.md",
)

README = """# Roadmap Delivery Claude Adapter

This is a generated Claude Code plugin package for Roadmap Delivery Skill.

It includes the main roadmap delivery skill, canonical workflow references,
and a read-only reviewer agent pattern for phase-gated review.

## Draft Local Test

1. Regenerate the package from the repository root:
   `python3 scripts/build_adapters.py --adapter claude --write`
2. Load the generated plugin in Claude Code:
   `claude --plugin-dir ./dist/claude`
3. Invoke the skill as
   `/roadmap-delivery:roadmap-delivery-skill <roadmap path or automation id>`.

This package does not claim live runtime support yet. Later roadmap phases add
hooks, provider-neutral model-role mapping, smoke tests, and release artifacts.
"""


def adapter_metadata(repo_root: Path) -> AdapterMetadata:
    reference_files = [
        FileSpec(
            output=f"{SKILL_ROOT}/references/{name}",
            source=f"core/references/{name}",
            core_source=f"core/references/{name}",
        )
        for name in CORE_REFERENCES
    ]
    return AdapterMetadata(
        adapter=ADAPTER,
        output_dir="dist/claude",
        template_dir=TEMPLATE_DIR,
        capability_file=CAPABILITY_FILE,
        output_committed=True,
        files=[
            FileSpec(output=".claude-plugin/plugin.json", template="plugin.json.template"),
            FileSpec(output="README.md", literal=README),
            FileSpec(
                output=f"{SKILL_ROOT}/SKILL.md",
                template="templates/skills/roadmap-delivery-skill/SKILL.md",
            ),
            FileSpec(output="agents/reviewer.md", template="templates/agents/reviewer.md"),
            *reference_files,
        ],
    )
