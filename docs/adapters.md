# Adapters

Roadmap Delivery uses adapters to package the same host-neutral workflow for
different AI coding hosts. Canonical behavior stays in `core/`, `schemas/`, and
`src/roadmap_delivery/`; adapter directories only describe how a host receives
that workflow.

## Current Adapter Set

| Adapter | Status | Default build | Purpose |
|---|---|---:|---|
| `codex` | Supported package | Yes | Generated Codex skill package. |
| `claude` | Roadmap package | Yes | Generated Claude plugin package. |
| `generic` | Documentation template | No | Markdown and schema pack for future adapter planning. |

The generic adapter is intentionally not a support claim for Continue, Cline,
Roo Code, OpenHands, or any other named host. Those hosts need separate
capability files, package metadata, tests, smoke checks, and compatibility notes
before they can be listed as supported.

## Generic Pack

Generate the generic documentation pack into a temporary output directory:

```bash
python3 scripts/build_adapters.py --adapter generic --write --output-root /tmp/roadmap-adapter-pack
```

Check that the generic adapter still renders:

```bash
python3 scripts/build_adapters.py --adapter generic --check
```

The default adapter build remains limited to concrete package outputs:

```bash
python3 scripts/build_adapters.py --check
```

## Adding A Host Adapter

Use this minimum path for a new host:

1. Create `host-capabilities/<host>.yaml` with support status, parity levels,
   fallbacks, model readback behavior, filesystem expectations, and protected
   operations.
2. Add `adapters/<host>/package.py` that renders deterministic output from
   core references, schemas, and host-specific templates.
3. Keep unsupported host features explicit in the capability file and generated
   README.
4. Add focused adapter tests for render checks, output-root regeneration,
   snapshot or manifest drift, host capability metadata, and support-claim
   wording.
5. Add install or runtime smoke checks that can pass without credentials or
   global host mutation.
6. Update compatibility and release documentation only after the checks prove
   the support boundary.

Do not add a host to the default build until its package is meant to be treated
as a concrete maintained adapter.
