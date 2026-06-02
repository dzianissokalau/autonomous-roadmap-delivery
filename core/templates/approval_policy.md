# Approval Policy Template

Use this template for `automation/<roadmap-slug>/approval_policy.json`.

```json
{
  "schema_version": 1,
  "approval_mode": "conservative",
  "operations": {
    "edit_phase_owned_files": true,
    "write_state_log_review_artifacts": true,
    "create_or_switch_phase_branch": true,
    "run_verification": true,
    "commit_delivered_phase_locally": false,
    "retarget_saved_automation": false,
    "pause_saved_automation": false,
    "push_current_phase_branch": false
  },
  "pause_automation_on_completion": false,
  "pause_automation_on_stall": false,
  "never_auto": [
    "force_push",
    "git_reset_hard",
    "delete_branches_or_tags",
    "merge_or_promote_to_main",
    "publish_releases_or_packages",
    "use_unavailable_credentials",
    "change_repository_security_or_billing",
    "install_or_sync_global_tools",
    "destructive_filesystem_outside_phase_scope"
  ]
}
```

Missing approval policy files keep legacy conservative behavior. Invalid policy
files must fail validation before delivery work relies on them.

Setup wizard output must default to `conservative`. Delegated modes are valid
only when explicitly selected by the operator and recorded in this file.

`pause_automation_on_completion` and `pause_automation_on_stall` are
context-specific safety approvals. Delegated modes normally allow them through
`pause_saved_automation`; conservative mode may set one of these flags to
`true` as an explicit setup choice without approving unrelated runner edits.
