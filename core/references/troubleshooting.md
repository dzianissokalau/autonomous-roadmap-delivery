# Troubleshooting Reference

Use this reference when roadmap, state, log, review, policy, branch, worktree,
runner config, or verification evidence disagree.

## Core Contract

Classify the issue before retrying delivery. Repair only local current-phase
bookkeeping, stale paths, missing generated artifacts, branch drift, malformed
state/log entries, or already-approved runner configuration changes. Keep state
blocked and ask for human action when the repair needs credentials, product
input, destructive git, broad publication, promotion, or unapproved runner
configuration changes.

## Common Blockers

- Missing or invalid state JSON.
- Missing delivery log or review directory.
- State roadmap path does not exist.
- Roadmap current phase and state current phase disagree.
- Latest review verdict is invalid or does not match state.
- Required model/reasoning and configured runner values mismatch.
- Automation prompt references a stale roadmap path.
- Completed state would keep running without a hard-stop guard.
- Dirty worktree includes unexplained current-phase owned files.
- Branch exists with unexpected base or unexplained changes.
- Required verification cannot run.

## Warning Handling

Warnings are reconciliation work, not automatic failure. Explain branch mismatch,
dirty worktree, lifecycle filename drift, missing optional prompt paths, or
legacy artifact compatibility in the log before continuing. Treat warnings as
blockers only when they affect current-phase correctness or verification.

## Blocked Run Remediation

On a blocked run:

1. Read the blocked reason, failed verification, latest review findings, and
   runner readback.
2. Classify the blocker.
3. Repair only local or already-authorized runner configuration blockers.
4. Rerun validation/readback.
5. Record `last_blocker_repair`, clear `blocked_reason`, and reset stall
   counters only after repair evidence passes.
6. Resume the current phase only after reconciliation is clean.

Do not write another blocked review for the same issue until remediation
classification has been attempted.

## Completed-State Issues

If completed state is detected, do not start phase work. Confirm completed alert
evidence, confirm pause status or record pause-required action, and preserve the
final verification record.

## Host Adapter Boundary

The core defines classifications and repair rules. Host adapters own concrete
runner edits, credential surfaces, external notifications, and publication
mechanisms.
