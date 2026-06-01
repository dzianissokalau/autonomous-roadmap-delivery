# Compatibility

This document records the support boundary for the framework core, generated
Codex skill package, generated Claude plugin package, and future-adapter
planning surface.

## Supported Surfaces

| Surface | Status | Compatibility promise |
|---|---|---|
| `skill/roadmap-delivery-skill/` | Supported | Remains the installable Codex skill package path. |
| Codex helper scripts | Supported | Existing script paths remain executable compatibility wrappers. |
| `python3 -m roadmap_delivery.cli` | Supported | Works from an uninstalled checkout through the repository shim. |
| `roadmap-delivery` console script | Supported after install | Exposed by the local Python package metadata. |
| `automation/<roadmap-slug>/` layout | Supported | State, log, review, alert, and guide files stay repository-local. |
| State schema version 1 | Supported | Current artifacts validate against `schemas/delivery_state.schema.json`. |
| Legacy states without schema version | Compatibility mode | Accepted where legacy behavior is explicitly warning-backed. |
| Model policy file | Supported | `phase_model_policy.json` gates required model and reasoning readback. |
| Adapter package generation | Supported | `scripts/build_adapters.py --check` verifies committed Codex and Claude output. |
| Codex package generation | Supported | `scripts/build_codex_package.py --check` remains a compatibility wrapper check. |
| Claude plugin package | Supported local package | Generated under `dist/claude/` with skill, reviewer agent, hooks, and references. |
| Generic markdown pack | Documentation template | Built only as an explicit release artifact for future adapter planning. |
| Local release artifacts | Supported | `scripts/build_release.py --check` verifies reproducible source, Codex, Claude, schema, CLI, and generic bundles. |
| Host capability metadata | Supported | `host-capabilities/codex.yaml` and `host-capabilities/claude.yaml` define the adapter support contract. |

## Host Capability Notes

Codex support is package-based and assumes the Codex runtime supplies skills,
tools, filesystem permissions, model selection, reasoning effort, and
automation scheduling. The framework validates saved automation config when it
is available, but it does not switch the active model from prompt text.

Claude consumes the same `core/`, `schemas/`, and shared library contracts
through a generated plugin package under `dist/claude/`. Offline package
structure checks, adapter parity tests, and demo-roadmap runtime validation are
part of the maintained local support boundary. Live Claude Code loading is an
optional maintainer smoke check when the `claude` binary is available.

Future host adapters should consume the same `core/`, `schemas/`, and shared
library contracts. Any host-specific differences must be represented as
explicit capability metadata, parity tests, smoke checks, and compatibility
notes before a host is listed as supported.

## Host Capability Contract

The multi-host adapter work uses explicit capability files instead of burying
host assumptions in prompts:

- `host-capabilities/codex.yaml` records the current Codex baseline.
- `host-capabilities/claude.yaml` records the supported local Claude plugin
  package and host-specific fallback boundaries.
- `host-capabilities/generic.yaml` records the documentation-only generic
  adapter template for future host planning.

Parity levels:

- `required_parity`: behavior must be equivalent across supported hosts.
- `host_specific_enhancement`: behavior may exceed the shared contract on one
  host without becoming required elsewhere.
- `unsupported_by_host`: the host does not expose the capability, so the
  adapter must document the fallback.
- `future_work`: the capability is intentionally outside the current roadmap
  phase.

Claude support is a required-parity target for the core phase-gated workflow,
file-backed state, validation, review artifacts, and release privacy gates. It
uses host-specific fallbacks for recurring automation, model/reasoning
readback, hooks, subagents, and approval UX where Claude Code does not expose
the same surfaces as Codex.

## Claude Hook Safety Boundary

The generated Claude plugin now includes `hooks/hooks.json` plus a small
command helper that reinforces the roadmap delivery contract where Claude Code
plugin hooks support it:

- `PreToolUse` on `Bash` asks for confirmation before destructive git commands,
  broad git staging, publication commands, branch promotion, and package
  upload commands.
- `UserPromptSubmit` injects Blocked Remediation Mode context when a matching
  repository delivery state is blocked.
- `UserPromptSubmit` blocks matching phase-delivery prompts when the delivery
  state is completed, `completed_pending_pause`, or `all_phases_complete`.
- `UserPromptSubmit` injects a privacy/release reminder when the user prompt
  asks for publication, promotion, package, or release work.
- `Stop` blocks a delivered-phase claim that lacks verification evidence and a
  delivered review verdict in the final response.

Unsupported behavior is explicit: these hooks are not a live Claude runtime
smoke test, do not replace repository validators, do not bypass Claude
permissions, do not install or sync any plugin globally, do not provide a
custom MCP server, and do not perform an exhaustive secret scan. Protected
operations still require human approval, and release privacy checks remain the
authoritative gate.

## Human-Approved Operations

The following operations are intentionally outside automatic delivery:

- pushing branches
- merging or promoting to `main`
- publishing release artifacts
- syncing an installed global Codex skill copy
- editing live app automation configuration
- using credentials or external notification sinks
- destructive git operations

Automation and CLI checks may identify that one of these actions is needed,
but the action itself requires explicit operator approval.
