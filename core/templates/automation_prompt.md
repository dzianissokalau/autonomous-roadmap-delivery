# Automation Prompt Template

Use concrete paths before saving a runner prompt.

```text
Run the next safe phase-gated delivery step for `ROADMAP_PATH`.

Read these files before acting:
- `automation/<roadmap-slug>/automation_guide.md`
- `automation/codex_phase_gated_delivery_automation_template.md`
- `automation/<roadmap-slug>/delivery_state.json`
- `automation/<roadmap-slug>/delivery_log.md`
- `automation/<roadmap-slug>/review_fix_state.json`
- `automation/<roadmap-slug>/phase_model_policy.json`

Operate on exactly one current phase at a time. Reconcile roadmap, state, log,
review files, phase model policy, branch, worktree status, and saved runner
configuration before editing.

If state is blocked, enter Blocked Remediation Mode before normal delivery.
Hard stop before delivery if all phases are complete, status is completed, or
status is completed_pending_pause.

For the current phase only, extract objective, owned files, implementation
steps, acceptance criteria, required verification, non-goals, and stop
conditions. Create or reuse the correct phase branch when implementation work
is required. Verify saved runner model and reasoning against policy before
delivery. Make only phase-scoped changes, run required verification, update
state/log, write a fresh review, and advance only after the review verdict is
delivered.

Do not push, merge, promote, delete branches, edit runner configuration, install
global packages, or run destructive commands without explicit human approval.
After advancing state to the next phase, stop.
```
