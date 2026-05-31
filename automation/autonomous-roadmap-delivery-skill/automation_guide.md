# Codex Automation Guide: Autonomous Roadmap Delivery Skill Roadmap

Status: Delivered
Created: 2026-05-20
Primary roadmap: `roadmaps/delivered_autonomous-roadmap-delivery-skill-phased-roadmap.md`

## Purpose

This guide describes how to run Codex as a phase-gated delivery system for the
first roadmap in this project: building the `autonomous-roadmap-delivery` skill.

The intended loop is:

```text
deliver one roadmap phase
verify the phase against its required checks
review the delivered artifacts in a fresh context
route findings back to the delivery context
fix and verify
repeat until clean or blocked
advance to the next roadmap phase
```

## Configuration

```text
ROADMAP_PATH=roadmaps/delivered_autonomous-roadmap-delivery-skill-phased-roadmap.md
ROADMAP_SLUG=autonomous-roadmap-delivery-skill
CURRENT_PHASE=Complete
CURRENT_STATUS=completed
CURRENT_BRANCH=codex/autonomous-roadmap-delivery-skill-phase-10
STATE_FILE=automation/autonomous-roadmap-delivery-skill/delivery_state.json
DELIVERY_LOG=automation/autonomous-roadmap-delivery-skill/delivery_log.md
REVIEW_FIX_STATE=automation/autonomous-roadmap-delivery-skill/review_fix_state.json
REVIEW_FIX_LOG=automation/autonomous-roadmap-delivery-skill/review_fix_log.md
REVIEW_DIR=automation/autonomous-roadmap-delivery-skill/reviews
MAX_REVIEW_ITERATIONS=3
AUTOMATION_ID=autonomous-roadmap-delivery-skill
AUTOMATION_STATUS=PAUSED
CADENCE=hourly
MODEL=gpt-5.5
REASONING=xhigh
EXECUTION_ENVIRONMENT=worktree
```

This workspace is a git repository synced to:

```text
<repository-remote-url>
```

The initial planning artifacts are synced on `main`. For future roadmap phase
delivery work, use one branch per phase:

```text
codex/autonomous-roadmap-delivery-skill-phase-<n>
```

## Last Completed Phase 0 Contract

Phase 0 confirms the v1 installation target, source-of-truth documents, and the
first supported repository before writing the skill.

Confirmed inputs:

- Skill name: `autonomous-roadmap-delivery`
- Install target: `$CODEX_HOME/skills/autonomous-roadmap-delivery`
- First supported repository: `$PILOT_REPO_ROOT`
- Platform/control-plane topics: backlog, not v1 blockers
- Pilot inspection target: `<pilot-roadmap-slug>`

## Phase 0 Verification

Run or confirm:

```bash
test -d $CODEX_HOME/skills && test -w $CODEX_HOME/skills
test -r $PILOT_REPO_ROOT/roadmaps/automation/codex_phase_gated_delivery_automation_template.md
test -r $PILOT_REPO_ROOT/roadmaps/automation/README.md
test -r $PILOT_REPO_ROOT/roadmaps/automation/roadmap_closeout_checklist.md
find $PILOT_REPO_ROOT/roadmaps/automation -maxdepth 3 -type f
```

Phase 0 should not create the skill files. Phase 1 owns the skill skeleton and
metadata.

## Last Completed Phase 1 Contract

Phase 1 creates the skill directory structure and machine-readable metadata so
Codex can discover and trigger the skill.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/SKILL.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/agents/openai.yaml
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-1
```

Writes under `$CODEX_HOME/skills/autonomous-roadmap-delivery`
may require narrow sandbox escalation.

Phase 1 delivered on 2026-05-20 after approved narrow escalation created the
skill skeleton, `SKILL.md`, `agents/openai.yaml`, `scripts/`, and
`references/`.

## Last Completed Phase 2 Contract

Phase 2 writes the concise `SKILL.md` router body that sends Codex to the right
future reference file and enforces core safety rules.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/SKILL.md
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-2
```

Do not create Phase 3 reference content during Phase 2; only mention the
reference destinations that Phase 3 will create.

Phase 2 delivered on 2026-05-20 after approved narrow escalation updated the
installed `SKILL.md` router body and skill validation passed.

## Last Completed Phase 3 Contract

Phase 3 creates the detailed reference files used by the Phase 2 router for
setup, phase delivery, review/fix handling, status inspection, finalization, and
repair.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/setup-automation.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/phase-loop.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/review-and-fix.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/state-log-and-branches.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/finalization-and-promotion.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/troubleshooting.md
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-3
```

Phase 3 delivered on 2026-05-20 after approved narrow escalation wrote the six
installed reference files, skill validation passed, stale-placeholder checks
passed, and unsafe git/promotion scans found no unsafe reference-pack matches.

Do not create helper scripts during Phase 3. Script work starts in Phase 4.

## Last Completed Phase 4 Contract

Phase 4 implements the read-only status helper script that reduces stale and
confused status reports.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-4
```

Phase 4 delivered on 2026-05-20 after approved narrow escalation wrote
`inspect_delivery_state.py`. Compile checks, skill validation, and pilot smoke
inspection against `<pilot-roadmap-slug>` passed.

The helper is read-only, dependency-free, emits machine-readable JSON warnings,
accepts hyphen or underscore roadmap slugs, and cross-checks automation ids
when provided.

## Last Completed Phase 5 Contract

Phase 5 validates the skill package and runs a realistic dry inspection against
an existing roadmap automation.

Owned files:

```text
Skill files created in Phases 1-4.
Temporary fixtures under $TMPDIR only if needed.
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-5
```

Phase 5 must not activate automations, run a full roadmap phase delivery, push
branches, or promote to `main`. Fixes are allowed only when smoke findings show
unclear routing, missing reference details, or vague script warnings within the
skill v1 surface.

Phase 5 delivered on 2026-05-20 without modifying installed skill files. Skill
validation, compile checks, pilot status inspection, setup-reference smoke, and
completed-state handling checks passed.

## Last Completed Phase 6 Contract

Phase 6 adds a read-only artifact validator that catches inconsistent roadmap
automation state before a Codex run acts on it.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/validate_delivery_artifacts.py
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/state-log-and-branches.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/troubleshooting.md
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-6
```

Phase 6 must keep the validator read-only, distinguish warnings from blocking
errors, catch the known ACTIVE/completed mismatch, catch stale roadmap prompt
paths after lifecycle rename, and catch missing deep-review prompts in completed
state. Required verification includes compile checks, one real automation run,
and local fixtures for missing state, invalid JSON, stale roadmap path,
completed-but-active, and invalid review verdict cases.

Phase 6 delivered on 2026-05-20 after approved narrow escalation wrote
`validate_delivery_artifacts.py` and updated the state/status and
troubleshooting references. Compile, skill validation, real automation
validation, current automation validation, read-only scan, and fixtures for
missing state, invalid JSON, stale roadmap path, completed-but-active, and
invalid review verdict passed.

The validator is read-only, emits JSON reports with `errors`, `warnings`, and
`info`, returns non-zero for blocking errors, supports `--strict`, catches stale
roadmap prompt references after lifecycle rename, catches ACTIVE/completed
mismatches, and reports missing deep-review prompts in completed state.

## Last Completed Phase 7 Contract

Phase 7 makes setup and repair flows operationally reliable while preserving a
conservative approval boundary.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/setup-automation.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/troubleshooting.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/finalization-and-promotion.md
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-7
```

Phase 7 delivered on 2026-05-20 after approved narrow escalation updated the
installed setup, troubleshooting, and finalization references. The delivered
references now define repository-local setup artifacts, a PAUSED automation
proposal, readback checks, stale prompt repair, activation refusal when
validation reports errors, pause rules, and operator-facing path summaries.
Verification passed for the non-live setup fixture, prompt/path checks,
state/log/review directory creation, troubleshooting coverage, skill
validation, current artifact validation, and unsafe push/staging scan.

## Last Completed Phase 8 Contract

Phase 8 improves the quality and repeatability of the review/fix loop without
creating a peer-agent swarm.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/review-and-fix.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/phase-loop.md
```

Phase 8 delivered on 2026-05-21 after approved narrow escalation updated the
installed review/fix and phase-loop references. The delivered references now
tighten reviewer prompts, exact verdict rules, fix-loop disposition handling,
max-iteration behavior, verification after fixes, and same-context review risk
recording. Verification passed for historical review prompt checks, exact
verdict examples, future-phase implementation guards, skill validation, and
current artifact validation.

## Last Completed Phase 9 Contract

Phase 9 creates a lightweight evidence loop that tests whether the skill
behaves correctly on representative roadmap delivery situations.

Owned files are conditional. If the skill remains installed directly under
`.codex/skills`, keep eval prompts and fixture notes in `references/` only when
they are necessary for using the skill. If a source repository is created for
the skill, place fixtures and tests there.

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-9
```

Phase 9 should test helper scripts against representative scenarios, run both
helpers against fixtures, and avoid copying private credentials or mutating live
roadmap artifacts.

Phase 9 delivered on 2026-05-21 after adding repository-local unittest fixtures
and private replay prompts. The fixture harness covers clean in-progress
status, stale prompt path warnings, completed-active hard-stop errors, missing
review evidence, invalid review verdicts, and unrelated dirty worktree
warnings. Required verification passed for the unit harness, skill validation,
and current artifact validation.

## Last Completed Phase 10 Contract

Phase 10 turns the skill into a maintainable workflow asset after v1 and evals
prove useful.

Owned files:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/SKILL.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/*.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/*.py
```

Optional future source repository files:

```text
CHANGELOG.md
tests/
evals/
.github/workflows/
```

Before implementation, create or reuse:

```text
codex/autonomous-roadmap-delivery-skill-phase-10
```

Phase 10 must keep platform concerns separate from the installed skill, avoid
bloating the trigger surface, run skill validation, run script tests, and rerun
representative status and artifact validation scenarios.

Phase 10 delivered on 2026-05-21 after approved narrow escalation updated
the installed status helper, maintenance checklist, troubleshooting layout
guidance, and repository-local fixture tests. Validation passed for skill
metadata, script compilation, seven helper-script fixture tests,
representative status inspection, current artifact validation, and
`SKILL.md` routing checks. Platform concerns, GitHub integration,
publication, and promotion remain outside the installed skill artifact.

## Codex App Automation

The Codex app automation is saved as:

```text
id=autonomous-roadmap-delivery-skill
status=PAUSED
rrule=FREQ=HOURLY;INTERVAL=1
model=gpt-5.5
reasoning_effort=xhigh
execution_environment=worktree
cwd=$ROADMAP_REPO_ROOT
```

The automation prompt must keep automation artifacts under
`automation/autonomous-roadmap-delivery-skill/` and must stop after advancing
state to the next phase so the next hourly run handles the next phase.

## Operating Rules

1. Work exactly one roadmap phase at a time.
2. Do not begin Phase N+1 until Phase N is delivered, reviewed, fixed if
   needed, verified, and recorded.
3. Treat the roadmap phase acceptance criteria as the source of truth.
4. Keep durable state in `delivery_state.json`.
5. Keep `delivery_log.md` append-only.
6. Use `review_fix_state.json` and `review_fix_log.md` only for review-driven
   repair loops.
7. Stop and record a blocker when a product decision, credential, destructive
   operation, or unclear scope decision is required.
8. Do not write outside the workspace unless the user approves the required
   sandbox escalation.

## Permission Handling

The saved Codex automation prompt uses phase-agnostic permission handling for
the installed skill target.

- Keep the automation rooted in the roadmap workspace only; do not add
  `$CODEX_HOME/skills` to `cwds` or patch Codex global state.
- For any current phase whose owned files, required verification, or targeted
  checks touch `$CODEX_HOME/skills` or the installed
  `autonomous-roadmap-delivery` skill directory, first run the normal sandbox
  command.
- If that command fails because of sandbox restrictions, permission denial, or
  a false negative write probe, retry only the exact command, or the smallest
  equivalent single write/validation command, with narrow approval escalation
  naming the current phase and path.
- Keep escalations command-scoped. Do not request broad writable roots, shell
  bundles, global state patches, pushes, promotion to `main`, or destructive
  git operations.
- If approval is denied or unavailable, record the blocker in state/log/review
  and stop.

## Delivery Agent Prompt

```text
Deliver Phase N of roadmaps/delivered_autonomous-roadmap-delivery-skill-phased-roadmap.md.

Use this phase-gated delivery template:
automation/codex_phase_gated_delivery_automation_template.md

Work only on Phase N. Do not start Phase N+1.

Before editing:
- Extract the phase scope, non-goals, acceptance criteria, and required checks.
- Identify owned files.
- Identify which paths require sandbox escalation.

During delivery:
- Keep changes scoped to the phase.
- Preserve unrelated user changes.
- Update automation/autonomous-roadmap-delivery-skill/delivery_log.md with
  scope, changed files, verification, review status, residual risks, and next
  action.

At the end:
- Report changed files.
- Report verification results.
- Report remaining risks.
- Do not claim Phase N is delivered until a fresh review verdict says delivered.
```

## Reviewer Prompt

```text
Review the delivered Phase N changes against
roadmaps/delivered_autonomous-roadmap-delivery-skill-phased-roadmap.md.

Take a skeptical code-review stance. Lead with findings.

Review:
- roadmap phase acceptance criteria
- automation guide
- delivery state
- delivery log
- changed files
- verification evidence

Look for missed criteria, unsafe scope expansion, over-claimed delivery,
missing verification, stale paths, and contradictions between roadmap, state,
and log.

Return:
- Findings ordered by severity with file/line references
- Missing tests or checks
- Residual risks
- Verdict: delivered, needs-fix, or blocked
```

## Phase Advancement

Phase 0 advanced to Phase 1 on 2026-05-20 after:

- the install target, source documents, and pilot target are confirmed
- the delivery log records the verification evidence
- a fresh review verdict is `delivered`
- the roadmap header and delivery state are updated

Phase 1 advanced to Phase 2 on 2026-05-20 after:

- approved narrow escalation created the skill skeleton
- `SKILL.md` frontmatter and `agents/openai.yaml` matched the Phase 1 intent
- skill validation passed with the validator run through `python3` and
  temporary `$TMPDIR` PyYAML support
- a fresh review verdict is `delivered`
- the roadmap header and delivery state are updated

Phase 2 advanced to Phase 3 on 2026-05-20 after:

- approved narrow escalation updated the installed `SKILL.md` router body
- the body routed each supported intent to its planned reference file
- skill validation passed with the validator run through `python3` and
  temporary `$TMPDIR` PyYAML support
- a fresh review verdict is `delivered`
- the roadmap header and delivery state are updated

Phase 3 advanced to Phase 4 on 2026-05-20 after:

- approved narrow escalation wrote the installed reference pack
- all six `SKILL.md` reference destinations existed
- skill validation passed with the validator run through `python3` and
  temporary `$TMPDIR` PyYAML support
- stale-placeholder and unsafe command scans passed for the reference files
- a fresh review verdict is `delivered`
- the roadmap header, delivery log, review/fix tracker, and delivery state are
  updated

Phase 4 advanced to Phase 5 on 2026-05-20 after:

- approved narrow escalation wrote `inspect_delivery_state.py`
- the helper compiled with `PYTHONPYCACHEPREFIX` under `$TMPDIR`
- skill validation passed with the validator run through `python3` and
  temporary `$TMPDIR` PyYAML support
- pilot smoke inspection returned coherent JSON for
  `<pilot-roadmap-slug>`
- a fresh review verdict is `delivered`
- the roadmap header, delivery log, review/fix tracker, and delivery state are
  updated

Phase 5 advanced to Phase 6 on 2026-05-20 after:

- skill validation passed with the validator run through `python3` and
  temporary `$TMPDIR` PyYAML support
- `inspect_delivery_state.py` compiled with `PYTHONPYCACHEPREFIX` under
  `$TMPDIR`
- pilot smoke inspection returned coherent JSON for
  `<pilot-roadmap-slug>`
- setup-reference smoke confirmed new automations are described as conservative,
  repository-local, and PAUSED by default
- completed-state handling reports complete roadmaps and pause-oriented warnings
- a fresh review verdict is `delivered`
- the roadmap header, delivery log, review/fix tracker, and delivery state are
  updated

Phase 6 advanced to Phase 7 on 2026-05-20 after:

- approved narrow escalation wrote the read-only artifact validator and
  reference updates
- compile, skill validation, real automation validation, current automation
  validation, read-only scan, and required fixtures passed
- a fresh review verdict is `delivered`
- the roadmap header, delivery log, review/fix tracker, and delivery state are
  updated

Phase 7 advanced to Phase 8 on 2026-05-20 after:

- approved narrow escalation updated the installed setup, troubleshooting, and
  finalization references
- a non-live setup fixture validated artifact directory, state JSON, delivery
  log, review directory, PAUSED proposal, cwd, and prompt paths
- troubleshooting coverage and activation refusal guidance were verified
- skill validation and current artifact validation passed
- a fresh review verdict is `delivered`
- the roadmap header, delivery log, review/fix tracker, and delivery state are
  updated

Phase 8 advanced to Phase 9 on 2026-05-21 after:

- approved narrow escalation updated the installed review/fix and phase-loop
  references
- manual historical review checks passed against Phase 7 delivered and Phase 8
  blocked review files
- exact verdict examples and future-phase implementation guard checks passed
- skill validation and current artifact validation passed
- a fresh same-context review recorded its limitation and returned `delivered`
- the roadmap header, delivery log, review/fix tracker, and delivery state are
  updated
