# Roadmap Delivery Alert: Retarget Failed

- Alert kind: `retarget-failed`
- Created at: `2026-06-02T09:55:29Z`
- Roadmap: `roadmaps/in_progress_onboarding_wizard_and_proof_demos_roadmap.md`
- Phase: `Phase 2 - Wizard Implementation And Scaffold Integration`
- Status: `blocked`
- Reason: Phase 1 delivered, but Phase 2 requires saved automation retarget from gpt-5.5/xhigh to gpt-5.5/high. retarget_saved_automation is not pre-approved in approval_policy.json.
- Required model: `gpt-5.5`
- Configured model: `gpt-5.5`
- Required reasoning effort: `high`
- Configured reasoning effort: `xhigh`
- Last verification: python3 -m unittest tests.test_cli tests.test_onboarding_wizard tests.test_schema_validation -v: passed; python3 -m roadmap_delivery.cli scaffold --help: passed; git diff --check: passed
- Last review: automation/onboarding-wizard-and-proof-demos/reviews/onboarding-wizard-and-proof-demos-phase-1-review-iteration-1.md - verdict delivered
- State file: `automation/onboarding-wizard-and-proof-demos/delivery_state.json`
- Delivery log: `automation/onboarding-wizard-and-proof-demos/delivery_log.md`
- Review directory: `automation/onboarding-wizard-and-proof-demos/reviews`
- Notification sink: `alert_file`
- Notification status: `local_alert_only`
- Next human action: Approve retargeting the saved automation reasoning effort to high for Phase 2, or update the phase model and approval policy with an explicit different decision.

Local alert file is the durable fallback. External notification sinks are optional and must not remove this file on failure.
