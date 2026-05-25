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
- CI, release-check, demo smoke, privacy, and release artifact gates.
- Deterministic local release artifacts with checksums and manifest metadata.

### Compatibility Notes

- `skill/roadmap-delivery-skill/` remains the installable Codex package path.
- Existing helper scripts under `skill/roadmap-delivery-skill/scripts/` remain
  compatibility wrappers.
- Legacy state artifacts continue to use warning-backed compatibility where the
  schema validators allow it.
- Publication to external release channels remains a separate human-approved
  action.
