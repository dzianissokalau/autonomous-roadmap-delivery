# Phase 1 Review - Iteration 1

Roadmap: `roadmaps/in_progress_onboarding_wizard_and_proof_demos_roadmap.md`
Phase: Phase 1 - Setup Wizard UX And CLI Contract
Reviewed at: 2026-06-02T09:55:29Z
Branch: `codex/onboarding-wizard-and-proof-demos-phase-1`
Reviewer context: same Codex session; no separate fresh-context reviewer was
available without explicit delegation, so this review relies on concrete diff
and command evidence.
Verdict: delivered

## Findings

No blocking findings remain.

## Scope Review

- `src/roadmap_delivery/cli.py:441` wires the `wizard` command and
  `src/roadmap_delivery/cli.py:607` exposes non-interactive flags for roadmap
  slug, automation id, roadmap path, approval mode, initial model, reasoning
  effort, cadence, execution environment, host target, dry-run/write mode, and
  force handling.
- `src/roadmap_delivery/scaffold.py:175` plans repository-local roadmap and
  automation artifacts, records conservative approval policy defaults, and
  reports live automation creation as false.
- `src/roadmap_delivery/scaffold.py:347` generates schema-versioned delivery
  state with approval policy readback, model/stall fields, completion fields,
  and planned runner target fields needed by validation before live automation
  creation.
- `src/roadmap_delivery/wizard.py:19` wraps the scaffold plan into stable wizard
  JSON output with dry-run/write mode, setup choices, expected setup warnings,
  and conflict refusal before write mode without `--force`.
- `docs/onboarding-wizard.md:16` documents the implemented command examples,
  `docs/onboarding-wizard.md:55` documents conservative defaults and explicit
  delegated mode selection, and `docs/onboarding-wizard.md:111` documents the
  validation command.
- `tests/test_onboarding_wizard.py:34` covers dry-run planning,
  `tests/test_onboarding_wizard.py:63` covers write mode plus validation,
  `tests/test_onboarding_wizard.py:119` covers delegated mode recording, and
  `tests/test_onboarding_wizard.py:145` covers existing artifact refusal.

## Missing Tests Or Checks

No missing required checks. The required Phase 1 verification passed after the
review fix.

## Verification Evidence

- `python3 -m unittest tests.test_cli tests.test_onboarding_wizard tests.test_schema_validation -v`:
  passed, 21 tests.
- `python3 -m roadmap_delivery.cli scaffold --help`: passed.
- `git diff --check`: passed.

## Finding Disposition

- Pre-review gap: generated wizard validation commands omitted
  `--allow-warning worktree_dirty`, so a fresh write in a git checkout could
  fail strict validation despite generated artifacts being valid. Fixed in
  `src/roadmap_delivery/scaffold.py:158`, mirrored in
  `src/roadmap_delivery/wizard.py:38`, and covered by
  `tests/test_onboarding_wizard.py:60`.

## Residual Risks

- Review was same-context rather than delegated fresh-context review.
- The command records a planned runner target in generated delivery state so
  repository-local validation can run before saved automation creation; docs
  and templates explicitly require replacing those fields with saved runner
  readback before activation.
- Phase 2 requires `gpt-5.5` with `high` reasoning, while the saved automation
  currently reads back `gpt-5.5` with `xhigh` reasoning. Retargeting saved
  automation config is not pre-approved by the conservative approval policy, so
  the next phase must remain blocked until the operator approves the retarget
  or updates the policy.

## Verdict

delivered
