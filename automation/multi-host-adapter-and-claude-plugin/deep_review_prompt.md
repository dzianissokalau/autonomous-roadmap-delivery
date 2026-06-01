# Final Deep Review Prompt

Review `roadmaps/delivered_multi_host_adapter_and_claude_plugin_roadmap.md`
against the complete delivery history for
`multi-host-adapter-and-claude-plugin`.

Use a skeptical code-review stance. Check:

- every numbered phase and finalization acceptance criterion
- `delivery_state.json`, `delivery_log.md`, `review_fix_state.json`, and
  review artifacts for consistency
- final verification sufficiency, including adapter checks, release build,
  privacy scan, full tests, and checksum evidence
- branch, worktree, publication, promotion, and installed-skill
  synchronization risks
- whether generated Codex, Claude, and generic adapter artifacts support the
  roadmap's multi-host support claims without overstating live Claude runtime
  coverage

Verdict options: `ready_for_human_review`, `needs_fix`, or `blocked`.

Known state at prompt creation: all numbered phases and finalization are
locally delivered, the completion alert is expected to exist, release artifacts
under `dist/` are local ignored outputs, and the live Codex automation remains
active until the operator approves pause.
