# Compatibility

This document records the support boundary for the framework core and the
Codex adapter after the framework hardening migration.

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
| Codex package generation | Supported | `scripts/build_codex_package.py --check` verifies committed output. |
| Local release artifacts | Supported | `scripts/build_release.py --check` verifies reproducible local artifacts. |
| Host capability metadata | Supported | `host-capabilities/codex.yaml` and `host-capabilities/claude.yaml` define the adapter support contract. |
| Claude plugin package | Active roadmap | Planned by the multi-host adapter roadmap; not installable until the Claude package phases are delivered. |

## Host Capability Notes

Codex support is package-based and assumes the Codex runtime supplies skills,
tools, filesystem permissions, model selection, reasoning effort, and
automation scheduling. The framework validates saved automation config when it
is available, but it does not switch the active model from prompt text.

Claude and other host adapters should consume the same `core/`, `schemas/`,
and shared library contracts. Any host-specific differences must be represented
as explicit capability metadata and parity tests in the active multi-host
roadmap.

## Host Capability Contract

The multi-host adapter work uses explicit capability files instead of burying
host assumptions in prompts:

- `host-capabilities/codex.yaml` records the current Codex baseline.
- `host-capabilities/claude.yaml` records the planned Claude target and known
  gaps before implementation.

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
is a best-effort target for host-specific scheduling, hooks, subagents, and
approval UX until the Claude plugin phases prove the exact runtime surfaces.

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
