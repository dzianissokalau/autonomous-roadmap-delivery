# Contributor Workflow

Use this workflow when changing the framework, generated Codex package, docs,
or roadmap automation artifacts.

## Before Editing

1. Read the active roadmap phase and owned file list.
2. Read `automation/<roadmap-slug>/delivery_state.json`,
   `delivery_log.md`, `review_fix_state.json`, latest reviews, and
   `phase_model_policy.json` when present.
3. Read back the saved automation config when the run is automation-backed.
4. Check `git branch --show-current` and `git status --short --branch`.
5. Run artifact validation when state, branch, or review evidence might
   disagree.

Stop instead of guessing when the roadmap, state, log, review, branch,
worktree, or automation config disagree.

## During Implementation

- Work on `codex/<roadmap-slug>-phase-<n>` for implementation phases.
- Change only files owned by the current phase plus required bookkeeping.
- Preserve unrelated worktree changes.
- Keep canonical workflow changes in `core/`, schema changes in `schemas/`,
  shared behavior in `src/roadmap_delivery/`, and host-specific package
  behavior in `adapters/<host>/`.
- Regenerate or check generated Codex package output with
  `scripts/build_codex_package.py --check`.

## Verification

Run every command named by the current phase. For broad framework changes, the
usual local gate is:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_codex_package.py --check
python3 scripts/build_release.py --check
python3 scripts/check_release_privacy.py --repo-root .
git diff --check
```

Add targeted tests when behavior changes. Do not claim delivery if verification
only exercises pre-existing behavior.

## Review And Bookkeeping

Write a review artifact under
`automation/<roadmap-slug>/reviews/` with a verdict of `delivered`,
`needs-fix`, or `blocked`. Update delivery state, delivery log, review/fix
state, and progress tracking only after the review gate is satisfied.

Local commits should stage explicit paths only. Do not push, publish, sync the
installed Codex skill, merge to `main`, or edit live automation config unless
the operator explicitly approves that operation.
