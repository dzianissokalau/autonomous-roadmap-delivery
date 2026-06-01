# Automation Guide Template

Use this template for `automation/<roadmap-slug>/automation_guide.md`.

```markdown
# <Roadmap Name> Automation Guide

Status: Active | Paused | Completed
Roadmap: `roadmaps/<roadmap-file>.md`
Roadmap slug: `<roadmap-slug>`
State file: `automation/<roadmap-slug>/delivery_state.json`
Delivery log: `automation/<roadmap-slug>/delivery_log.md`
Review directory: `automation/<roadmap-slug>/reviews`
Policy file: `automation/<roadmap-slug>/phase_model_policy.json`
Approval policy file: `automation/<roadmap-slug>/approval_policy.json`
Approval mode: `conservative | delegated_local | delegated_delivery | custom`
Automation: `<runner-id>`
Cadence: `<cadence>`
Model: `<configured-model>`
Reasoning effort: `<configured-reasoning-effort>`
Execution environment: `<runner-environment>`

## Operating Policy

- Deliver exactly one roadmap phase at a time.
- Reconcile durable artifacts, runner config, branch, and worktree before edits.
- Preserve unrelated user changes.
- Run required verification before claiming delivery.
- Require a fresh review verdict before phase advancement.
- Validate approval policy before relying on any pre-approved operation.
- Treat missing approval policy as conservative legacy behavior.
- Keep publication, promotion, destructive operations, credentials, and
  ambiguous product decisions operator-approved.
```
