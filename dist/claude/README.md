# Roadmap Delivery Claude Adapter

This is a generated Claude Code plugin package for Roadmap Delivery Skill.

It includes the main roadmap delivery skill, canonical workflow references,
a read-only reviewer agent pattern for phase-gated review, and conservative
Claude hook guards for roadmap delivery safety reminders. It also includes
provider-neutral model-role guidance that records when a host cannot prove or
set a reasoning-effort value.

Approval policy, adaptive model policy, and completion/stall self-pause rules
come from the same core workflow sources used by the Codex package. Claude
adapters must preserve conservative fallbacks: unsupported recurring
automation, model/reasoning readback, or status-only pause surfaces fall back to
repository validation, local alerts, and explicit operator action rather than
claiming host support.

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
