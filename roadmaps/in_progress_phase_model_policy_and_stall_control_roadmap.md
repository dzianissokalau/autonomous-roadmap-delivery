# Phase Model Policy And Stall Control Roadmap

Status: Active
Current phase: Phase 9 - Tests, Fixtures, And Replay Prompts
Last completed phase: Phase 8 - Automation Setup Integration
Last updated: 2026-05-21
Next action: Start Phase 9 and add tests, fixtures, and replay prompts.
Blocked by: None

## Purpose

This roadmap adds model-aware automation control to Roadmap Delivery Skill.

The current skill can instruct Codex how to deliver a phase, inspect state, and
validate artifacts, but it cannot itself control which model or reasoning level
the active Codex run uses. Model choice belongs to the execution surface:
Codex app automation config, CLI/config profile, or another runner.

This roadmap makes that boundary explicit and operational:

```text
read current phase
resolve required model and reasoning for that phase
verify the automation is configured for that model
deliver only when configuration matches
after phase delivery, retarget automation to the next phase model
pause and alert on completion, blocker, or repeated non-progress
```

## Target Outcome

Roadmap Delivery Skill should support self-retargeting, phase-aware
automations:

- A roadmap automation starts on the model required for the first phase.
- Every run checks the current phase's required model and reasoning effort.
- A run does not start delivery work if the configured automation model does
  not match the phase policy.
- At the end of each delivered phase, the automation is updated to the model
  and reasoning effort required for the next phase.
- If delivery does not make progress for a configurable number of runs, the
  automation pauses and emits an operator alert.
- When the roadmap is fully delivered, the automation pauses and emits an
  operator alert.

## Design Principles

- Treat model choice as execution policy, not hidden prompt preference.
- Keep policy file-backed, versionable, and inspectable.
- Never claim that a skill can force a model switch inside an already-running
  Codex session.
- Prefer a retarget-and-exit flow over continuing on the wrong model.
- Detect progress through durable state changes, not optimistic narration.
- Always write an alert file locally, even when richer notification sinks fail.
- Pause safely on completion, repeated non-progress, or irreconcilable mismatch.
- Keep notification integrations optional and conservative.

## Core Artifacts

New artifacts should live under each roadmap automation directory:

```text
automation/<roadmap_slug>/
  phase_model_policy.json
  automation_run_log.jsonl
  alerts/
    <timestamp>-stalled.md
    <timestamp>-completed.md
    <timestamp>-blocked.md
```

Existing `delivery_state.json` should gain model-policy and progress fields:

```json
{
  "required_model": "gpt-5.5",
  "required_reasoning_effort": "high",
  "configured_automation_model": "gpt-5.5",
  "configured_automation_reasoning_effort": "high",
  "run_count": 12,
  "stalled_run_count": 0,
  "max_stalled_runs": 3,
  "last_progress_signature": "sha256:...",
  "last_progress_at": "2026-05-21T10:00:00+01:00",
  "last_operator_alert": null
}
```

## Policy File Shape

Recommended `phase_model_policy.json`:

```json
{
  "schema_version": 1,
  "max_stalled_runs": 3,
  "notification": {
    "mode": "alert_file",
    "fallback": "alert_file"
  },
  "defaults": {
    "model": "gpt-5.4",
    "reasoning_effort": "high"
  },
  "phases": {
    "1": {
      "model": "gpt-5.4",
      "reasoning_effort": "medium"
    },
    "2": {
      "model": "gpt-5.5",
      "reasoning_effort": "high"
    },
    "finalization": {
      "model": "gpt-5.5",
      "reasoning_effort": "xhigh"
    }
  }
}
```

Supported notification modes for the first implementation:

- `alert_file`: always available; writes a Markdown alert under `alerts/`.
- `github_issue`: optional; opens or updates a GitHub issue when a GitHub
  connector or CLI token is available.
- `none`: allowed only for tests and dry runs; completion/stall still appears
  in the final run response.

Future notification modes:

- `slack`
- `email`
- `codex_thread`
- `webhook`

## Phase 0 Decisions

Phase 0 confirms the policy contract as follows:

- Public term: `phase model policy`.
- Operator-facing description: model-aware automation.
- Required policy fields:
  - `schema_version`
  - `max_stalled_runs`
  - `notification`
  - `defaults`
  - `phases`
- Allowed `reasoning_effort` values:
  - `minimal`
  - `low`
  - `medium`
  - `high`
  - `xhigh`
- `finalization` is a pseudo-phase entry, not a numbered implementation phase.
- Initial notification sinks:
  - `alert_file`: required local fallback
  - `github_issue`: optional external sink
  - `none`: allowed only for tests and dry runs
- Repeated non-progress is reported as `stalled`; delivery state becomes
  `blocked`, automation is paused, and a stalled alert is written.
- Retarget failures are blocking. After a phase is delivered, failed retargeting
  pauses or blocks the automation, writes an alert, and prevents the next phase
  from starting.
- The skill must keep saying explicitly that it cannot switch the model of an
  already-running Codex session. The automation or runner must be configured
  before the next run starts.
- This roadmap delivery automation is configured for `gpt-5.5` with `xhigh`
  reasoning until a later phase implements per-phase retargeting.

## Progress Signature

Stall detection should not depend only on phase number. Some phases legitimately
need multiple runs. Compute a progress signature from durable surfaces:

```text
current_phase
status
last_delivered_phase
review_iterations
last_verification timestamp/result
last_review file/verdict
git HEAD
delivery_log size/hash
blocked_reason
```

If the signature changes at the end of a run, reset `stalled_run_count` to `0`.
If it does not change, increment `stalled_run_count`.

When `stalled_run_count >= max_stalled_runs`, pause the automation, record a
blocker, and emit a stalled alert.

## Phase Overview

```text
Phase 0 - Policy Contract
Phase 1 - Skill Routing And Reference Docs
Phase 2 - Policy And State Validation
Phase 3 - Start-Run Model Gate
Phase 4 - End-Run Retargeting Gate
Phase 5 - Progress Signature And Stall Counter
Phase 6 - Alert Files And Optional Notification Sinks
Phase 7 - Completion Pause And Alert Flow
Phase 8 - Automation Setup Integration
Phase 9 - Tests, Fixtures, And Replay Prompts
Phase 10 - Migration, Release, And Documentation
```

## Phase 0 - Policy Contract

### Objective

Define the model policy contract, notification semantics, progress definition,
and stop conditions before implementation.

### Owned Files

```text
roadmaps/in_progress_phase_model_policy_and_stall_control_roadmap.md
```

### Implementation Steps

1. Confirm whether the public concept should be called "phase model policy",
   "automation model policy", or another term.
2. Confirm the minimum required policy fields:
   - `schema_version`
   - `max_stalled_runs`
   - `notification`
   - `defaults`
   - `phases`
3. Confirm allowed `reasoning_effort` values:
   - `minimal`
   - `low`
   - `medium`
   - `high`
   - `xhigh`
4. Confirm whether `finalization` is a pseudo-phase or a normal phase entry.
5. Confirm the initial notification sinks:
   - `alert_file`
   - `github_issue`
   - `none`
6. Confirm whether repeated non-progress should mark state as:
   - `blocked`
   - `paused`
   - `stalled`
7. Decide whether automation retarget failures should block delivery or only
   alert after phase commit.

### Acceptance Criteria

- The policy file shape is stable enough for scripts and docs.
- The default `max_stalled_runs` is defined and configurable.
- The roadmap states that skills cannot force a running model switch.
- Notification fallback behavior is explicit.
- Completion and stall stop conditions are explicit.

### Required Verification

- Manually review this roadmap for contradictions with existing skill
  guarantees.
- Confirm the policy can represent at least:
  - a low-cost docs phase
  - a high-reasoning implementation phase
  - finalization
  - disabled notifications for tests

### Non-Goals

- Do not implement scripts.
- Do not change installed skill behavior.
- Do not edit Codex app automations.

### Stop Conditions

- Stop if model names or reasoning effort values are uncertain.
- Stop if notification expectations require integrations not available to the
  user.

## Phase 1 - Skill Routing And Reference Docs

### Objective

Teach the skill where model-policy work lives and how Codex should reason about
model selection without pretending it controls the active model directly.

### Owned Files

```text
skill/roadmap-delivery-skill/SKILL.md
skill/roadmap-delivery-skill/references/setup-automation.md
skill/roadmap-delivery-skill/references/phase-loop.md
skill/roadmap-delivery-skill/references/state-log-and-branches.md
skill/roadmap-delivery-skill/references/troubleshooting.md
```

Optional new file:

```text
skill/roadmap-delivery-skill/references/model-policy-and-stall-control.md
```

### Implementation Steps

1. Add model-policy routing to `SKILL.md`.
2. Add a concise rule:
   - read `phase_model_policy.json` before delivery
   - stop before implementation if configured automation model mismatches the
     current phase policy
3. Add setup guidance for creating `phase_model_policy.json`.
4. Add phase-loop guidance for start-run and end-run gates.
5. Add status guidance for reporting required/configured model and stall state.
6. Add troubleshooting entries for:
   - missing policy file
   - invalid model policy
   - current automation model mismatch
   - retarget update failure
   - repeated non-progress
   - blocked runs that repeat without remediation
   - automation worktrees missing local-only phase artifacts
7. Add Blocked Remediation Mode so a blocked run classifies and repairs
   local or already-authorized automation blockers before retrying phase
   advancement.

### Acceptance Criteria

- The skill can explain how to set a phase-specific model policy.
- The skill can distinguish model policy from model control.
- Existing setup, phase-loop, and status workflows mention model policy only
  where relevant.
- Missing or invalid policy has clear behavior.
- Blocked runs have clear repair behavior and do not endlessly retry the same
  failed advancement path.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=/private/tmp/autonomous-roadmap-delivery-pyyaml \
  python3 /Users/dzianissokalau/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skill/roadmap-delivery-skill
```

### Non-Goals

- Do not make the skill mutate automation config in this phase.
- Do not introduce notification integrations yet.

### Stop Conditions

- Stop if the new reference advice conflicts with existing hard rules.

## Phase 2 - Policy And State Validation

### Objective

Extend validation so bad model policies, missing progress fields, and
inconsistent automation configuration are caught before delivery starts.

### Owned Files

```text
skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py
tests/test_helper_scripts.py
automation/codex_phase_gated_delivery_automation_template.md
```

### Implementation Steps

1. Add optional discovery of `phase_model_policy.json`.
2. Validate:
   - JSON is valid
   - `schema_version` is supported
   - `max_stalled_runs` is a positive integer
   - `defaults.model` exists
   - `defaults.reasoning_effort` is allowed
   - phase entries use valid model/reasoning fields
   - notification mode is known
3. Inspect automation config model and reasoning effort when an automation id is
   provided.
4. Compare configured automation model/reasoning with the required current
   phase policy.
5. Report warnings or errors with stable codes.
6. Add state output fields for:
   - required model
   - configured model
   - model mismatch
   - stalled run count
7. Add blocked-remediation prompt validation so active blocked automations
   cannot keep retrying the same failed advancement path.
8. Update the shared automation template so new automations inherit Blocked
   Remediation Mode by default.

### Acceptance Criteria

- Validation passes when no policy file exists and the roadmap does not require
  model policy.
- Validation errors on malformed policy files.
- Validation errors or blocks when the current phase has a required model and
  automation config mismatches it.
- Status inspection reports model policy and stall counters.
- Active blocked automations without Blocked Remediation Mode fail validation.
- New automation templates describe blocked remediation as a framework rule.

### Required Verification

- Add fixture coverage for:
  - no policy file
  - valid policy
  - malformed JSON
  - invalid reasoning effort
  - current phase policy match
  - current phase policy mismatch
  - invalid notification mode
  - active blocked automation without blocked-remediation prompt guard
  - model policy match and mismatch

Run:

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=$TMPDIR/roadmap-delivery-skill-policy-compile-pycache \
  python3 -m py_compile \
  skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py \
  skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
```

### Non-Goals

- Do not update automation config.
- Do not pause automations.
- Do not emit alerts.

### Stop Conditions

- Stop if automation config format cannot be read reliably.

## Phase 3 - Start-Run Model Gate

### Objective

Add a start-of-run gate that prevents delivery on a mismatched automation model.

### Owned Files

```text
skill/roadmap-delivery-skill/references/phase-loop.md
skill/roadmap-delivery-skill/references/model-policy-and-stall-control.md
skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
```

### Implementation Steps

1. Define start-run sequence:
   - read roadmap
   - read delivery state
   - read model policy
   - read automation config
   - resolve current phase required model
   - compare required vs configured
2. If the model matches, continue normal phase extraction.
3. If the model mismatches:
   - do not edit phase-owned files
   - update state with mismatch details if safe
   - report the required model and current configured model
   - recommend or perform automation retarget only with explicit permission
4. For manual CLI use, provide relaunch commands.
5. For unknown active model, require a conservative operator confirmation before
   delivery unless automation config proves the intended model.

### Acceptance Criteria

- The documented phase loop starts with model-policy validation.
- Mismatch behavior is retarget-and-exit, not deliver-anyway.
- Manual users get exact CLI/profile examples.
- Automation users get exact automation update expectations.

### Required Verification

- Run status/validation fixtures.
- Manually inspect docs for any instruction that allows delivery after a known
  mismatch.

### Non-Goals

- Do not implement end-of-run retargeting.
- Do not implement stall alerting.

### Stop Conditions

- Stop if the active runner cannot prove or configure the model and the phase is
  marked model-strict.

## Phase 4 - End-Run Retargeting Gate

### Objective

After a phase is delivered, retarget the automation to the model and reasoning
effort required for the next phase.

### Owned Files

```text
skill/roadmap-delivery-skill/references/phase-loop.md
skill/roadmap-delivery-skill/references/finalization-and-promotion.md
skill/roadmap-delivery-skill/references/troubleshooting.md
```

Optional future helper:

```text
skill/roadmap-delivery-skill/scripts/plan_automation_retarget.py
```

### Implementation Steps

1. Resolve the next phase after a delivered review verdict.
2. Read `phase_model_policy.json`.
3. Compute next required model and reasoning effort.
4. Update `delivery_state.json` with next required model fields.
5. Update automation config to next model/reasoning when the execution surface
   supports it and approval is available.
6. Read back automation config after update.
7. If readback matches, leave automation active.
8. If retarget fails:
   - pause or mark blocked depending on policy
   - emit a retarget-failed alert
   - do not proceed to next phase delivery

### Acceptance Criteria

- Delivered phase advancement includes next-model resolution.
- Automation config readback is required after update.
- Retarget failure cannot silently leave the automation running on the wrong
  model.
- The skill can generate an operator-readable retarget plan.

### Required Verification

- Add fixture or dry-run checks for:
  - next phase policy found
  - next phase falls back to defaults
  - finalization policy found
  - retarget failure path

### Non-Goals

- Do not bypass approval boundaries for automation config edits.
- Do not start the next phase in the same run after retargeting.

### Stop Conditions

- Stop if automation config update is not available or readback fails.

## Phase 5 - Progress Signature And Stall Counter

### Objective

Detect repeated non-progress across automation runs and stop before wasting
more scheduled runs.

### Owned Files

```text
skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py
skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
skill/roadmap-delivery-skill/references/state-log-and-branches.md
tests/test_helper_scripts.py
```

Optional future helper:

```text
skill/roadmap-delivery-skill/scripts/compute_progress_signature.py
```

### Implementation Steps

1. Define progress signature fields.
2. Store `last_progress_signature` in `delivery_state.json`.
3. Store `run_count` and `stalled_run_count`.
4. Append each run summary to `automation_run_log.jsonl`.
5. At end of each run:
   - compute new signature
   - compare to previous signature
   - reset or increment `stalled_run_count`
6. If `stalled_run_count >= max_stalled_runs`, mark the run as stalled and
   trigger Phase 6 alerting behavior.

### Acceptance Criteria

- Progress changes reset stall count.
- No-progress runs increment stall count.
- `max_stalled_runs` is read from policy and defaults to `3`.
- Status inspection reports stall status.
- Run log is append-only JSONL.

### Required Verification

- Add fixture coverage for:
  - first run
  - progress detected
  - no progress detected
  - threshold reached
  - custom threshold
  - corrupt run log

### Non-Goals

- Do not decide notification sink behavior.
- Do not pause automation yet.

### Stop Conditions

- Stop if progress signature cannot be computed from durable surfaces.

## Phase 6 - Alert Files And Optional Notification Sinks

### Objective

Ensure stalled, blocked, retarget-failed, and completed automations produce a
durable operator alert, with optional richer notification sinks.

### Owned Files

```text
skill/roadmap-delivery-skill/references/model-policy-and-stall-control.md
skill/roadmap-delivery-skill/references/troubleshooting.md
skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
```

Optional future helper:

```text
skill/roadmap-delivery-skill/scripts/write_operator_alert.py
```

### Implementation Steps

1. Define alert file templates:
   - stalled
   - completed
   - blocked
   - retarget failed
2. Always write alerts to:
   - `automation/<slug>/alerts/<timestamp>-<kind>.md`
3. Define optional `github_issue` behavior:
   - create one tracking issue per roadmap automation
   - append or comment on repeated alerts
   - include state/log/review paths
4. Define fallback behavior:
   - if notification sink fails, preserve alert file
   - record notification failure in state/log
5. Keep Slack/email/webhook as future extension points.

### Acceptance Criteria

- Alert files are deterministic enough to test.
- Alert content includes:
  - roadmap path
  - phase
  - status
  - reason
  - required/current model if relevant
  - last verification/review summary
  - next human action
- Notification failure does not erase the local alert.

### Required Verification

- Add fixture coverage for alert generation.
- Manually inspect alert templates for enough operator context.

### Non-Goals

- Do not require GitHub, Slack, email, or webhook credentials.
- Do not send external notifications from tests.

### Stop Conditions

- Stop if notification would expose secrets or private paths unintentionally.

## Phase 7 - Completion Pause And Alert Flow

### Objective

When a roadmap is delivered, pause automation and notify the operator without
starting any further delivery work.

### Owned Files

```text
skill/roadmap-delivery-skill/references/finalization-and-promotion.md
skill/roadmap-delivery-skill/references/model-policy-and-stall-control.md
skill/roadmap-delivery-skill/references/troubleshooting.md
```

### Implementation Steps

1. Extend finalization checklist:
   - final verification passed
   - latest review verdict delivered
   - deep-review prompt written
   - final branch pushed if allowed
   - `all_phases_complete` true
2. Pause automation when completion state is written.
3. Write completed alert file.
4. Notify via configured sink.
5. Add hard-stop behavior:
   - if already complete, never start delivery
   - if automation still active, pause or ask for pause permission

### Acceptance Criteria

- Completion always produces an alert file.
- Completion always attempts or requests automation pause.
- Completed state cannot start future phase work.
- Status inspection clearly says the roadmap is complete and automation should
  be paused.

### Required Verification

- Add fixture coverage for:
  - complete and paused
  - complete but active
  - complete with missing alert
  - complete with notification failure

### Non-Goals

- Do not promote to `main` automatically.
- Do not delete automation artifacts after completion.

### Stop Conditions

- Stop if final verification or review verdict is missing.

## Phase 8 - Automation Setup Integration

### Objective

Make new automation setup create and apply model policy from the beginning.

### Owned Files

```text
skill/roadmap-delivery-skill/references/setup-automation.md
skill/roadmap-delivery-skill/references/model-policy-and-stall-control.md
skill/roadmap-delivery-skill/references/state-log-and-branches.md
```

### Implementation Steps

1. Add setup questions:
   - default model
   - default reasoning effort
   - per-phase overrides
   - finalization model
   - `max_stalled_runs`
   - notification mode
2. Generate initial `phase_model_policy.json`.
3. Configure automation for the first phase's required model/reasoning.
4. Read back automation config after creation.
5. If automation saves with wrong model/reasoning, correct or pause before
   responding.
6. Document the initial state fields that mirror policy.

### Acceptance Criteria

- New automation setup includes a policy file by default.
- First phase automation config matches policy.
- Setup docs explain how to choose lower-cost versus high-reasoning phases.
- Setup refuses to activate if policy validation fails.

### Required Verification

- Dry-run setup against a fixture roadmap.
- Validate generated policy.
- Validate generated prompt includes model-policy hard stop.

### Non-Goals

- Do not require users to provide per-phase overrides.
- Do not infer expensive models for every phase by default.

### Stop Conditions

- Stop if first-phase model cannot be configured or read back.

## Phase 9 - Tests, Fixtures, And Replay Prompts

### Objective

Add test and eval coverage so model-policy behavior does not regress.

### Owned Files

```text
tests/test_helper_scripts.py
evals/status-inspection-prompts.md
evals/review-fix-prompts.md
```

Optional new file:

```text
evals/model-policy-prompts.md
```

### Implementation Steps

1. Add fixture utilities for policy files.
2. Add test cases for policy validation.
3. Add test cases for stall thresholds and alert generation.
4. Add replay prompts for:
   - wrong model at start
   - retarget next phase
   - three stalled runs
   - custom stalled run threshold
   - delivered roadmap completion alert
5. Keep replay prompts answer-oriented, not implementation-leaking.

### Acceptance Criteria

- Unit tests cover success and failure paths.
- Replay prompts cover operator-facing behavior.
- Tests do not require network or external notification credentials.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=$TMPDIR/roadmap-delivery-skill-model-policy-compile-pycache \
  python3 -m py_compile \
  skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py \
  skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
```

### Non-Goals

- Do not test real Codex app automation updates in unit tests.
- Do not send real GitHub issues or external notifications in tests.

### Stop Conditions

- Stop if tests require private credentials.

## Phase 10 - Migration, Release, And Documentation

### Objective

Document migration for existing Roadmap Delivery Skill users and release the
model-policy/stall-control update cleanly.

### Owned Files

```text
README.md
skill/roadmap-delivery-skill/SKILL.md
skill/roadmap-delivery-skill/references/*.md
roadmaps/in_progress_phase_model_policy_and_stall_control_roadmap.md
```

### Implementation Steps

1. Add README section for model-aware automation.
2. Document migration for existing automation directories:
   - create `phase_model_policy.json`
   - add state fields
   - set first next-phase model
   - configure `max_stalled_runs`
   - choose notification mode
3. Document backward compatibility:
   - no policy file means legacy behavior unless the user asks for strict
     model policy
4. Update skill metadata if needed.
5. Run final validation and tests.
6. Commit and push only with explicit approval.

### Acceptance Criteria

- Existing users can adopt model policy incrementally.
- New users get model policy during setup.
- The README explains the limitation clearly:
  - the skill cannot switch a running model
  - the automation/runner must be retargeted
- Release notes or roadmap notes capture residual risks.

### Required Verification

- Run all tests.
- Run skill validation.
- Run status/artifact validation against a fixture with model policy.
- Check README examples for old repo or old skill names.

### Non-Goals

- Do not build a general notification service.
- Do not require all roadmaps to use model policy.
- Do not break existing installed skill users silently.

### Stop Conditions

- Stop if migration would require destructive edits to existing automation
  artifacts.

## Cross-Phase Acceptance Criteria

The roadmap is complete when:

- `phase_model_policy.json` is documented and validated.
- Setup can create a phase model policy.
- Status inspection reports required/configured model and stall counters.
- Start-run gate stops delivery on a known model mismatch.
- End-run gate retargets automation to the next phase model or stops safely.
- Repeated non-progress pauses automation after configurable threshold.
- Delivered roadmaps pause automation and write a completion alert.
- Alert files are always written locally.
- External notification sinks are optional and failure-safe.
- Tests cover model policy, stall detection, completion alerts, and legacy
  behavior without a policy file.

## Recommended Implementation Order

1. Confirm policy terminology and JSON shape.
2. Add model-policy reference docs.
3. Extend validation and inspection scripts.
4. Add start-run model gate.
5. Add end-run retarget plan/readback behavior.
6. Add progress signatures and stall counters.
7. Add alert files.
8. Integrate policy into setup automation.
9. Add fixture and replay coverage.
10. Document migration and release.

## Backlog

- GitHub issue notifications.
- Slack/email notifications.
- Webhook notifications.
- Codex thread heartbeat follow-up for alert review.
- UI surface for editing phase model policy.
- Cost-aware model recommendations per phase type.
- Historical analytics for which phase types need higher reasoning.
