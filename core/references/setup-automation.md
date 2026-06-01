# Setup Automation Reference

Use this reference when creating a file-backed roadmap delivery automation.
The goal is a conservative, inspectable workflow that starts inactive unless
the operator explicitly asks for scheduled delivery.

## Core Contract

An automation is suitable only when the roadmap is decomposed into phases with
owned files, non-goals, acceptance criteria, required verification, and stop
conditions. The repository must tolerate local branch work, and publication,
promotion, destructive operations, credentials, and product decisions must stay
operator-approved.

Create durable artifacts under the repository automation directory:

```text
automation/<roadmap-slug>/
  automation_guide.md
  approval_policy.json
  delivery_state.json
  delivery_log.md
  review_fix_state.json
  review_fix_log.md
  phase_model_policy.json
  automation_run_log.jsonl
  alerts/
  reviews/
```

Record the same roadmap path and slug in the roadmap header, state, delivery
log, review state, automation guide, and saved runner prompt. If a lifecycle
rename changes the roadmap filename, repair all durable references before
delivery continues.

If the operator manually activates a runner that setup originally recorded as
paused, the next run must reconcile the durable artifacts instead of treating
ACTIVE as a permanent setup failure. Accept ACTIVE only when readback proves the
model/reasoning, prompt, cwd, and safety guards still match, then update
guide/log/state to ACTIVE and record the activation.

## Required Initial Artifacts

The initial state must identify the roadmap, slug, current phase, phase branch
when known, status, review iteration counters, model policy fields, verification
evidence, latest review evidence, blocker fields, run/stall counters, and
updated timestamp. It must also record the approval policy path, active
approval mode, and last approval-policy readback.

The approval policy must start as `conservative` unless the operator explicitly
selects `delegated_local`, `delegated_delivery`, or `custom`. A missing approval
policy keeps legacy conservative behavior. An invalid approval policy must fail
validation before delivery relies on pre-approval. Custom policy must provide an
operation allow/deny map, with missing operations treated as denied.

The initial delivery log must describe the roadmap, state path, review path,
operating policy, configured runner, and next action. The log is append-only
after delivery starts.

The phase model policy must define default model and reasoning requirements,
optional phase overrides, finalization requirements, stall threshold, and alert
mode. Configured runner model and reasoning values may be written to state only
after readback proves them.

## Prompt Requirements

The saved runner prompt must require the agent to:

- read the roadmap, state, log, review state, policy, latest reviews, runner
  configuration, branch, and worktree status before editing
- read and validate approval policy before relying on pre-approved operations
- use conservative legacy behavior when approval policy is missing
- stop before delivery when approval policy is invalid
- operate on exactly one current phase
- enter blocked remediation before retrying delivery when state is blocked
- hard-stop on completed or completed-pending-pause state
- verify model and reasoning against policy before phase-owned edits
- preserve unrelated worktree changes
- run required verification
- write a fresh review artifact before phase advancement
- avoid publication, promotion, destructive git, credentials, and unapproved
  runner configuration changes

## Host Adapter Boundary

The core controls file-backed state, policy, logs, review artifacts, and safety
gates. Host adapters own how a scheduled runner is created, paused, activated,
or read back, and how model and reasoning settings are configured in that
runner.
