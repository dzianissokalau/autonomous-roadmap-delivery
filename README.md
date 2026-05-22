# Roadmap Delivery Skill

This workspace contains the strategy, phased roadmap, and local automation
artifacts for building the Roadmap Delivery Skill for Codex.

GitHub repository: `git@github.com:dzianissokalau/roadmap-delivery-skill.git`

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

- `roadmaps/not_started_framework_core_and_release_readiness_roadmap.md`:
  canonical workflow core, schemas, shared library/CLI, CI, security, release,
  and demo readiness.
- `roadmaps/not_started_multi_host_adapter_and_claude_plugin_roadmap.md`:
  generated host adapters, Claude plugin packaging, provider-neutral model
  roles, and adapter parity tests.

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
