# Review Artifact Template

Use this shape for phase review files.

```markdown
# <Roadmap Name> Phase N Review - Iteration M

Reviewed at: YYYY-MM-DDTHH:MM:SSZ
Roadmap: `roadmaps/<roadmap-file>.md`
Phase: Phase N - Name
Branch: `<phase-branch>`
Reviewer context: <fresh-context-or-same-context-limitation>

## Findings

- [P1] ...

## Missing Tests Or Checks

- ...

## Finding Disposition

- [P1] finding summary: fixed | deferred | rejected | blocked

## Verification Evidence

- `command`: passed | failed | not run

## Residual Risks

- ...

## Verdict

delivered | needs-fix | blocked
```

The final verdict value must be exact lowercase text.
