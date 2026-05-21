# Model Policy And Stall Control Reference

Use this reference when a roadmap automation has `phase_model_policy.json`,
phase-specific model requirements, stalled-run thresholds, or completion/stall
alerts.

## Model Control Boundary

The skill cannot switch the model or reasoning effort of an already-running
Codex session. Model and reasoning selection belong to the runner:

- Codex app automation config
- CLI model/reasoning flags or profile
- another explicit execution surface

The skill may read policy, compare required versus configured model, update
state, write a retarget plan, and request or perform an approved automation
update. It must not claim that prompt text alone changes the active model.

## Policy File

Recommended location:

```text
automation/<roadmap-slug>/phase_model_policy.json
```

Recommended shape:

```json
{
  "schema_version": 1,
  "max_stalled_runs": 3,
  "notification": {
    "mode": "alert_file",
    "fallback": "alert_file"
  },
  "defaults": {
    "model": "gpt-5.5",
    "reasoning_effort": "xhigh"
  },
  "phases": {
    "1": {
      "model": "gpt-5.5",
      "reasoning_effort": "xhigh"
    },
    "finalization": {
      "model": "gpt-5.5",
      "reasoning_effort": "xhigh"
    }
  }
}
```

Allowed `reasoning_effort` values:

- `minimal`
- `low`
- `medium`
- `high`
- `xhigh`

## Start-Run Gate

Before implementation:

1. Read delivery state and current phase.
2. Read `phase_model_policy.json` when present.
3. Resolve required model and reasoning for the current phase.
4. Read saved automation config or explicit runner config when available.
5. Compare required versus configured values.

If required and configured values match, continue normal phase extraction.

If they mismatch, do not edit phase-owned files. Record the mismatch, retarget
the automation only when the operator already approved that surface, then exit
so the next run starts on the correct model.

If the active model cannot be proven and the roadmap is model-strict, stop and
ask for confirmation rather than guessing.

## End-Run Retargeting

After a phase is delivered and reviewed:

1. Resolve the next phase.
2. Resolve the next phase model and reasoning from policy.
3. Update state with next required model/reasoning.
4. Retarget automation only when that update is approved.
5. Read back automation config.
6. If readback fails or mismatches, mark blocked, write an alert, and do not
   start the next phase.

Do not deliver the next phase in the same run after retargeting.

## Progress And Stall Control

Use a durable progress signature, not narration, to detect repeated
non-progress. Include surfaces such as current phase, status, last delivered
phase, review iteration count, verification result, latest review verdict, git
HEAD, delivery log hash/size, and blocker reason.

When the signature changes, reset `stalled_run_count` to `0`.

When it does not change, increment `stalled_run_count`.

When `stalled_run_count >= max_stalled_runs`, keep or set state blocked, pause
or request pause for the automation, and write an operator alert.

## Blocked Runs

Blocked state is not permission to repeat the same failed phase advancement.
Before incrementing stall count or writing another blocked review, use Blocked
Run Remediation from `troubleshooting.md`.

If the blocker is repaired, record `last_blocker_repair`, clear
`blocked_reason`, reset the stall counter, and resume the current phase.

If the blocker cannot be repaired without human action, keep state blocked and
make the required action explicit.

## Alerts

Always write a local alert file before relying on optional external
notifications:

```text
automation/<roadmap-slug>/alerts/<timestamp>-<kind>.md
```

Initial alert kinds:

- `stalled`
- `completed`
- `blocked`
- `retarget-failed`

External sinks such as GitHub issues, Slack, email, or webhooks are optional
and must fail safe to the local alert file.
