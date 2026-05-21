# Troubleshooting Reference

Use this reference when roadmap, state, log, automation config, branch, or
verification evidence disagree.

## Automation Saved ACTIVE Despite Requested PAUSED

Read back the saved automation config. If it is active and the setup contract
required paused:

- record the drift in state/log
- pause only if the user approves or the setup flow explicitly authorized it
- rerun readback
- do not begin delivery until status matches the contract or the operator
  accepts the active state

## Status-Only Automation Update Rejected

Record:

- attempted update
- app/tool error
- current saved status
- safest manual next step

Do not edit unrelated automation fields to sneak in a status change.

## Stale Roadmap Path After Lifecycle Rename

Symptoms:

- roadmap moved from draft/in-progress to delivered filename
- state still points to old path
- automation prompt still references old path

Repair only after confirming the intended current roadmap file. Update state,
guide, log, and automation prompt references together, then rerun validation or
status inspection. If app automation edits require approval, stop and ask.

## Completed State But Automation Still ACTIVE

If state says the roadmap is complete and the automation is active:

- do not start a new phase
- record a hard-stop warning
- ask whether to pause the automation
- preserve final verification evidence

## User Confusion Between Roadmaps

When a request names a roadmap vaguely:

- list candidate roadmap paths and automation ids
- identify current phase/status for each
- ask only if local evidence cannot disambiguate safely

Do not operate on the most recent roadmap merely because it appears first.

## Review Finds Medium Gaps After Delivery

If gaps are valid and in current phase scope, set status to `fixing`, patch
only that scope, rerun verification, and write a new review. If gaps belong to
a future phase, record residual risk and keep the current verdict grounded in
the current acceptance criteria.

## Dirty Worktree With Unrelated Files

Use path-specific diffs to separate owned files from unrelated work. Continue
only if unrelated changes do not affect phase verification. Never clean or
restore unrelated files without explicit instruction.

## Branch Exists With Unexpected Base

Stop when a phase branch exists but its base or contents are unexplained.
Record:

- expected branch name
- current branch
- relevant commit summary
- dirty files
- needed human decision

Do not recreate, delete, or rewrite the branch unless explicitly approved.

## Verification Cannot Run

Classify the failure:

- missing dependency
- sandbox permission
- network restriction
- command missing
- phase implementation failure
- ambiguous expected result

Retry with the narrowest approved escalation only when the workflow permits it.
If verification still cannot run, mark blocked with the exact command and
reason.

## Roadmap/State Current Phase Mismatch

If roadmap and state disagree:

- inspect delivery log for the last phase advancement
- inspect latest review verdict
- inspect branch and dirty files
- prefer the last fully recorded phase gate
- if still ambiguous, record blocker and stop

Never advance based only on one surface.

## Artifact Validator Reports Errors

Run the validator before delivering when the durable surfaces may disagree:

```bash
python3 $CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/validate_delivery_artifacts.py \
  --repo-root /path/to/repo \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --json
```

Treat `errors` as blockers. Record the exact code and message in state/log, then
stop unless the current phase explicitly owns the repair. Common blocking codes:

- `missing_state_file` or `invalid_state_json`: state cannot be trusted.
- `missing_delivery_log` or `missing_review_dir`: phase history is incomplete.
- `missing_roadmap_file`: state points at a roadmap that cannot be read.
- `current_phase_mismatch`: roadmap and state select different active phases.
- `completed_state_active_automation`: completed state would keep running
  without a hard-stop guard.
- `invalid_review_verdict`: review evidence cannot support phase advancement.

Treat `warnings` as explicit reconciliation work, not automatic failure. Stale
automation roadmap paths, missing hard-stop guard text, missing deep-review
prompt paths in older completed automations, branch mismatch, and dirty worktree
warnings should be explained in the delivery log before continuing.

Do not use the validator to auto-repair artifacts. Repairs still follow the
phase-gated workflow and require current-phase scope or explicit operator
approval.

## Phase-Gated Repair Procedure

Use this procedure when repair is explicitly requested or when the current
phase owns the affected artifacts.

1. Read roadmap, delivery state, delivery log, review/fix state, latest review
   file, automation config, branch, and worktree status.
2. Run `validate_delivery_artifacts.py` when available.
3. Classify each issue as blocking `error`, non-blocking `warning`, or
   unrelated user work.
4. Repair only artifacts in current-phase scope unless the operator explicitly
   approves a broader repair.
5. Rerun validation and targeted readback.
6. Record the repair, verification, residual risks, and next action in
   state/log/review.

Do not use repair as a shortcut around the normal phase gate.

## Stale Prompt Path Repair

Repair stale roadmap prompt references only after confirming the current
roadmap path from durable state and the actual roadmap file.

- Update the automation prompt reference to the current `ROADMAP_PATH`.
- Keep the automation artifact directory unchanged unless the slug changed.
- Update state/log/guide references together when repository artifacts are
  stale.
- Read back the saved automation config after any app-level update.
- Rerun `validate_delivery_artifacts.py`.

If the app update is rejected or requires approval that is not available,
record the exact stale path, current path, and safest manual next step.

## Activation Refusal Rules

Refuse activation when any of these are true:

- artifact validation reports one or more `errors`.
- state says all phases are complete.
- state status is `blocked` and the blocker has not been fixed.
- roadmap and state disagree on the current phase.
- automation prompt still points at a stale roadmap path.
- direct config edits would be required without explicit approval.

Report the exact validation code or file mismatch that caused the refusal.

## Pause Rules

Pause, or ask for approval to pause, in these cases:

- all phases are complete and final evidence has been recorded.
- the run is blocked by product decision, credentials, or verification
  environment.
- max review iterations have been reached.
- completed state is detected while automation remains active.

When pause approval is unavailable, record that the automation should be
paused and stop without starting new delivery work.

## Known Failure Mode Coverage

The troubleshooting surface must cover these known modes:

- automation saved `ACTIVE` despite a requested `PAUSED` setup.
- status-only automation update rejected.
- stale roadmap path after lifecycle rename.
- completed state but automation still `ACTIVE`.
- user confusion between similarly named roadmaps.
- review finds medium gaps after delivery.
- dirty worktree with unrelated files.
- branch exists with unexpected base.
- verification cannot run.
- roadmap/state current phase mismatch.
- repository layout mismatch between `roadmaps/automation/<slug>` and
  `automation/<slug>`.
- artifact validator reports blocking errors.
- activation requested while validation errors remain.

## Repository Layout Mismatch

Some roadmap repositories store automation artifacts under
`roadmaps/automation/<slug>/`, while newer roadmap-delivery workspaces may use
`automation/<slug>/` at the repository root.

When status inspection reports a missing state file:

- check both candidate layouts before treating the state as missing
- prefer the state file that exists and matches the requested `roadmap_slug`
- record a warning only when neither layout exists or the found state disagrees
  with the requested slug
- add a fixture test when a new repository layout is observed

Do not move existing automation artifacts just to normalize layout. Layout
repair is only safe when the roadmap explicitly owns that migration or the
operator approves it.
