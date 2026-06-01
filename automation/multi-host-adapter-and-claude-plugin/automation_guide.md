# Multi-Host Adapter And Claude Plugin Automation Guide

Status: Completed pending pause
Roadmap: `roadmaps/delivered_multi_host_adapter_and_claude_plugin_roadmap.md`
Roadmap slug: `multi-host-adapter-and-claude-plugin`
State file: `automation/multi-host-adapter-and-claude-plugin/delivery_state.json`
Delivery log: `automation/multi-host-adapter-and-claude-plugin/delivery_log.md`
Review directory: `automation/multi-host-adapter-and-claude-plugin/reviews`
Policy file: `automation/multi-host-adapter-and-claude-plugin/phase_model_policy.json`
Codex automation: `multi-host-adapter-and-claude-plugin`
Cadence: hourly
Model: `gpt-5.5`
Reasoning effort: `xhigh`
Execution environment: local

## Operating Policy

- Deliver exactly one roadmap phase at a time.
- Read the roadmap, state file, delivery log, review/fix state, phase model
  policy, latest reviews, automation config, branch, and worktree status before
  editing.
- Preserve unrelated user changes.
- Use `codex/multi-host-adapter-and-claude-plugin-phase-<n>` branches for
  implementation phases.
- Run every verification command or manual verification required by the current
  phase before claiming delivery.
- Require a fresh review verdict of `delivered` before advancing state.
- Stop after 3 review/fix iterations if the phase remains unresolved.
- If state is `blocked`, enter Blocker Remediation Mode before attempting
  normal phase delivery.
- Do not push, promote to `main`, merge, delete branches, install/sync the
  global Codex skill, publish packages, use credentials, or run destructive
  commands without explicit human approval.
- Keep this automation configured as `gpt-5.5` with `xhigh` reasoning unless a
  later delivered phase changes the model policy and retarget flow.

## Next Run Prompt

Run the next safe phase-gated delivery step for
`roadmaps/delivered_multi_host_adapter_and_claude_plugin_roadmap.md`.

Use the installed `roadmap-delivery-skill` and read these files before acting:

- `automation/multi-host-adapter-and-claude-plugin/automation_guide.md`
- `automation/codex_phase_gated_delivery_automation_template.md`
- `automation/multi-host-adapter-and-claude-plugin/delivery_state.json`
- `automation/multi-host-adapter-and-claude-plugin/delivery_log.md`
- `automation/multi-host-adapter-and-claude-plugin/review_fix_state.json`
- `automation/multi-host-adapter-and-claude-plugin/phase_model_policy.json`

Operate on exactly one current phase at a time. Reconcile roadmap, state, log,
review files, phase model policy, git branch, worktree status, and saved
automation configuration before editing. If they disagree, record the blocker
in state, log, and review, then stop.

If `delivery_state.json` has `status: blocked`, do not try to advance the
phase first. Enter Blocker Remediation Mode: classify the blocker as
local-repairable, automation-config repairable, permission-gated,
external-decision, or destructive-risk. If the blocker is local-repairable or
automation-config repairable and the operator has already authorized the needed
surface, fix the blocker first, rerun reconciliation and validation, clear
`blocked_reason`, record the repair in state/log, and only then start or resume
the current phase. If credentials, a product decision, destructive git,
publication, promotion, installed-skill synchronization, or unapproved config
changes are required, keep state blocked and ask for the missing human action.

Hard stop before delivery if `all_phases_complete` is true, state is
`completed`, or state is `completed_pending_pause`. In that case, confirm the
automation is paused or request pause permission, write any missing completion
alert, and do not start phase work.

For the current phase only:

- extract objective, owned files, implementation steps, acceptance criteria,
  required verification, non-goals, and stop conditions
- create or reuse the correct
  `codex/multi-host-adapter-and-claude-plugin-phase-<n>` branch when
  implementation work is required
- read `phase_model_policy.json`, resolve the current phase's required model
  and reasoning, and verify the saved automation config matches before delivery
- make only phase-scoped changes
- run required verification and targeted checks
- update `automation/multi-host-adapter-and-claude-plugin/delivery_log.md` and
  `automation/multi-host-adapter-and-claude-plugin/delivery_state.json`
- perform a skeptical review from fresh context where available
- write review output under `automation/multi-host-adapter-and-claude-plugin/reviews/`
- if the verdict is `needs-fix`, fix only current-phase findings and rerun
  verification
- stop after 3 review/fix iterations and mark blocked if still not delivered

Do not advance unless acceptance criteria are satisfied, verification passed,
review verdict is `delivered`, and roadmap/state/log agree. After advancing
state to the next phase, stop. Do not push, merge, promote to `main`, delete
branches, edit app automation config, install/sync the global Codex skill, or
run destructive commands without explicit human approval.
