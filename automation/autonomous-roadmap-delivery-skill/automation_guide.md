# Codex Automation Guide: Autonomous Roadmap Delivery Skill Roadmap

Status: Active kickoff guide
Created: 2026-05-20
Primary roadmap: `roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md`

## Purpose

This guide describes how to run Codex as a phase-gated delivery system for the
first roadmap in this project: building the `autonomous-roadmap-delivery` skill.

The intended loop is:

```text
deliver one roadmap phase
verify the phase against its required checks
review the delivered artifacts in a fresh context
route findings back to the delivery context
fix and verify
repeat until clean or blocked
advance to the next roadmap phase
```

## Configuration

```text
ROADMAP_PATH=roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md
ROADMAP_SLUG=autonomous-roadmap-delivery-skill
CURRENT_PHASE=Phase 0 - Scope Confirmation
STATE_FILE=automation/autonomous-roadmap-delivery-skill/delivery_state.json
DELIVERY_LOG=automation/autonomous-roadmap-delivery-skill/delivery_log.md
REVIEW_FIX_STATE=automation/autonomous-roadmap-delivery-skill/review_fix_state.json
REVIEW_FIX_LOG=automation/autonomous-roadmap-delivery-skill/review_fix_log.md
REVIEW_DIR=automation/autonomous-roadmap-delivery-skill/reviews
MAX_REVIEW_ITERATIONS=3
CADENCE=manual until Phase 0 is reviewed
```

This workspace is a git repository synced to:

```text
git@github.com:dzianissokalau/autonomous-roadmap-delivery.git
```

The initial planning artifacts are synced on `main`. For future roadmap phase
delivery work, use one branch per phase:

```text
codex/autonomous-roadmap-delivery-skill-phase-<n>
```

## Current Phase Contract

Phase 0 confirms the v1 installation target, source-of-truth documents, and the
first supported repository before writing the skill.

Confirmed inputs:

- Skill name: `autonomous-roadmap-delivery`
- Install target: `/Users/dzianissokalau/.codex/skills/autonomous-roadmap-delivery`
- First supported repository: `/Users/dzianissokalau/Documents/projects/async-research`
- Platform/control-plane topics: backlog, not v1 blockers
- Pilot inspection target: `real_research_product_readiness`

## Phase 0 Verification

Run or confirm:

```bash
test -d /Users/dzianissokalau/.codex/skills && test -w /Users/dzianissokalau/.codex/skills
test -r /Users/dzianissokalau/Documents/projects/async-research/roadmaps/automation/codex_phase_gated_delivery_automation_template.md
test -r /Users/dzianissokalau/Documents/projects/async-research/roadmaps/automation/README.md
test -r /Users/dzianissokalau/Documents/projects/async-research/roadmaps/automation/roadmap_closeout_checklist.md
find /Users/dzianissokalau/Documents/projects/async-research/roadmaps/automation -maxdepth 3 -type f
```

Phase 0 should not create the skill files. Phase 1 owns the skill skeleton and
metadata.

## Operating Rules

1. Work exactly one roadmap phase at a time.
2. Do not begin Phase N+1 until Phase N is delivered, reviewed, fixed if
   needed, verified, and recorded.
3. Treat the roadmap phase acceptance criteria as the source of truth.
4. Keep durable state in `delivery_state.json`.
5. Keep `delivery_log.md` append-only.
6. Use `review_fix_state.json` and `review_fix_log.md` only for review-driven
   repair loops.
7. Stop and record a blocker when a product decision, credential, destructive
   operation, or unclear scope decision is required.
8. Do not write outside the workspace unless the user approves the required
   sandbox escalation.

## Delivery Agent Prompt

```text
Deliver Phase N of roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md.

Use this phase-gated delivery template:
automation/codex_phase_gated_delivery_automation_template.md

Work only on Phase N. Do not start Phase N+1.

Before editing:
- Extract the phase scope, non-goals, acceptance criteria, and required checks.
- Identify owned files.
- Identify which paths require sandbox escalation.

During delivery:
- Keep changes scoped to the phase.
- Preserve unrelated user changes.
- Update automation/autonomous-roadmap-delivery-skill/delivery_log.md with
  scope, changed files, verification, review status, residual risks, and next
  action.

At the end:
- Report changed files.
- Report verification results.
- Report remaining risks.
- Do not claim Phase N is delivered until a fresh review verdict says delivered.
```

## Reviewer Prompt

```text
Review the delivered Phase N changes against
roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md.

Take a skeptical code-review stance. Lead with findings.

Review:
- roadmap phase acceptance criteria
- automation guide
- delivery state
- delivery log
- changed files
- verification evidence

Look for missed criteria, unsafe scope expansion, over-claimed delivery,
missing verification, stale paths, and contradictions between roadmap, state,
and log.

Return:
- Findings ordered by severity with file/line references
- Missing tests or checks
- Residual risks
- Verdict: delivered, needs-fix, or blocked
```

## Phase Advancement

Advance from Phase 0 to Phase 1 only after:

- the install target, source documents, and pilot target are confirmed
- the delivery log records the verification evidence
- a fresh review verdict is `delivered`
- the roadmap header and delivery state are updated
