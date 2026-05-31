# Roadmap Delivery Claude Adapter

This is a generated Claude Code plugin skeleton for Roadmap Delivery Skill.

## Draft Local Test

1. Regenerate the package from the repository root:
   `python3 scripts/build_adapters.py --adapter claude --write`
2. Load the generated plugin in Claude Code:
   `claude --plugin-dir ./dist/claude`
3. Invoke the skill as
   `/roadmap-delivery:roadmap-delivery-skill <roadmap path or automation id>`.

This skeleton does not claim runtime support yet. Later roadmap phases add
reviewer agents, hooks, provider-neutral model-role mapping, smoke tests, and
release artifacts.
