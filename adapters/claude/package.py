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
a read-only reviewer agent pattern for phase-gated review, and conservative
Claude hook guards for roadmap delivery safety reminders. It also includes
provider-neutral model-role guidance that records when a host cannot prove or
set a reasoning-effort value.

## Local Checks

1. Regenerate the package from the repository root:
   `python3 scripts/build_adapters.py --adapter claude --write`
2. Check committed output:
   `python3 scripts/build_adapters.py --adapter claude --check`
3. Build local release artifacts:
   `python3 scripts/build_release.py --check`

The package is verified by offline structure checks and local demo-roadmap
runtime validation. Live Claude Code loading remains an optional maintainer
smoke check when the `claude` binary is available; publication or installed
plugin synchronization still requires explicit human approval.
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
            FileSpec(output="hooks/hooks.json", template="templates/hooks/hooks.json"),
            FileSpec(
                output="hooks/roadmap_delivery_safety.py",
                template="templates/hooks/roadmap_delivery_safety.py",
                mode=0o755,
            ),
            *reference_files,
        ],
    )
