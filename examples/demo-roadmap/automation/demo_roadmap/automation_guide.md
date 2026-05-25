# Demo Roadmap Automation Guide

Status: Demo fixture
Roadmap: `roadmaps/in_progress_demo_roadmap.md`
Roadmap slug: `demo-roadmap`
State file: `automation/demo_roadmap/delivery_state.json`
Delivery log: `automation/demo_roadmap/delivery_log.md`
Review directory: `automation/demo_roadmap/reviews`
Policy file: `automation/demo_roadmap/phase_model_policy.json`
Sample automation: `demo-roadmap-delivery`
Model: `gpt-5.5`
Reasoning effort: `xhigh`

## Operating Policy

- Deliver exactly one demo phase at a time.
- Validate the state, roadmap, log, review files, policy, and saved automation
  config before editing.
- If state is blocked, enter Blocker Remediation Mode before retrying delivery.
- Do not use network access, credentials, publication, or live automation
  changes for this demo fixture.
