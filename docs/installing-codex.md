# Installing The Codex Package

The Codex adapter is generated into `skill/roadmap-delivery-skill/`. Treat that
directory as the installable package snapshot; do not sync it into a live Codex
home until the generated package and smoke checks pass.

## Check The Generated Package

From the repository root:

```bash
python3 scripts/build_adapters.py --adapter codex --check
```

## Stage An Isolated Install

This stages the package in a temporary Codex home and leaves the active Codex
installation untouched.

```bash
export SMOKE_HOME="$(mktemp -d)"
mkdir -p "$SMOKE_HOME/.codex/skills"
cp -R skill/roadmap-delivery-skill \
  "$SMOKE_HOME/.codex/skills/roadmap-delivery-skill"
```

If the `codex` binary is installed, this optional host check should return
usage text without touching the active Codex home:

```bash
CODEX_HOME="$SMOKE_HOME/.codex" codex --help
```

If `codex` is not installed, skip only the host binary check. The package
layout and helper-script smoke checks still run offline.

## Prepare Demo Automation Readback

Copy the demo fixture into a temporary git checkout, then copy its committed
sample automation config into the temporary home and rewrite the checkout path
for this machine:

```bash
export SMOKE_REPO="$SMOKE_HOME/demo-roadmap"
cp -R examples/demo-roadmap "$SMOKE_REPO"
git -C "$SMOKE_REPO" init -b codex/demo-roadmap-phase-1
git -C "$SMOKE_REPO" add .
git -C "$SMOKE_REPO" \
  -c user.name=Demo \
  -c user.email=demo.invalid \
  commit -m "demo fixture"

mkdir -p "$SMOKE_HOME/.codex/automations/demo-roadmap-delivery"
python3 - <<'PY'
from pathlib import Path
import os

repo = Path(os.environ["SMOKE_REPO"]).resolve()
home = Path(os.environ["SMOKE_HOME"])
source = repo / "automation-config" / "demo-roadmap-delivery" / "automation.toml"
target = home / ".codex" / "automations" / "demo-roadmap-delivery" / "automation.toml"
text = source.read_text(encoding="utf-8")
text = text.replace('cwds = ["."]', f'cwds = ["{repo}"]')
target.write_text(text, encoding="utf-8")
PY
```

## Validate The Demo Roadmap

Run the installed helper scripts against the demo roadmap:

```bash
AUTONOMOUS_ROADMAP_AUTOMATIONS_DIR="$SMOKE_HOME/.codex/automations" \
PYTHONPATH="$PWD/src" \
"$SMOKE_HOME/.codex/skills/roadmap-delivery-skill/scripts/inspect_delivery_state.py" \
  --repo-root "$SMOKE_REPO" \
  --roadmap-slug demo-roadmap \
  --automation-id demo-roadmap-delivery \
  --json

AUTONOMOUS_ROADMAP_AUTOMATIONS_DIR="$SMOKE_HOME/.codex/automations" \
PYTHONPATH="$PWD/src" \
"$SMOKE_HOME/.codex/skills/roadmap-delivery-skill/scripts/validate_delivery_artifacts.py" \
  --repo-root "$SMOKE_REPO" \
  --roadmap-slug demo-roadmap \
  --automation-id demo-roadmap-delivery \
  --strict \
  --json
```

For blocked-remediation and model-policy-mismatch fixtures, follow
`examples/demo-roadmap/runtime-checklist.md` in a temporary copy of the fixture.
