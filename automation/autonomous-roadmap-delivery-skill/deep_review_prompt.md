# Final Deep Review Prompt

You are reviewing the completed `autonomous-roadmap-delivery` skill delivery
roadmap. Take a skeptical code-review stance: lead with findings, cite files
and commands, and do not give credit for intent unless the delivered artifacts
actually support it.

## Repository And Branch

- GitHub repository: https://github.com/<owner>/autonomous-roadmap-delivery
  (replace `<owner>` with the owner from the branch URL provided for review)
- Local repository root:
  `$ROADMAP_REPO_ROOT`
- Review branch: `codex/autonomous-roadmap-delivery-skill-phase-10`
- Review the branch HEAD for that branch. Do not assume `main` contains
  these changes until a push, PR, and merge have explicitly happened.
- Roadmap:
  `roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md`
- Delivery state:
  `automation/autonomous-roadmap-delivery-skill/delivery_state.json`
- Delivery log:
  `automation/autonomous-roadmap-delivery-skill/delivery_log.md`
- Review/fix state and log:
  `automation/autonomous-roadmap-delivery-skill/review_fix_state.json`
  and `automation/autonomous-roadmap-delivery-skill/review_fix_log.md`
- Review artifacts:
  `automation/autonomous-roadmap-delivery-skill/reviews/`

The live installed skill files are at:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/
```

The GitHub branch also includes a source snapshot for external review at:

```text
skill/autonomous-roadmap-delivery/
```

Use the repository snapshot for GitHub-only review and compare it with the live
installed skill directory before publication if local access is available.

## What Was Supposed To Be Delivered

The roadmap was supposed to deliver a reusable Codex skill named
`autonomous-roadmap-delivery` for file-backed, phase-gated roadmap delivery.
The skill should help Codex:

- set up roadmap delivery automation artifacts
- inspect roadmap automation status
- pause or activate roadmap automation only under explicit approval rules
- repair stale roadmap paths and inconsistent state
- deliver exactly one current roadmap phase at a time
- run verification before claiming delivery
- require review verdicts before phase advancement
- handle review/fix loops with exact verdicts
- finalize delivered roadmap branches without automatically pushing, merging,
  promoting to `main`, or changing app automation config

The implementation was intentionally not supposed to create a general project
management system, multi-agent swarm, CI/CD platform, GitHub auto-promotion
tool, observability platform, or replacement for human merge authority.

## How It Is Supposed To Work

The installed skill router is:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/SKILL.md
```

It should remain lean and route each task to a reference file:

- setup new automation:
  `references/setup-automation.md`
- deliver one current phase:
  `references/phase-loop.md`
- handle review findings:
  `references/review-and-fix.md`
- inspect status, branches, state, or logs:
  `references/state-log-and-branches.md`
- finalize, promote, or close out delivered work:
  `references/finalization-and-promotion.md`
- repair bad state, stale paths, blocked runs, or lifecycle drift:
  `references/troubleshooting.md`

The helper scripts should be deterministic and read-only:

- `scripts/inspect_delivery_state.py` reports roadmap automation status,
  branch state, matching branches, completion state, dirty worktree warnings,
  stale prompt-path warnings, and deep-review prompt presence.
- `scripts/validate_delivery_artifacts.py` validates delivery artifacts and
  returns JSON with `errors`, `warnings`, and `info`; errors are blockers,
  warnings require explanation, and `--strict` should fail on warnings.

The skill should preserve unrelated user changes, avoid broad staging, avoid
force-pushes, and stop when roadmap, state, log, review files, verification
evidence, automation config, branch, or worktree evidence disagree.

## Delivered Roadmap Summary

Review whether these phase outcomes are genuinely supported by files and
verification evidence:

- Phase 0 confirmed the skill name, install target, source documents, and pilot
  automation target.
- Phase 1 created the installed skill skeleton and metadata.
- Phase 2 wrote the lean `SKILL.md` router.
- Phase 3 created the six installed reference files.
- Phase 4 added the read-only status inspection helper.
- Phase 5 validated the skill package and pilot status smoke.
- Phase 6 added the read-only artifact validator and fixture coverage for key
  failure modes.
- Phase 7 hardened setup, pause, and repair workflows.
- Phase 8 tightened review/fix loop reliability.
- Phase 9 added repository-local unittest fixtures and replay prompts.
- Phase 10 added operational maintenance guidance, repository layout mismatch
  handling, and support for both `roadmaps/automation/<slug>/...` and
  `automation/<slug>/...` state layouts in status inspection.

## What Needs To Be Tested

Run or inspect evidence for these checks:

```bash
cd $ROADMAP_REPO_ROOT
git status --short --branch
python3 -m json.tool automation/autonomous-roadmap-delivery-skill/delivery_state.json
python3 -m json.tool automation/autonomous-roadmap-delivery-skill/review_fix_state.json
git diff --check
PYTHONPYCACHEPREFIX=$TMPDIR/autonomous-roadmap-review-test-pycache python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=$TMPDIR/autonomous-roadmap-review-compile-pycache python3 -m py_compile skill/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py skill/autonomous-roadmap-delivery/scripts/validate_delivery_artifacts.py
PYTHONPATH=$TMPDIR/autonomous-roadmap-delivery-pyyaml PYTHONPYCACHEPREFIX=$TMPDIR/autonomous-roadmap-review-skill-pycache python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py skill/autonomous-roadmap-delivery
PYTHONPYCACHEPREFIX=$TMPDIR/autonomous-roadmap-review-inspect-pycache python3 skill/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py --repo-root $ROADMAP_REPO_ROOT --roadmap-slug autonomous-roadmap-delivery-skill --automation-id autonomous-roadmap-delivery-skill --json
PYTHONPYCACHEPREFIX=$TMPDIR/autonomous-roadmap-review-validate-pycache python3 skill/autonomous-roadmap-delivery/scripts/validate_delivery_artifacts.py --repo-root $ROADMAP_REPO_ROOT --roadmap-slug autonomous-roadmap-delivery-skill --automation-id autonomous-roadmap-delivery-skill --json
```

Also inspect these behavior-specific questions:

- Does `SKILL.md` route every supported intent to the correct reference?
- Do references tell Codex to stop on mismatched roadmap/state/log/review
  surfaces?
- Do references avoid broad `git add .`, force-push, automatic promotion to
  `main`, or hidden GitHub publication?
- Does `inspect_delivery_state.py` support both automation artifact layouts and
  report ambiguity as warnings?
- Does `validate_delivery_artifacts.py` catch missing state, invalid JSON,
  missing review directory, stale automation prompt path, active completed
  automation without a hard-stop guard, invalid review verdict, branch mismatch,
  and dirty worktree?
- Do `tests/test_helper_scripts.py` fixture scenarios cover both helper scripts
  without copying secrets or mutating live roadmap artifacts?
- Do eval prompts under `evals/` measure behavior without leaking expected
  answers?

## Known Residual Risks To Judge

Treat these as explicit review questions, not automatic failures:

- The roadmap workspace may be dirty if this prompt was edited after the local
  commit; verify whether the review branch includes the latest prompt change.
- The saved Codex automation currently reads back as `PAUSED`, but its prompt
  may still lack an explicit `all_phases_complete` or
  `completed_pending_pause` hard-stop guard.
- The roadmap filename is still
  `autonomous-roadmap-delivery-skill-phased-roadmap.md`, not a `delivered_`
  lifecycle filename.
- The GitHub branch includes a repository skill snapshot; if local access is
  available, compare it with the installed skill directory before publication.
- No push, PR, merge, or promotion to `main` should be assumed from local
  delivery.

## Review Output Required

Return:

- findings first, ordered by severity, with file/line references when possible
- missing tests or verification gaps
- residual risks that remain after local completion
- whether the GitHub branch is ready for human review or PR publication
- whether the repository skill snapshot matches the installed skill behavior
  and tests
- verdict: `ready-for-human-review`, `needs-fix`, or `blocked`

Do not push, promote, merge, edit app automation config, or alter automation
status as part of this review.
