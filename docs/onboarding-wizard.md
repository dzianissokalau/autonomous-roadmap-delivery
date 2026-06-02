# Onboarding Wizard Contract

This document defines the target contract for the setup wizard. It is a Phase 0
contract only; later phases implement the CLI and scaffold integration.

The wizard should guide a user from an empty or existing checkout to a validated
starter roadmap automation contract. It must support a safe demo path before it
offers real-project writes.

## Target Commands

The future command surface should be explicit about whether it is planning,
writing local files, or preparing a saved automation prompt:

```bash
roadmap-delivery wizard --repo-root "$PWD" --dry-run --json
roadmap-delivery wizard --repo-root "$PWD" --write --json
roadmap-delivery wizard --repo-root "$PWD" --from-demo --dry-run --json
```

`--dry-run` is the default recommendation for first use. `--write` may create
repository-local artifacts only after showing the paths and approval policy.
The wizard must not edit a live Codex or Claude home, push branches, publish
artifacts, or promote work.

## Required Inputs

The wizard must collect or derive:

- roadmap title
- roadmap slug
- automation id
- repository root
- initial phase name
- phase-owned files
- acceptance criteria
- required verification commands
- non-goals
- stop conditions
- approval mode
- default model
- default reasoning effort
- optional per-phase model and reasoning overrides
- execution environment label
- cadence recommendation

The wizard should default to conservative approval mode and local execution.
It should require explicit confirmation before any delegated mode is selected.

## Optional Inputs

The wizard may ask for:

- branch prefix, defaulting to `codex/`
- finalization model and reasoning effort
- alert mode, defaulting to local alert files
- provider-role config path
- existing roadmap path
- existing automation directory
- paths to copy from the demo fixture
- whether to create placeholder review and alert directories

Optional values must be visible in the JSON output. Missing optional values
must not be guessed silently.

## Generated Files

For a new roadmap automation, the wizard should generate or plan:

```text
roadmaps/not_started_<roadmap_slug>_roadmap.md
automation/<roadmap_slug>/automation_guide.md
automation/<roadmap_slug>/delivery_state.json
automation/<roadmap_slug>/delivery_log.md
automation/<roadmap_slug>/review_fix_state.json
automation/<roadmap_slug>/review_fix_log.md
automation/<roadmap_slug>/phase_model_policy.json
automation/<roadmap_slug>/approval_policy.json
automation/<roadmap_slug>/automation_run_log.jsonl
automation/<roadmap_slug>/reviews/.gitkeep
automation/<roadmap_slug>/alerts/.gitkeep
```

Generated state must include `schema_version: 1`, the roadmap path, current
phase, review iteration limits, model/readback fields, approval policy
readback, run/stall counters, completion fields, and blocked-remediation fields
used by the validators.

Generated approval policy must be valid against
`schemas/approval_policy.schema.json`. Generated model policy must be valid
against `schemas/phase_model_policy.schema.json`.

## Validation Contract

Every wizard result must include the next validation commands:

```bash
python3 -m roadmap_delivery.cli validate \
  --repo-root "$PWD" \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --strict \
  --allow-warning missing_automation_config \
  --allow-warning current_branch_name_mismatch \
  --allow-warning worktree_dirty \
  --json

python3 -m roadmap_delivery.cli inspect \
  --repo-root "$PWD" \
  --roadmap-slug <roadmap-slug> \
  --automation-id <automation-id> \
  --json
```

The wizard should explain warnings as setup evidence. It must not mark a phase
delivered or advance the roadmap.

## Safety Warnings

The wizard must warn before any path that would:

- write outside the selected repository root
- overwrite an existing roadmap or automation directory
- depend on credentials
- edit a live saved automation config
- install or sync global tools
- commit, push, merge, promote, publish, or delete branches
- run destructive filesystem or git operations

For existing files, the wizard should emit a conflict report and stop unless a
future implementation adds a narrow, reviewed merge mode.

## Output Shape

JSON output should be stable enough for tests and demos:

```json
{
  "command": "wizard",
  "status": "planned",
  "repo_root": "/path/to/repo",
  "roadmap_slug": "example-roadmap",
  "automation_id": "example-roadmap-delivery",
  "approval_mode": "conservative",
  "model_policy": {
    "default_model": "gpt-5.5",
    "default_reasoning_effort": "high",
    "phase_overrides": {}
  },
  "planned_paths": [],
  "would_create": [],
  "warnings": [],
  "errors": [],
  "next_commands": []
}
```

Text output may be friendlier, but it must be derived from the same structured
result so tests can verify the contract.

## Demo Requirements

The wizard should offer a demo route before real-project writes:

- validate `examples/demo-roadmap`
- inspect `examples/demo-roadmap`
- show the blocked-remediation fixture
- show the model-policy mismatch fixture
- show the scaffold dry-run output

The demo route must not require a live host binary. If a host binary is present,
live checks may be offered as optional follow-up only.
