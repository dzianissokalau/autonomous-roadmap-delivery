import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_codex_package.py"
MANIFEST = REPO_ROOT / "adapters" / "codex" / "package_manifest.json"
SNAPSHOT = REPO_ROOT / "tests" / "snapshots" / "codex" / "package_snapshot.json"


class CodexAdapterGenerationTests(unittest.TestCase):
    maxDiff = None

    def run_build_check(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(BUILD_SCRIPT),
                "--repo-root",
                str(REPO_ROOT),
                "--check",
                "--json",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        return json.loads(proc.stdout)

    def test_build_check_has_no_generated_package_drift(self):
        report = self.run_build_check()

        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["adapter"], "codex")
        self.assertEqual(report["diffs"], [])
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["output_dir"], str(REPO_ROOT / "skill" / "roadmap-delivery-skill"))

    def test_rendered_package_matches_snapshot(self):
        report = self.run_build_check()
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

        self.assertEqual(snapshot["schema_version"], 1)
        self.assertEqual(snapshot["adapter"], "codex")
        actual = [
            {
                key: value
                for key, value in item.items()
                if key in {"path", "sha256", "size", "mode", "core_source", "core_sha256", "core_size"}
            }
            for item in report["files"]
        ]
        self.assertEqual(snapshot["files"], actual)

    def test_reference_templates_are_tied_to_core_sources(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        reference_entries = [
            item for item in manifest["files"] if str(item.get("output", "")).startswith("references/")
        ]

        self.assertTrue(reference_entries)
        for item in reference_entries:
            with self.subTest(output=item["output"]):
                core_source = item.get("core_source")
                self.assertIsInstance(core_source, str)
                self.assertTrue((REPO_ROOT / core_source).exists())

    def test_cli_package_plan_reports_renderer_ready(self):
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "roadmap_delivery.cli",
                "package",
                "--repo-root",
                str(REPO_ROOT),
                "--adapter",
                "codex",
                "--dry-run",
                "--json",
            ],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        report = json.loads(proc.stdout)

        self.assertTrue(report["renderer_ready"])
        self.assertTrue(report["adapter_overlay_present"])


if __name__ == "__main__":
    unittest.main()
