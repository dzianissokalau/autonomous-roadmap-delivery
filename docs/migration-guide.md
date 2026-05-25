# Migration Guide

This guide is for moving an existing Codex-only roadmap delivery setup onto the
framework core layout.

## What Changed

The old shape treated `skill/roadmap-delivery-skill/` as both source of truth
and installable package. The framework layout keeps that path installable, but
moves canonical behavior into:

- `core/references/` for workflow rules
- `core/templates/` and `core/prompts/` for reusable artifact text
- `schemas/` for versioned state, policy, review, and run-log contracts
- `src/roadmap_delivery/` for shared Python behavior
- `adapters/codex/` for Codex package rendering inputs

## Migration Steps

1. Keep the existing Codex install path:
   `skill/roadmap-delivery-skill/`.
2. Add or verify repository-local automation artifacts under
   `automation/<roadmap-slug>/`.
3. Add `schema_version: 1` to active delivery state when the automation is
   ready for schema validation.
4. Add `phase_model_policy.json` with required model and reasoning values.
5. Update automation prompts to include blocked remediation, model-policy
   gates, review gates, and completion hard stops.
6. Run artifact validation and status inspection from the repository checkout.
7. Use `scripts/build_codex_package.py --check` to prove the committed Codex
   package matches canonical core sources and the Codex adapter overlay.

## Validation Commands

```bash
python3 -m roadmap_delivery.cli inspect \
  --repo-root /path/to/repo \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --json

python3 -m roadmap_delivery.cli validate \
  --repo-root /path/to/repo \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --strict \
  --allow-warning worktree_dirty \
  --json

python3 scripts/build_codex_package.py --check
```

## Compatibility Rules

- Do not mutate installed copies under
  `${CODEX_HOME:-$HOME/.codex}/skills/roadmap-delivery-skill` during migration.
- Do not rewrite historical roadmap evidence to satisfy new schemas unless a
  roadmap phase explicitly owns that migration.
- Keep generated package updates committed and reviewable.
- Treat publication, promotion, live automation config edits, and installed
  skill synchronization as human-approved follow-ups.
