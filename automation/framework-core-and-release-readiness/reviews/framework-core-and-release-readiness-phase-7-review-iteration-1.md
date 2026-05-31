# Framework Core And Release Readiness Phase 7 Review - Iteration 1

Reviewed at: 2026-05-25T08:14:53Z
Roadmap: `roadmaps/in_progress_framework_core_and_release_readiness_roadmap.md`
Phase: Phase 7 - Security And Privacy Guardrails
Branch: `codex/framework-core-and-release-readiness-phase-7`
Reviewer context: same Codex session; delegated fresh-context review was not used because the available sub-agent tool requires an explicit sub-agent request.
Verdict: delivered

## Findings

No blocking findings.

## Scope Review

- `SECURITY.md:3` defines supported-version policy, and
  `SECURITY.md:10` documents a responsible disclosure path that avoids putting
  sensitive details in public issues.
- `SECURITY.md:24` identifies unsafe automation surfaces, including saved
  automation configuration, local automation artifacts, operator-local paths,
  repository remotes, credentials, and generated release bundles.
- `docs/privacy-and-sanitization.md:6` documents release-bound content and
  excludes automation, roadmap, git, Codex, alert, review, and operator-state
  artifacts from release bundles.
- `docs/privacy-and-sanitization.md:25` covers local paths and operator names,
  `docs/privacy-and-sanitization.md:33` covers repository remotes,
  `docs/privacy-and-sanitization.md:39` covers secrets, and
  `docs/privacy-and-sanitization.md:45` covers review artifacts.
- `docs/privacy-and-sanitization.md:53` adds the manual release checklist,
  including scanner and tarball scan steps.
- `scripts/check_release_privacy.py:15` defines the release-bound scan set,
  including `SECURITY.md` and `docs`, matching the release bundle inputs.
- `scripts/check_release_privacy.py:52` scans for unsanitized local paths,
  local temporary paths, private key markers, common token shapes, and generic
  secret assignments.
- `scripts/check_release_privacy.py:178` rejects release bundle paths that
  escape the archive root or include automation, roadmap, git, or private
  Codex directory segments.
- `tests/test_privacy_sanitization.py:33` verifies current release-bound files
  pass the privacy scan, and `tests/test_privacy_sanitization.py:42`,
  `tests/test_privacy_sanitization.py:64`, and
  `tests/test_privacy_sanitization.py:85` cover local-path, secret-shape, and
  forbidden-bundle-path failures.
- `.github/workflows/ci.yml:55` runs the release privacy scanner in CI.
- `.github/workflows/release-check.yml:35` includes `SECURITY.md` and `docs`
  in the release-check bundle so README links remain valid in the artifact.
- `README.md:11` links the security policy and privacy guide, and
  `README.md:197` documents the local privacy scan command.

## Verification Evidence

- `python3 scripts/check_release_privacy.py --repo-root .`: passed; 67 files
  scanned, 0 findings, 0 errors.
- `python3 -m unittest tests.test_privacy_sanitization -v`: passed, 5 tests.
- `python3 -m unittest discover -s tests -v`: passed, 76 tests.
- `PYTHONPYCACHEPREFIX=$TMPDIR/roadmap-delivery-phase7-pycache python3 -m py_compile scripts/build_codex_package.py scripts/check_release_privacy.py src/roadmap_delivery/*.py roadmap_delivery/__init__.py skill/roadmap-delivery-skill/scripts/*.py tests/*.py`: passed.
- `python3 scripts/build_codex_package.py --check`: passed with `status: ok`,
  14 files, zero diffs, and zero errors.
- Local release-bundle privacy smoke check:
  `tar -czf dist/roadmap-delivery-codex-skill.tar.gz README.md SECURITY.md LICENSE pyproject.toml docs core schemas src scripts adapters skill/roadmap-delivery-skill` followed by
  `python3 scripts/check_release_privacy.py --repo-root . --bundle dist/roadmap-delivery-codex-skill.tar.gz`: passed; 134 files scanned, 0 findings, 0 errors. The generated local bundle was removed afterward.
- `git diff --check`: passed.
- `python3 -m roadmap_delivery.cli validate --repo-root /Users/dzianissokalau/Documents/projects/roadmap-delivery-automation --roadmap-slug framework-core-and-release-readiness --automation-id framework-core-and-release-readiness --strict --allow-warning worktree_dirty --json`: passed with only the expected `worktree_dirty` warning.

## Missing Tests Or Checks

None for the Phase 7 contract. The scanner is intentionally a guardrail for
obvious local path and secret leaks, not a full DLP system.

## Finding Disposition

- No findings.

## Residual Risks

- Same-context review was used because delegated fresh-context review requires
  an explicit sub-agent request in this environment.
- The scanner uses conservative regexes for common leak shapes. It does not
  prove all sensitive business context has been removed from prose.
- The release-check workflow still contains its existing archive-member safety
  check; the richer content scan runs in CI and as a documented local/manual
  release command.
- Existing unrelated worktree dirt remains limited to `automation/README.md`
  and `roadmaps/in_progress_multi_host_adapter_and_claude_plugin_roadmap.md`.

## Verdict

delivered
