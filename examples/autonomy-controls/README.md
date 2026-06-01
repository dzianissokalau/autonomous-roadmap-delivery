# Autonomy Controls Examples

These examples show the control-plane artifacts an operator reviews before
choosing an autonomy mode, allowing adaptive model retargeting, or enabling
completion and stall self-pause. They are documentation fixtures only; they do
not mutate a live Codex or Claude automation.

## Approval Modes

Use `approval-policy-examples.json` to compare the four supported modes:

- `conservative`: local phase edits, state/log/review writes, phase branch
  creation or switching, and verification can proceed. Commits, pushes,
  saved automation retargeting, and pause actions still ask for approval.
- `delegated_local`: local commits, saved automation model/reasoning retargets,
  and completion or stall pause actions can proceed after policy and readback
  checks pass.
- `delegated_delivery`: includes delegated local behavior and allows pushing the
  current phase branch when branch and remote policy match.
- `custom`: every operation is explicit; omitted or false operations remain
  blocked or ask-first depending on the gate.

Never-auto operations stay forbidden in every mode.

## Adaptive Trace

`adaptive-escalation-trace.json` shows a `review_needs_fix` run that escalates
the next run to the policy cap. The important boundary is that the current run
does not change model by prompt text; only the next saved runner readback proves
the retarget.

## Self-Pause

`completion-self-pause-state.json` shows the successful delegated completion
pause shape: a completed alert exists, the pause operation was policy-allowed,
and readback confirms `PAUSED`.

`stall-self-pause-run-log.jsonl` shows the audit line produced when repeated
no-progress runs reach the stall threshold and the saved automation is paused
under delegated local policy.

The demo roadmap also includes a `delegated-local` scenario under
`examples/demo-roadmap/scenarios/` so the runtime checklist can exercise a
delegated approval-policy readback without touching a live automation.
