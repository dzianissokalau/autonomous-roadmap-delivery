# State, Log, And Branches Reference

Use this reference for status inspection and for reconciling roadmap delivery
surfaces before work.

## Core Contract

The roadmap, delivery state, delivery log, review/fix state, review artifacts,
phase model policy, branch, and worktree status are the durable control plane.
Do not advance a phase when these surfaces disagree unless the mismatch is
current-phase scoped and locally repairable.

## Delivery State

State must record:

- roadmap path and slug
- current phase and branch
- status
- review iteration counters
- latest verification and review evidence
- last delivered phase
- blocker and blocker repair evidence
- manual activation evidence when setup PAUSED is reconciled to ACTIVE
- required and configured model/reasoning values
- run/stall counters and progress signature
- operator alert evidence
- updated timestamp

Status values are `not_started`, `delivering`, `verifying`, `reviewing`,
`fixing`, `delivered`, and `blocked`. Blocked is a remediation state, not a
retry loop.

When a blocked run becomes repairable, record the repair in
`last_blocker_repair`, clear `blocked_reason` only after validation/readback
passes, and return the current phase to `not_started`, `delivering`, or
`fixing` as appropriate. A previous blocked review is historical evidence; it
does not prevent delivery when a later repair is recorded and reconciliation
passes.

When a manually activated runner resolves a setup PAUSED/ACTIVE mismatch, also
record `last_activation` with the accepted readback, source of acceptance, and
timestamp. The delivery log and automation guide must then agree that the
runner is ACTIVE before phase work resumes.

## Delivery Log

The log is append-only after delivery starts. Each phase entry records status,
branch, scope, changed files, verification commands and results, review file
and verdict, residual risks, and next action.

## Review Directory

Review artifacts live under:

```text
automation/<roadmap-slug>/reviews/
```

Names follow:

```text
<roadmap-slug>-phase-<n>-review-iteration-<m>.md
```

The latest review verdict must agree with state before phase advancement.

## Branches And Worktree

Implementation phases use a dedicated phase branch. The branch prefix is a
workflow setting supplied by the host adapter or project convention.

Dirty worktree entries are acceptable only when they are unrelated to current
phase-owned files and do not make verification unreliable. Never clean, stash,
restore, or rewrite unrelated work without operator approval.

## Progress And Stall Tracking

Progress signatures should include current phase, status, last delivered phase,
review iteration count, latest verification, latest review, git head, delivery
log hash/size, and blocker reason. If the signature changes, reset the stall
counter. If it repeats, increment the stall counter. When the configured
threshold is reached, keep or set blocked state and write an operator alert.

## Host Adapter Boundary

The core defines durable fields and reconciliation rules. Host adapters provide
concrete branch naming defaults, runner config readback, and status inspection
commands for their environment.
