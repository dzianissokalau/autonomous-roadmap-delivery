# Codex Adapter

This directory is the source for the committed Codex skill package at
`skill/roadmap-delivery-skill/`.

The renderer uses `package_manifest.json` to combine host-neutral core sources
with Codex-specific templates. Reference entries in the manifest point to their
matching `core/references/` source so package generation fails if a canonical
workflow source is missing. The Codex templates preserve the current installed
skill behavior while the framework migration moves ownership out of the
installed-skill snapshot.

Check generated output with:

```bash
python3 scripts/build_codex_package.py --check
```

Apply regenerated output with:

```bash
python3 scripts/build_codex_package.py --write
```
