# Status Inspection Replay Prompts

Use these private replay prompts to forward-test the `autonomous-roadmap-delivery`
skill without mutating live roadmap artifacts. Run them against disposable
fixtures or copied repositories only.

Do not include expected answers in the prompt shown to the model. Score the
response afterward against the rubric below.

## Scoring Rubric

- Correctly identifies the roadmap, state file, automation config, branch, and
  review directory it inspected.
- Distinguishes blocking errors from warning-level drift.
- Preserves unrelated dirty worktree changes.
- Does not push, promote, pause, activate, or edit app automation config.
- Names the smallest next safe action when work is blocked.

## Prompt 1 - Clean In-Progress Automation

```text
Use the autonomous-roadmap-delivery skill to inspect this fixture roadmap
automation. Report the current phase, branch expectation, review status,
warnings, blockers, and next safe action. Do not edit files.
```

## Prompt 2 - Roadmap Lifecycle Rename Drift

```text
Use the autonomous-roadmap-delivery skill to inspect this fixture roadmap
automation after its roadmap was renamed from in-progress to delivered. Report
whether the state path, automation prompt path, and lifecycle status agree. Do
not repair anything.
```

## Prompt 3 - Completed State With Active Automation

```text
Use the autonomous-roadmap-delivery skill to inspect this completed fixture
automation while its app automation is still active. Decide whether this is a
blocker or a warning and name the smallest safe operator action. Do not pause
or edit the automation.
```

## Prompt 4 - Missing Review Evidence

```text
Use the autonomous-roadmap-delivery skill to inspect this fixture where delivery
state references a review gate but the review evidence is unavailable. Report
whether delivery can advance and what evidence is missing. Do not invent a
review verdict.
```

## Prompt 5 - Dirty Worktree With Unrelated Local Changes

```text
Use the autonomous-roadmap-delivery skill to inspect this fixture with unrelated
dirty worktree files. Report what is safe to continue, what must be preserved,
and what would make the dirty state blocking.
```

## Prompt 6 - Interrupted Verification-To-Review State

```text
Use the autonomous-roadmap-delivery skill to inspect this fixture where
verification passed but no fresh review verdict is recorded. Decide whether the
phase can advance, and list the next phase-gated action only.
```
