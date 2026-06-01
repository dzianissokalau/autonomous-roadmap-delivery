# Final Deep Review Prompt

Roadmap:
`roadmaps/delivered_autonomous_operation_modes_and_adaptive_control_roadmap.md`

Automation:
`automation/autonomous-operation-modes-and-adaptive-control/`

Branch:
`codex/autonomous-operation-modes-and-adaptive-control-phase-7`

## GitHub Fetch Target

Fetch the pushed review branch from GitHub:

- Repository: `git@github.com:dzianissokalau/roadmap-delivery-skill.git`
- Branch: `codex/autonomous-operation-modes-and-adaptive-control-phase-7`
- Branch URL: `https://github.com/dzianissokalau/roadmap-delivery-skill/tree/codex/autonomous-operation-modes-and-adaptive-control-phase-7`
- Raw prompt URL: `https://raw.githubusercontent.com/dzianissokalau/roadmap-delivery-skill/codex/autonomous-operation-modes-and-adaptive-control-phase-7/automation/autonomous-operation-modes-and-adaptive-control/final_deep_review_prompt.md`

Use that branch as the source of truth for this review. Do not review `main`
unless the operator explicitly asks for promotion review after this branch is
accepted.

## Reviewer Task

Perform a whole-roadmap acceptance review for Autonomous Operation Modes And
Adaptive Control. Evaluate all delivered phases, not only the latest Phase 7
diff.

Review these sources:

- roadmap header, phase contract, and phase history
- `automation/autonomous-operation-modes-and-adaptive-control/delivery_state.json`
- `automation/autonomous-operation-modes-and-adaptive-control/delivery_log.md`
- `automation/autonomous-operation-modes-and-adaptive-control/review_fix_state.json`
- all review artifacts under
  `automation/autonomous-operation-modes-and-adaptive-control/reviews/`
- approval, adaptive model, completion pause, and migration documentation
- demo fixtures under `examples/demo-roadmap/` and
  `examples/autonomy-controls/`
- verification evidence from the Phase 7 delivery log

## Questions To Answer

1. Do the delivered artifacts satisfy every phase objective and acceptance
   criterion in the roadmap?
2. Do state, log, review files, roadmap header, branch, and saved automation
   readback agree?
3. Is verification sufficient for human merge review to begin?
4. Are approval policy, adaptive model, completion pause, stall pause, and
   migration behaviors documented clearly enough for an operator to use?
5. Are there unresolved risks around conservative fallback,
   `completed_pending_pause`, saved automation pause readback, publication,
   promotion, or installed-skill synchronization?
6. Is the roadmap ready for finalization, completed alert handling, and a
   separate human promotion decision?

## Required Output

Lead with findings ordered by severity. Include file and line references where
possible. Then include:

- verification gaps
- state or log consistency gaps
- residual risks
- promotion-readiness notes
- verdict: `ready-for-finalization`, `needs-fix`, or `blocked`

Do not approve publication, package release, promotion to `main`, installed
skill sync, credential use, or destructive git. Those remain separate
human-approved actions.
