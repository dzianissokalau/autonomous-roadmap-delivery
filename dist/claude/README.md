# Roadmap Delivery Claude Adapter

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
