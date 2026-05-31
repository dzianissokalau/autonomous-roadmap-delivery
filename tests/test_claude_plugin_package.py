import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_adapters.py"
DIST_ROOT = REPO_ROOT / "dist" / "claude"
PLUGIN_MANIFEST = DIST_ROOT / ".claude-plugin" / "plugin.json"
SKILL_ROOT = DIST_ROOT / "skills" / "roadmap-delivery-skill"
SKILL_FILE = SKILL_ROOT / "SKILL.md"
REFERENCE_ROOT = SKILL_ROOT / "references"
CORE_REFERENCE_ROOT = REPO_ROOT / "core" / "references"

CORE_REFERENCES = (
    "finalization-and-promotion.md",
    "model-policy-and-stall-control.md",
    "phase-loop.md",
    "review-and-fix.md",
    "setup-automation.md",
    "state-log-and-branches.md",
    "troubleshooting.md",
)


class ClaudePluginPackageTests(unittest.TestCase):
    maxDiff = None

    def run_build_check(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(BUILD_SCRIPT),
                "--repo-root",
                str(REPO_ROOT),
                "--adapter",
                "claude",
                "--check",
                "--json",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        report = json.loads(proc.stdout)
        self.assertEqual(report["adapters"], ["claude"])
        claude = report["reports"][0]
        self.assertEqual(claude["adapter"], "claude")
        return report, claude

    def generated_text_files(self):
        return sorted(path for path in DIST_ROOT.rglob("*") if path.is_file())

    def test_build_check_has_no_generated_plugin_drift(self):
        report, claude = self.run_build_check()

        self.assertEqual(report["status"], "ok")
        self.assertEqual(claude["status"], "ok")
        self.assertEqual(claude["diffs"], [])
        self.assertEqual(claude["errors"], [])
        self.assertEqual(claude["check_mode"], "output")
        self.assertTrue(claude["output_committed"])
        self.assertEqual(claude["output_dir"], str(DIST_ROOT))

    def test_manifest_declares_minimal_plugin_identity(self):
        self.run_build_check()
        manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))

        self.assertEqual(manifest["name"], "roadmap-delivery")
        self.assertEqual(manifest["displayName"], "Roadmap Delivery Skill")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["license"], "Apache-2.0")
        self.assertIsInstance(manifest["description"], str)
        self.assertTrue(manifest["description"])
        self.assertEqual(set(path.name for path in PLUGIN_MANIFEST.parent.iterdir()), {"plugin.json"})

    def test_skill_and_core_references_are_generated(self):
        _, claude = self.run_build_check()
        files = {item["path"]: item for item in claude["files"]}

        self.assertIn(".claude-plugin/plugin.json", files)
        self.assertIn("skills/roadmap-delivery-skill/SKILL.md", files)
        for name in CORE_REFERENCES:
            with self.subTest(reference=name):
                output = f"skills/roadmap-delivery-skill/references/{name}"
                self.assertIn(output, files)
                self.assertEqual(files[output]["core_source"], f"core/references/{name}")
                self.assertEqual(
                    (REFERENCE_ROOT / name).read_text(encoding="utf-8"),
                    (CORE_REFERENCE_ROOT / name).read_text(encoding="utf-8"),
                )

    def test_skill_preserves_core_phase_gate_safety_rules(self):
        self.run_build_check()
        skill = SKILL_FILE.read_text(encoding="utf-8")

        self.assertIn("Work exactly one roadmap phase at a time.", skill)
        self.assertIn("When state is `blocked`, try blocked-run remediation", skill)
        self.assertIn("Run required verification before claiming delivery.", skill)
        self.assertIn("Require a fresh review verdict before phase advancement.", skill)
        self.assertIn("Do not promote, merge, push, publish", skill)

    def test_generated_claude_files_have_no_codex_only_runtime_paths(self):
        self.run_build_check()
        forbidden = (
            "~/.codex",
            "/.codex/",
            "skill/roadmap-delivery-skill",
            "agents/openai.yaml",
            "codex exec",
        )

        for path in self.generated_text_files():
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                with self.subTest(path=path.relative_to(DIST_ROOT).as_posix(), pattern=pattern):
                    self.assertNotIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
