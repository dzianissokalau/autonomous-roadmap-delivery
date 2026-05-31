# Multi-Host Adapter And Claude Plugin Phase 8 Review - Iteration 1

Reviewed at: 2026-05-31T21:57:07Z
Roadmap: `roadmaps/in_progress_multi_host_adapter_and_claude_plugin_roadmap.md`
Phase: Phase 8 - Install And Runtime Smoke Tests
Branch: `codex/multi-host-adapter-and-claude-plugin-phase-8`
Verdict: delivered
Reviewer context: same Codex session. A delegated subagent review was not used
because the current operator prompt did not explicitly authorize sub-agent
delegation; this limitation is recorded explicitly.

## Findings

No blocking findings.

## Missing Tests Or Checks

No missing automated checks for the Phase 8 contract. The `claude` binary is
not installed on this machine, so the optional live Claude host help check is
skipped with an explicit unittest skip. The offline Claude plugin staging and
demo runtime validation paths passed.

## Scope Review

- `tests/test_install_smoke.py` stages the generated Codex package in a
  temporary Codex home, verifies required package files, and runs the installed
  inspect and validate helper scripts against a temporary demo roadmap checkout.
- `tests/test_install_smoke.py` stages the generated Claude plugin under a
  temporary plugin directory, verifies manifest, skill, reviewer agent, and
  hook files, and runs strict inspect and validate commands against the same
  demo roadmap fixture.
- `docs/installing-codex.md` and `docs/installing-claude.md` provide exact
  package check, isolated staging, demo inspect, and demo validate commands.
- `examples/demo-roadmap/runtime-checklist.md` gives maintainers repeatable
  commands for install staging, inspect, validate, blocked-remediation fixture,
  and model-policy-mismatch fixture checks.
- Changed files are limited to Phase 8 owned surfaces plus automation
  bookkeeping.

## Verification Evidence

- `python3 -m unittest tests.test_install_smoke -v`: passed, 5 tests with 1
  expected skip because the `claude` binary is not installed.
- `python3 -m unittest discover -s tests -v`: passed, 128 tests with 1
  expected skip.
- `python3 scripts/build_adapters.py --check`: passed for Codex and Claude,
  0 diffs and 0 errors.
- `git diff --check`: passed.
- Retarget plan for Phase 9: no automation config update required; saved
  automation already reads back `gpt-5.5` with `xhigh` reasoning.

## Finding Disposition

- No blocking findings.

## Residual Risks

- Live Claude plugin loading still needs a maintainer with Claude Code
  installed; the checklist documents the command surface and offline checks.
- The Codex live binary check only verifies host CLI availability with an
  isolated `CODEX_HOME`; the stronger behavior check is the installed helper
  validation against the demo roadmap.
- Same-context review is less independent than a delegated fresh review.

## Verdict

delivered
