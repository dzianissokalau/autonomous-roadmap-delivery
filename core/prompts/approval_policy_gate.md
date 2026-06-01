# Approval Policy Gate Prompt Fragment

Before asking for approval or performing an operation automatically, read and
validate `approval_policy.json` when present. Resolve the named operation to
`allowed`, `ask`, or `forbidden`: proceed only for `allowed`, ask or block for
`ask`, and record a blocker for `forbidden` or unknown operations. Missing
policy keeps conservative legacy behavior, and never-auto operations remain
forbidden in every approval mode.
