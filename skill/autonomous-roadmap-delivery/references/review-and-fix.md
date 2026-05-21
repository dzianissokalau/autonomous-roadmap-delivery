# Review And Fix Reference

Use this reference after a phase delivery attempt or when handling review
findings.

## Fresh Reviewer Prompt

```text
Review the delivered Phase N changes against ROADMAP_PATH.

Take a skeptical code-review stance. Lead with findings.

Review:
- roadmap phase objective, owned files, non-goals, stop conditions, acceptance
  criteria, and required verification
- automation guide, delivery state, review/fix state, delivery log, and latest
  review files
- changed files or artifacts, including generated helper scripts and reference
  docs
- verification evidence, command outputs, and whether checks ran after the
  final fix
- git branch, worktree status, and whether unrelated dirty files were preserved

Look for:
- missed acceptance criteria
- insufficient verification or verification that only checks pre-existing
  behavior
- scope creep into future phases
- stale roadmap/state/log/review contradictions
- unsafe branch, path, data integrity, credential, or approval-boundary risks
- mutation that should have required human approval
- claims that evaluate intent instead of delivered behavior

Return:
- findings ordered by severity with file/line references where possible
- missing tests or checks
- finding dispositions that say fixed, deferred, rejected, or blocked
- residual risks, including same-context review limitations
- verdict: delivered, needs-fix, or blocked
```

When no fresh reviewer context is available, record that limitation in the
review and be stricter about evidence. Same-context review is acceptable only
when the limitation is explicit and the phase acceptance criteria are directly
evidenced by changed artifacts and verification output.

## Verdict Rules

Use exact lowercase verdict values:

- `delivered`: acceptance criteria are met, required verification passed after
  the last change, scope stayed inside the current phase, and no blocking
  findings remain.
- `needs-fix`: at least one valid current-phase finding can be fixed without a
  product decision, missing permission, destructive operation, or forbidden
  scope expansion.
- `blocked`: required inputs, permissions, credentials, environment, or scope
  clarity are missing; reviewer and delivery evidence disagree after the max
  iterations; or the next fix would exceed current-phase scope.

Do not use alternate final verdicts such as `approved`, `pass`, `failed`,
`complete`, or `ok`.

## Review File Naming

```text
automation/<slug>/reviews/<slug>-phase-<n>-review-iteration-<m>.md
```

Each review should include:

```markdown
# Phase N Review - Iteration M

Roadmap: `...`
Phase: ...
Reviewed at: ...
Branch: `...`
Verdict: delivered | needs-fix | blocked

## Findings

- [P1] ...

## Missing Tests Or Checks

- ...

## Finding Disposition

- [P1] finding summary: fixed | deferred | rejected | blocked

## Residual Risks

- ...

## Verdict

delivered | needs-fix | blocked
```

## Findings Format

Use priorities:

- `[P0]` data loss, destructive action, security exposure, or phase corruption
- `[P1]` missed acceptance criteria, broken required behavior, missing required
  verification, or unsafe phase advancement
- `[P2]` important reliability, operator clarity, path, or state drift gap
- `[P3]` minor cleanup that should not block delivery

Findings should cite concrete files, line numbers, review files, state fields,
or commands whenever possible. If line references are unavailable, cite the
smallest concrete artifact and explain the exact evidence.

## Fix Loop Decision Table

| Finding type | Required action |
| --- | --- |
| Valid and in current phase scope | Fix it, rerun all required and targeted verification affected by the fix, update state/log evidence, then write a new review iteration. |
| Valid but future phase | Do not implement it during this phase; record it as residual risk, backlog, or next-phase input. |
| Invalid or already satisfied | Explain why, citing file, state, log, review, or command evidence. |
| Blocked by permission/input/environment | Stop, update state/log/review, and name the smallest approval, input, or environment change needed. |

`needs-fix` closes the phase gate. It is not advisory. A phase with
`needs-fix` cannot advance until a later review iteration says `delivered`.

## Verification After Fixes

After every valid current-phase fix:

1. Rerun the phase's required verification.
2. Rerun targeted checks for files or behavior touched by the fix.
3. Record command, status, and important output in `delivery_log.md`.
4. Update `delivery_state.json` and `review_fix_state.json` when present.
5. Write a new review iteration; do not edit the earlier review verdict.

If verification cannot run, the verdict is `blocked` unless the phase is
explicitly read-only and the roadmap allows confirmation without execution.

## Max Iterations

Default maximum is 3 review/fix iterations. If the phase is still not
`delivered` after the maximum:

- set delivery and review/fix state to `blocked`
- record unresolved findings and missing checks
- keep the current phase unchanged
- stop without beginning the next phase

## Residual Risk Recording

Residual risks are not a replacement for acceptance criteria. Use them for:

- environment limitations that do not invalidate verification
- deferred future-phase improvements
- same-context review limitations
- known operator follow-up
- warnings from read-only validators that are outside current phase scope

Do not bury an unmet acceptance criterion in residual risks. If it is required
by the current phase and not satisfied, the verdict is `needs-fix` or
`blocked`.
