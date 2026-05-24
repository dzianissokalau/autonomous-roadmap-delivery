# Delivery State Template

Use this template for `automation/<roadmap-slug>/delivery_state.json`.

```json
{
  "roadmap": "roadmaps/<roadmap-file>.md",
  "roadmap_slug": "<roadmap-slug>",
  "current_phase": "Phase N - Name",
  "branch": "<phase-branch-or-null>",
  "status": "not_started",
  "review_iterations": 0,
  "max_review_iterations": 3,
  "last_verification": null,
  "last_review": null,
  "last_delivered_phase": null,
  "blocked_reason": null,
  "last_blocker_repair": null,
  "required_model": "<required-model-or-null>",
  "required_reasoning_effort": "<required-reasoning-or-null>",
  "configured_automation_model": "<configured-model-or-null>",
  "configured_automation_reasoning_effort": "<configured-reasoning-or-null>",
  "run_count": 0,
  "stalled_run_count": 0,
  "max_stalled_runs": 3,
  "last_progress_signature": null,
  "last_progress_at": null,
  "last_operator_alert": null,
  "auto_advance_after_delivered_review": true,
  "push_to_github": false,
  "all_phases_complete": false,
  "updated_at": null
}
```

Configured model and reasoning fields must come from runner readback, not from
desired policy values.
