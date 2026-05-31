# Future Adapter Checklist

Use this checklist before adding support for a new host.

- Add `host-capabilities/<host>.yaml` with explicit parity levels, fallbacks,
  support status, model-selection behavior, and approval boundaries.
- Add `adapters/<host>/package.py` with deterministic metadata and no
  host-unsupported claims.
- Render from `core/`, `schemas/`, and shared library contracts instead of
  forking workflow rules.
- Add generated package checks, snapshot coverage, and drift diagnostics that
  identify the failing adapter.
- Add install or runtime smoke checks that do not require credentials for the
  default test path.
- Update compatibility and install documentation to distinguish supported,
  planned, unsupported, and future-work surfaces.
- Include the adapter in release artifacts only after privacy checks pass.
- Require explicit human approval for publication, promotion, global install
  synchronization, credentials, and destructive git operations.
