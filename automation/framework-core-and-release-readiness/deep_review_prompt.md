# Framework Core And Release Readiness Deep Review Prompt

Review the completed framework core and release readiness roadmap for human
merge and promotion readiness.

GitHub review location:

- Repository:
  `https://github.com/dzianissokalau/roadmap-delivery-skill`
- Review branch:
  `codex/framework-core-and-release-readiness-phase-10`
- Branch URL:
  `https://github.com/dzianissokalau/roadmap-delivery-skill/tree/codex/framework-core-and-release-readiness-phase-10`
- Phase 10 comparison:
  `https://github.com/dzianissokalau/roadmap-delivery-skill/compare/codex/framework-core-and-release-readiness-phase-9...codex/framework-core-and-release-readiness-phase-10`

Use these artifacts:

- Roadmap:
  `roadmaps/delivered_framework_core_and_release_readiness_roadmap.md`
- Delivery state:
  `automation/framework-core-and-release-readiness/delivery_state.json`
- Delivery log:
  `automation/framework-core-and-release-readiness/delivery_log.md`
- Reviews:
  `automation/framework-core-and-release-readiness/reviews/`
- Completion alert:
  `automation/framework-core-and-release-readiness/alerts/2026-05-25T11-56-13Z-completed.md`
- Release notes:
  `docs/release-notes-0.1.0.md`

Take a skeptical code-review stance. Lead with findings and cite file paths and
line numbers where possible.

Evaluate:

- Whether all roadmap phases are delivered or explicitly deferred.
- Whether state, log, reviews, model policy, branch, and completion alert agree.
- Whether the final verification evidence is sufficient.
- Whether docs and release artifacts are internally consistent.
- Whether Codex package generation, schemas, CLI, CI, privacy, demo, and release
  checks are covered by tests.
- Whether the companion multi-host roadmap can start without redesigning the
  framework core.
- Whether publication, promotion, installed-skill synchronization, and
  automation pause remain safely human-approved.
- Whether the active automation and stale saved prompt path create any unsafe
  residual risk despite the completion hard stop.

Output:

- Findings ordered by severity.
- Missing tests or missing release checks.
- Residual risks.
- Promotion readiness recommendation.
- Verdict: `ready-for-human-review`, `needs-fix`, or `blocked`.
