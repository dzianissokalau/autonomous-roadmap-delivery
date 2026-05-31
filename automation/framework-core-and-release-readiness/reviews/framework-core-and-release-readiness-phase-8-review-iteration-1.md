# Framework Core And Release Readiness Phase 8 Review - Iteration 1

Reviewed at: 2026-05-25T09:18:32Z
Roadmap: `roadmaps/in_progress_framework_core_and_release_readiness_roadmap.md`
Phase: Phase 8 - Demo Fixture And Smoke Tests
Branch: `codex/framework-core-and-release-readiness-phase-8`
Reviewer context: same Codex session; delegated fresh-context review was not used because no explicit sub-agent request was present.
Verdict: delivered

## Findings

No blocking findings.

## Scope Review

- `examples/demo-roadmap/roadmaps/in_progress_demo_roadmap.md:1` defines a
  small in-progress demo roadmap with three phases, and lines 35-80 record a
  delivered Phase 0 fixture contract.
- `examples/demo-roadmap/automation/demo_roadmap/delivery_state.json:1`
  provides schema-versioned state, records Phase 0 as delivered at lines 25-31,
  and leaves Phase 1 as the current not-started phase at lines 5-7.
- `examples/demo-roadmap/automation-config/demo-roadmap-delivery/automation.toml:5`
  includes both the completion hard stop and Blocker Remediation Mode prompt
  guard, with `gpt-5.5` and `xhigh` readback values at lines 7-8.
- `examples/demo-roadmap/README.md:7` lists the fixture behaviors, including
  scaffold dry-run, validate/inspect, blocked-run behavior, and model-policy
  mismatch scenarios.
- `examples/demo-roadmap/scenarios/blocked-remediation/delivery_state.json:7`
  records a blocked Phase 1 state, failed verification at lines 10-20, and a
  concrete blocked reason at line 29.
- `examples/demo-roadmap/scenarios/model-policy-mismatch/automation.toml:7`
  intentionally sets a mismatched model and reasoning effort for the mismatch
  smoke test.
- `tests/test_smoke_demo.py:119` verifies scaffold dry-run writes no files,
  lines 141-183 validate and inspect the copied demo with a temporary saved
  automation config, lines 185-222 exercise blocked-remediation reporting, and
  lines 224-260 assert model-policy mismatch blocks validation.
- `README.md:173` documents the demo fixture quickstart, and `README.md:229`
  adds the targeted smoke test to local CI equivalents.

## Verification Evidence

- `python3 -m unittest tests.test_smoke_demo -v`: passed, 5 tests.
- `python3 -m roadmap_delivery.cli validate --repo-root examples/demo-roadmap --roadmap-slug demo-roadmap --json`: passed with expected local-demo warnings for missing saved demo automation config, parent branch mismatch, and dirty parent worktree.
- `python3 -m unittest discover -s tests -v`: passed, 81 tests.
- `PYTHONPYCACHEPREFIX=$TMPDIR/roadmap-delivery-phase8-pycache python3 -m py_compile tests/test_smoke_demo.py`: passed.
- `git diff --check`: passed.

## Missing Tests Or Checks

None for the Phase 8 contract. The smoke tests avoid live Codex app automation
by using a temporary home directory and repository-local fixture copy.

## Finding Disposition

- No findings.

## Residual Risks

- Same-context review was used because delegated fresh-context review requires
  an explicit sub-agent request in this environment.
- The direct demo validation command intentionally does not depend on a real
  saved demo automation, so it can report expected warnings when run inside the
  parent repository checkout.
- Existing unrelated worktree dirt remains limited to `automation/README.md`
  and `roadmaps/in_progress_multi_host_adapter_and_claude_plugin_roadmap.md`.

## Verdict

delivered
