# Finalization And Promotion Reference

Use this reference only after all roadmap phases are delivered or when the
operator explicitly requests finalization or promotion.

## Core Contract

Before finalization, confirm every phase is delivered or explicitly deferred,
latest review verdict is `delivered`, required final verification passed, state
and log contain final evidence, no blocker remains, completion alert evidence
exists or is the next required action, runner status has been reviewed, and any
dirty worktree entries are explained.

## Completion Hard Stop

When all phases are complete, do not extract or start another phase. Instead:

1. Confirm final verification and latest delivered review evidence.
2. Confirm a final review artifact or deep-review prompt exists when required.
3. Write a completed operator alert before relying on optional notification
   sinks.
4. Set completed state or completed-pending-pause state.
5. Pause the runner only when the pause surface is approved and read back.
6. If pause approval is unavailable, record the required human pause action.

Completed state is a hard stop for future scheduled runs.

## Final Verification

Run roadmap final checks plus targeted smoke checks for changed workflow,
scripts, schemas, templates, generated packages, and release artifacts. Do not
rely only on older phase verification if final bookkeeping changed shared
behavior.

## Promotion Boundary

Promotion, publication, merging, pushing, release upload, and destructive branch
operations are separate operator-approved actions. A finalization run may
prepare evidence, but it must not publish or promote without explicit approval.

## Host Adapter Boundary

The core defines completion gates, alert requirements, and promotion separation.
Host adapters own concrete pause, publication, and runner status mechanisms.
