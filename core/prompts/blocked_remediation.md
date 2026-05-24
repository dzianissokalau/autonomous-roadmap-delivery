# Blocked Remediation Prompt Fragment

If delivery state is `blocked`, do not attempt normal phase advancement first.
Classify the blocker as local-repairable, automation-config, permission-gated,
external-decision, or destructive-risk. Repair only local or already-approved
runner configuration blockers, rerun reconciliation and validation, clear
`blocked_reason` only after the repair is verified, and then resume the current
phase. If credentials, product input, destructive operations, publication,
promotion, or unapproved runner configuration changes are required, keep state
blocked and ask for the missing human action.
