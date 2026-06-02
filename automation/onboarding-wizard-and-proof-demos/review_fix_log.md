# Onboarding Wizard And Proof Demos Review/Fix Log

## Phase 0 - 2026-06-02 - Review Iteration 1

Status: delivered review, blocked advancement

- Review file:
  `automation/onboarding-wizard-and-proof-demos/reviews/onboarding-wizard-and-proof-demos-phase-0-review-iteration-1.md`
- Verdict: delivered
- Fix before formal review: added a direct fit/non-fit section to
  `docs/quickstart.md` so the quickstart itself satisfies the Phase 0
  acceptance criterion.
- Advancement blocker recorded during the original run: Phase 1 required
  lifecycle rename to
  `roadmaps/in_progress_onboarding_wizard_and_proof_demos_roadmap.md`; the
  original framework also required a saved automation prompt update.
- Superseded by the 2026-06-02T09:21:39Z lifecycle repair: the framework now
  treats `delivery_state.json` as authoritative when the saved prompt
  references stable state/guide/log artifacts, so no saved automation prompt
  edit is required for lifecycle-only renames.

## Blocked Remediation - 2026-06-02T09:06:35Z

Status: blocked

- Original classification: permission-gated.
- Reclassified after framework fix: local-repairable.
- Latest review remains
  `automation/onboarding-wizard-and-proof-demos/reviews/onboarding-wizard-and-proof-demos-phase-0-review-iteration-1.md`
  with verdict `delivered`.
- No review/fix iteration was opened because Phase 0 remained delivered.
- Repository-local lifecycle repair was later applied without a saved prompt
  retarget.
- Artifact validation passed with no errors and only the expected
  `worktree_dirty` warning.

## Phase 1 - 2026-06-02 - Review Iteration 1

Status: delivered review, blocked next phase retarget

- Review file:
  `automation/onboarding-wizard-and-proof-demos/reviews/onboarding-wizard-and-proof-demos-phase-1-review-iteration-1.md`
- Verdict: delivered
- Fix before final verdict: added `--allow-warning worktree_dirty` to the
  generated wizard validation command and mirrored it in wizard JSON expected
  warnings and tests.
- Required verification passed after the fix:
  `python3 -m unittest tests.test_cli tests.test_onboarding_wizard tests.test_schema_validation -v`,
  `python3 -m roadmap_delivery.cli scaffold --help`, and `git diff --check`.
- End-run blocker: Phase 2 requires saved automation reasoning `high`, but the
  saved automation currently reads back `xhigh`; conservative approval policy
  does not pre-approve `retarget_saved_automation`.

## Blocked Remediation - 2026-06-02T10:05:28Z

Status: repaired

- Operator decision: keep `xhigh` reasoning for every roadmap stage.
- Updated roadmap phase guidance and
  `automation/onboarding-wizard-and-proof-demos/phase_model_policy.json` so
  Phase 2 no longer requires a saved automation retarget.
- Cleared the review/fix blocked state; Phase 2 is ready to start on the next
  automation run.
- The previous retarget-failed alert remains as historical evidence and is
  marked superseded in delivery state.
