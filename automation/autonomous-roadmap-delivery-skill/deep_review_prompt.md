# Final Deep Review Prompt

You are reviewing the completed `autonomous-roadmap-delivery` skill delivery
roadmap. Take a skeptical code-review stance: lead with findings, cite files
and commands, and do not give credit for intent unless the delivered artifacts
actually support it.

## Repository And Branch

- GitHub repository: https://github.com/<owner>/autonomous-roadmap-delivery
  (replace `<owner>` with the owner from the branch URL provided for review)
- Review branch: `codex/autonomous-roadmap-delivery-skill-phase-10`
- Review the branch HEAD for that branch. The branch was sanitized and
  history-cleaned after initial publication, so do not review old local hashes
  or cached pre-sanitization commits.
- Expected branch shape: the review branch is based on `main` and contains the
  completed roadmap delivery artifacts plus the repository skill snapshot.
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
- Repository skill snapshot for GitHub-only review:
  `skill/roadmap-delivery-skill/`

The live installed skill files are outside this repository at:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/
```

Use the repository snapshot for GitHub-only review. If local access is
available, compare the snapshot with the live installed skill before
publication or installation decisions.

## Sanitization Context

The branch was pushed once before privacy review, then sanitized and
history-cleaned. The current review target should not expose concrete local
home paths, local workspace paths, temp-directory paths, pilot repository
names, pilot roadmap slugs, repository-owner strings, or fixture email values.

Intentional placeholders include:

- `$CODEX_HOME`
- `$ROADMAP_REPO_ROOT`
- `$PILOT_REPO_ROOT`
- `$TMPDIR`
- `<owner>`
- `<repository-remote-url>`
- `<pilot-roadmap-slug>`
- `<pilot-automation-id>`
- `automation.invalid`

These placeholders are not failures by themselves. Treat them as failures only
if they make the committed instructions impossible to run after substitution,
or if concrete local/personal values still appear elsewhere in the branch.

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

In this branch, review the source snapshot at:

```text
skill/roadmap-delivery-skill/SKILL.md
```

The router should remain lean and route each task to a reference file:

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
  warnings require explanation, and `--strict` should fail on warnings except
  codes explicitly passed with `--allow-warning`.

The skill should preserve unrelated user changes, avoid broad staging, avoid
force-pushes unless explicitly approved by a human for publication cleanup, and
stop when roadmap, state, log, review files, verification evidence, automation
config, branch, or worktree evidence disagree.

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
- Post-delivery publication hygiene added the repository skill snapshot,
  sanitized review artifacts, and rewrote the review branch so reachable branch
  history contains only sanitized artifacts.

## What Needs To Be Tested

Set local placeholders before running commands from a clone:

```bash
export ROADMAP_REPO_ROOT="$(pwd)"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export TMPDIR="${TMPDIR:-/tmp}"
```

Run or inspect evidence for these checks:

```bash
cd "$ROADMAP_REPO_ROOT"
git status --short --branch
git log --oneline --decorate origin/main..HEAD
python3 -m json.tool automation/autonomous-roadmap-delivery-skill/delivery_state.json
python3 -m json.tool automation/autonomous-roadmap-delivery-skill/review_fix_state.json
git diff --check
PYTHONPYCACHEPREFIX="$TMPDIR/roadmap-delivery-skill-review-test-pycache" python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX="$TMPDIR/roadmap-delivery-skill-review-compile-pycache" python3 -m py_compile skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
PYTHONPATH="$TMPDIR/roadmap-delivery-skill-pyyaml" PYTHONPYCACHEPREFIX="$TMPDIR/roadmap-delivery-skill-review-skill-pycache" python3 "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" skill/roadmap-delivery-skill
PYTHONPYCACHEPREFIX="$TMPDIR/roadmap-delivery-skill-review-inspect-pycache" python3 skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py --repo-root "$ROADMAP_REPO_ROOT" --roadmap-slug autonomous-roadmap-delivery-skill --automation-id autonomous-roadmap-delivery-skill --json
PYTHONPYCACHEPREFIX="$TMPDIR/roadmap-delivery-skill-review-validate-pycache" python3 skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py --repo-root "$ROADMAP_REPO_ROOT" --roadmap-slug autonomous-roadmap-delivery-skill --automation-id autonomous-roadmap-delivery-skill --json
PYTHONPYCACHEPREFIX="$TMPDIR/roadmap-delivery-skill-review-strict-pycache" python3 skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py --repo-root "$ROADMAP_REPO_ROOT" --roadmap-slug autonomous-roadmap-delivery-skill --automation-id autonomous-roadmap-delivery-skill --strict --allow-warning missing_automation_config --allow-warning roadmap_lifecycle_filename_unconfirmed --allow-warning automation_prompt_missing_hard_stop_guard
```

Also inspect these behavior-specific questions:

- Does `SKILL.md` route every supported intent to the correct reference?
- Do references tell Codex to stop on mismatched roadmap/state/log/review
  surfaces?
- Do references avoid broad `git add .`, unapproved force-push, automatic
  promotion to `main`, or hidden GitHub publication?
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
- Does the branch avoid concrete local/personal identifiers while preserving
  enough placeholder context for external review?

## Privacy And Branch-History Checks

Verify the current review branch, not old cached commits:

- the branch contains no concrete local home-directory values from the delivery
  machine
- the branch contains no concrete local roadmap workspace path
- the branch contains no concrete temp-directory path from the delivery machine
- the branch contains no concrete pilot repository name or pilot roadmap slug
- the branch contains no fixture email address that looks like a real address
- the branch contains no obvious private-key, API-key, GitHub-token, AWS-key,
  password, secret, or token assignment material
- the branch history reachable from the review branch does not include the
  pre-sanitization commits

If a scanner reports placeholder values such as `$CODEX_HOME` or
`<pilot-roadmap-slug>`, that is expected. If it reports concrete local values,
treat that as a blocking finding.

## Known Residual Risks To Judge

Treat these as explicit review questions, not automatic failures:

- The saved Codex automation currently reads back as `PAUSED`, but its prompt
  may still lack an explicit `all_phases_complete` or
  `completed_pending_pause` hard-stop guard.
- The roadmap filename is still
  `autonomous-roadmap-delivery-skill-phased-roadmap.md`, not a `delivered_`
  lifecycle filename.
- The GitHub branch includes a repository skill snapshot; if local access is
  available, compare it with the installed skill directory before publication.
- A review-branch push has happened, but no PR, merge, promotion to `main`, or
  app automation config change should be assumed.
- Previously pushed unsanitized commits should no longer be reachable from the
  branch. Exact old SHA URLs or external caches may still exist outside the
  repository branch; that is a hosting/cache concern, not current branch
  content.

## Review Output Required

Return:

- findings first, ordered by severity, with file/line references when possible
- missing tests or verification gaps
- privacy/sanitization findings, including whether placeholders are coherent
- residual risks that remain after branch publication cleanup
- whether the GitHub branch is ready for human review or PR publication
- whether the repository skill snapshot matches the installed skill behavior
  and tests, or whether local access was unavailable
- verdict: `ready-for-human-review`, `needs-fix`, or `blocked`

Do not push, promote, merge, edit app automation config, or alter automation
status as part of this review.
