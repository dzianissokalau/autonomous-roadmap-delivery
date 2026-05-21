# Final Deep Review Prompt

Review `roadmaps/delivered_phase_model_policy_and_stall_control_roadmap.md`
against the complete delivery history for
`phase-model-policy-and-stall-control`.

Use a skeptical code-review stance. Check:

- every numbered phase and finalization acceptance criterion
- `delivery_state.json`, `delivery_log.md`, `review_fix_state.json`, and
  review artifacts for consistency
- final verification sufficiency
- completion alert presence and automation pause status
- branch, publication, promotion, and installed-skill synchronization risks

Verdict options: `ready_for_human_review`, `needs_fix`, or `blocked`.

Known state at prompt creation: all roadmap phases are locally delivered, the
completion alert is expected to exist, and the live automation remains active
until the operator approves pause.
