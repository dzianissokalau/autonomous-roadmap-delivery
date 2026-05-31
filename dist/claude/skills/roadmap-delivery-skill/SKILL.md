---
description: Use when Claude Code needs to set up, inspect, deliver, review, remediate blockers for, or finalize a file-backed phase-gated roadmap delivery workflow. Use only when a roadmap path or automation id is explicit.
---

# Roadmap Delivery Skill

Use this skill for file-backed, phase-gated roadmap delivery workflows. Keep
work anchored to the roadmap, delivery state, delivery log, review files, git
branch and commit history, verification output, and runner configuration.

## First Move

1. Identify the exact roadmap path or automation id before acting.
2. Read the roadmap, delivery state, delivery log, review files, phase model
   policy when present, saved runner configuration, branch, and worktree status.
3. Reconcile lifecycle rename drift, stale roadmap paths, branch names, and
   completed or blocked hard-stop states before editing.
4. If state is `blocked`, route through blocked-run remediation before
   attempting normal phase delivery.
5. Stop and report mismatches when roadmap, state, log, reviews, verification,
   runner config, branch, or worktree evidence disagree in a way that cannot be
   repaired locally.

## Route The Task

- Setup new automation: read `references/setup-automation.md`.
- Deliver one current phase: read `references/phase-loop.md`.
- Handle review findings: read `references/review-and-fix.md`.
- Inspect status, branches, state, or logs: read
  `references/state-log-and-branches.md`.
- Finalize, promote, or close out delivered work: read
  `references/finalization-and-promotion.md`.
- Repair bad state, stale paths, blocked runs, or lifecycle drift: read
  `references/troubleshooting.md`.
- Use phase model policy, stalled-run handling, or model-aware automation: read
  `references/model-policy-and-stall-control.md`.

## Hard Rules

- Work exactly one roadmap phase at a time.
- When state is `blocked`, try blocked-run remediation before retrying normal
  phase advancement.
- Run required verification before claiming delivery.
- Require a fresh review verdict before phase advancement.
- Preserve unrelated worktree changes; never revert user work without explicit
  instruction.
- Do not broadly stage files or hide unrelated diffs inside phase work.
- Do not force-push.
- Do not promote, merge, push, publish, install global packages, use
  credentials, or change runner configuration without explicit human approval.

## Claude Host Notes

- This plugin is a generated Claude Code package. It relies on repository-local
  roadmap artifacts and host runner readback supplied by the operator.
- Treat recurring automation as a host-runner concern; the repository state,
  logs, reviews, and alerts remain authoritative.
- If no independent reviewer agent is available, same-context review is allowed
  only when that limitation is recorded explicitly and the evidence satisfies
  the current phase gate.
