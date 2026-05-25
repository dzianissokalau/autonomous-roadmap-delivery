# Roadmap Delivery Skill

This workspace contains the strategy, phased roadmap, and local automation
artifacts for building the Roadmap Delivery Skill for Codex.

GitHub repository: `git@github.com:dzianissokalau/roadmap-delivery-skill.git`

[![CI](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/ci.yml)
[![Release Check](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/release-check.yml/badge.svg)](https://github.com/dzianissokalau/roadmap-delivery-skill/actions/workflows/release-check.yml)

Security policy: `SECURITY.md`. Privacy and release sanitization guide:
`docs/privacy-and-sanitization.md`.

## Roadmaps

- Roadmap: `roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md`
- Status: Delivered
- Current phase: Complete
- Review branch: `codex/autonomous-roadmap-delivery-skill-phase-10`
- Automation guide: `automation/autonomous-roadmap-delivery-skill/automation_guide.md`
- Delivery state: `automation/autonomous-roadmap-delivery-skill/delivery_state.json`
- Delivery log: `automation/autonomous-roadmap-delivery-skill/delivery_log.md`
- Final review prompt: `automation/autonomous-roadmap-delivery-skill/deep_review_prompt.md`
- Codex automation: `autonomous-roadmap-delivery-skill` hourly, PAUSED
- Repository skill snapshot: `skill/roadmap-delivery-skill/`

## Model-Aware Automation Update

- `roadmaps/delivered_phase_model_policy_and_stall_control_roadmap.md`:
  model-aware automation retargeting, stalled-run pause behavior, and local
  operator alerts. The roadmap is delivered and the automation pause has been
  confirmed.

Model-aware roadmap delivery uses a repository-local policy file:

```text
automation/<roadmap-slug>/phase_model_policy.json
```

The policy records default model/reasoning choices, optional per-phase
overrides, the finalization model, stalled-run threshold, and notification
fallback. New roadmap delivery automations created with the current setup
guidance should create this file by default.

Important limitation: the skill cannot switch the model or reasoning effort of
an already-running Codex session. The Codex app automation, CLI command, or
runner profile must be configured for the required model before delivery work
starts. The skill validates that readback and stops before implementation when
the configured model or reasoning effort cannot be proven.

### Migrating Existing Automations

Existing roadmap delivery automations can adopt model policy incrementally:

1. Create `automation/<roadmap-slug>/phase_model_policy.json` with
   `schema_version`, `max_stalled_runs`, `notification`, `defaults`, and
   `phases`.
2. Add or verify state fields for `required_model`,
   `required_reasoning_effort`, configured automation model/reasoning,
   `run_count`, `stalled_run_count`, `max_stalled_runs`,
   `last_progress_signature`, `last_progress_at`, and `last_operator_alert`.
3. Resolve the current phase's required model from the policy and read back the
   saved automation or runner config before editing phase files.
4. Update the automation prompt to include the start-run model-policy hard
   stop, Blocker Remediation Mode, completion hard stop, and one-phase delivery
   guard.
5. Run artifact validation and status inspection before reactivating scheduled
   delivery:

```bash
python3 skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py \
  --repo-root /path/to/repo \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --json

python3 skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py \
  --repo-root /path/to/repo \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --json
```

Backward compatibility is intentional: roadmaps without
`phase_model_policy.json` continue to use legacy behavior unless the roadmap,
automation guide, or operator explicitly makes model policy strict. Do not add
policy state fields by guessing desired automation values; configured
model/reasoning fields should come from readback.

Release notes and residual risks:

- Alert files are always local first; GitHub issues and other external
  notification sinks are optional and require credentials plus approval.
- Completed roadmaps still need explicit pause handling when the automation
  remains active. A hard-stop prompt is a safety backstop, not a substitute for
  a paused automation.
- Publication, promotion to `main`, branch deletion, and live automation config
  changes remain human-approved actions.
- The repository skill snapshot is the releasable source. Installed
  `${CODEX_HOME:-$HOME/.codex}/skills/roadmap-delivery-skill` copies should be
  synchronized only by an approved install or maintenance step.

## Planned Roadmaps

- `roadmaps/in_progress_framework_core_and_release_readiness_roadmap.md`:
  canonical workflow core, schemas, shared library/CLI, CI, security, release,
  and demo readiness. Automation is configured as
  `framework-core-and-release-readiness` with hourly cadence, `gpt-5.5`, and
  `xhigh`, currently ACTIVE. This roadmap is the active migration contract for
  separating canonical core, Codex adapter, generated package, and release
  responsibilities while preserving the existing Codex install path.
- `roadmaps/not_started_multi_host_adapter_and_claude_plugin_roadmap.md`:
  generated host adapters, Claude plugin packaging, provider-neutral model
  roles, and adapter parity tests. This companion roadmap intentionally waits
  on the framework core roadmap through the generated Codex adapter baseline.

## Operating Model

Use a phase-gated delivery loop:

1. Treat the roadmap as the phase contract.
2. Deliver exactly one phase at a time.
3. Record durable state before and after each phase pass.
4. Run required verification before claiming phase delivery.
5. Require a fresh review verdict before phase advancement.
6. Stop on blockers, stale state, failed verification, or unclear scope.

The roadmap is complete locally. The pushed branch contains the roadmap
evidence plus a source snapshot of the installed skill package so external
reviewers can inspect the delivered skill without access to the local
`~/.codex/skills` directory.

## Framework CLI

The shared package exposes a stable CLI for local inspection, validation, and
dry-run planning:

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
The legacy helper scripts under `skill/roadmap-delivery-skill/scripts/` remain
compatibility wrappers around the same shared library behavior.

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
  scripts/check_release_privacy.py \
  src/roadmap_delivery/*.py \
  roadmap_delivery/__init__.py \
  skill/roadmap-delivery-skill/scripts/*.py \
  tests/*.py

python3 -m unittest tests.test_schema_validation -v
python3 scripts/build_codex_package.py --check
python3 -m unittest tests.test_quality_gates -v
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

Local equivalent for the release-check artifact build:

```bash
mkdir -p dist
tar -czf dist/roadmap-delivery-codex-skill.tar.gz \
  README.md \
  SECURITY.md \
  LICENSE \
  pyproject.toml \
  docs \
  core \
  schemas \
  src \
  scripts \
  adapters \
  skill/roadmap-delivery-skill
```

## Install The Codex Skill

The installable skill lives at:

```text
skill/roadmap-delivery-skill/
```

Install it with Codex's skill installer:

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

To run the repository-local checks:

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=$TMPDIR/roadmap-delivery-skill-review-compile-pycache \
  python3 -m py_compile \
  skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py \
  skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
```

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
