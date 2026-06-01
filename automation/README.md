# Roadmap Automation Artifacts

This folder keeps low-level Codex delivery machinery separate from the
human-facing strategy and roadmap documents in `../roadmaps/`.

Use `../roadmaps/` for human-facing documents:

- `../roadmaps/automated-roadmap-delivery-strategy.md`
- `../roadmaps/delivered_autonomous-roadmap-delivery-skill-phased-roadmap.md`
- `../roadmaps/delivered_framework_core_and_release_readiness_roadmap.md`
- `../roadmaps/delivered_multi_host_adapter_and_claude_plugin_roadmap.md`

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

## Configured Roadmaps

| Roadmap | Status | Phase | Automation | State |
|---|---|---|---|---|
| `../roadmaps/delivered_autonomous-roadmap-delivery-skill-phased-roadmap.md` | Delivered | Complete | `autonomous-roadmap-delivery-skill` hourly, PAUSED | `autonomous-roadmap-delivery-skill/delivery_state.json` |
| `../roadmaps/delivered_phase_model_policy_and_stall_control_roadmap.md` | Delivered | Complete | `phase-model-policy-and-stall-control` hourly, PAUSED | `phase-model-policy-and-stall-control/delivery_state.json` |
| `../roadmaps/delivered_framework_core_and_release_readiness_roadmap.md` | Completed | Complete | `framework-core-and-release-readiness` hourly, PAUSED | `framework-core-and-release-readiness/delivery_state.json` |
| `../roadmaps/delivered_multi_host_adapter_and_claude_plugin_roadmap.md` | Completed pending pause | Complete | `multi-host-adapter-and-claude-plugin` hourly, ACTIVE pending pause approval | `multi-host-adapter-and-claude-plugin/delivery_state.json` |
