# Phase Model Policy And Stall Control Automation Guide

Status: Completed
Roadmap: `roadmaps/delivered_phase_model_policy_and_stall_control_roadmap.md`
Roadmap slug: `phase-model-policy-and-stall-control`
State file: `automation/phase-model-policy-and-stall-control/delivery_state.json`
Delivery log: `automation/phase-model-policy-and-stall-control/delivery_log.md`
Review directory: `automation/phase-model-policy-and-stall-control/reviews`
Policy file: `automation/phase-model-policy-and-stall-control/phase_model_policy.json`
Codex automation: `phase-model-policy-and-stall-control`
Cadence: hourly
Model: `gpt-5.5`
Reasoning effort: `xhigh`
Execution environment: local

## Operating Policy

- Deliver exactly one roadmap phase at a time.
- Read the roadmap, state file, delivery log, review/fix state, latest reviews,
  phase model policy, automation config, branch, and worktree status before
  editing.
- Preserve unrelated user changes.
- Use `codex/phase-model-policy-and-stall-control-phase-<n>` branches for
  implementation phases.
- Run every verification command or manual verification required by the current
  phase before claiming delivery.
- Require a fresh review verdict of `delivered` before advancing state.
- Stop after 3 review/fix iterations if the phase remains unresolved.
- If state is `blocked`, enter Blocker Remediation Mode before attempting
  normal phase delivery.
- Do not push, promote to `main`, merge, delete branches, or run destructive
  commands without explicit human approval.
- Keep this automation configured as `gpt-5.5` with `xhigh` reasoning unless a
  later delivered phase changes the model policy and retarget flow.

## Next Run Prompt

Run the next safe step for
`roadmaps/delivered_phase_model_policy_and_stall_control_roadmap.md` using
the phase-gated workflow in `automation/`.

Read these first:

- `automation/phase-model-policy-and-stall-control/automation_guide.md`
- `automation/codex_phase_gated_delivery_automation_template.md`
- `automation/phase-model-policy-and-stall-control/delivery_state.json`
- `automation/phase-model-policy-and-stall-control/delivery_log.md`
- `automation/phase-model-policy-and-stall-control/review_fix_state.json`
- `automation/phase-model-policy-and-stall-control/phase_model_policy.json`

Operate on exactly one current phase at a time. Reconcile roadmap, state, log,
review files, model policy, git branch, working tree, and saved automation
configuration before editing. If they disagree, record the blocker in state,
log, and review, then stop.

If `delivery_state.json` has `status: blocked`, do not try to advance the
phase first. Enter Blocker Remediation Mode:

1. Classify the blocker as local-repairable, automation-config repairable,
   permission-gated, external-decision, or destructive-risk.
2. If the blocker is local-repairable or automation-config repairable and the
   operator has already authorized the needed surface, fix the blocker first.
3. Rerun reconciliation and artifact validation.
4. If the blocker is resolved, clear `blocked_reason`, reset stalled counters
   as appropriate, record a repair entry in state/log, and only then start or
   resume the current phase.
5. If the blocker requires credentials, a product decision, destructive git, or
   unapproved publication/promotion, keep state blocked and ask for the missing
   human action.

A previous blocked review does not by itself block delivery when state contains
a later successful blocker repair, `blocked_reason` is null, and reconciliation
passes.

Hard stop before delivery if `all_phases_complete` is true, state is
`completed`, or state is `completed_pending_pause`. In that case, confirm the
automation is paused or request pause permission, write any missing completion
alert, and do not start phase work.

For the current phase only:

- extract objective, owned files, implementation steps, acceptance criteria,
  required verification, non-goals, and stop conditions
- create or reuse the correct `codex/phase-model-policy-and-stall-control-phase-<n>`
  branch when implementation work is required
- verify the automation model is `gpt-5.5` and reasoning effort is `xhigh`
- make only phase-scoped changes
- run required verification and targeted checks
- update `automation/phase-model-policy-and-stall-control/delivery_log.md` and
  `automation/phase-model-policy-and-stall-control/delivery_state.json`
- perform a skeptical review from fresh context where available
- write review output under `automation/phase-model-policy-and-stall-control/reviews/`
- if the verdict is `needs-fix`, fix only current-phase findings and rerun
  verification
- stop after 3 review/fix iterations and mark blocked if still not delivered

Do not advance unless acceptance criteria are satisfied, verification passed,
review verdict is `delivered`, and roadmap/state/log agree. After advancing
state to the next phase, stop.
