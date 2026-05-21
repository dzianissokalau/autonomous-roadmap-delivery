# Phase Loop Reference

Use this reference to deliver exactly one current roadmap phase.

## Reconcile First

Before editing, read:

- roadmap file
- `automation/<slug>/delivery_state.json`
- `automation/<slug>/delivery_log.md`
- `automation/<slug>/review_fix_state.json` when present
- `automation/<slug>/phase_model_policy.json` when present
- latest review files under `automation/<slug>/reviews/`
- saved automation config when available
- `git branch --show-current`
- `git status --short --branch`

Stop if the current phase, roadmap path, branch, status, review verdicts,
verification evidence, or automation config disagree. Record the mismatch in
state/log/review instead of guessing.

This reconciliation is the start-run gate. When `phase_model_policy.json`
exists, validate the current phase's required model and reasoning effort
before extracting the phase contract or changing phase-owned files.

## Blocked Remediation Gate

If `delivery_state.json` has `status: blocked`, do not immediately retry
normal phase delivery and do not blindly write another blocked review.

First classify the blocker:

- `local-repairable`: stale paths, missing generated bookkeeping, branch drift,
  dirty current-phase files, or malformed state/log entries that the current
  roadmap or operator already allows repairing.
- `automation-config`: saved automation prompt, cwd, status, execution
  environment, model, or reasoning configuration needs a permitted update.
- `permission-gated`: sandbox escalation, network, credentials, or filesystem
  access is required.
- `external-decision`: product, policy, or scope decision is missing.
- `destructive-risk`: repair would require reset, force push, branch deletion,
  or overwriting user work.

For `local-repairable` or already-authorized `automation-config` blockers,
repair the blocker first, rerun reconciliation and artifact validation, record
the repair in state/log, clear `blocked_reason`, reset stalled counters when
progress is real, and only then resume the current phase.

For `permission-gated`, `external-decision`, or `destructive-risk` blockers,
keep state blocked, record the missing human action, and stop. Do not count a
successful blocker repair as a delivered phase.

## Model Policy Gate

When `phase_model_policy.json` exists:

1. Read delivery state and resolve the current phase number.
2. Read the policy defaults and the current phase override; if the phase has no
   override, use policy defaults.
3. Read the saved automation config from
   `~/.codex/automations/<automation-id>/automation.toml`, or read an explicit
   CLI/profile runner config for manual runs.
4. Compare required versus configured model and reasoning values before
   implementation.
5. If they match, continue to phase extraction.
6. If they mismatch, do not edit phase-owned files. Update state/log/review
   with the required and configured values, retarget only when that automation
   surface is already approved, then stop so the next run starts on the right
   model.
7. If the configured model or reasoning effort cannot be proven and the roadmap
   is model-strict, stop for operator confirmation rather than guessing.

For manual CLI runs, relaunch with explicit model and reasoning settings, for
example:

```bash
codex exec -m <required-model> \
  -c 'model_reasoning_effort="<required-reasoning-effort>"' \
  -C <repo-root> \
  "<phase-gated prompt>"
```

or use a profile that sets both values:

```bash
codex exec -p <profile-name> -C <repo-root> "<phase-gated prompt>"
```

For Codex app automations, the saved config must read back with matching
`model` and `reasoning_effort` values. If an approved retarget changes those
fields, stop immediately after readback; do not continue delivery in the same
run.

## Extract The Phase Contract

From the current phase only, extract:

- objective
- owned files
- inputs
- implementation steps
- acceptance criteria
- required verification
- non-goals
- stop conditions

Treat this extraction as the working contract. Future-phase ideas belong in
residual risks or backlog notes, not in the implementation.

## Scope Rules

- Change only owned files and required automation bookkeeping.
- Preserve unrelated dirty files.
- Do not revert user work without explicit instruction.
- Do not hide unrelated changes inside delivery commits.
- Do not create helper scripts unless the phase owns them.
- Do not mutate live external services unless the phase explicitly says to and
  approval is available.
- Do not implement future-phase findings during the current phase; record them
  as residual risks or backlog notes.

## Branch Rules

Implementation phases use:

```text
codex/<roadmap-slug>-phase-<n>
```

If the branch already exists, reuse it after checking that its current state is
consistent with state/log/reviews. If it exists with an unexpected base or
unexplained changes, stop and record a blocker. Read-only phases may stay on
the current branch if the roadmap allows it.

## Dirty Worktree Handling

Use:

```bash
git status --short --branch
git diff -- <owned-file>
```

Ignore unrelated dirty files unless they conflict with owned files or make
verification unreliable. Never clean, stash, or restore unrelated files unless
the user explicitly asks.

## Verification Selection

Run every command named in the phase. Add targeted checks only when they are
directly tied to changed behavior. If a required command cannot run, record:

- command
- exit status or reason it could not run
- whether the issue is environmental, permission-related, or a phase bug
- next action

Do not claim delivery when verification only checked pre-existing behavior.

## Review Gate

After implementation and verification, write a fresh review file before
advancing the phase. Treat the review as a gate:

- `delivered`: advance only after state, log, roadmap, verification evidence,
  and branch all agree.
- `needs-fix`: do not advance; enter the fix loop, fix only valid current-phase
  findings, rerun verification, and write a new review iteration.
- `blocked`: do not advance; record the blocker in state, log, and review.

When review happens in the same context as delivery, record that limitation in
the review and residual risks. A same-context review may still deliver a phase
only when the acceptance criteria are directly evidenced, verification passed,
and the limitation is explicit.

## Fix Loop

For each review finding, record the disposition:

| Finding disposition | Action |
| --- | --- |
| Valid and current-phase scoped | Fix it, rerun required verification, update the log, then write a new review iteration. |
| Valid but future phase | Do not implement it now; record it as residual risk or backlog. |
| Invalid | Explain why it does not apply, with file or command evidence when possible. |
| Blocked | Stop, update state/log/review, and ask for the missing decision, permission, or input. |

`needs-fix` is not advisory text. It means the phase gate is closed until the
fixes are made, verification is rerun, and a later review verdict is
`delivered`.

## Max Iterations

Default maximum is 3 review/fix iterations. If the phase is still not
`delivered` after the maximum:

1. Set `delivery_state.json` status to `blocked`.
2. Set `review_fix_state.json` status to `blocked` when present.
3. Record unresolved findings and commands that did not pass.
4. Stop without starting the next phase.

## Delivery Log Entry

Use this shape:

```markdown
## Phase N - YYYY-MM-DD - Delivery Pass M

Status: delivering | reviewing | fixing | delivered | blocked
Branch: `codex/<slug>-phase-N`

### Scope

- ...

### Changes

- ...

### Tests And Verification

- `command`: passed | failed | not run

### Review

- Review file: `automation/<slug>/reviews/<slug>-phase-N-review-iteration-M.md`
- Verdict: delivered | needs-fix | blocked

### Finding Disposition

- [P1] finding summary: fixed | deferred | rejected | blocked

### Residual Risks

- ...

### Next Action

- ...
```

Do not write a final review verdict until a review exists. Final review
verdicts must use one of the exact lowercase values `delivered`, `needs-fix`,
or `blocked`.

## Commit And Advancement

Do not advance to the next phase until all are true:

- phase acceptance criteria are satisfied
- required verification passed after the final fix, if any
- a fresh review verdict is `delivered`
- roadmap header/status is updated
- delivery log is updated
- delivery state is updated
- review/fix state is updated when present

Local commits are optional unless the roadmap or operator requires them. If a
commit is made, stage only phase-owned files and bookkeeping files by explicit
path. Publication remains a separate human-approved action.
