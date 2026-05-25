# Framework Core And Release Readiness Roadmap

Status: Completed
Current phase: Complete
Last updated: 2026-05-25
Next action: Review the pushed Phase 10 branch and keep promotion,
publication, and installed-skill synchronization human-approved.
Blocked by: None for roadmap delivery closeout; promotion remains a separate
human-approved decision.

## Purpose

This roadmap turns Roadmap Delivery Skill from a Codex skill snapshot into a
versioned, testable framework with a canonical workflow core.

The deep-research review identified the main technical gap: the product already
has a strong phase-gated workflow, but too much of the source of truth still
lives inside host-specific Codex packaging and duplicated helper scripts.

This roadmap focuses on non-marketing improvements:

- canonical workflow core
- versioned state and policy schemas
- shared Python library and CLI
- generated Codex package
- CI, release, and security gates
- demo fixtures and install smoke tests

Claude and broader host support are handled by the companion roadmap:

```text
roadmaps/not_started_multi_host_adapter_and_claude_plugin_roadmap.md
```

## Automation Artifacts

Phase-gated delivery artifacts for this roadmap live under:

```text
automation/framework-core-and-release-readiness/
```

Codex app automation:

- ID: `framework-core-and-release-readiness`
- Status: PAUSED
- Cadence: hourly
- Model: `gpt-5.5`
- Reasoning effort: `xhigh`
- Execution environment: local

## Strategic Outcome

Roadmap Delivery Skill should become a framework with Codex as one adapter, not
a framework whose source of truth is a Codex skill directory.

The repository should be able to answer:

- What is the canonical workflow contract?
- What state schema version does this automation use?
- Which host adapter generated this package?
- Can the package be installed and validated from a clean checkout?
- Can CI catch drift between core docs, schemas, scripts, and generated skill
  packages?
- Can release artifacts be produced without exposing local private paths or
  secrets?

## Design Principles

- Keep the file-backed control plane. Roadmap, state, log, reviews, and branch
  evidence remain durable files.
- Make the canonical source host-neutral. Host packages should adapt the core,
  not redefine it.
- Prefer schema-backed validation over filename and path heuristics.
- Preserve the existing Codex skill install path during migration.
- Keep generated artifacts either clearly generated or snapshot-tested.
- Make blocked remediation a framework invariant.
- Keep publication, promotion, destructive git, and credential use
  human-approved.
- Avoid service-backed control planes in this roadmap.

## Phase 0 Migration Contract

Phase 0 fixes the migration boundary before any files move. Later phases may
create new directories, schemas, and generated packages, but they must preserve
the compatibility promises in this section.

### Canonical Core Responsibilities

The canonical source of truth will move into host-neutral repository sources:

- `core/references/` owns the workflow rules for setup, phase delivery,
  review/fix loops, state and branch handling, finalization, troubleshooting,
  model policy, stall control, and blocked remediation.
- `core/templates/` owns durable artifact templates for delivery state, logs,
  reviews, automation guides, and automation prompts.
- `core/prompts/` owns reusable guard text for blocked remediation, model
  policy gates, review gates, and completion hard stops.
- `schemas/` owns versioned JSON contracts for state, policy, review, and run
  log artifacts.
- `src/roadmap_delivery/` owns shared Python behavior used by CLI commands,
  helper-script wrappers, validators, inspection, rendering, and packaging.

### Codex Adapter Responsibilities

Codex-specific behavior remains adapter-owned:

- `skill/roadmap-delivery-skill/SKILL.md` owns Codex skill metadata, trigger
  routing, and Codex-specific operating notes.
- `skill/roadmap-delivery-skill/agents/openai.yaml` owns Codex reviewer-agent
  packaging.
- Codex automation prompt expectations remain adapter guidance because the
  Codex app controls automation status, model, reasoning effort, cwd, cadence,
  and execution environment.
- Codex reference files must mirror canonical core behavior after Phase 1, with
  Codex-only notes isolated as adapter overlays or explicitly documented
  exceptions.

### Generated And Hand-Maintained Files

Generated-file strategy is committed-source first:

- Through Phase 4, `skill/roadmap-delivery-skill/` remains the hand-maintained,
  installable Codex skill snapshot.
- Starting in Phase 5, `skill/roadmap-delivery-skill/` becomes the committed
  generated Codex package, rendered from canonical core sources plus
  `adapters/codex/` overlays and protected by snapshot tests.
- `dist/` is reserved for release bundles and check artifacts. It is not the
  only source of the installable Codex package.
- Generated-file headers may be added only where they do not reduce skill or
  prompt readability.
- Any generated output drift must be caught by tests or release checks before
  publication.

### Compatibility Promise

Existing Codex users must keep working during the migration:

- The repository path `skill/roadmap-delivery-skill/` remains present and
  installable.
- Existing helper script entrypoints under
  `skill/roadmap-delivery-skill/scripts/` remain available as wrappers even
  after shared library extraction.
- The repository-local automation layout under `automation/<roadmap-slug>/`
  remains supported.
- Legacy state artifacts without newer schema fields keep a warning-backed
  compatibility path until an explicit migration phase changes that contract.
- Installed copies under `${CODEX_HOME:-$HOME/.codex}/skills/` are not mutated
  by this roadmap. Synchronization remains an explicit install or maintenance
  action.

### Release Boundary

Release work is separate from core and adapter migration:

- Release phases add `VERSION`, `CHANGELOG.md`, reproducible bundles, checksum
  generation, release checks, and privacy/security gates.
- Publication to GitHub Releases, package indexes, or other external channels
  remains human-approved.
- Local automation artifacts may support development and review, but release
  packages must exclude or sanitize private paths, credentials, and
  operator-local state.

### Companion Roadmap Dependency

The multi-host adapter and Claude plugin roadmap depends on this roadmap
through Phase 10 closeout. It should consume the canonical workflow contract,
schemas, shared library, CLI, generated Codex adapter baseline, release checks,
privacy guardrails, and closeout docs from this roadmap before building Claude
packaging or parity claims. This roadmap does not create a Claude plugin.

## Target Repository Shape

Recommended end-state layout:

```text
core/
  references/
  templates/
  prompts/
schemas/
  delivery_state.schema.json
  phase_model_policy.schema.json
  review_artifact.schema.json
  automation_run_log.schema.json
src/
  roadmap_delivery/
    __init__.py
    cli.py
    git.py
    state.py
    policy.py
    validation.py
    automation.py
    rendering.py
adapters/
  codex/
    templates/
    package.py
skill/
  roadmap-delivery-skill/
tests/
  fixtures/
  snapshots/
  test_cli.py
  test_schema.py
  test_adapter_codex.py
examples/
  demo-roadmap/
.github/
  workflows/
```

## Phase Overview

```text
Phase 0 - Scope And Migration Contract
Phase 1 - Canonical Core Layout
Phase 2 - JSON Schemas And Versioned State
Phase 3 - Shared Python Library Extraction
Phase 4 - Stable CLI
Phase 5 - Codex Adapter Generation
Phase 6 - CI And Quality Gates
Phase 7 - Security And Privacy Guardrails
Phase 8 - Demo Fixture And Smoke Tests
Phase 9 - Release And Versioning System
Phase 10 - Migration, Documentation, And Closeout
```

## Phase 0 - Scope And Migration Contract

Delivery status: Delivered 2026-05-24.

### Objective

Define exactly what becomes canonical core, what remains Codex-specific, and
what backward compatibility must be preserved.

### Owned Files

```text
roadmaps/in_progress_framework_core_and_release_readiness_roadmap.md
README.md
```

### Inputs

- `deep-research-report-ard.md`
- Current `skill/roadmap-delivery-skill/`
- Current helper scripts under `skill/roadmap-delivery-skill/scripts/`
- Current automation template
- Current phase model policy roadmap

### Implementation Steps

1. Define the canonical source of truth:
   - core workflow references
   - prompt fragments
   - schemas
   - shared Python library
2. Define host-specific surfaces:
   - Codex `SKILL.md`
   - Codex `agents/openai.yaml`
   - Codex automation prompt expectations
3. Define generated versus hand-maintained files.
4. Define migration rules:
   - existing `skill/roadmap-delivery-skill/` remains installable
   - current helper script entrypoints remain available
   - current automation artifact layout remains supported
5. Decide whether generated files are committed in `skill/` or produced only
   under `dist/`.
6. Add a README pointer to this roadmap and its companion adapter roadmap.

### Acceptance Criteria

- The roadmap clearly separates core, adapter, generated artifact, and release
  responsibilities.
- Existing Codex users have a compatibility promise.
- The companion multi-host roadmap has a clear dependency on this roadmap.
- No implementation files move in this phase.

### Required Verification

- Manually inspect the roadmap for conflicts with current skill behavior.
- Confirm no Codex install path is removed or renamed.
- Run:

```bash
git diff --check
```

### Non-Goals

- Do not refactor scripts.
- Do not add schemas yet.
- Do not create a Claude plugin.

### Stop Conditions

- Stop if the generated-file strategy is undecided.
- Stop if preserving the current Codex install path is not possible.

## Phase 1 - Canonical Core Layout

Delivery status: Delivered 2026-05-24.

### Objective

Create the canonical `core/` layout and move or copy workflow references into
host-neutral source files without changing runtime behavior.

### Owned Files

```text
core/references/*.md
core/templates/*.md
core/prompts/*.md
skill/roadmap-delivery-skill/references/*.md
automation/codex_phase_gated_delivery_automation_template.md
tests/test_core_sources.py
```

### Implementation Steps

1. Create `core/references/` for host-neutral workflow references:
   - setup automation
   - phase loop
   - review and fix
   - state, log, and branches
   - finalization and promotion
   - troubleshooting
   - model policy and stall control
2. Create `core/templates/` for shared artifact templates:
   - delivery state
   - delivery log
   - review artifact
   - automation guide
   - automation prompt
3. Create `core/prompts/` for reusable prompt fragments:
   - blocked remediation
   - model policy gate
   - review gate
   - completion hard stop
4. Keep the Codex package unchanged functionally.
5. Add tests that assert every Codex reference has a canonical core source or
   an explicit adapter-only reason.

### Acceptance Criteria

- Core files exist and are readable independently of Codex.
- Codex references still exist at their current paths.
- There is no behavioral drift in the installed Codex package.
- Tests detect missing canonical source files.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=$TMPDIR/roadmap-delivery-core-compile-pycache \
  python3 -m py_compile \
  skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py \
  skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
git diff --check
```

### Non-Goals

- Do not generate host packages yet.
- Do not remove existing `skill/roadmap-delivery-skill/references/`.

### Stop Conditions

- Stop if a reference cannot be expressed without Codex-specific assumptions.

## Phase 2 - JSON Schemas And Versioned State

Delivery status: Delivered 2026-05-24.

### Objective

Add explicit schemas for state, policy, reviews, and run logs so drift is caught
by tools instead of inferred from conventions.

### Owned Files

```text
schemas/delivery_state.schema.json
schemas/phase_model_policy.schema.json
schemas/review_artifact.schema.json
schemas/automation_run_log.schema.json
tests/test_schema_validation.py
skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py
```

### Implementation Steps

1. Add `schema_version` to canonical state examples.
2. Create JSON Schema for `delivery_state.json`.
3. Create JSON Schema for `phase_model_policy.json`.
4. Define review artifact requirements:
   - roadmap path
   - phase
   - reviewed timestamp
   - findings
   - verification evidence
   - verdict
5. Define JSONL schema for `automation_run_log.jsonl` entries.
6. Update validators to load and apply schemas.
7. Keep compatibility mode for legacy states without `schema_version`, but warn.
8. Add fixtures for valid, legacy, and invalid states.

### Acceptance Criteria

- Valid current automation artifacts pass schema validation.
- Missing or invalid `schema_version` is reported clearly.
- Legacy state files still pass with a migration warning.
- Review verdict validation uses schema-aware logic.
- Automation run log entries are validated line by line.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py \
  --repo-root /Users/dzianissokalau/Documents/projects/roadmap-delivery-automation \
  --roadmap-slug phase-model-policy-and-stall-control \
  --automation-id phase-model-policy-and-stall-control \
  --json
git diff --check
```

### Non-Goals

- Do not require all historical automation artifacts to be migrated in this
  phase.
- Do not introduce a database or service-backed control plane.

### Stop Conditions

- Stop if schema validation would reject current supported legacy artifacts
  without a migration path.

## Phase 3 - Shared Python Library Extraction

Delivery status: Delivered 2026-05-25.

### Objective

Extract duplicated helper-script logic into a shared package while preserving
existing script entrypoints.

### Owned Files

```text
src/roadmap_delivery/
skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py
skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
tests/test_helper_scripts.py
tests/test_library_units.py
pyproject.toml
```

### Implementation Steps

1. Create `src/roadmap_delivery/`.
2. Move shared logic into modules:
   - `paths.py`
   - `toml.py`
   - `git.py`
   - `state.py`
   - `policy.py`
   - `validation.py`
   - `reports.py`
3. Convert helper scripts into thin wrappers.
4. Keep script command-line behavior stable.
5. Add unit tests for library functions.
6. Add regression tests for existing helper-script fixtures.
7. Ensure the installed Codex skill can still run scripts without requiring an
   editable package install, or document and package the dependency.

### Acceptance Criteria

- Duplicated TOML parsing, slug normalization, path resolution, roadmap
  reference extraction, and git helpers are centralized.
- Current script outputs remain stable except for intentional new fields.
- Tests pass from a clean checkout.
- Existing script paths remain executable.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=$TMPDIR/roadmap-delivery-library-compile-pycache \
  python3 -m py_compile \
  skill/roadmap-delivery-skill/scripts/inspect_delivery_state.py \
  skill/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py
```

### Non-Goals

- Do not change the public CLI names yet.
- Do not remove compatibility wrappers.

### Stop Conditions

- Stop if wrapper scripts cannot import the shared package in installed-skill
  mode.

## Phase 4 - Stable CLI

Delivery status: Delivered 2026-05-25.

### Objective

Expose stable commands for inspection, validation, scaffolding, and packaging.

### Owned Files

```text
src/roadmap_delivery/cli.py
pyproject.toml
README.md
tests/test_cli.py
```

### Implementation Steps

1. Add a console script, tentatively `roadmap-delivery`.
2. Implement subcommands:
   - `inspect`
   - `validate`
   - `scaffold`
   - `package`
   - `version`
3. Keep existing helper scripts as compatibility wrappers.
4. Add JSON and text output modes.
5. Add `--strict`, `--allow-warning`, and `--repo-root` consistently.
6. Add `scaffold` dry-run mode for new automation directories.
7. Add `package` dry-run mode for Codex package rendering.

### Acceptance Criteria

- CLI can validate the current repository automation.
- CLI output includes stable machine-readable fields.
- Existing helper scripts call the same library paths as CLI.
- README contains CLI usage examples.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m roadmap_delivery.cli version
python3 -m roadmap_delivery.cli validate \
  --repo-root /Users/dzianissokalau/Documents/projects/roadmap-delivery-automation \
  --roadmap-slug phase-model-policy-and-stall-control \
  --automation-id phase-model-policy-and-stall-control \
  --json
```

### Non-Goals

- Do not publish to PyPI in this phase.
- Do not build a TUI or web UI.

### Stop Conditions

- Stop if packaging requires a dependency that breaks installed-skill usage.

## Phase 5 - Codex Adapter Generation

Delivery status: Delivered 2026-05-25.

### Objective

Make the Codex skill package render from canonical core sources and snapshot
test the output.

### Owned Files

```text
adapters/codex/
skill/roadmap-delivery-skill/
tests/snapshots/codex/
tests/test_adapter_codex.py
scripts/build_codex_package.py
```

### Implementation Steps

1. Add Codex adapter templates for:
   - `SKILL.md`
   - `agents/openai.yaml`
   - references
   - scripts
2. Add a renderer that builds `skill/roadmap-delivery-skill/` from core
   sources plus adapter overlays.
3. Snapshot-test generated files.
4. Ensure generated package passes `quick_validate.py`.
5. Preserve manual install instructions.
6. Add a generated-file header only where it will not harm skill readability.

### Acceptance Criteria

- `skill/roadmap-delivery-skill/` can be regenerated from core and adapter
  sources.
- Snapshot tests catch unintended prompt/reference drift.
- Installed Codex package remains valid.
- Existing users can keep installing from `skill/roadmap-delivery-skill/`.

### Required Verification

```bash
python3 scripts/build_codex_package.py --check
python3 -m unittest discover -s tests -v
PYTHONPATH=/private/tmp/autonomous-roadmap-delivery-pyyaml \
  python3 /Users/dzianissokalau/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skill/roadmap-delivery-skill
```

### Non-Goals

- Do not create Claude package generation yet.
- Do not publish a release artifact yet.

### Stop Conditions

- Stop if generated output differs from hand-maintained package without an
  explicit migration note.

## Phase 6 - CI And Quality Gates

Delivery status: Delivered 2026-05-25.

### Objective

Add GitHub Actions so tests, schemas, packaging checks, and basic security
checks run automatically.

### Owned Files

```text
.github/workflows/ci.yml
.github/workflows/release-check.yml
tests/
README.md
```

### Implementation Steps

1. Add CI workflow for:
   - unit tests
   - py_compile
   - schema validation fixtures
   - Codex package generation check
   - skill validation where dependencies are available
2. Add markdown/ASCII/whitespace checks.
3. Add a release-check workflow that builds artifacts without publishing.
4. Add status badges only after workflow names are stable.
5. Document local equivalents of every CI command.

### Acceptance Criteria

- CI passes on a clean branch.
- Local commands match CI commands.
- Failure messages are actionable.
- CI does not require private Codex directories or credentials.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
git diff --check
```

After pushing:

```bash
gh run list --limit 5
```

### Non-Goals

- Do not require cloud credentials.
- Do not deploy release artifacts.

### Stop Conditions

- Stop if CI cannot run without local private paths.

## Phase 7 - Security And Privacy Guardrails

Delivery status: Delivered 2026-05-25.

### Objective

Document and test privacy/safety expectations for committed automation
artifacts and release packages.

### Owned Files

```text
SECURITY.md
docs/privacy-and-sanitization.md
scripts/check_release_privacy.py
tests/test_privacy_sanitization.py
.github/workflows/ci.yml
```

### Implementation Steps

1. Add `SECURITY.md` with:
   - supported versions
   - responsible disclosure contact/process
   - unsafe automation surfaces
   - secret-handling expectations
2. Add privacy guidance for:
   - local paths
   - operator names
   - repository remotes
   - secrets and tokens
   - review artifacts
3. Add a privacy scanner for release-bound artifacts.
4. Fail CI on obvious secrets and unsanitized local absolute paths in release
   packages.
5. Add a manual release checklist.

### Acceptance Criteria

- Release packages can be scanned before publication.
- CI catches common local-path and secret leaks.
- Docs explain what automation artifacts are safe to commit.
- Security policy exists and is linked from README.

### Required Verification

```bash
python3 scripts/check_release_privacy.py --repo-root .
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not build a full DLP system.
- Do not rewrite historical git history in this phase.

### Stop Conditions

- Stop if current release-bound files fail privacy checks and need a product
  decision about what to sanitize.

## Phase 8 - Demo Fixture And Smoke Tests

Delivery status: Delivered 2026-05-25.

### Objective

Add a small realistic demo repository fixture and end-to-end smoke tests for
scaffold, validate, inspect, and one phase loop.

### Owned Files

```text
examples/demo-roadmap/
tests/test_smoke_demo.py
README.md
```

### Implementation Steps

1. Create a tiny demo roadmap with 2-3 phases.
2. Add expected automation artifacts for the fixture.
3. Add tests that run:
   - scaffold dry-run
   - validate
   - inspect
   - blocked-remediation fixture
   - model-policy mismatch fixture
4. Add README quickstart using the demo.
5. Keep demo independent of private Codex paths.

### Acceptance Criteria

- A new user can understand the workflow from the demo alone.
- Smoke tests run without network or credentials.
- Demo shows both successful delivery and safe blocker behavior.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m roadmap_delivery.cli validate \
  --repo-root examples/demo-roadmap \
  --roadmap-slug demo-roadmap \
  --json
```

### Non-Goals

- Do not create a separate demo GitHub repository in this phase.
- Do not include a large sample app.

### Stop Conditions

- Stop if smoke tests need live Codex app automation access.

## Phase 9 - Release And Versioning System

Delivery status: Delivered 2026-05-25.

### Objective

Create versioned release artifacts and a repeatable release checklist.

### Owned Files

```text
CHANGELOG.md
VERSION
scripts/build_release.py
dist/
.github/workflows/release-check.yml
README.md
```

### Implementation Steps

1. Choose versioning policy.
2. Add `VERSION`.
3. Add `CHANGELOG.md`.
4. Build release artifacts:
   - source archive
   - Codex skill package
   - schema bundle
   - CLI package artifact if available
5. Add checksum generation.
6. Add release-check workflow.
7. Document upgrade and rollback process.

### Acceptance Criteria

- A release can be built locally from a clean checkout.
- Release artifacts contain no private paths or secrets.
- Changelog identifies compatibility notes.
- Codex package artifact validates.

### Required Verification

```bash
python3 scripts/build_release.py --check
python3 scripts/check_release_privacy.py --repo-root .
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not publish to PyPI, npm, or Homebrew yet.
- Do not publish GitHub Release without explicit approval.

### Stop Conditions

- Stop if release artifacts cannot be reproduced from committed files.

## Phase 10 - Migration, Documentation, And Closeout

Delivery status: Delivered 2026-05-25.

### Objective

Finish the framework hardening migration and leave the repository ready for
multi-host adapter work.

### Owned Files

```text
README.md
docs/
roadmaps/delivered_framework_core_and_release_readiness_roadmap.md
roadmaps/not_started_multi_host_adapter_and_claude_plugin_roadmap.md
automation/README.md
```

### Implementation Steps

1. Update README with:
   - quickstart
   - architecture summary
   - install options
   - local verification
   - compatibility matrix
   - release links
2. Fix stale `automation/README.md`.
3. Add contributor workflow.
4. Add migration guide from pre-core layout.
5. Update companion adapter roadmap with any new dependencies.
6. Run final test, schema, package, and privacy gates.
7. Write closeout review and release notes.

### Acceptance Criteria

- Repository has a clear framework structure.
- Codex package is still valid and installable.
- CI, schema, privacy, and release-check gates exist.
- Docs no longer contradict current state.
- Companion multi-host roadmap is ready to start.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_codex_package.py --check
python3 scripts/build_release.py --check
python3 scripts/check_release_privacy.py --repo-root .
git diff --check
```

### Non-Goals

- Do not build the Claude plugin in this roadmap.
- Do not introduce a hosted service.

### Stop Conditions

- Stop if final docs or release artifacts contain stale project names or private
  local paths.

## Cross-Phase Acceptance Criteria

This roadmap is complete when:

- canonical core files exist and are the workflow source of truth
- state, policy, review, and run-log schemas exist
- helper scripts share one Python library
- a stable CLI exists
- Codex package generation is tested
- CI runs tests, schema checks, package checks, and privacy checks
- release artifacts can be built locally
- docs are internally consistent
- the installed Codex package remains valid
- the multi-host adapter roadmap can start without redesigning the core

## Backlog

- Publish CLI package to PyPI.
- Add Homebrew or npm wrapper.
- Add richer telemetry and metrics collection.
- Add service-backed control plane research.
- Add hosted eval corpus.
- Add docs site after release packaging stabilizes.
