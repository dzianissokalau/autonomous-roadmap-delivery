# Model Policy And Stall Control Reference

Use this reference when a roadmap automation has phase-specific model
requirements, reasoning requirements, stalled-run thresholds, or operator
alerts.

## Core Contract

Model and reasoning selection belong to the runner. The workflow may read
policy, compare required and configured values, update durable state, write
retarget plans, and request or perform approved runner updates. Prompt text
alone does not prove the active model or reasoning effort.

## Policy Shape

Policy lives with automation artifacts:

```text
automation/<roadmap-slug>/phase_model_policy.json
```

Minimum structure:

```json
{
  "schema_version": 1,
  "max_stalled_runs": 3,
  "notification": {
    "mode": "alert_file",
    "fallback": "alert_file"
  },
  "defaults": {
    "model": "<default-model>",
    "reasoning_effort": "<default-reasoning-effort>"
  },
  "phases": {
    "finalization": {
      "model": "<finalization-model>",
      "reasoning_effort": "<finalization-reasoning-effort>"
    }
  },
  "adaptive_model_policy": {
    "enabled": false,
    "escalate_on": [
      "delivered_with_fixes",
      "verification_failed",
      "review_needs_fix",
      "stalled",
      "retarget_failed"
    ],
    "human_gated_qualities": [
      "blocked_human_required",
      "completion_closeout_failed"
    ],
    "deescalate_after_flawless_runs": 0,
    "escalation": {
      "model": "<stronger-approved-model>",
      "reasoning_effort": "<stronger-approved-reasoning>"
    },
    "caps": {
      "allowed_models": ["<approved-model>"],
      "max_reasoning_effort": "<maximum-approved-reasoning>",
      "allowed_providers": ["<provider>"],
      "allowed_cost_classes": ["<cost-class>"]
    }
  }
}
```

Allowed reasoning effort values are `minimal`, `low`, `medium`, `high`, and
`xhigh`.

## Adaptive Model Policy

Run quality is classified after verification and review:

- `flawless`
- `delivered_with_fixes`
- `verification_failed`
- `review_needs_fix`
- `blocked_local_repairable`
- `blocked_human_required`
- `stalled`
- `retarget_failed`
- `completion_closeout_failed`

Adaptive policy changes only the next run. It never claims to switch the active
model inside an already-running session. Non-flawless local delivery outcomes
may escalate to the configured `escalation` target. Human-gated blockers skip
model escalation and keep asking for the missing human action. A flawless streak
may de-escalate only when `deescalate_after_flawless_runs` and explicit floor
targets are configured.

Caps are mandatory when adaptive policy is enabled. `allowed_models`,
`max_reasoning_effort`, and optional provider or cost-class caps prevent
unbounded model, provider, or cost changes without requiring the workflow to
infer provider-specific pricing.

## Provider Role Config

Provider-role config is an optional, host-neutral input that describes which
model policy should be used for workflow roles such as executor, reviewer,
inspector, finalizer, and repairer.

Repository examples live at:

```text
config/providers.example.yaml
schemas/provider_config.schema.json
```

The provider-role config maps each role to:

- the `phase_model_policy.json` field names it can populate (`model` and
  `reasoning_effort`)
- provider-specific model names
- whether the provider supports an explicit reasoning-effort control
- runner config field names when a host exposes them

`phase_model_policy.json` remains the durable start-run gate for a roadmap
phase. A provider-role config can be used to prepare or explain policy values,
but it does not prove the active runner is configured with those values. The
start-run gate still needs trusted runner readback before phase-owned edits.

## Start-Run Gate

Before implementation:

1. Resolve current phase from delivery state.
2. Resolve required model and reasoning from numbered policy override or
   defaults.
3. Read configured runner model and reasoning from a trusted config or readback
   source.
4. Stop before phase-owned edits if required and configured values differ or
   cannot be proven.

Retarget runner configuration only when `approval_policy.json` resolves
`retarget_saved_automation` to `allowed` or explicit human approval is already
present. If the decision is `ask`, record the required approval and stop. If the
decision is `forbidden`, record a blocker and do not attempt the retarget.
After retargeting, read back the saved config and stop so a later run starts
with the right settings.

## End-Run Retargeting

After a delivered review verdict, resolve the next phase's model and reasoning,
classify the run quality, apply `adaptive_model_policy` to the next target,
update durable state, compare against runner readback, and retarget only when
the approval-policy decision is `allowed` or explicit human approval is already
present. The retarget plan should surface the run quality, adaptive action,
operation decision, and target source so conservative mode preserves ask-first
behavior and delegated modes avoid repeated prompts only for explicitly allowed
runner updates. If readback fails or mismatches, keep or set blocked state,
write an alert, and do not start the next phase.

## Progress And Stall Control

Use durable progress signatures from state, latest review, verification, git
head, delivery log hash/size, and blocker reason. Reset stalled count when the
signature changes. Increment it when the signature repeats. At threshold, keep
or set blocked state and write an operator alert.

## Alerts

Local alert files are the durable fallback for `stalled`, `completed`,
`blocked`, and `retarget-failed` states. External notifications are optional
and must fail safe to the local alert file.

## Host Adapter Boundary

The core defines policy fields, comparison rules, stall counters, and alert
requirements, including adaptive run quality and model-target decisions. Host
adapters own concrete model names, provider-role guidance, runner readback, and
runner update mechanisms. If a host cannot prove or set a role's model or
reasoning value, the adapter must record that limitation rather than claiming
unsupported control.
