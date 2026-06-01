# Demo Roadmap Fixture

This fixture is a tiny self-contained repository for trying the roadmap
delivery workflow without network access, credentials, or a live Codex app
automation.

It demonstrates:

- a roadmap with one delivered phase and one current phase
- committed automation state, log, review, policy, and run-log artifacts
- a scaffold dry-run that plans files without writing them
- validation and inspection of the file-backed control plane
- safe blocked-run and model-policy mismatch scenarios
- conservative fallback and delegated local approval-policy scenarios
- an install and runtime checklist for the generated Codex and Claude packages

## Try The Fixture

From the repository root:

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

The direct `validate` and `inspect` commands may report that no saved Codex
automation config exists in your local home directory. That is expected for the
fixture. The committed sample config under `automation-config/` is used by the
smoke tests and can be copied into a temporary home when you want to exercise
automation readback.

## Scenario Files

`scenarios/blocked-remediation/` contains a blocked Phase 1 state and review.
It shows the shape an automation should preserve when a local artifact is
missing: keep the run blocked, retain the reason, and enter Blocker Remediation
Mode on the next pass.

`scenarios/model-policy-mismatch/automation.toml` intentionally configures the
wrong model and reasoning effort. Validation should stop before delivery when
that saved automation config is used with the demo policy.

`scenarios/delegated-local/approval_policy.json` can be copied into
`automation/demo_roadmap/approval_policy.json` in a temporary checkout. Inspect
should then report `delegated_local`, allow local commits, model retargets, and
completion or stall pause, and keep branch push ask-first.

## Runtime Checklist

Use `runtime-checklist.md` to stage the generated Codex package and Claude
plugin in temporary directories, run inspect and validate on a temporary demo
checkout, trigger the delegated-local policy fixture, trigger the
blocked-remediation fixture, and trigger the model-policy-mismatch fixture
without credentials or live automation changes.
