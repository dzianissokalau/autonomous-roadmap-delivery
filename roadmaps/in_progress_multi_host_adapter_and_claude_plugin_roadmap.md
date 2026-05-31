# Multi-Host Adapter And Claude Plugin Roadmap

Status: Active
Current phase: Phase 6 - Provider-Neutral Model Role Config
Last updated: 2026-05-31
Next action: Deliver Phase 6 with the configured phase-gated automation.
Blocked by: None.

## Purpose

This roadmap makes Roadmap Delivery Skill portable beyond Codex by adding a
multi-host adapter layer and a first-class Claude plugin package.

It intentionally depends on the framework core roadmap. The workflow contract,
schemas, shared library, CLI, generated Codex adapter, release checks, and
privacy gates should be stable before Claude work starts in earnest.

Dependency roadmap:

```text
roadmaps/delivered_framework_core_and_release_readiness_roadmap.md
```

## Automation Artifacts

Phase-gated delivery artifacts for this roadmap live under:

```text
automation/multi-host-adapter-and-claude-plugin/
```

Codex app automation:

- ID: `multi-host-adapter-and-claude-plugin`
- Status: ACTIVE
- Cadence: hourly
- Model: `gpt-5.5`
- Reasoning effort: `xhigh`
- Execution environment: local

## Strategic Outcome

Roadmap Delivery Skill should support multiple AI coding hosts from one
canonical workflow contract.

The first supported hosts should be:

- Codex skill package
- Claude plugin package

The work should prove that the product is not merely a Codex-local instruction
bundle. It is a phase-gated roadmap delivery framework with host-specific
packaging.

## Design Principles

- Do not fork the workflow logic per host.
- Generate host packages from canonical core sources.
- Keep host capability differences explicit.
- Snapshot-test generated prompts and manifests.
- Keep model-role policy provider-neutral.
- Treat Codex and Claude parity as a testable product claim.
- Keep publication and release steps human-approved.
- Avoid adding adapters for every ecosystem until Codex and Claude are stable.

## Target Repository Shape

Recommended end-state layout:

```text
host-capabilities/
  codex.yaml
  claude.yaml
config/
  providers.example.yaml
adapters/
  codex/
    templates/
    package.py
  claude/
    templates/
    package.py
    plugin.json.template
tests/
  snapshots/
    codex/
    claude/
  test_adapter_parity.py
  test_claude_plugin_package.py
dist/
  codex/
  claude/
docs/
  compatibility.md
  installing-codex.md
  installing-claude.md
```

## Phase Overview

```text
Phase 0 - Host Capability Contract
Phase 1 - Adapter Build System
Phase 2 - Codex Generated Package Baseline
Phase 3 - Claude Plugin Skeleton
Phase 4 - Claude Skills And Reviewer Agent
Phase 5 - Claude Hooks And Safety Guards
Phase 6 - Provider-Neutral Model Role Config
Phase 7 - Adapter Parity And Snapshot Tests
Phase 8 - Install And Runtime Smoke Tests
Phase 9 - Generic Adapter Preparation
Phase 10 - Compatibility Docs And Release Artifacts
```

## Phase 0 - Host Capability Contract

Delivery status: Delivered 2026-05-31.

### Objective

Define the supported host capabilities and the parity promise before adapter
implementation begins.

### Owned Files

```text
roadmaps/in_progress_multi_host_adapter_and_claude_plugin_roadmap.md
docs/compatibility.md
host-capabilities/codex.yaml
host-capabilities/claude.yaml
```

### Inputs

- Framework core roadmap through Phase 10 closeout
- Current Codex skill package
- Claude plugin packaging requirements
- Current model-policy and blocked-remediation framework behavior
- Framework compatibility, migration, contributor, and release notes docs

### Implementation Steps

1. Define supported host capability categories:
   - skill/instruction packaging
   - agent/subagent support
   - hooks/guards
   - recurring automation
   - model selection
   - filesystem sandboxing
   - approval boundaries
   - MCP/tool integration
2. Create `host-capabilities/codex.yaml`.
3. Create `host-capabilities/claude.yaml`.
4. Define parity levels:
   - required parity
   - host-specific enhancement
   - unsupported by host
   - future work
5. Decide whether Claude support is a parity target or a best-effort target.
6. Document what "supported" means.

### Acceptance Criteria

- Codex and Claude capabilities are explicit and versioned.
- Adapter work has a clear compatibility contract.
- Missing host capabilities are documented instead of hidden in prompts.
- The roadmap states which features must behave the same across hosts.

### Required Verification

- Manually inspect compatibility docs against current core behavior.
- Run:

```bash
git diff --check
```

### Non-Goals

- Do not implement adapter rendering.
- Do not create the Claude plugin package yet.

### Stop Conditions

- Stop if the support promise for Claude is undecided.

## Phase 1 - Adapter Build System

Delivery status: Delivered 2026-05-31.

### Objective

Create a host adapter build system that can render packages from canonical core
sources.

### Owned Files

```text
src/roadmap_delivery/rendering.py
adapters/codex/package.py
adapters/claude/package.py
scripts/build_adapters.py
tests/test_adapter_build_system.py
```

### Implementation Steps

1. Define a renderer interface:
   - input core references
   - input templates
   - input host capabilities
   - output package directory
2. Add adapter metadata model.
3. Add package rendering for Codex and Claude as empty or minimal packages.
4. Add `--check` mode.
5. Add snapshot output directories.
6. Ensure generated artifacts are deterministic.

### Acceptance Criteria

- Adapter renderer can produce deterministic output for Codex and Claude.
- `--check` fails when generated output is stale.
- Tests do not require host applications to be installed.

### Required Verification

```bash
python3 scripts/build_adapters.py --check
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not implement complete Claude behavior yet.
- Do not publish packages.

### Stop Conditions

- Stop if adapter output cannot be made deterministic.

## Phase 2 - Codex Generated Package Baseline

Delivery status: Delivered 2026-05-31.

### Objective

Make the Codex package the baseline generated adapter and prove no behavior is
lost.

### Owned Files

```text
adapters/codex/
skill/roadmap-delivery-skill/
dist/codex/
tests/snapshots/codex/
tests/test_adapter_codex.py
```

### Implementation Steps

1. Render Codex `SKILL.md` from core router and Codex adapter metadata.
2. Render Codex references from core references plus adapter-specific notes.
3. Include helper scripts or CLI wrappers in the generated package.
4. Render `agents/openai.yaml`.
5. Validate generated skill with Codex skill validator.
6. Compare generated output to committed skill package.
7. Document any intentional Codex-only behavior.

### Acceptance Criteria

- Codex package can be regenerated.
- Generated Codex package validates.
- Snapshot tests detect prompt drift.
- Existing install instructions still work.

### Required Verification

```bash
python3 scripts/build_adapters.py --adapter codex --check
PYTHONPATH=/private/tmp/autonomous-roadmap-delivery-pyyaml \
  python3 /Users/dzianissokalau/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skill/roadmap-delivery-skill
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not add Claude package behavior in this phase.

### Stop Conditions

- Stop if Codex generation changes safety rules or blocked-remediation
  behavior.

## Phase 3 - Claude Plugin Skeleton

Delivery status: Delivered 2026-05-31.

### Objective

Create a valid Claude plugin skeleton generated from the adapter system.

### Owned Files

```text
adapters/claude/plugin.json.template
adapters/claude/package.py
dist/claude/.claude-plugin/plugin.json
dist/claude/skills/roadmap-delivery-skill/SKILL.md
tests/test_claude_plugin_package.py
```

### Implementation Steps

1. Define Claude plugin manifest fields.
2. Render `.claude-plugin/plugin.json`.
3. Render Claude skill directory.
4. Include core references in Claude-compatible layout.
5. Add package validation tests:
   - manifest exists
   - skill exists
   - references exist
   - no Codex-only paths appear in Claude files
6. Add install instructions in draft docs.

### Acceptance Criteria

- Claude plugin skeleton is generated deterministically.
- Package structure is valid according to local checks.
- Claude package does not reference `~/.codex` as a runtime requirement.
- Core safety rules appear in the Claude skill.

### Required Verification

```bash
python3 scripts/build_adapters.py --adapter claude --check
python3 -m unittest discover -s tests -v
git diff --check
```

### Non-Goals

- Do not implement Claude hooks yet.
- Do not claim runtime support until smoke tests exist.

### Stop Conditions

- Stop if manifest requirements are unclear or unstable.

## Phase 4 - Claude Skills And Reviewer Agent

Delivery status: Delivered 2026-05-31.

### Objective

Add Claude-specific skills and a reviewer agent pattern that preserves the
phase-gated review loop.

### Owned Files

```text
adapters/claude/templates/skills/
adapters/claude/templates/agents/reviewer.md
dist/claude/skills/
dist/claude/agents/
tests/snapshots/claude/
```

### Implementation Steps

1. Render main Claude skill instructions from the core workflow.
2. Add a read-only reviewer agent template.
3. Ensure reviewer agent:
   - reads roadmap/state/log/reviews
   - checks acceptance criteria
   - leads with findings
   - emits `delivered`, `needs-fix`, or `blocked`
   - does not edit files
4. Add Claude-specific notes for tool permissions.
5. Add snapshot tests for skill and reviewer prompts.

### Acceptance Criteria

- Claude package contains a main skill and reviewer agent.
- Reviewer agent enforces the same review gate as Codex references.
- Snapshot tests catch prompt drift.
- No host-specific prompt contradicts core workflow rules.

### Required Verification

```bash
python3 scripts/build_adapters.py --adapter claude --check
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not add model-role config yet.
- Do not run live Claude runtime tests yet.

### Stop Conditions

- Stop if reviewer agent needs write permissions to perform its role.

## Phase 5 - Claude Hooks And Safety Guards

Delivery status: Delivered 2026-05-31.

### Objective

Add Claude hook templates for safety checks where host capability supports
them.

### Owned Files

```text
adapters/claude/templates/hooks/
dist/claude/hooks/
tests/test_claude_hooks.py
docs/compatibility.md
```

### Implementation Steps

1. Identify hook points that can support:
   - destructive git command guard
   - broad staging guard
   - blocked-remediation reminder
   - completion hard stop
   - privacy scan reminder
2. Render hook configuration.
3. Add tests that validate hook files exist and reference core guard text.
4. Mark unsupported hook behavior explicitly in compatibility docs.
5. Keep hooks conservative and non-destructive.

### Acceptance Criteria

- Claude package includes safety hook configuration where supported.
- Hooks reinforce core safety rules.
- Unsupported guard behavior is documented.
- Hook tests pass without live Claude runtime.

### Required Verification

```bash
python3 scripts/build_adapters.py --adapter claude --check
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not implement custom MCP servers.
- Do not block every risky command without a tested escape hatch.

### Stop Conditions

- Stop if hook behavior would create false safety claims.

## Phase 6 - Provider-Neutral Model Role Config

### Objective

Add provider-neutral model role configuration for executor, reviewer,
inspector, and finalizer roles.

### Owned Files

```text
config/providers.example.yaml
schemas/provider_config.schema.json
core/references/model-policy-and-stall-control.md
adapters/codex/
adapters/claude/
tests/test_provider_config.py
```

### Implementation Steps

1. Define model roles:
   - executor
   - reviewer
   - inspector
   - finalizer
   - repairer
2. Define provider-neutral config shape.
3. Map roles to Codex model/reasoning fields.
4. Map roles to Claude model fields when supported.
5. Add schema validation.
6. Add examples for high-reasoning and low-cost policies.
7. Keep phase model policy compatible with role config.

### Acceptance Criteria

- Provider config validates.
- Roles can be mapped to current `phase_model_policy.json`.
- Codex and Claude adapters render model-role guidance without claiming
  unsupported control.
- Tests cover role config success and failure.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_adapters.py --check
```

### Non-Goals

- Do not integrate billing or cost estimation.
- Do not auto-select models from live provider APIs.

### Stop Conditions

- Stop if host model-control boundaries cannot be stated honestly.

## Phase 7 - Adapter Parity And Snapshot Tests

### Objective

Make Codex and Claude packages testably equivalent for core workflow behavior.

### Owned Files

```text
tests/test_adapter_parity.py
tests/snapshots/codex/
tests/snapshots/claude/
core/prompts/
adapters/
```

### Implementation Steps

1. Define required parity assertions:
   - one phase at a time
   - blocked remediation before retry
   - model policy boundary
   - review verdict gate
   - completion hard stop
   - human approval for risky actions
2. Add snapshot tests for generated packages.
3. Add semantic tests that search generated prompts for required guard text.
4. Add drift reports that identify which adapter failed parity.
5. Require parity tests in CI.

### Acceptance Criteria

- Codex and Claude packages contain required core safety rules.
- Snapshot tests are deterministic.
- Adapter parity failures are easy to diagnose.
- Host-specific differences are documented.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_adapters.py --check
```

### Non-Goals

- Do not require perfect text equality between hosts.
- Do not implement Continue/Cline adapters yet.

### Stop Conditions

- Stop if core workflow rules diverge between adapters without an explicit
  compatibility note.

## Phase 8 - Install And Runtime Smoke Tests

### Objective

Validate install and basic runtime ergonomics for Codex and Claude packages.

### Owned Files

```text
tests/test_install_smoke.py
docs/installing-codex.md
docs/installing-claude.md
examples/demo-roadmap/
```

### Implementation Steps

1. Add local install smoke test for Codex package where possible.
2. Add structure/install smoke test for Claude package.
3. Add demo-roadmap validation under each adapter.
4. Add manual runtime checklist:
   - install
   - inspect
   - validate
   - run blocked-remediation fixture
   - run model-policy mismatch fixture
5. Record known limitations.

### Acceptance Criteria

- Codex install smoke test passes or is clearly skipped when Codex is absent.
- Claude package structure smoke test passes.
- Docs show exact install and validation commands.
- Runtime checklist is repeatable by a maintainer.

### Required Verification

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_adapters.py --check
```

Manual verification when hosts are available:

```text
install generated package
run inspect on demo roadmap
run validate on demo roadmap
trigger blocked-remediation fixture
```

### Non-Goals

- Do not rely on private credentials in automated tests.
- Do not publish packages yet.

### Stop Conditions

- Stop if smoke tests need unreproducible local state.

## Phase 9 - Generic Adapter Preparation

### Objective

Prepare the adapter system for future Continue, Cline, Roo Code, OpenHands, or
generic markdown packages without implementing full support.

### Owned Files

```text
adapters/generic/
docs/adapters.md
host-capabilities/generic.yaml
```

### Implementation Steps

1. Define minimal generic output:
   - workflow markdown pack
   - schema bundle
   - CLI install instructions
2. Add host capability template.
3. Document what a new adapter must implement.
4. Add checklist for future adapters.
5. Keep Codex and Claude as only supported adapters.

### Acceptance Criteria

- Future adapter work has a documented path.
- Generic package can be generated for documentation use.
- Supported host list remains honest.

### Required Verification

```bash
python3 scripts/build_adapters.py --adapter generic --check
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not claim support for Continue, Cline, Roo Code, or OpenHands yet.
- Do not build custom integrations for those hosts.

### Stop Conditions

- Stop if generic output blurs support claims.

## Phase 10 - Compatibility Docs And Release Artifacts

### Objective

Publish-ready multi-host package documentation and release artifacts.

### Owned Files

```text
docs/compatibility.md
docs/installing-codex.md
docs/installing-claude.md
CHANGELOG.md
scripts/build_release.py
dist/
```

### Implementation Steps

1. Update compatibility matrix.
2. Document Codex install and update flow.
3. Document Claude install and update flow.
4. Build release artifacts:
   - Codex package
   - Claude plugin package
   - schema bundle
   - generic markdown pack
5. Run privacy scan against artifacts.
6. Add release notes for host limitations.
7. Stop for human approval before publishing.

### Acceptance Criteria

- Release artifacts build reproducibly.
- Codex and Claude packages pass adapter checks.
- Compatibility matrix is current.
- Privacy scan passes.
- Human approval remains required for publication.

### Required Verification

```bash
python3 scripts/build_adapters.py --check
python3 scripts/build_release.py --check
python3 scripts/check_release_privacy.py --repo-root .
python3 -m unittest discover -s tests -v
```

### Non-Goals

- Do not publish without explicit approval.
- Do not create hosted services.

### Stop Conditions

- Stop if release artifacts contain stale names, private paths, or unsupported
  host claims.

## Cross-Phase Acceptance Criteria

This roadmap is complete when:

- Codex and Claude capabilities are documented
- adapters render from canonical core sources
- Codex package remains valid
- Claude plugin package exists and passes structure checks
- reviewer agent pattern exists for Claude
- safety hooks exist where supported
- provider-neutral model-role config exists
- adapter parity tests pass
- install smoke tests exist
- compatibility docs and release artifacts are ready

## Backlog

- Continue adapter.
- Cline/Roo Code adapter.
- OpenHands adapter.
- MCP server package.
- Hosted telemetry or metrics dashboard.
- Public docs site.
