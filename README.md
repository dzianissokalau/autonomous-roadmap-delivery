# Roadmap Delivery Skill

Roadmap Delivery Skill is a file-backed, phase-gated delivery framework for
roadmap-driven coding work. The repository now separates the canonical workflow
core from host-specific packaging, with Codex as the first generated adapter.

GitHub repository: `git@github.com:dzianissokalau/roadmap-delivery-skill.git`

[![CI](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/ci.yml)
[![Release Check](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/release-check.yml/badge.svg)](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/release-check.yml)

Key docs:

- Architecture: `docs/architecture.md`
- Autonomy and approval policy: `docs/autonomy-and-approval-policy.md`
- Compatibility: `docs/compatibility.md`
- Contributor workflow: `docs/contributor-workflow.md`
- Migration guide: `docs/migration-guide.md`
- Privacy and release sanitization: `docs/privacy-and-sanitization.md`
- Release notes: `docs/release-notes-0.1.0.md`
- Security policy: `SECURITY.md`

## Quickstart

### Install In Codex

The installable Codex skill package is committed in this repository:

```text
skill/roadmap-delivery-skill/
```

Install it from inside Codex first:

1. Open Codex and ask:

   ```text
   Install the Codex skill from GitHub repo dzianissokalau/roadmap-delivery-skill at path skill/roadmap-delivery-skill
   ```

2. Approve the install if Codex asks for confirmation.
3. Restart Codex if prompted.

If your Codex build has a Skills or Plugins import screen, use the same values:

- Repository: `dzianissokalau/roadmap-delivery-skill`
- Skill path: `skill/roadmap-delivery-skill`

This repository ships the generated skill package, so users do not need to run
the renderer before installing it.

After restart, try:

```text
$roadmap-delivery-skill inspect this roadmap automation state
```

### CLI Install Fallback

If the in-Codex install path is unavailable or you are scripting setup, use
Codex's bundled skill installer:

```bash
python3 "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo dzianissokalau/roadmap-delivery-skill \
  --path skill/roadmap-delivery-skill
```

This installs to:

```text
${CODEX_HOME:-$HOME/.codex}/skills/roadmap-delivery-skill
```

Restart Codex after installation so the skill is picked up.

Manual fallback:

```bash
git clone git@github.com:dzianissokalau/roadmap-delivery-skill.git /tmp/roadmap-delivery-skill
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R /tmp/roadmap-delivery-skill/skill/roadmap-delivery-skill \
  "${CODEX_HOME:-$HOME/.codex}/skills/"
```

To verify the generated package before installing:

```bash
python3 scripts/build_codex_package.py --check
python3 -m unittest tests.test_adapter_codex -v
```

### Developer Setup

Run the framework from a checkout:

```bash
python3 -m roadmap_delivery.cli version

python3 -m roadmap_delivery.cli inspect \
  --repo-root "$PWD" \
  --roadmap-slug framework-core-and-release-readiness \
  --automation-id framework-core-and-release-readiness \
  --json

python3 -m roadmap_delivery.cli validate \
  --repo-root "$PWD" \
  --roadmap-slug framework-core-and-release-readiness \
  --automation-id framework-core-and-release-readiness \
  --strict \
  --allow-warning worktree_dirty \
  --json
```

Install the local Python package when you want the `roadmap-delivery` console
script during development:

```bash
python3 -m pip install -e .
roadmap-delivery version
```

## Architecture

The repository is organized around durable files rather than a service-backed
control plane:

| Surface | Path | Responsibility |
|---|---|---|
| Core workflow | `core/references/` | Host-neutral setup, delivery, review, state, finalization, and troubleshooting rules. |
| Templates and prompts | `core/templates/`, `core/prompts/` | Reusable state, log, review, prompt, and guard text. |
| Schemas | `schemas/` | Versioned contracts for delivery state, model policy, reviews, and run logs. |
| Shared library | `src/roadmap_delivery/` | Validation, inspection, model policy, progress, git, state, and CLI behavior. |
| Codex adapter | `adapters/codex/` | Rendering inputs for the committed Codex skill package. |
| Codex package | `skill/roadmap-delivery-skill/` | Generated installable skill snapshot and compatibility scripts. |
| Automation evidence | `automation/<roadmap-slug>/` | Local state, logs, alerts, reviews, and guide files for roadmap runs. |
| Release output | `dist/` | Ignored local build artifacts created by `scripts/build_release.py`. |

The Codex package is generated from canonical core sources plus the Codex
adapter overlay. `scripts/build_codex_package.py --check` fails when the
committed package drifts from those inputs.

## Compatibility Matrix

| Surface | Current support | Notes |
|---|---|---|
| Codex skill path | Supported | `skill/roadmap-delivery-skill/` remains installable. |
| Legacy helper script paths | Supported | Scripts under `skill/roadmap-delivery-skill/scripts/` are compatibility wrappers. |
| Python CLI | Supported | Use `python3 -m roadmap_delivery.cli` from a checkout or `roadmap-delivery` after install. |
| State schema | Versioned | `schema_version: 1` is validated; legacy states remain warning-backed where supported. |
| Model policy | Supported | `phase_model_policy.json` gates required model and reasoning readback. |
| Release artifacts | Local only | Build and verify locally; publication requires explicit human approval. |
| Claude adapter | Supported locally | Generated Claude plugin package, reviewer agent, hooks, install docs, and offline smoke tests ship as local release artifacts; live Claude binary checks remain optional. |
| Hosted control plane | Not included | This roadmap keeps state, logs, reviews, and alerts file-backed. |

## Roadmaps

- `roadmaps/delivered_autonomous-roadmap-delivery-skill-phased-roadmap.md`: delivered
  original Codex roadmap and repository skill snapshot.
- `roadmaps/delivered_phase_model_policy_and_stall_control_roadmap.md`:
  delivered model-aware automation retargeting, stalled-run handling, and local
  operator alerts.
- `roadmaps/delivered_framework_core_and_release_readiness_roadmap.md`:
  delivered framework hardening roadmap for the canonical core, schemas, shared
  library, CLI, generated Codex adapter, CI, privacy, release, and closeout.
- `roadmaps/delivered_multi_host_adapter_and_claude_plugin_roadmap.md`:
  completed companion roadmap for generated host adapters and Claude packaging;
  the saved automation is paused.
- `roadmaps/delivered_autonomous_operation_modes_and_adaptive_control_roadmap.md`:
  completed roadmap for autonomy modes, adaptive model escalation, and
  automatic pause behavior; the saved automation is pending a human pause
  decision.

## Operating Model

Roadmap delivery uses a single-phase loop:

1. Reconcile the roadmap, state, log, reviews, model policy, saved automation
   config, branch, and worktree before editing.
2. Deliver exactly one current phase on `codex/<roadmap-slug>-phase-<n>`.
3. Run every required verification command plus targeted checks for changed
   behavior.
4. Write a skeptical review artifact with verdict `delivered`, `needs-fix`, or
   `blocked`.
5. Advance state only after acceptance criteria, verification, and review all
   agree.
6. Preserve publication, promotion, installed-skill sync, destructive git, and
   credential use as explicit human-approved actions.

Completed roadmaps still need an automation pause decision when the saved
automation remains active. The local completion alert is the durable fallback;
pausing the Codex app automation is a separate approved operation.

## Autonomy Controls

Autonomy is selected per roadmap automation with `approval_policy.json`.
Existing automations without that file stay conservative: they may edit
phase-owned files, write state/log/review artifacts, create or switch the
current phase branch, and run verification. Retargeting saved automation
model/reasoning, pausing a saved automation, committing locally, pushing a
branch, publication, promotion, credential use, installed-skill sync, and
destructive git remain approval-gated unless a durable policy explicitly allows
the lower-risk operation.

Use these files when choosing a mode:

- `docs/autonomy-and-approval-policy.md`: policy contract and operation table.
- `docs/migration-guide.md`: opt-in steps for existing automations.
- `examples/autonomy-controls/`: approval policy examples, adaptive model
  trace, and completion/stall pause examples.
- `examples/demo-roadmap/scenarios/delegated-local/approval_policy.json`: demo
  fixture for inspecting delegated local decisions without live automation
  changes.

Never-auto operations remain forbidden in every mode: force push,
`git reset --hard`, branch or tag deletion, promotion to `main`, release or
package publication, unavailable credential use, repository security or billing
changes, global tool sync, and destructive filesystem operations outside phase
scope.

## Framework CLI

The shared package exposes stable inspection, validation, scaffold, package,
and version commands:

```bash
python3 -m roadmap_delivery.cli version

python3 -m roadmap_delivery.cli inspect \
  --repo-root "$PWD" \
  --roadmap-slug framework-core-and-release-readiness \
  --automation-id framework-core-and-release-readiness \
  --json

python3 -m roadmap_delivery.cli validate \
  --repo-root "$PWD" \
  --roadmap-slug framework-core-and-release-readiness \
  --automation-id framework-core-and-release-readiness \
  --strict \
  --allow-warning worktree_dirty \
  --json

python3 -m roadmap_delivery.cli scaffold \
  --repo-root "$PWD" \
  --roadmap-slug example-roadmap \
  --automation-id example-roadmap-delivery \
  --dry-run \
  --json

python3 -m roadmap_delivery.cli package \
  --repo-root "$PWD" \
  --adapter codex \
  --dry-run \
  --json
```

After installation, the same interface is available as `roadmap-delivery`.
The legacy helper scripts under `skill/roadmap-delivery-skill/scripts/` call
the same shared library paths.

## Demo Fixture

`examples/demo-roadmap/` is a self-contained fixture for trying the workflow
without network access, credentials, or live Codex app automation. It includes
a three-phase demo roadmap, state/log/review artifacts, a model policy, and
scenarios for blocked remediation and model-policy mismatch.

```bash
python3 -m roadmap_delivery.cli scaffold \
  --repo-root /tmp/demo-roadmap-plan \
  --roadmap-slug demo-roadmap \
  --automation-id demo-roadmap-delivery \
  --dry-run \
  --json

python3 -m roadmap_delivery.cli validate \
  --repo-root examples/demo-roadmap \
  --roadmap-slug demo-roadmap \
  --json

python3 -m roadmap_delivery.cli inspect \
  --repo-root examples/demo-roadmap \
  --roadmap-slug demo-roadmap \
  --json
```

The smoke tests copy the fixture to a temporary git repository and temporary
home directory so automation readback and blocker behavior can be exercised
without touching a real saved Codex automation.

## CI And Release Checks

GitHub Actions run repository-local checks only. The optional Codex skill
validator runs only when `CODEX_QUICK_VALIDATE` points at an available
`quick_validate.py` script, so CI does not require private Codex directories or
credentials.

Local equivalents for the CI workflow:

```bash
python3 -m unittest discover -s tests -v

PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/roadmap-delivery-ci-pycache" \
  python3 -m py_compile \
  scripts/build_codex_package.py \
  scripts/build_release.py \
  scripts/check_release_privacy.py \
  src/roadmap_delivery/*.py \
  roadmap_delivery/__init__.py \
  skill/roadmap-delivery-skill/scripts/*.py \
  tests/*.py

python3 -m unittest tests.test_schema_validation -v
python3 scripts/build_codex_package.py --check
python3 -m unittest tests.test_quality_gates -v
python3 -m unittest tests.test_smoke_demo -v
python3 scripts/check_release_privacy.py --repo-root .

python3 -m roadmap_delivery.cli validate \
  --repo-root "$PWD" \
  --roadmap-slug framework-core-and-release-readiness \
  --automation-id framework-core-and-release-readiness \
  --strict \
  --allow-warning missing_automation_config \
  --allow-warning current_branch_name_mismatch \
  --allow-warning worktree_dirty \
  --json

git diff --check

if [ -n "${CODEX_QUICK_VALIDATE:-}" ] && [ -f "${CODEX_QUICK_VALIDATE}" ]; then
  python3 "${CODEX_QUICK_VALIDATE}" skill/roadmap-delivery-skill
fi
```

## Release Artifacts

The repository release version is stored in `VERSION`. The Python package
metadata stays unpublished until a separate publication phase, so local
release artifacts use `VERSION` for archive names, manifests, and checksums.

`scripts/build_release.py` builds these deterministic local artifacts:

- source archive
- Codex skill package
- Claude plugin package
- schema bundle
- CLI source package
- generic markdown pack for future adapter planning
- release manifest
- SHA-256 checksum file

Local equivalent for the release-check artifact build:

```bash
python3 scripts/build_release.py --check
python3 scripts/build_release.py --output-dir dist --json
(cd dist && shasum -a 256 -c roadmap-delivery-0.1.0-checksums.sha256)
python3 scripts/check_release_privacy.py --repo-root . \
  --bundle dist/roadmap-delivery-0.1.0-source.tar.gz \
  --bundle dist/roadmap-delivery-codex-skill-0.1.0.tar.gz \
  --bundle dist/roadmap-delivery-claude-plugin-0.1.0.tar.gz \
  --bundle dist/roadmap-delivery-schemas-0.1.0.tar.gz \
  --bundle dist/roadmap-delivery-cli-0.1.0.tar.gz \
  --bundle dist/roadmap-delivery-generic-markdown-pack-0.1.0.tar.gz
```

Release links:

- Changelog: `CHANGELOG.md`
- Release notes: `docs/release-notes-0.1.0.md`
- Release check workflow:
  `https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/release-check.yml`

Rollback is file-backed: keep the previous `VERSION`, changelog entry, and
checksum file together, rebuild from that commit, and reinstall the prior
`skill/roadmap-delivery-skill/` package if an operator needs to revert a local
Codex installation. Do not publish GitHub Releases, PyPI packages, Homebrew
formulae, or other external artifacts without explicit approval.

## Contributor Workflow

Use `docs/contributor-workflow.md` for the full workflow. The short form is:
pick the current roadmap phase, verify the owned file list, keep changes
phase-scoped, run required checks, write review evidence, and avoid publishing
or syncing installed skills without explicit approval.

## Migration Guide

Use `docs/migration-guide.md` when moving an existing Codex-only automation to
the framework layout. The migration keeps `skill/roadmap-delivery-skill/`
installable while moving source-of-truth behavior into `core/`, `schemas/`,
`src/roadmap_delivery/`, and adapter templates.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
