# Delivery Log Template

Use this shape for append-only delivery log entries.

```markdown
## Phase N - YYYY-MM-DD - Delivery Pass M

Status: delivering | reviewing | fixing | delivered | blocked
Branch: `<phase-branch-or-not-available>`

### Scope

- ...

### Changes

- ...

### Tests And Verification

- `command`: passed | failed | not run

### Review

- Review file: `automation/<roadmap-slug>/reviews/<review-file>.md`
- Verdict: delivered | needs-fix | blocked | pending

### Residual Risks

- ...

### Next Action

- ...
```

Do not rewrite prior entries after delivery starts.
