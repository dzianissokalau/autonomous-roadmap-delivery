# Final Deep Review Prompt

Review the GitHub branch for `multi-host-adapter-and-claude-plugin` against
the complete delivery history.

Repository:

```text
https://github.com/dzianissokalau/roadmap-delivery-skill
```

Branch:

```text
codex/multi-host-adapter-and-claude-plugin-finalization
```

GitHub branch URL:

```text
https://github.com/dzianissokalau/roadmap-delivery-skill/tree/codex/multi-host-adapter-and-claude-plugin-finalization
```

Fetch the review branch from GitHub:

```bash
git clone https://github.com/dzianissokalau/roadmap-delivery-skill.git roadmap-delivery-skill-review
cd roadmap-delivery-skill-review
git fetch origin codex/multi-host-adapter-and-claude-plugin-finalization
git switch -c review/multi-host-adapter-and-claude-plugin FETCH_HEAD
```

Primary roadmap file on that branch:

```text
roadmaps/delivered_multi_host_adapter_and_claude_plugin_roadmap.md
```

Do not rely on local-only paths from the delivery machine. Use the GitHub
branch contents as the review source of truth.

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

Known state at prompt update: all numbered phases and finalization are
delivered on the finalization branch, the completion alert is expected to
exist, release artifacts under `dist/` are local ignored outputs, and the
saved Codex automation currently reads back as paused.
