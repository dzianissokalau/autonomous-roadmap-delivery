# Autonomous Roadmap Delivery Skill Phased Roadmap

Status: Delivered
Current phase: Complete
Last updated: 2026-05-21
Last completed phase: Phase 10 - Operational Hardening And Maintenance
Next action: Final human review or publication can begin only with explicit approval; do not push, promote, or merge automatically.
Blocked by: None
Phase 10 note: Delivered after approved narrow escalation updated the
installed status helper, maintenance checklist, troubleshooting layout
guidance, and repository-local fixture tests. Skill validation, script
compilation, unittest fixtures, status inspection, artifact validation,
and SKILL.md routing checks passed.
Phase 9 note: Delivered after adding repository-local unittest fixtures and
private replay prompts. The helper script harness covers six representative
scenarios across status inspection and artifact validation; skill validation
and current artifact validation passed.
Phase 8 note: Delivered after approved narrow escalation updated
`review-and-fix.md` and `phase-loop.md`. Manual historical review checks,
exact verdict checks, future-phase guard checks, skill validation, and current
artifact validation passed.
Phase 7 note: Delivered after approved narrow escalation updated setup,
troubleshooting, and finalization references. The setup fixture, prompt/path
checks, troubleshooting coverage checks, skill validation, current artifact
validation, and safety scan passed.
Phase 6 note: Delivered after approved narrow escalation wrote the read-only
artifact validator and reference updates. Compile, skill validation, real
automation validation, current automation validation, read-only scan, and all
required local fixtures passed.
Phase 5 note: Delivered after skill validation, compile checks, pilot status
inspection, setup-reference smoke, and completed-state handling checks passed.
Phase 4 note: Delivered after approved narrow escalation wrote the read-only
status script and compile, skill validation, and pilot smoke checks passed.
Phase 3 note: Delivered after approved narrow escalation wrote the installed skill reference pack and validation/safety checks passed.
Phase 2 note: Delivered after approved narrow escalation for updating `$CODEX_HOME/skills/autonomous-roadmap-delivery/SKILL.md`.
Phase 1 note: Delivered after approved narrow escalation for creating and updating `$CODEX_HOME/skills/autonomous-roadmap-delivery`.

## Source Inputs

This roadmap distills three source documents into an implementation plan for:

1. Skill v1: a small, practical Codex skill that can be installed and used.
2. Skill hardening: reliability, repair, evaluation, and operational safeguards after v1.

Source documents:

- `$PILOT_REPO_ROOT/roadmaps/automation/autonomous_roadmap_delivery_skill_development_brief.md`
- `$PILOT_REPO_ROOT/roadmaps/automation/codex_phase_gated_delivery_automation_template.md`
- `$ROADMAP_REPO_ROOT/roadmaps/automated-roadmap-delivery-strategy.md`

## Automation Artifacts

Phase-gated delivery artifacts for this roadmap live under:

```text
automation/autonomous-roadmap-delivery-skill/
```

Current files:

- `automation/autonomous-roadmap-delivery-skill/automation_guide.md`
- `automation/autonomous-roadmap-delivery-skill/delivery_state.json`
- `automation/autonomous-roadmap-delivery-skill/delivery_log.md`
- `automation/autonomous-roadmap-delivery-skill/review_fix_state.json`
- `automation/autonomous-roadmap-delivery-skill/review_fix_log.md`
- `automation/autonomous-roadmap-delivery-skill/reviews/`

Codex app automation:

- ID: `autonomous-roadmap-delivery-skill`
- Status: PAUSED
- Cadence: hourly
- Execution environment: worktree

## Target Outcome

Create a reusable Codex skill named `autonomous-roadmap-delivery` that helps Codex set up, inspect, operate, pause, resume, review, repair, and finalize phase-gated roadmap delivery workflows.

The first release should be intentionally small:

- Codex-native, not a separate orchestration platform.
- File-backed, using roadmap files, JSON state, delivery logs, review files, and git history.
- Phase-gated, delivering exactly one roadmap phase at a time.
- Review-gated, requiring verification and a review verdict before phase advancement.
- Safe by default, preserving unrelated worktree changes and stopping on ambiguity.

The hardening release should improve confidence and repeatability:

- Stronger artifact validation.
- Better automation setup and repair flows.
- Review/fix loop reliability checks.
- Seeded evals and replay tests.
- Clear operational runbooks embedded as skill references, not standalone docs.

## Operating Principles

- Treat the roadmap as the phase contract.
- Deliver exactly one phase at a time.
- Keep state durable and inspectable on disk.
- Prefer deterministic helper scripts for repeated inspection and validation.
- Do not silently expand scope into future phases.
- Do not mark a phase delivered unless required verification passed.
- Do not advance a phase unless review verdict is `delivered`.
- Do not push, promote, or release unless the roadmap and human instruction allow it.
- Never revert unrelated user changes.
- Stop and report mismatches when roadmap, state, log, branch, and automation config disagree.

## Skill Shape

Recommended install target:

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/
```

Recommended source package:

```text
autonomous-roadmap-delivery/
  SKILL.md
  agents/
    openai.yaml
  references/
    setup-automation.md
    phase-loop.md
    review-and-fix.md
    state-log-and-branches.md
    finalization-and-promotion.md
    troubleshooting.md
  scripts/
    inspect_delivery_state.py
    validate_delivery_artifacts.py
```

For v1, `validate_delivery_artifacts.py` may be stubbed or deferred if `inspect_delivery_state.py` is complete and tested.

## Non-Goals

The v1 and hardening tracks should not build:

- a general project management system
- a multi-agent swarm
- a LangGraph or Temporal control plane
- a release automation system
- a generic CI/CD framework
- a fine-tuned model
- a hidden branch-pushing tool
- a replacement for human merge authority

Future platform concepts from the strategy document can be preserved as later backlog, but they should not block the skill.

## Delivery Tracks

Track 1 is the minimal useful skill. Track 2 hardens the same skill after it proves useful.

```text
Track 1: Skill v1
  Phase 0 - Scope Confirmation
  Phase 1 - Skill Skeleton And Metadata
  Phase 2 - Core Skill Instructions
  Phase 3 - Reference Pack
  Phase 4 - Read-Only Status Script
  Phase 5 - Validation And Pilot Smoke

Track 2: Skill Hardening
  Phase 6 - Artifact Validator
  Phase 7 - Automation Setup, Pause, And Repair Workflows
  Phase 8 - Review/Fix Reliability Pack
  Phase 9 - Eval And Replay Harness
  Phase 10 - Operational Hardening And Maintenance
```

## Phase 0 - Scope Confirmation

### Objective

Confirm the v1 installation target, source-of-truth documents, and the first supported repository before writing the skill.

### Owned Files

- This roadmap file.
- Optional planning notes inside the current workspace.

### Inputs

- Skill development brief.
- Phase-gated delivery template.
- Strategy document.
- Existing roadmap automation examples in `$PILOT_REPO_ROOT`.

### Implementation Steps

1. Confirm the skill name is `autonomous-roadmap-delivery`.
2. Confirm the install target is `$CODEX_HOME/skills/autonomous-roadmap-delivery`.
3. Confirm v1 is repo-specific to `$PILOT_REPO_ROOT`.
4. Confirm that platform topics remain backlog, not v1 blockers.
5. Pick one delivered or active roadmap automation as the pilot inspection target.

### Acceptance Criteria

- The install path is confirmed or an alternate target is chosen.
- The v1 scope is limited to skill files, references, and one read-only helper script.
- The hardening track is explicitly deferred until v1 is installed and smoke-tested.
- A pilot roadmap automation is selected for status inspection.

### Required Verification

- Confirm the target directory can be created or updated.
- Confirm the source documents are readable.
- Confirm at least one existing automation-backed roadmap is available for smoke testing.

### Non-Goals

- Do not create the skill in this phase unless the target is already confirmed.
- Do not change any pilot repository roadmap files.
- Do not create or modify Codex app automations.

### Stop Conditions

- Stop if the install target requires approval and approval is not granted.
- Stop if source documents are missing.
- Stop if v1 scope expands into a control plane or CI/CD rollout.

## Phase 1 - Skill Skeleton And Metadata

### Objective

Create the skill directory structure and machine-readable metadata so Codex can discover and trigger the skill.

### Owned Files

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/SKILL.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/agents/openai.yaml
```

### Implementation Steps

1. Use the `skill-creator` initialization workflow.
2. Create the skill folder with `scripts` and `references` resources.
3. Write frontmatter with only:
   - `name: roadmap-delivery-skill`
   - `description: ...`
4. Make the description trigger on:
   - setting up roadmap delivery automation
   - inspecting status
   - pausing or activating roadmap automation
   - repairing stale roadmap paths
   - delivering or reviewing one current phase
   - finalizing or promoting delivered roadmap branches
5. Avoid triggering on:
   - ordinary feature implementation
   - generic PR review
   - general project management
   - unrelated Codex skill creation
6. Generate `agents/openai.yaml` from the final skill intent.

### Acceptance Criteria

- The skill folder has the expected structure.
- `SKILL.md` has valid YAML frontmatter.
- The description includes concrete trigger contexts from the brief.
- The description excludes unrelated work clearly enough to reduce false triggers.
- `agents/openai.yaml` exists and matches the skill purpose.

### Required Verification

Run:

```bash
$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py $CODEX_HOME/skills/autonomous-roadmap-delivery
```

### Non-Goals

- Do not fill the skill body with the full workflow details.
- Do not duplicate every section of the source brief.
- Do not create README, installation guide, changelog, or extra documentation files.

### Stop Conditions

- Stop if skill validation fails and the error cannot be fixed locally.
- Stop if metadata cannot be generated without writing outside approved paths.

## Phase 2 - Core Skill Instructions

### Objective

Write a concise `SKILL.md` body that routes Codex to the right reference file and enforces the core safety rules.

### Owned Files

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/SKILL.md
```

### Implementation Steps

1. Add a short "First move" checklist:
   - identify exact roadmap path or automation id
   - read state, log, roadmap, and git status
   - reconcile lifecycle rename drift
   - check completed hard-stop state
2. Add a task routing map:
   - setup new automation: `references/setup-automation.md`
   - deliver a phase: `references/phase-loop.md`
   - handle review findings: `references/review-and-fix.md`
   - inspect status: `references/state-log-and-branches.md`
   - finalize or promote: `references/finalization-and-promotion.md`
   - repair bad state: `references/troubleshooting.md`
3. Include hard safety rules:
   - one phase at a time
   - verification before delivery
   - review before phase advancement
   - no unrelated reverts
   - no broad staging
   - no force-push
   - no main promotion without explicit human approval
4. Include stop conditions from the brief.
5. Point to `scripts/inspect_delivery_state.py` for status questions once Phase 4 exists.

### Acceptance Criteria

- `SKILL.md` remains lean and procedural.
- `SKILL.md` tells Codex exactly which reference to read for each user intent.
- The body does not rely on hidden conversation context.
- The body mentions durable surfaces:
  - roadmap
  - `delivery_state.json`
  - `delivery_log.md`
  - review files
  - git branch and commit history
  - verification output
  - `automation.toml`
- The stop behavior is explicit when those surfaces disagree.

### Required Verification

- Run skill validation.
- Manually inspect the file for duplication with reference docs.
- Check that every referenced file name will exist by the end of Phase 3.

### Non-Goals

- Do not include full automation prompt skeletons in `SKILL.md`.
- Do not include long examples in `SKILL.md`.
- Do not make `SKILL.md` an operational manual.

### Stop Conditions

- Stop if `SKILL.md` exceeds the useful scope of a skill router.
- Stop if critical setup, phase, review, finalization, or repair instructions have no reference destination.

## Phase 3 - Reference Pack

### Objective

Create the detailed reference files used by the skill for setup, delivery, review/fix, status inspection, finalization, and repair.

### Owned Files

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/setup-automation.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/phase-loop.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/review-and-fix.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/state-log-and-branches.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/finalization-and-promotion.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/troubleshooting.md
```

### Reference Requirements

#### `setup-automation.md`

Include:

- suitability checklist for autonomous phase-gated delivery
- roadmap slug and path selection
- artifact directory layout
- initial state JSON shape
- initial delivery log shape
- full automation prompt skeleton with concrete path placeholders
- cron versus heartbeat guidance
- hourly cadence default for detached repository automations
- model and reasoning defaults
- PAUSED-by-default creation rule
- readback checklist for the known ACTIVE-save caveat

#### `phase-loop.md`

Include:

- state reconciliation checklist
- phase contract extraction checklist
- implementation scope rules
- branch creation/reuse rules
- verification command selection
- delivery log update format
- commit and phase advancement rules
- handling of dirty unrelated worktree files

#### `review-and-fix.md`

Include:

- fresh reviewer prompt
- review verdict definitions
- review file naming convention
- findings format
- max review iteration rule
- fix-loop prompt
- residual risk recording
- reviewer bias note when fresh context is unavailable

#### `state-log-and-branches.md`

Include:

- delivery state schema
- known status values
- delivery log schema
- review directory layout
- branch naming model
- status inspection checklist
- exact commands for branch/status inspection
- warning rules for mismatched roadmap/state/automation paths

#### `finalization-and-promotion.md`

Include:

- all-phases-complete checklist
- final verification requirement
- deep-review prompt requirements
- final branch naming
- final bookkeeping commit rule
- push rules
- automation pause procedure
- explicit separate flow for promotion to `main`
- fast-forward-only promotion guard

#### `troubleshooting.md`

Include:

- automation saved ACTIVE despite requested PAUSED
- status-only automation update rejected
- stale roadmap path after lifecycle rename
- completed state but automation still ACTIVE
- user confusion between roadmaps
- review finds medium gaps after delivery
- dirty worktree with unrelated files
- branch exists with unexpected base
- verification cannot run
- roadmap/state current phase mismatch

### Acceptance Criteria

- Each reference file is directly linked from `SKILL.md`.
- Each reference has enough procedure for a fresh Codex session to act without reading the whole source brief.
- The automation prompt skeleton includes concrete path variables and hard-stop guards.
- The phase loop is faithful to the existing phase-gated template.
- The troubleshooting guide captures observed failure modes from the brief.

### Required Verification

- Run skill validation.
- Search for stale source-only placeholders.
- Confirm no reference tells Codex to push, promote, or release without explicit approval.
- Confirm no reference tells Codex to use broad `git add .`.

Suggested checks:

```bash
rg -n "git add \\.|force-push|push origin HEAD:main|completed_pending_pause|all_phases_complete" $CODEX_HOME/skills/autonomous-roadmap-delivery
```

### Non-Goals

- Do not copy the full strategy document into references.
- Do not include broad platform sections on OTel, artifact attestation, fine-tuning, or dashboards.
- Do not create standalone README or runbook files outside the skill resource structure.

### Stop Conditions

- Stop if the reference pack contradicts the source template.
- Stop if references encode repository mutation in a status-only workflow.

## Phase 4 - Read-Only Status Script

### Objective

Implement `inspect_delivery_state.py` as a deterministic read-only helper that reduces stale and confused status reports.

### Owned Files

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py
```

### Interface

Inputs:

```text
--repo-root $PILOT_REPO_ROOT
--roadmap-slug <slug>
--automation-id <automation-id>
--json
```

At least one of `--roadmap-slug` or `--automation-id` should be accepted. If both are provided, the script should cross-check them.

Output JSON:

```json
{
  "automation_id": "example-delivery",
  "automation_status": "ACTIVE",
  "roadmap_path": "$PILOT_REPO_ROOT/roadmaps/in_progress_example_roadmap.md",
  "state_file": "$PILOT_REPO_ROOT/roadmaps/automation/example/delivery_state.json",
  "state_status": "not_started",
  "current_phase": 1,
  "last_delivered_phase": 0,
  "blocked_reason": null,
  "all_phases_complete": false,
  "current_branch": "codex/example-phase-1",
  "matching_branches": [],
  "worktree_dirty": false,
  "deep_review_prompt_exists": false,
  "warnings": []
}
```

### Implementation Steps

1. Parse arguments with `argparse`.
2. Load `delivery_state.json` if a roadmap slug is available.
3. Load `$CODEX_HOME/automations/<automation-id>/automation.toml` if an automation id is available.
4. Extract:
   - automation status
   - roadmap path from state
   - roadmap path references from automation prompt
   - current phase
   - last delivered phase
   - blocked reason
   - completion state
5. Run read-only git commands:
   - `git branch --show-current`
   - `git branch --list 'codex/<slug>*'`
   - `git status --short`
6. Check whether the deep-review prompt exists when complete or near complete.
7. Emit warnings for:
   - missing state file
   - invalid JSON
   - missing roadmap file
   - automation prompt points to stale roadmap path
   - completed state but automation is active
   - dirty worktree
   - current branch does not match state branch
   - multiple matching roadmap lifecycle files

### Acceptance Criteria

- The script never mutates files.
- The script exits non-zero only for invocation errors or unreadable required inputs.
- Status warnings are explicit and machine-readable.
- The script can inspect at least one existing roadmap automation.
- The script works without third-party dependencies.

### Required Verification

Run against a fixture or existing automation:

```bash
python3 $CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py --repo-root $PILOT_REPO_ROOT --roadmap-slug <slug> --json
```

Run static checks:

```bash
python3 -m py_compile $CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py
```

### Non-Goals

- Do not repair state.
- Do not edit automation configs.
- Do not create branches.
- Do not stage, commit, or push.

### Stop Conditions

- Stop if script behavior would require network access.
- Stop if automation config parsing requires unavailable dependencies.
- Stop if a status ambiguity cannot be represented as a warning.

## Phase 5 - Validation And Pilot Smoke

### Objective

Validate the skill package and run a realistic dry inspection against an existing roadmap automation.

### Owned Files

- Skill files created in Phases 1-4.
- Temporary fixtures under `$TMPDIR` only if needed.

### Implementation Steps

1. Run `quick_validate.py`.
2. Run Python compile checks for scripts.
3. Run `inspect_delivery_state.py` against a known delivered or active roadmap automation.
4. Ask a fresh Codex context, if approved and useful, to use the skill for a status-inspection task.
5. Fix any unclear routing, missing reference details, or script warnings that are too vague.
6. Document residual risks in the final implementation response.

### Acceptance Criteria

- `quick_validate.py` passes.
- `inspect_delivery_state.py` returns coherent JSON for a real automation.
- The skill can answer a status question without stale roadmap path confusion.
- The skill can describe setup steps for a new automation without mutating anything.
- The skill can identify completed state and recommend pausing rather than starting work.

### Required Verification

```bash
$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py $CODEX_HOME/skills/autonomous-roadmap-delivery
python3 -m py_compile $CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py
python3 $CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py --repo-root $PILOT_REPO_ROOT --roadmap-slug <pilot-slug> --json
```

### Non-Goals

- Do not activate any automation.
- Do not run a full roadmap phase delivery.
- Do not push branches.
- Do not promote to `main`.

### Stop Conditions

- Stop if validation fails.
- Stop if the pilot status output contradicts known repo state and the mismatch cannot be explained.
- Stop if smoke testing would mutate live roadmap artifacts.

## Phase 6 - Artifact Validator

### Objective

Add `validate_delivery_artifacts.py` to catch inconsistent roadmap automation state before a Codex run acts on it.

### Owned Files

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/scripts/validate_delivery_artifacts.py
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/state-log-and-branches.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/troubleshooting.md
```

### Interface

Inputs:

```text
--repo-root $PILOT_REPO_ROOT
--roadmap-slug <slug>
--automation-id <automation-id>
--strict
--json
```

Output:

- JSON report with `errors`, `warnings`, and `info`.
- Non-zero exit for `errors`.
- Zero exit for warnings unless `--strict` is set.

### Checks

1. State file exists and is valid JSON.
2. Delivery log exists.
3. Review directory exists.
4. Roadmap path exists.
5. Roadmap lifecycle filename matches roadmap header status.
6. State `roadmap` path matches current roadmap file.
7. Automation prompt references current roadmap path.
8. Automation prompt includes hard-stop guard.
9. State `current_phase` agrees with roadmap current phase unless complete.
10. Completion state includes deep-review prompt path.
11. Completed state has paused automation or an explicit hard-stop warning.
12. Review verdict files use valid verdicts.
13. Branch naming matches roadmap slug and current phase.
14. Dirty worktree is reported.

### Acceptance Criteria

- The script is read-only.
- The script distinguishes warnings from blocking errors.
- The script catches the known ACTIVE/completed mismatch.
- The script catches stale roadmap path references after lifecycle rename.
- The script catches missing deep-review prompt in completed state.

### Required Verification

- Compile the script.
- Run on at least one valid existing automation.
- Run on local fixtures for:
  - missing state
  - invalid JSON
  - stale roadmap path
  - completed but active
  - invalid review verdict

### Non-Goals

- Do not auto-repair artifacts in this phase.
- Do not edit automation configs.
- Do not infer product decisions from roadmap gaps.

### Stop Conditions

- Stop if validation requires brittle Markdown parsing beyond the current roadmap conventions.
- Stop if repair logic starts leaking into the validator.

## Phase 7 - Automation Setup, Pause, And Repair Workflows

### Objective

Make setup and repair flows operationally reliable while preserving a conservative approval boundary.

### Owned Files

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/setup-automation.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/troubleshooting.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/finalization-and-promotion.md
```

Optional scripts may be added only after repeated manual steps prove deterministic enough.

### Implementation Steps

1. Add a setup checklist that creates:
   - artifact directory
   - state JSON
   - delivery log
   - review directory
   - paused cron automation proposal
2. Add a readback checklist:
   - inspect `automation.toml`
   - confirm `status = "PAUSED"`
   - confirm prompt paths are current
   - confirm cwd is repo root
3. Add repair procedures for:
   - saved ACTIVE despite requested PAUSED
   - stale prompt path after lifecycle rename
   - completed state but active automation
   - status-only update rejected
4. Add activation rules:
   - activate only when explicitly requested
   - never activate if validation has errors
   - never activate if state says complete
5. Add pause rules:
   - pause before final response when complete
   - pause when blocked by product decision or verification environment
   - pause when max review iterations reached

### Acceptance Criteria

- Codex can set up a new automation in PAUSED state from a roadmap path.
- Codex reads back the saved config and corrects or reports ACTIVE drift.
- Codex can explain exactly which paths and prompt references were created.
- Codex can repair stale roadmap path references safely.
- Codex refuses activation when validation reports blocking errors.

### Required Verification

- Dry-run the setup procedure against a fixture roadmap or non-live copy.
- Validate generated prompt paths.
- Validate state/log/review directory creation.
- Verify the troubleshooting reference covers all known failure modes from the brief.

### Non-Goals

- Do not create an external service wrapper.
- Do not create a scheduling dashboard.
- Do not support multi-repo automation.
- Do not bypass Codex app automation approval mechanisms.

### Stop Conditions

- Stop if direct config edits are required and not explicitly approved.
- Stop if a repair would overwrite user changes.
- Stop if activation would start delivery before the operator requested it.

## Phase 8 - Review/Fix Reliability Pack

### Objective

Improve the quality and repeatability of the review/fix loop without creating a peer-agent swarm.

### Owned Files

```text
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/review-and-fix.md
$CODEX_HOME/skills/autonomous-roadmap-delivery/references/phase-loop.md
```

Optional fixture files may be added under a test or fixture directory if a source-controlled skill repository is later created.

### Implementation Steps

1. Tighten the reviewer prompt:
   - lead with findings
   - use file/line references
   - check acceptance criteria
   - check verification sufficiency
   - check scope creep
   - check security/path/data integrity risks
   - evaluate behavior, not intent
2. Define verdict rules:
   - `delivered`
   - `needs-fix`
   - `blocked`
3. Add a fix-loop decision table:
   - valid and in scope: fix
   - valid but future phase: record as backlog/residual risk
   - invalid: explain why
   - blocked: stop and ask
4. Add max iteration handling:
   - default 3 review/fix loops
   - mark blocked after max iterations
   - record unresolved findings
5. Add residual risk language when review is same-context rather than fresh.

### Acceptance Criteria

- Review files have consistent naming and verdict format.
- Codex treats `needs-fix` as a gated loop, not as advisory text.
- Codex records why each finding was fixed, deferred, rejected, or blocked.
- Codex reruns verification after fixes.
- Codex does not advance a phase after same-context review unless the limitation is recorded.

### Required Verification

- Run manual prompt checks against at least two historical diffs or review files.
- Confirm all verdict examples use exact allowed values.
- Confirm the fix-loop instructions do not allow future-phase implementation.

### Non-Goals

- Do not implement a general autonomous reviewer service.
- Do not fine-tune a reviewer model.
- Do not replace human final review for merge or promotion.

### Stop Conditions

- Stop if review findings require product decisions not in the roadmap.
- Stop if reviewer and delivery context disagree on acceptance after max iterations.
- Stop if fixing would require broad refactoring outside phase scope.

## Phase 9 - Eval And Replay Harness

### Objective

Create a lightweight evidence loop that tests whether the skill behaves correctly on representative roadmap delivery situations.

### Owned Files

If the skill remains installed directly under `.codex/skills`, keep eval prompts and fixture notes in `references/` only when they are necessary for using the skill. If a source repository is created for the skill, place fixtures and tests there.

Potential future files:

```text
tests/fixtures/
tests/test_inspect_delivery_state.py
tests/test_validate_delivery_artifacts.py
evals/status-inspection-prompts.md
evals/review-fix-prompts.md
```

### Eval Set

Build small private evals from real and synthetic cases:

- status inspection of a clean in-progress automation
- status inspection after roadmap lifecycle rename
- completed state but active automation
- missing review file
- invalid review verdict
- dirty unrelated worktree
- stale automation prompt path
- review finds missing tests
- review finds future-phase scope creep
- interrupted state between verification and review

### Implementation Steps

1. Create a minimal fixture model of:
   - roadmap file
   - automation directory
   - state file
   - delivery log
   - review files
   - automation config
2. Add unit tests for helper scripts.
3. Add replay prompts for human or subagent forward-testing.
4. Track expected outcomes:
   - answer status
   - stop as blocked
   - warn only
   - repair with approval
5. Preserve raw outputs from pilot runs as future eval examples, excluding secrets.

### Acceptance Criteria

- Helper scripts have tests for happy paths and known failure modes.
- The skill is tested against at least five representative scenarios.
- The eval prompts measure behavior without leaking expected answers.
- Failures produce concrete skill/reference/script edits.

### Required Verification

- Run unit tests if a test harness exists.
- Run both helper scripts against fixtures.
- Forward-test status inspection in a fresh context if the risk is low and the user approves.

### Non-Goals

- Do not use public coding benchmarks as release gates.
- Do not build dashboards.
- Do not build full OTel instrumentation.
- Do not introduce model fine-tuning.

### Stop Conditions

- Stop if fixtures risk copying private credentials or sensitive content.
- Stop if forward-testing would mutate live roadmap artifacts.
- Stop if eval failures reveal ambiguous workflow policy that needs human decision.

## Phase 10 - Operational Hardening And Maintenance

### Objective

Turn the skill into a maintainable workflow asset after v1 and evals prove useful.

### Owned Files

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

Do not add these optional files to the installed skill directory unless they directly support skill use.

### Implementation Steps

1. Add version notes inside `SKILL.md` only if useful and concise.
2. Add maintenance checklist to a reference file:
   - refresh prompt skeletons after automation API changes
   - rerun validation after source template changes
   - update troubleshooting after each new failure mode
   - run fixture tests before publishing skill updates
3. Decide whether to create a separate source repo for the skill.
4. If a source repo exists, add:
   - unit tests
   - fixture tests
   - CI for script compilation and validation
   - packaging/install instructions outside the skill artifact
5. Consider optional GitHub integration only after the local skill loop is stable.

### Acceptance Criteria

- There is a clear path for updating the skill without bloating the installed skill.
- New failure modes have an obvious destination in troubleshooting or tests.
- Skill updates can be validated before use.
- Platform concerns remain separated from the core skill artifact.

### Required Verification

- Run skill validation.
- Run script tests.
- Run representative status and artifact validation scenarios.
- Confirm `SKILL.md` still routes correctly to all references.

### Non-Goals

- Do not add OTel, dashboards, artifact attestation, or multi-repo APIs to the installed skill.
- Do not make GitHub branch promotion automatic.
- Do not make human review optional for merge or deployment.

### Stop Conditions

- Stop if maintenance additions make the installed skill noisy or hard to trigger correctly.
- Stop if CI/CD hardening starts delaying fixes to the core skill.

## Cross-Phase Acceptance Criteria

The v1 plus hardening roadmap is complete when:

- The skill can be discovered by Codex.
- The skill routes tasks to the right reference files.
- The skill can set up or describe a paused automation safely.
- The skill can inspect current roadmap delivery status accurately.
- The skill can detect stale roadmap paths after lifecycle renames.
- The skill can detect completed state and avoid starting new work.
- The skill can guide one-phase-at-a-time delivery.
- The skill can guide review/fix loops with exact verdicts.
- The skill can create or validate final deep-review prompt requirements.
- Helper scripts are read-only unless explicitly designed otherwise.
- Validation catches the known operational failure modes.
- Unrelated worktree changes are preserved.
- Promotion to `main` remains explicitly human-approved and fast-forward-only.

## Recommended Immediate Build Order

1. Confirm install target and pilot roadmap.
2. Create skill skeleton with `scripts` and `references`.
3. Write `SKILL.md`.
4. Write reference pack.
5. Implement `inspect_delivery_state.py`.
6. Validate and smoke-test.
7. Add `validate_delivery_artifacts.py`.
8. Harden setup/pause/repair procedures.
9. Add review/fix reliability examples.
10. Add eval fixtures if a source repository is created.

## Backlog Beyond Tracks 1 And 2

These items come from the strategy document but are intentionally outside the v1 and hardening tracks:

- multi-repo control plane
- LangGraph or Temporal orchestration
- OpenTelemetry dashboards
- GitHub reusable workflow suite
- artifact attestation and signing
- security scanner orchestration
- dedicated prompt optimizer workflow
- fine-tuned reviewer or classifier model
- production rollout playbooks
- enterprise handover process

Keep these as future platform work only after the Codex-native skill proves valuable.
