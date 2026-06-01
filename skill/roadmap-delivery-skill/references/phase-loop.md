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

If the only blocker is that setup artifacts expected PAUSED while the saved
Codex automation now reads ACTIVE, treat clear operator/manual activation as an
already-authorized status decision when model/reasoning, prompt path, cwd,
hard-stop guard, and blocked-remediation guard all still match. Reconcile
durable guide/log/state to ACTIVE, record `last_activation` and
`last_blocker_repair`, clear `blocked_reason` after validation, and resume the
current phase rather than looping on the same automation-config blocker.

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

## Approval Policy Gate

Before asking the operator or performing an operation automatically, read and
validate `automation/<slug>/approval_policy.json` when present. Missing policy
keeps conservative legacy behavior. Resolve each named operation to `allowed`,
`ask`, or `forbidden`:

- `allowed`: the approval policy pre-approves the operation; proceed and record
  the decision in state/log/review evidence.
- `ask`: stop before the operation unless explicit human approval is already
  present in the current workflow.
- `forbidden`: record a blocker and do not run it automatically.

Use named decisions for phase-owned edits, state/log/review writes, branch
creation, local commits, automation retarget, automation pause, branch push,
installed-skill sync, publication, promotion, credential use, and destructive
git. Never-auto and unknown operations are always `forbidden`, even in
delegated or custom modes.

## End-Run Retargeting Gate

After a delivered review verdict and before advancing state to the next phase:

1. Resolve the next numbered phase from the roadmap. If no numbered phase
   remains, stop the normal phase loop, load
   `references/finalization-and-promotion.md`, and resolve the `finalization`
   pseudo-phase.
2. Read `phase_model_policy.json` and compute the next required model and
   reasoning effort. Use the next phase override when present; otherwise use
   policy defaults.
3. Update `delivery_state.json` with the next phase, next required
   model/reasoning fields, and the configured automation values observed by
   readback.
4. If the current automation config already matches the next required
   model/reasoning, record that no retarget was needed and keep the automation
   active.
5. If the config does not match, update it only when the approval-policy
   decision for `retarget_saved_automation` is `allowed` or explicit human
   approval is already present. Read the saved config back after the update.
6. If readback matches, record the retarget result and stop. The next run
   starts the next phase.
7. If the update or readback fails, set or keep the state blocked, write or
   request a `retarget-failed` alert, and do not start the next phase.

When there is no next numbered phase, do not set `all_phases_complete`,
`completed`, or `completed_pending_pause` from this phase-loop path. The
finalization reference owns final verification, final deep-review prompt or
waiver evidence, completed alert, pause handling, and promotion readiness.

Use the read-only helper when a deterministic plan is useful:

```bash
python3 skill/roadmap-delivery-skill/scripts/plan_automation_retarget.py \
  --repo-root <repo-root> \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --delivered-phase "Phase N - Name" \
  --json
```

The helper does not mutate state or automation config. It is evidence for the
review gate, not a substitute for an approved update and readback.

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
- next model/reasoning requirements are resolved and either already match the
  saved automation config or have an approved retarget readback
- roadmap header/status is updated
- delivery log is updated
- delivery state is updated
- review/fix state is updated when present

Local commits are optional unless the roadmap or operator requires them. If a
commit is made, stage only phase-owned files and bookkeeping files by explicit
path. Publication remains a separate human-approved action.

If this was the final numbered phase, the next action is finalization, not
completion. A same-context phase review remains a phase review and does not
satisfy the final deep-review prompt requirement.
