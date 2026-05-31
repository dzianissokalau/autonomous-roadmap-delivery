# Installing The Claude Plugin

The Claude adapter is generated into `dist/claude/`. Treat that directory as a
local Claude Code plugin package snapshot. The package includes the roadmap
delivery skill, canonical references, a read-only reviewer agent, and safety
hook reminders.

## Check The Generated Package

From the repository root:

```bash
python3 scripts/build_adapters.py --adapter claude --check
python3 -m json.tool dist/claude/.claude-plugin/plugin.json >/dev/null
```

## Stage An Isolated Plugin

This stages the plugin in a temporary plugin directory and leaves any active
Claude Code plugin directory untouched.

```bash
export SMOKE_HOME="$(mktemp -d)"
mkdir -p "$SMOKE_HOME/claude/plugins"
cp -R dist/claude "$SMOKE_HOME/claude/plugins/roadmap-delivery"
```

If the `claude` binary is installed, this optional host check should return
usage text:

```bash
CLAUDE_PLUGIN_DIR="$SMOKE_HOME/claude/plugins" claude --help
```

If `claude` is not installed, skip only the host binary check. The plugin
structure and file-backed runtime checks still run offline.

## Prepare Demo Automation Readback

Copy the demo fixture into a temporary git checkout, then copy its committed
sample automation config into the temporary Codex-style automation readback
directory used by the local validators:

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

Run the same file-backed runtime commands the Claude skill asks a maintainer to
use before claiming delivery:

```bash
AUTONOMOUS_ROADMAP_AUTOMATIONS_DIR="$SMOKE_HOME/.codex/automations" \
PYTHONPATH="$PWD/src" \
python3 -m roadmap_delivery.cli inspect \
  --repo-root "$SMOKE_REPO" \
  --roadmap-slug demo-roadmap \
  --automation-id demo-roadmap-delivery \
  --strict \
  --json

AUTONOMOUS_ROADMAP_AUTOMATIONS_DIR="$SMOKE_HOME/.codex/automations" \
PYTHONPATH="$PWD/src" \
python3 -m roadmap_delivery.cli validate \
  --repo-root "$SMOKE_REPO" \
  --roadmap-slug demo-roadmap \
  --automation-id demo-roadmap-delivery \
  --strict \
  --json
```

For blocked-remediation and model-policy-mismatch fixtures, follow
`examples/demo-roadmap/runtime-checklist.md` in a temporary copy of the fixture.
