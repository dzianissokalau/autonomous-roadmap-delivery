# Release Notes 0.1.0

Version `0.1.0` is the first local framework release candidate for Roadmap
Delivery Skill. It is buildable and verifiable from committed sources, but it
has not been published to an external package registry.

## Highlights

- Canonical workflow rules live under `core/references/`.
- Durable artifact templates and prompt guards live under `core/templates/`
  and `core/prompts/`.
- JSON schemas validate delivery state, phase model policy, review artifacts,
  and automation run logs.
- Shared Python helpers power inspection, validation, progress tracking, and
  CLI commands from `src/roadmap_delivery/`.
- `skill/roadmap-delivery-skill/` is a generated Codex package snapshot backed
  by adapter templates and drift checks.
- `dist/claude/` is a generated Claude plugin package snapshot with the main
  skill, reviewer agent, safety hooks, and canonical references.
- A documentation-only generic markdown pack is built for future adapter
  planning without claiming support for named hosts.
- CI and release-check workflows run local tests, package checks, schema
  checks, privacy scanning, and release reproducibility checks.
- `examples/demo-roadmap/` provides an offline fixture for smoke testing the
  workflow.
- `examples/autonomy-controls/` documents approval modes, adaptive retarget
  traces, and completion or stall self-pause evidence.

## Local Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_adapters.py --check
python3 scripts/build_release.py --check
python3 scripts/check_release_privacy.py --repo-root .
git diff --check
```

## Compatibility

- Existing Codex users can continue installing from
  `skill/roadmap-delivery-skill/`.
- Claude users can stage the generated local plugin package from
  `dist/claude/` or the local release artifact, but live Claude Code loading is
  still a maintainer smoke check when the host binary is available.
- The generic markdown pack is a planning artifact, not a supported runtime
  integration for future named hosts.
- Existing helper script paths remain available as wrappers.
- Legacy state artifacts remain supported where compatibility warnings are
  explicit.
- Existing automations without `approval_policy.json` remain conservative.
  Delegated local and delegated delivery modes require durable policy artifacts
  and readback evidence before saved automation retarget or pause actions.
- External publication, branch promotion, and installed-skill synchronization
  are not part of this release candidate and require operator approval.
