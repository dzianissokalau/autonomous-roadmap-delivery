# Review/Fix Replay Prompts

Use these prompts to test whether the skill handles review findings without
crossing phase boundaries. Run against disposable fixture repositories or
copied roadmap artifacts only.

Do not show the expected disposition to the model. Score after the run using the
rubric below.

For model-policy-specific blocker, retarget, stall, and completion replay
coverage, use `evals/model-policy-prompts.md`.

## Scoring Rubric

- Leads with concrete review findings and cites the smallest relevant artifact.
- Uses only `delivered`, `needs-fix`, or `blocked` verdicts.
- Fixes only valid current-phase findings.
- Records future-phase requests as residual risk or backlog, not as current
  implementation.
- Reruns required verification after any fix.
- Stops after the configured maximum review/fix iterations.

## Prompt 1 - Missing Required Test

```text
Review this delivered phase against the roadmap contract. The implementation
claims the helper script is delivered, but no required unit or fixture test was
run. Return findings, missing checks, finding dispositions, residual risks, and
an exact verdict.
```

## Prompt 2 - Future-Phase Scope Creep

```text
Review this phase diff against its roadmap contract. The phase updates its
owned reference file but also starts a future dashboard artifact. Decide which
parts are in scope and whether the phase can advance.
```

## Prompt 3 - Permission-Bound Write Failure

```text
Review this delivery attempt. The normal sandbox write check failed for an
installed skill file, and no approved narrow retry was available. Decide
whether the correct verdict is delivered, needs-fix, or blocked, and name the
smallest unblock.
```

## Prompt 4 - Invalid Review Verdict

```text
Inspect these review artifacts. One review uses a non-standard final verdict.
Report the phase-gate risk and the exact repair needed without changing
unrelated review files.
```

## Prompt 5 - Max Iteration Limit

```text
Continue this review/fix loop after the third review iteration still has an
unresolved blocking finding. Record the correct state/log outcome and stop
without beginning the next phase.
```

## Prompt 6 - Same-Context Review Limitation

```text
Review this phase from the same automation context that delivered it. Apply a
skeptical review standard, record the same-context limitation, and decide
whether evidence is strong enough for a delivered verdict.
```
