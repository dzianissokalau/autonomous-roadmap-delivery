# Setup Automation Reference

Use this reference when creating a new file-backed roadmap delivery automation.
The goal is a conservative, inspectable workflow that starts paused unless the
human operator explicitly asks for activation.

## Suitability Checklist

Use autonomous phase-gated delivery only when all of these are true:

- The roadmap is already decomposed into clear phases.
- Each phase has owned files, non-goals, acceptance criteria, verification, and
  stop conditions.
- The repository can tolerate local branch work without hidden publication.
- Durable artifacts can live in the repository under `automation/<slug>/`.
- Human approval remains required for publication, promotion, destructive
  operations, credentials, and ambiguous product decisions.

Do not set it up for broad project management, open-ended refactors, release
automation, or workflows where the model must infer phase scope.

## Roadmap Slug And Path

Pick a short lowercase slug from the roadmap title:

```text
ROADMAP_PATH=roadmaps/<roadmap-file>.md
ROADMAP_SLUG=<short-lowercase-slug>
AUTOMATION_DIR=automation/<roadmap-slug>
```

Record the exact path in the roadmap header, state JSON, delivery log, and
automation prompt. If the roadmap becomes active or advances to Phase 1+, it
must not keep a `not_started_` filename. If the roadmap filename changes during
a lifecycle rename, stop and repair every durable reference before doing
delivery work.

## Artifact Layout

Create this repository-local layout:

```text
automation/<roadmap-slug>/
  automation_guide.md
  delivery_state.json
  delivery_log.md
  review_fix_state.json
  review_fix_log.md
  phase_model_policy.json
  automation_run_log.jsonl
  alerts/
  reviews/
```

Keep app automation config outside the repository unless the user explicitly
asks to edit it. Keep the automation `cwd` rooted at the repository root.

## Initial State JSON

Start with this shape and fill in concrete values:

```json
{
  "roadmap": "roadmaps/<roadmap-file>.md",
  "roadmap_slug": "<roadmap-slug>",
  "current_phase": "Phase 0 - Scope Confirmation",
  "branch": null,
  "status": "not_started",
  "review_iterations": 0,
  "max_review_iterations": 3,
  "last_verification": null,
  "last_review": null,
  "last_delivered_phase": null,
  "blocked_reason": null,
  "required_model": null,
  "required_reasoning_effort": null,
  "configured_automation_model": null,
  "configured_automation_reasoning_effort": null,
  "run_count": 0,
  "stalled_run_count": 0,
  "max_stalled_runs": 3,
  "last_progress_signature": null,
  "last_progress_at": null,
  "last_operator_alert": null,
  "auto_advance_after_delivered_review": true,
  "push_to_github": false,
  "updated_at": null
}
```

Use ISO-8601 UTC timestamps for `updated_at` and verification/review times.

## Initial Delivery Log

Start the log with:

```markdown
# <Roadmap Name> Delivery Log

Status: Active
Roadmap: `roadmaps/<roadmap-file>.md`
State file: `automation/<roadmap-slug>/delivery_state.json`
Review directory: `automation/<roadmap-slug>/reviews`

## Operating Policy

- Deliver one phase at a time.
- Run required verification before claiming a phase is delivered.
- Require a fresh review verdict before phase advancement.
- Preserve unrelated worktree changes.
- Keep all publication and promotion human-approved.
```

Append entries only. Do not rewrite history except to fix malformed setup
before delivery starts.

## Automation Prompt Skeleton

Use concrete paths before saving:

```text
Run the next safe step for `ROADMAP_PATH` using the phase-gated workflow in
`automation/`.

Read these first:
- `automation/<roadmap-slug>/automation_guide.md`
- `automation/codex_phase_gated_delivery_automation_template.md`
- `automation/<roadmap-slug>/delivery_state.json`
- `automation/<roadmap-slug>/delivery_log.md`
- `automation/<roadmap-slug>/review_fix_state.json` when present
- `automation/<roadmap-slug>/phase_model_policy.json` when present

Operate on exactly one current phase at a time. Reconcile roadmap, state, log,
review files, git branch, and working tree before editing. If they disagree,
record the blocker in state/log/review and stop.

If state is `blocked`, enter Blocked Remediation Mode before normal delivery:
classify the blocker, repair local or already-authorized automation-config
blockers, rerun validation, clear `blocked_reason` only when the repair is
verified, and then resume the current phase. If the blocker needs credentials,
approval, a product decision, or destructive git, keep state blocked and ask for
the missing human action.

For the current phase only:
- extract objective, owned files, implementation steps, acceptance criteria,
  required verification, non-goals, and stop conditions
- create or reuse `codex/<roadmap-slug>-phase-<n>` when implementation work is
  required
- preserve unrelated user changes
- read `phase_model_policy.json` when present and verify the configured model
  and reasoning match the current phase policy before implementation
- make only phase-scoped changes
- run required verification and targeted checks
- update `automation/<roadmap-slug>/delivery_log.md` and
  `automation/<roadmap-slug>/delivery_state.json`
- perform a skeptical review from fresh context where available
- write review output under `automation/<roadmap-slug>/reviews/`
- if the verdict is `needs-fix`, fix only in current phase scope and rerun
  verification
- stop after 3 review/fix iterations and mark blocked if still not delivered

Do not advance unless acceptance criteria are satisfied, verification passed,
review verdict is `delivered`, and roadmap/state/log are updated.

After advancing state to the next phase, stop. Do not publish, promote to
`main`, edit app automation config, or run destructive git operations without
explicit human approval.
```

## Cadence And Model

- Use cron for detached repository automation.
- Use a heartbeat/manual run while designing or repairing the workflow.
- Default detached cadence: hourly.
- Default model: the strongest available coding model for the operator.
- Default reasoning: high or extra high for delivery, medium for status-only
  inspection when no edits are expected.

## PAUSED By Default

Create new automations in `PAUSED` status unless the user explicitly requests
activation. If the app saves an automation as active despite a paused request,
record the drift, pause it if authorized, and do not start delivery until the
readback is correct.

## Readback Checklist

After creation or update, inspect the saved config:

- `id` matches the intended automation id.
- `status` is `PAUSED` unless explicit activation was requested.
- `cwd` is the repository root.
- prompt references the current roadmap path.
- prompt references the current automation artifact directory.
- cadence matches the requested schedule.
- no broad writable roots or global state edits were introduced.

## Operational Setup Checklist

Use this checklist when the operator asks to set up a new roadmap delivery
automation from a roadmap path. Keep the work repository-local until the
operator explicitly approves saving or activating an app automation.

### Inputs To Confirm

- `REPO_ROOT`: absolute path to the repository that owns the roadmap.
- `ROADMAP_PATH`: repository-relative path to the phased roadmap.
- `ROADMAP_SLUG`: short lowercase slug used under `automation/<slug>/`.
- `AUTOMATION_ID`: stable Codex automation id, usually derived from the slug.
- `BRANCH_PREFIX`: normally `codex/`.
- `MAX_REVIEW_ITERATIONS`: normally `3`.

Stop before creating anything if the roadmap does not define phases, owned
files, acceptance criteria, required verification, non-goals, and stop
conditions.

### Repository Artifacts To Create

Create or verify exactly these repository-local artifacts:

```text
automation/<roadmap-slug>/
  automation_guide.md
  delivery_state.json
  delivery_log.md
  review_fix_state.json
  review_fix_log.md
  phase_model_policy.json
  automation_run_log.jsonl
  alerts/
  reviews/
```

The initial state must point at the current roadmap path, start on the first
phase, set `status` to `not_started`, set `review_iterations` to `0`, set
`max_review_iterations`, and leave `blocked_reason` null.

When model policy is enabled, create `phase_model_policy.json` with defaults,
per-phase overrides if known, `max_stalled_runs`, and a notification fallback.
Mirror the current required/configured model and reasoning fields in state.

The initial delivery log must record the roadmap path, state file, review
directory, operating policy, branch naming model, and publication guard. The
review directory should contain only a placeholder such as `.gitkeep` until the
first review is written.

### Paused Automation Proposal

Prepare a concrete automation proposal before saving anything in the Codex app:

```text
id=<automation-id>
kind=cron
status=PAUSED
rrule=FREQ=HOURLY;INTERVAL=1
execution_environment=worktree
cwd=<repo-root>
model=<approved model>
reasoning_effort=high or xhigh
```

The prompt must include the current `ROADMAP_PATH`, the required files to read
first, one-phase-at-a-time delivery rules, review/fix iteration limits,
Blocked Remediation Mode, phase-model-policy validation when present, the
no-push/no-main-promotion guard, and installed-skill permission handling when
relevant.

Do not activate the automation as part of setup unless the operator explicitly
asks for activation after validation.

### Setup Readback Checklist

After saving or updating an automation, read back the saved `automation.toml`
or connector response and confirm:

- `id` is the intended `AUTOMATION_ID`.
- `status = "PAUSED"` unless the operator explicitly requested activation.
- `cwd` is exactly `REPO_ROOT`.
- the prompt references the current `ROADMAP_PATH`.
- the prompt references `automation/<roadmap-slug>/automation_guide.md`.
- the prompt references `delivery_state.json` and `delivery_log.md`.
- the prompt keeps work to one current phase and stops after phase advancement.
- no broad writable roots, global state patches, pushes, main promotion, or
  destructive git operations were introduced.

If readback shows `ACTIVE` when `PAUSED` was requested, do not start delivery.
Pause it only with explicit approval or an already-approved setup flow; then
read back again. If pausing cannot be performed, record the drift in state/log
and stop.

### Activation Gate

Activation is a separate operator decision. Before activating:

- the operator must explicitly request activation in the current conversation.
- `validate_delivery_artifacts.py` must report no `errors` for the roadmap.
- state must not say all phases are complete.
- state must not be blocked unless the blocker has been fixed and recorded.
- roadmap, state, log, review directory, branch, and automation prompt paths
  must agree.

If any activation gate fails, refuse activation, report the blocking evidence,
and leave the automation paused or unchanged.

### Operator Summary

After setup or repair, report the exact paths created or changed:

- roadmap path
- automation artifact directory
- state file
- delivery log
- review directory
- automation id
- automation status after readback
- cwd after readback
- prompt roadmap references after readback
