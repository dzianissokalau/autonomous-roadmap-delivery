# Roadmap Delivery Automation

This workspace contains the strategy, phased roadmap, and local automation
artifacts for building the `autonomous-roadmap-delivery` Codex skill.

GitHub repository: `git@github.com:dzianissokalau/autonomous-roadmap-delivery.git`

## Current Roadmap

- Roadmap: `roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md`
- Status: In Progress
- Current phase: Phase 0 - Scope Confirmation
- Automation guide: `automation/autonomous-roadmap-delivery-skill/automation_guide.md`
- Delivery state: `automation/autonomous-roadmap-delivery-skill/delivery_state.json`
- Delivery log: `automation/autonomous-roadmap-delivery-skill/delivery_log.md`
- Repository branch: `main`

## Operating Model

Use a phase-gated delivery loop:

1. Treat the roadmap as the phase contract.
2. Deliver exactly one phase at a time.
3. Record durable state before and after each phase pass.
4. Run required verification before claiming phase delivery.
5. Require a fresh review verdict before phase advancement.
6. Stop on blockers, stale state, failed verification, or unclear scope.

The first roadmap has been kicked off in Phase 0. The next action is to review
the kickoff artifacts and begin Phase 1 only after a `delivered` review verdict.
