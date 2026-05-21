# Roadmap Automation Artifacts

This folder keeps low-level Codex delivery machinery separate from the
human-facing strategy and roadmap documents in `../roadmaps/`.

Use `../roadmaps/` for human-facing documents:

- `../roadmaps/automated-roadmap-delivery-strategy.md`
- `../roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md`

Use this folder for automation templates, state, logs, review outputs, and
closeout checklists.

## Layout

```text
automation/
  README.md
  codex_phase_gated_delivery_automation_template.md
  roadmap_closeout_checklist.md
  <roadmap_slug>/
    automation_guide.md
    delivery_state.json
    delivery_log.md
    review_fix_state.json
    review_fix_log.md
    reviews/
      ...
```

Do not place delivery state, automation logs, or review iteration files directly
in the project root or `../roadmaps/`.

## Active Roadmaps

| Roadmap | Status | Phase | Automation | State |
|---|---|---|---|---|
| `../roadmaps/autonomous-roadmap-delivery-skill-phased-roadmap.md` | In Progress | Phase 0 - Scope Confirmation | `autonomous-roadmap-delivery-skill` hourly, ACTIVE | `autonomous-roadmap-delivery-skill/delivery_state.json` |
