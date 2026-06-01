# Autonomous Operation Modes And Adaptive Control Roadmap

Status: In Progress
Current phase: Phase 2 - Approval Gate Enforcement
Last updated: 2026-06-01
Next action: Deliver Phase 2 approval gate enforcement.
Blocked by: None.

## Purpose

This roadmap closes three operational gaps found while running Roadmap Delivery
Skill on real roadmaps:

- the model choice is static even after a non-flawless run
- delivery still asks for manual approval for operations that a user may want
  to pre-approve once
- completed automations can keep running instead of pausing themselves

The work turns these into explicit, durable policies rather than prompt-only
preferences.

## Automation Readiness

Recommended automation setup:

```text
ROADMAP_PATH=roadmaps/in_progress_autonomous_operation_modes_and_adaptive_control_roadmap.md
ROADMAP_SLUG=autonomous-operation-modes-and-adaptive-control
AUTOMATION_DIR=automation/autonomous-operation-modes-and-adaptive-control
AUTOMATION_ID=autonomous-operation-modes-and-adaptive-control
INITIAL_MODEL=gpt-5.5
INITIAL_REASONING=xhigh
CADENCE=hourly
EXECUTION_ENVIRONMENT=local
```

The first phase should run with high reasoning because it defines the safety
boundary for future autonomous operation. New automations should default to
`conservative` approval mode until the user explicitly chooses a more
delegated mode.

## Strategic Outcome

Roadmap Delivery Skill should be able to run with a user-selected autonomy
level, adapt the next run's model after poor delivery quality, and pause itself
when delivery is complete or when stall controls say continuing is wasteful.

The framework should still keep high-risk operations human-approved unless a
specific, durable policy explicitly allows them.

## Design Principles

- Prompt text cannot change the active model. Adaptive policy retargets the
  next run through the runner or saved automation config.
- Pre-approval must be stored in repository artifacts and validated before use.
- The skill must distinguish local delivery work from publication, credentials,
  destructive git, billing, and repository security changes.
- Self-pausing after completion is a safety operation, not publication.
- Every automatic action must leave durable evidence in state, logs, review
  artifacts, and inspection output.
- Backward compatibility matters: old automations without approval policy keep
  conservative behavior.

## Autonomy Modes

Initial modes:

```text
conservative
delegated_local
delegated_delivery
custom
```

Mode meanings:

- `conservative`: current behavior. Ask before automation config edits, pushes,
  installed-skill sync, publication, promotion, destructive git, and external
  side effects.
- `delegated_local`: may edit phase-owned files, create or switch phase
  branches, run verification, commit locally, retarget model/reasoning for the
  saved automation, and pause the saved automation on completion or stall.
- `delegated_delivery`: includes `delegated_local`, plus may push phase
  branches and update saved automation config when policy and readback agree.
- `custom`: explicit per-operation allow/deny map.

Never-auto operations in every mode:

```text
force push
git reset --hard
delete branches or tags
merge or promote to main
publish releases or package registry artifacts
use credentials not already available to the runner
change repository visibility, secrets, permissions, or billing
install or sync global tools outside the approved scope
perform destructive filesystem operations outside phase-owned paths
```

## Adaptive Model Policy

Run quality classifications:

```text
flawless
delivered_with_fixes
verification_failed
review_needs_fix
blocked_local_repairable
blocked_human_required
stalled
retarget_failed
completion_closeout_failed
```

Default adaptive behavior:

- Escalate the next run after `verification_failed`, `review_needs_fix`,
  `delivered_with_fixes`, `stalled`, or `retarget_failed`.
- Do not escalate for `blocked_human_required`; ask for the missing decision or
  permission instead.
- Optionally de-escalate after a configurable number of `flawless` runs.
- Never exceed policy caps for model, reasoning effort, cost class, or provider.

## Target Repository Shape

Recommended end-state layout additions:

```text
schemas/
  approval_policy.schema.json
core/references/
  approval-policy-and-autonomy.md
core/templates/
  approval_policy.md
core/prompts/
  approval_policy_gate.md
  adaptive_model_gate.md
src/roadmap_delivery/
  approval.py
  adaptive.py
docs/
  autonomy-and-approval-policy.md
tests/
  test_approval_policy.py
  test_adaptive_model_policy.py
  test_completion_pause_policy.py
```

Existing files likely to change:

```text
schemas/delivery_state.schema.json
schemas/phase_model_policy.schema.json
src/roadmap_delivery/automation.py
src/roadmap_delivery/cli.py
src/roadmap_delivery/policy.py
src/roadmap_delivery/progress.py
src/roadmap_delivery/reports.py
src/roadmap_delivery/validation.py
core/references/finalization-and-promotion.md
core/references/model-policy-and-stall-control.md
core/references/setup-automation.md
core/references/phase-loop.md
adapters/codex/templates/
adapters/claude/templates/
skill/roadmap-delivery-skill/
README.md
automation/codex_phase_gated_delivery_automation_template.md
```

## Phase Overview

```text
Phase 0 - Policy Contract And Safety Boundary
Phase 1 - Approval Policy Schema And Setup UX
Phase 2 - Approval Gate Enforcement
Phase 3 - Run Quality Classification And Adaptive Model Policy
Phase 4 - Automation Self-Pause On Completion And Stall
Phase 5 - Validation, Inspection, And Migration
Phase 6 - Adapter Package Propagation
Phase 7 - Documentation, Demo, And Closeout
```

## Phase 0 - Policy Contract And Safety Boundary

### Objective

Define exactly which operations can be pre-approved, which operations can never
be automatic, how adaptive model policy reacts to run quality, and when
automation self-pause is allowed.

### Owned Files

```text
roadmaps/in_progress_autonomous_operation_modes_and_adaptive_control_roadmap.md
docs/autonomy-and-approval-policy.md
README.md
automation/README.md
```

### Inputs

- Current phase model and stall control behavior
- Current finalization and completion alert behavior
- Existing validation and inspection reports
- User-reported issues from real roadmap runs

### Implementation Steps

1. Create `docs/autonomy-and-approval-policy.md`.
2. Define approval modes and never-auto operations.
3. Define run quality classifications and adaptive escalation behavior.
4. Define self-pause rules for completion and stall threshold states.
5. Add the roadmap to README and automation README indexes.

### Acceptance Criteria

- The approval boundary is explicit enough to implement without guessing.
- Adaptive model behavior distinguishes poor execution from human-gated
  blockers.
- Self-pause behavior is framed as a safety operation with readback evidence.
- Existing conservative behavior remains the compatibility baseline.

### Required Verification

```bash
git diff --check
python3 -m unittest tests.test_quality_gates -v
```

### Non-Goals

- Do not implement schemas or runtime policy yet.
- Do not change any saved Codex automation config.
- Do not migrate existing automations.

### Stop Conditions

- Stop if the never-auto boundary is ambiguous.
- Stop if self-pause would require unapproved automation config mutation.

## Phase 1 - Approval Policy Schema And Setup UX

### Objective

Add durable approval policy artifacts and setup flow support so users can pick
their autonomy mode once per roadmap automation.

### Owned Files

```text
schemas/approval_policy.schema.json
schemas/delivery_state.schema.json
core/templates/approval_policy.md
core/templates/delivery_state.md
core/templates/automation_guide.md
core/templates/automation_prompt.md
core/references/setup-automation.md
src/roadmap_delivery/approval.py
src/roadmap_delivery/cli.py
tests/test_approval_policy.py
tests/test_cli.py
```

### Implementation Steps

1. Add `approval_policy.schema.json`.
2. Add `approval_policy.json` to the standard automation layout.
3. Extend scaffold/setup planning to include approval policy defaults.
4. Add state fields for active approval mode, policy file path, and last
   approval-policy readback.
5. Add CLI dry-run output that shows which operations are approved.
6. Add tests for conservative, delegated local, delegated delivery, and custom
   policies.

### Acceptance Criteria

- New automations can be scaffolded with an approval policy.
- Missing policy keeps conservative behavior for legacy automations.
- Invalid policies fail validation before delivery work starts.
- Setup docs tell users how to choose an autonomy mode.

### Required Verification

```bash
python3 -m unittest tests.test_approval_policy tests.test_cli -v
python3 -m unittest tests.test_schema_validation -v
python3 scripts/build_codex_package.py --check
git diff --check
```

### Non-Goals

- Do not enforce automatic operations yet.
- Do not add adaptive model escalation yet.

### Stop Conditions

- Stop if the schema cannot represent a custom per-operation allow/deny map.
- Stop if legacy automations without policy become validation errors.

## Phase 2 - Approval Gate Enforcement

### Objective

Make phase-loop, troubleshooting, finalization, and automation retarget flows
consult `approval_policy.json` before asking the user or acting automatically.

### Owned Files

```text
src/roadmap_delivery/approval.py
src/roadmap_delivery/automation.py
src/roadmap_delivery/validation.py
src/roadmap_delivery/reports.py
core/prompts/approval_policy_gate.md
core/references/phase-loop.md
core/references/troubleshooting.md
core/references/finalization-and-promotion.md
core/references/model-policy-and-stall-control.md
skill/roadmap-delivery-skill/references/
tests/test_approval_policy.py
tests/test_helper_scripts.py
tests/test_library_units.py
```

### Implementation Steps

1. Add an approval resolver that returns `allowed`, `ask`, or `forbidden` for
   named operations.
2. Add operation names for local edits, local commits, branch creation,
   automation retarget, automation pause, branch push, installed-skill sync,
   publication, promotion, credentials, and destructive git.
3. Update references so allowed operations can proceed without repeated user
   approval.
4. Keep never-auto operations forbidden even in delegated modes.
5. Surface approval decisions in inspect and validation output.

### Acceptance Criteria

- Conservative mode preserves current ask-first behavior.
- Delegated modes remove manual prompts only for explicitly allowed operations.
- Forbidden operations produce clear blocker messages.
- Review artifacts record when an operation was performed under pre-approval.

### Required Verification

```bash
python3 -m unittest tests.test_approval_policy tests.test_helper_scripts -v
python3 -m unittest discover -s tests -v
python3 scripts/build_codex_package.py --check
git diff --check
```

### Non-Goals

- Do not implement adaptive model policy in this phase.
- Do not change completion finalization semantics yet.

### Stop Conditions

- Stop if an operation cannot be classified safely.
- Stop if generated Codex or Claude package output drifts without matching
  adapter updates.

## Phase 3 - Run Quality Classification And Adaptive Model Policy

### Objective

Classify every run outcome and use policy to retarget the next run's model and
reasoning after non-flawless runs.

### Owned Files

```text
schemas/phase_model_policy.schema.json
schemas/delivery_state.schema.json
src/roadmap_delivery/adaptive.py
src/roadmap_delivery/policy.py
src/roadmap_delivery/progress.py
src/roadmap_delivery/automation.py
src/roadmap_delivery/validation.py
src/roadmap_delivery/reports.py
core/prompts/adaptive_model_gate.md
core/references/model-policy-and-stall-control.md
core/references/phase-loop.md
tests/test_adaptive_model_policy.py
tests/test_helper_scripts.py
tests/test_smoke_demo.py
```

### Implementation Steps

1. Add adaptive model policy fields under `phase_model_policy.json`.
2. Add run quality classification from verification result, review verdict,
   fix iterations, blocker class, stall count, and retarget result.
3. Add state fields for last run quality, adaptive action, model history, and
   escalation/de-escalation counters.
4. Retarget the saved automation only when approval policy allows automation
   config updates.
5. Stop after retarget readback so the next run starts with the chosen model.
6. Add tests for escalation, de-escalation, caps, disabled policy, and
   human-gated blockers.

### Acceptance Criteria

- A non-flawless run can escalate the next run's model or reasoning according
  to policy.
- Human-gated blockers do not waste model escalation.
- Policy caps prevent unbounded cost or provider changes.
- Inspect output explains why the current required model was chosen.

### Required Verification

```bash
python3 -m unittest tests.test_adaptive_model_policy tests.test_helper_scripts -v
python3 -m unittest tests.test_schema_validation -v
python3 -m unittest discover -s tests -v
python3 scripts/build_codex_package.py --check
git diff --check
```

### Non-Goals

- Do not switch the active model inside an already-running session.
- Do not infer provider-specific pricing.

### Stop Conditions

- Stop if the runner's configured model/reasoning cannot be read back.
- Stop if escalation would exceed user-approved caps.

## Phase 4 - Automation Self-Pause On Completion And Stall

### Objective

Allow the framework to pause its saved automation automatically when completion
or stall policy says continuing would be unsafe or wasteful.

### Owned Files

```text
src/roadmap_delivery/automation.py
src/roadmap_delivery/approval.py
src/roadmap_delivery/validation.py
src/roadmap_delivery/reports.py
core/references/finalization-and-promotion.md
core/references/model-policy-and-stall-control.md
core/references/troubleshooting.md
core/templates/automation_prompt.md
skill/roadmap-delivery-skill/references/
tests/test_completion_pause_policy.py
tests/test_helper_scripts.py
```

### Implementation Steps

1. Define `pause_automation_on_completion` and `pause_automation_on_stall`
   policy flags.
2. Treat pause as an allowed safety operation in delegated modes and as an
   explicit setup option in conservative mode.
3. Update finalization so completion pause is attempted before final completed
   state when policy allows it.
4. Update stall threshold handling so the automation pauses or records a
   pause-needed blocker.
5. Require readback of `PAUSED` before setting `completed`; otherwise use
   `completed_pending_pause` with an alert.
6. Add tests for completion pause, stall pause, readback failure, and missing
   approval.

### Acceptance Criteria

- Completed automations pause themselves when policy allows it.
- Stall threshold can pause the automation and alert the operator.
- Failed pause readback never pretends the automation is paused.
- Validation catches completed active automations unless policy/readback
  evidence explains the state.

### Required Verification

```bash
python3 -m unittest tests.test_completion_pause_policy tests.test_helper_scripts -v
python3 -m unittest discover -s tests -v
python3 scripts/build_codex_package.py --check
git diff --check
```

### Non-Goals

- Do not delete automations.
- Do not pause unrelated automations.
- Do not merge or promote completed branches.

### Stop Conditions

- Stop if automation config readback is unavailable.
- Stop if approval policy does not allow self-pause and no explicit user
  approval is present.

## Phase 5 - Validation, Inspection, And Migration

### Objective

Make the new policies visible and enforceable across validators, inspectors,
run logs, migration paths, and existing automation artifacts.

### Owned Files

```text
src/roadmap_delivery/validation.py
src/roadmap_delivery/reports.py
src/roadmap_delivery/progress.py
src/roadmap_delivery/cli.py
schemas/automation_run_log.schema.json
automation/README.md
docs/migration-guide.md
tests/test_schema_validation.py
tests/test_quality_gates.py
tests/test_smoke_demo.py
```

### Implementation Steps

1. Add validation coverage for approval policy, adaptive policy, and self-pause
   evidence.
2. Extend inspect output with autonomy mode, allowed operations, last run
   quality, adaptive model decision, and pause status.
3. Add migration guidance for existing automations.
4. Ensure old automations keep conservative behavior without noisy false
   errors.
5. Add run-log schema coverage for run quality and adaptive decisions.

### Acceptance Criteria

- `validate` fails unsafe or malformed policy states.
- `inspect` gives a clear operator summary of autonomy and model decisions.
- Existing delivered roadmaps still validate or produce only expected legacy
  warnings.
- Migration docs cover how to opt in per automation.

### Required Verification

```bash
python3 -m unittest tests.test_schema_validation tests.test_quality_gates -v
python3 -m unittest tests.test_smoke_demo -v
python3 -m unittest discover -s tests -v
python3 scripts/check_release_privacy.py --repo-root .
git diff --check
```

### Non-Goals

- Do not mutate existing automation policies automatically.
- Do not require all users to adopt delegated modes.

### Stop Conditions

- Stop if validation cannot distinguish legacy conservative behavior from
  malformed delegated policy.

## Phase 6 - Adapter Package Propagation

### Objective

Propagate approval, adaptive model, and self-pause behavior into generated host
packages so Codex, Claude, and generic adapters share the same contract.

### Owned Files

```text
adapters/codex/
adapters/claude/
adapters/generic/
skill/roadmap-delivery-skill/
dist/claude/
dist/generic/
tests/test_adapter_codex.py
tests/test_adapter_parity.py
tests/test_claude_plugin_package.py
tests/test_generic_adapter_package.py
scripts/build_adapters.py
scripts/build_codex_package.py
```

### Implementation Steps

1. Render new references, prompts, and templates into Codex and Claude
   packages.
2. Update parity tests so approval and adaptive behavior cannot drift by host.
3. Update package manifests where new policy files must be included.
4. Ensure Claude and generic packages document unsupported host-specific
   automation pause surfaces and their fallback behavior.
5. Rebuild generated package snapshots.

### Acceptance Criteria

- Generated Codex package includes the new policy rules.
- Claude and generic adapters expose equivalent core behavior or documented
  fallbacks.
- Adapter parity tests cover approval, adaptive model, and self-pause text.
- No generated package drift remains.

### Required Verification

```bash
python3 scripts/build_adapters.py --check
python3 scripts/build_codex_package.py --check
python3 -m unittest tests.test_adapter_codex tests.test_adapter_parity tests.test_claude_plugin_package tests.test_generic_adapter_package -v
python3 -m unittest discover -s tests -v
git diff --check
```

### Non-Goals

- Do not publish packages.
- Do not require live Claude or Codex app execution in CI.

### Stop Conditions

- Stop if a host package cannot represent the new safety boundary clearly.

## Phase 7 - Documentation, Demo, And Closeout

### Objective

Finish operator-facing documentation, demo fixtures, final verification, and
final deep-review prompt so the new autonomous controls are ready to use.

### Owned Files

```text
README.md
docs/autonomy-and-approval-policy.md
docs/compatibility.md
docs/migration-guide.md
docs/release-notes-0.1.0.md
examples/
automation/autonomous-operation-modes-and-adaptive-control/
roadmaps/in_progress_autonomous_operation_modes_and_adaptive_control_roadmap.md
```

### Implementation Steps

1. Add user-facing examples for each autonomy mode.
2. Add an example adaptive model escalation trace.
3. Add completion self-pause and stall self-pause examples.
4. Update compatibility and migration docs.
5. Run full validation, package checks, release privacy scan, and smoke tests.
6. Prepare the final deep-review prompt before marking the roadmap complete.

### Acceptance Criteria

- A user can choose a mode without reading source code.
- The README explains what is and is not pre-approved.
- Demo fixtures cover conservative and delegated behavior.
- Finalization includes a final deep-review prompt or an explicit human waiver.
- Completion pause behavior is verified or the state records
  `completed_pending_pause` with an alert.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_adapters.py --check
python3 scripts/build_codex_package.py --check
python3 scripts/build_release.py --check
python3 scripts/check_release_privacy.py --repo-root .
python3 -m roadmap_delivery.cli validate --repo-root "$PWD" --roadmap-slug autonomous-operation-modes-and-adaptive-control --automation-id autonomous-operation-modes-and-adaptive-control --strict --allow-warning worktree_dirty --json
git diff --check
```

### Non-Goals

- Do not promote to `main`.
- Do not publish releases.
- Do not sync installed skills or plugins unless explicitly approved.

### Stop Conditions

- Stop if final deep-review prompt evidence is missing.
- Stop if completion pause state and saved automation readback disagree.
