# Privacy And Sanitization

This guide defines what is safe to publish from the roadmap delivery framework
and what must stay local.

## Release-Bound Content

The current Codex release bundle is expected to include:

```text
README.md
SECURITY.md
LICENSE
pyproject.toml
docs/
core/
schemas/
src/
scripts/
adapters/
skill/roadmap-delivery-skill/
```

It must not include `automation/`, `roadmaps/`, `.git/`, `.codex/`, local
alert files, review transcripts, or operator-specific state.

## Local Paths And Operator Names

Use placeholders such as `/path/to/repo`, `$HOME`, `${CODEX_HOME}`, and
`<operator>` in docs, examples, tests, and release notes. Do not publish
absolute paths under `/Users/<name>/`, `/home/<name>/`, Windows user
directories, or local temporary paths under `/private/tmp` and
`/private/var/folders`.

## Repository Remotes

Public repository URLs are acceptable in release docs. Private remotes, fork
names, customer organization names, and internal hostnames should be replaced
with neutral examples before publication.

## Secrets And Tokens

Never place credentials in roadmap state, delivery logs, review artifacts,
fixtures, screenshots, or release packages. Use environment variables or the
host secret store, and document only the variable names needed by an operator.

## Review Artifacts

Review files and delivery logs are commit-friendly project evidence, but they
can include local command output, branch names, paths, or operator context.
They are intentionally excluded from release bundles. Before quoting review
artifacts externally, redact private paths and any sensitive project or person
names.

## Manual Release Checklist

Run this checklist before publishing a bundle or copying release files outside
the repository:

```text
[ ] Build the package from committed sources only.
[ ] Run python3 scripts/check_release_privacy.py --repo-root .
[ ] If scanning a tarball, pass --bundle dist/<artifact>.tar.gz.
[ ] Confirm the bundle excludes automation/, roadmaps/, .git/, and .codex/.
[ ] Confirm no local absolute paths, operator names, or secrets are present.
[ ] Confirm release notes do not quote private automation state verbatim.
```
