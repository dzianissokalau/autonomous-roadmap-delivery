# Demo Roadmap

Status: In Progress
Current phase: Phase 1 - Add Smoke Checked Command
Last updated: 2026-05-25
Next action: Continue Phase 1 on `codex/demo-roadmap-phase-1`.
Blocked by: None

## Purpose

This demo is a small realistic roadmap delivery repository. It is intentionally
minimal so new users can inspect every control-plane artifact without private
paths, credentials, network calls, or live Codex app automation access.

## Automation Artifacts

```text
automation/demo_roadmap/
```

Sample saved automation configs are stored under:

```text
automation-config/demo-roadmap-delivery/
```

## Phase Overview

```text
Phase 0 - Establish Fixture Contract
Phase 1 - Add Smoke Checked Command
Phase 2 - Close Out Demo
```

## Phase 0 - Establish Fixture Contract

Delivery status: Delivered 2026-05-25.

### Objective

Create the demo roadmap and automation artifacts with one completed phase gate.

### Owned Files

```text
roadmaps/in_progress_demo_roadmap.md
automation/demo_roadmap/
README.md
```

### Implementation Steps

1. Create the demo roadmap with three small phases.
2. Add delivery state, log, review, model policy, and run-log artifacts.
3. Record a delivered Phase 0 review.
4. Leave Phase 1 as the current not-started phase.

### Acceptance Criteria

- The demo validates through the roadmap delivery CLI.
- The delivered review is readable without surrounding transcript context.
- The next phase is explicit and branch-scoped.

### Required Verification

```bash
python3 -m roadmap_delivery.cli validate \
  --repo-root examples/demo-roadmap \
  --roadmap-slug demo-roadmap \
  --json
```

### Non-Goals

- Do not require live automation access.
- Do not include a large sample application.

### Stop Conditions

- Stop if the fixture needs credentials or network access.

## Phase 1 - Add Smoke Checked Command

### Objective

Add a tiny command that prints the current demo roadmap phase and cover it with
a local smoke test.

### Owned Files

```text
demo_tool/
tests/
README.md
automation/demo_roadmap/
```

### Implementation Steps

1. Add a small dependency-free command module under `demo_tool/`.
2. Add a smoke test that runs the command locally.
3. Update the demo README with the command.
4. Record verification and review evidence before advancing to Phase 2.

### Acceptance Criteria

- The command runs without network or credentials.
- The smoke test proves the command reads the committed roadmap state.
- Blocked remediation remains available if the command artifact is missing.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m roadmap_delivery.cli validate \
  --repo-root . \
  --roadmap-slug demo-roadmap \
  --json
```

### Non-Goals

- Do not publish this fixture as a separate repository.
- Do not add external dependencies.

### Stop Conditions

- Stop if the smoke test needs live Codex app automation access.

## Phase 2 - Close Out Demo

### Objective

Mark the demo complete after the smoke command and documentation are reviewed.

### Owned Files

```text
roadmaps/in_progress_demo_roadmap.md
automation/demo_roadmap/
README.md
```

### Implementation Steps

1. Confirm Phase 1 verification and review are delivered.
2. Mark all phases complete in state.
3. Write a completed operator alert.
4. Keep the sample automation paused or explicitly guarded.

### Acceptance Criteria

- Completion state includes a completed alert.
- The automation config is paused or has a hard-stop guard.
- Final validation passes.

### Required Verification

```bash
python3 -m roadmap_delivery.cli validate \
  --repo-root . \
  --roadmap-slug demo-roadmap \
  --json
```

### Non-Goals

- Do not push or publish release artifacts.

### Stop Conditions

- Stop if completion would require a live automation config change.
