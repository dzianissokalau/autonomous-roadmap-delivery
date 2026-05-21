---
name: roadmap-delivery-skill
description: Use when Codex needs to set up roadmap delivery automation, inspect roadmap automation status, pause or activate roadmap automation, repair stale roadmap paths, deliver or review one current phase, or finalize/promote delivered roadmap branches in a phase-gated workflow. Do not use for ordinary feature implementation, generic PR review, general project management, unrelated Codex skill creation, or broad release automation without an explicit roadmap phase contract.
---

# Roadmap Delivery Skill

Use this skill for file-backed, phase-gated roadmap delivery workflows. Keep work anchored to the roadmap, `delivery_state.json`, `delivery_log.md`, review files, git branch and commit history, verification output, and `automation.toml`.

## First Move

1. Identify the exact roadmap path or automation id before acting.
2. Read the roadmap, delivery state, delivery log, review files, phase model policy when present, automation config, and `git status`.
3. Reconcile lifecycle rename drift, stale roadmap paths, branch names, and completed or blocked hard-stop states.
4. If state is `blocked`, route through blocked-run remediation before attempting normal phase delivery.
5. Stop and report the mismatch only when roadmap, state, log, review files, verification output, automation config, branch, or worktree evidence disagree and the blocker is not safely repairable in the current run.

## Route The Task

- Setup new automation: read `references/setup-automation.md`.
- Deliver one current phase: read `references/phase-loop.md`.
- Handle review findings: read `references/review-and-fix.md`.
- Inspect status, branches, state, or logs: read `references/state-log-and-branches.md`. Once Phase 4 exists, use `scripts/inspect_delivery_state.py` for status questions.
- Finalize, promote, or close out delivered work: read `references/finalization-and-promotion.md`.
- Repair bad state, stale paths, blocked runs, or lifecycle drift: read `references/troubleshooting.md`.
- Use phase model policy, stalled-run handling, or model-aware automation: read `references/model-policy-and-stall-control.md`.

## Hard Rules

- Work exactly one roadmap phase at a time.
- When state is `blocked`, try blocked-run remediation before retrying normal phase advancement.
- Run required verification before claiming delivery.
- Require a fresh review verdict before phase advancement.
- Preserve unrelated worktree changes; never revert user work without explicit instruction.
- Do not broadly stage files or hide unrelated diffs inside phase work.
- Do not force-push.
- Do not promote to `main`, merge, push, or change Codex app automation config without explicit human approval.

## Stop Conditions

Stop and report clearly when required files are missing, state surfaces disagree, verification cannot run, review/fix iterations reach their limit, credentials or approval are needed, the phase scope is ambiguous, destructive git operations would be required, or the requested work expands beyond the current roadmap phase.
