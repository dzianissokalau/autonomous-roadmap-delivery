# Roadmap Delivery Automation

This workspace contains the strategy, phased roadmap, and local automation
artifacts for building the `autonomous-roadmap-delivery` Codex skill.

GitHub repository: `<repository-remote-url>`

## Current Roadmap

- Roadmap: `roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md`
- Status: Delivered
- Current phase: Complete
- Review branch: `codex/autonomous-roadmap-delivery-skill-phase-10`
- Automation guide: `automation/autonomous-roadmap-delivery-skill/automation_guide.md`
- Delivery state: `automation/autonomous-roadmap-delivery-skill/delivery_state.json`
- Delivery log: `automation/autonomous-roadmap-delivery-skill/delivery_log.md`
- Final review prompt: `automation/autonomous-roadmap-delivery-skill/deep_review_prompt.md`
- Codex automation: `autonomous-roadmap-delivery-skill` hourly, PAUSED
- Repository skill snapshot: `skill/autonomous-roadmap-delivery/`

## Operating Model

Use a phase-gated delivery loop:

1. Treat the roadmap as the phase contract.
2. Deliver exactly one phase at a time.
3. Record durable state before and after each phase pass.
4. Run required verification before claiming phase delivery.
5. Require a fresh review verdict before phase advancement.
6. Stop on blockers, stale state, failed verification, or unclear scope.

The roadmap is complete locally. The pushed branch contains the roadmap
evidence plus a source snapshot of the installed skill package so external
reviewers can inspect the delivered skill without access to the local
`~/.codex/skills` directory.

To run the repository-local checks:

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=$TMPDIR/autonomous-roadmap-review-compile-pycache \
  python3 -m py_compile \
  skill/autonomous-roadmap-delivery/scripts/inspect_delivery_state.py \
  skill/autonomous-roadmap-delivery/scripts/validate_delivery_artifacts.py
```

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
