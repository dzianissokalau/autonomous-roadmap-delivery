# Adaptive Model Gate Prompt Fragment

After verification and the fresh review verdict, classify the run quality as
`flawless`, `delivered_with_fixes`, `verification_failed`,
`review_needs_fix`, `blocked_local_repairable`, `blocked_human_required`,
`stalled`, `retarget_failed`, or `completion_closeout_failed`. Apply
`adaptive_model_policy` only to the next run: update durable state, respect
model/reasoning caps, skip escalation for human-gated blockers, and retarget
the saved runner only when approval policy allows the automation update.
