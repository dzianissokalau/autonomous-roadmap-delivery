# Phase Loop Reference

Use this reference to deliver exactly one current roadmap phase.

## Core Contract

Before editing, reconcile the roadmap, delivery state, delivery log, review/fix
state, phase model policy, latest review artifact, saved runner config, branch,
and worktree status. Stop and record a blocker when the current phase, roadmap
path, branch, latest verdict, model policy, verification evidence, or runner
readback disagree in a way that cannot be locally repaired.

When a phase model policy exists, resolve the current phase's required model
and reasoning before extracting the phase contract. Compare those values with
the configured runner values from readback. A mismatch is a stop-before-delivery
condition unless the operator already approved the runner configuration repair.

## Blocked Remediation Gate

If state is `blocked`, classify the blocker before attempting normal delivery:

- `local-repairable`: stale paths, missing bookkeeping, branch drift, dirty
  current-phase files, or malformed state/log entries
- `automation-config`: saved prompt, cwd, status, execution environment, model,
  or reasoning configuration needs an approved repair
- `permission-gated`: sandbox, network, filesystem, or credential access is
  missing
- `external-decision`: product, policy, or scope input is missing
- `destructive-risk`: repair would overwrite user work or rewrite history

Repair only local or already-approved runner configuration blockers. Rerun
reconciliation after repair, clear `blocked_reason` only after validation
passes, then resume the current phase.

When the only blocker is saved runner ACTIVE versus setup artifacts that still
say PAUSED, treat a clear operator/manual activation as an already-approved
runner status decision if model/reasoning, prompt path, cwd, hard-stop guard,
and blocked-remediation guard all read back cleanly. Reconcile durable
guide/log/state to ACTIVE, record `last_activation` and `last_blocker_repair`,
clear `blocked_reason` after validation, and continue the current phase instead
of looping on the same blocker.

## Phase Contract

Extract only the current phase:

- objective
- owned files
- inputs
- implementation steps
- acceptance criteria
- required verification
- non-goals
- stop conditions

Future-phase ideas belong in residual risks or backlog notes, not in the
implementation.

## Delivery Rules

Change only phase-owned files and required automation bookkeeping. Preserve
unrelated dirty files. Use a dedicated phase branch for implementation phases.
If an existing branch has an unexpected base or unexplained content, record a
blocker instead of rewriting it.

Run every verification command named by the phase, then any targeted checks
directly tied to changed behavior. If a required command cannot run, record the
command, exit status or reason, classification, and next action.

## Review And Advancement

Write a fresh review artifact before advancing. Advance only when acceptance
criteria are met, required verification passed after the final change, the
fresh review verdict is `delivered`, and roadmap/state/log/review evidence
agree. Stop immediately after advancing state to the next phase.

When the delivered phase is the final numbered phase, stop the normal phase
loop and enter finalization. Load the finalization and promotion reference,
prepare or verify the final deep-review prompt/artifact, and do not set
`all_phases_complete` or completed-pending-pause state from the phase-loop
path.

## Host Adapter Boundary

The core defines gates and durable evidence. Host adapters choose the concrete
branch prefix, runner readback mechanism, and any host-specific review
delegation tooling.
