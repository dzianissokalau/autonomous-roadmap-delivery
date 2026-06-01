# Changelog

All notable local framework release changes are recorded here.

## 0.1.0 - 2026-05-25

Initial framework-core release candidate.

### Added

- Canonical workflow references, prompt fragments, and artifact templates.
- Versioned schemas for delivery state, model policy, review artifacts, and
  automation run logs.
- Shared `roadmap_delivery` Python helpers and a stable CLI.
- Generated Codex skill package checks backed by adapter snapshots.
- Generated Claude plugin package checks backed by adapter snapshots.
- Multi-host local release artifacts for Codex, Claude, schema, CLI, and the
  documentation-only generic markdown pack.
- CI, release-check, demo smoke, privacy, and release artifact gates.
- Deterministic local release artifacts with checksums and manifest metadata.

### Compatibility Notes

- `skill/roadmap-delivery-skill/` remains the installable Codex package path.
- `dist/claude/` is the local Claude plugin package snapshot; live Claude Code
  loading remains an optional maintainer smoke check when the host binary is
  available.
- The generic markdown pack is documentation-only and does not claim support
  for future named hosts.
- Existing helper scripts under `skill/roadmap-delivery-skill/scripts/` remain
  compatibility wrappers.
- Legacy state artifacts continue to use warning-backed compatibility where the
  schema validators allow it.
- Publication to external release channels remains a separate human-approved
  action.
