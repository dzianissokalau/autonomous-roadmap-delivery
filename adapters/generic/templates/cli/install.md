# Generic CLI Installation Notes

Future host adapters should treat the repository CLI as the portable execution
surface until the host-specific package has proven stronger integration.

## Local Checkout

From a repository checkout:

```bash
python3 -m roadmap_delivery.cli inspect --repo-root "$PWD" --roadmap-slug <slug> --automation-id <automation-id>
python3 -m roadmap_delivery.cli validate --repo-root "$PWD" --roadmap-slug <slug> --automation-id <automation-id> --strict
```

When the package is installed, the equivalent console script is:

```bash
roadmap-delivery inspect --repo-root "$PWD" --roadmap-slug <slug> --automation-id <automation-id>
roadmap-delivery validate --repo-root "$PWD" --roadmap-slug <slug> --automation-id <automation-id> --strict
```

## Adapter Requirements

A host-specific adapter must prove how it starts a phase, reads repository
state, runs required verification, writes review artifacts, and preserves the
human approval boundaries for destructive git, publication, promotion,
credentials, and installed adapter synchronization.

It must also prove policy propagation for:

- `approval_policy.json` operation decisions, including `allowed`, `ask`, and
  `forbidden` outcomes.
- `adaptive_model_policy` run-quality classification and next-run model target
  handling without claiming the active model changed mid-run.
- completion and stall self-pause behavior, including
  `pause_automation_on_completion`, `pause_automation_on_stall`, runner pause
  readback, `completed_pending_pause`, and local alert fallback.
