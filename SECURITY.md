# Security Policy

## Supported Versions

Security fixes are accepted for the active `main` branch and active roadmap
delivery branches in this repository. No separately versioned release line is
published yet; release version support begins when the release and versioning
phase introduces tagged artifacts.

## Reporting A Vulnerability

Prefer a private GitHub Security Advisory for this repository. If that channel
is unavailable, open a minimal public issue asking for a security contact and
do not include exploit details, secrets, private paths, or vulnerable
automation artifacts in the public issue.

Include:

- affected file paths or package versions
- impact and reproduction steps
- whether credentials, local automation state, or release artifacts are exposed
- a safe redacted example when evidence includes private data

## Unsafe Automation Surfaces

Treat these surfaces as sensitive before release or external publication:

- saved Codex automation configuration and prompts
- local `automation/<roadmap-slug>/` state, logs, alerts, and reviews
- operator-local paths, usernames, machine names, and temporary directories
- repository remotes that reveal private organization or fork names
- credentials, tokens, cookies, API keys, and private keys
- generated release bundles and any manually copied install package

Repository-local automation artifacts are useful review evidence, but they are
not release package inputs unless a future phase explicitly changes that
contract.

## Secret Handling

Do not commit secrets to roadmaps, reviews, automation logs, tests, examples,
or generated packages. Use environment variables or the hosting platform's
secret store for credentials. Redact local paths and operator names before
copying automation evidence into issues, pull requests, or release notes.

Run the release privacy scanner before publication:

```bash
python3 scripts/check_release_privacy.py --repo-root .
```

The scanner catches common local path leaks, obvious token shapes, private key
markers, and forbidden release bundle paths. It is a guardrail, not a complete
DLP system.
