import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.test_helper_scripts import DeliveryFixture, VALIDATE_SCRIPT
except ModuleNotFoundError:
    from test_helper_scripts import DeliveryFixture, VALIDATE_SCRIPT


REPO_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    maxDiff = None

    def run_cli(self, *args, env=None, allowed_returncodes=(0,)):
        proc = subprocess.run(
            [sys.executable, "-m", "roadmap_delivery.cli", *args],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        self.assertIn(proc.returncode, allowed_returncodes, proc.stderr or proc.stdout)
        return proc

    def test_version_runs_from_source_tree(self):
        proc = self.run_cli("version")

        self.assertEqual(proc.stdout.strip(), "roadmap-delivery 0.0.0")

    def test_validate_uses_same_report_as_helper_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True)

            cli = self.run_cli(
                "validate",
                "--repo-root",
                str(fixture.repo_root),
                "--roadmap-slug",
                fixture.slug,
                "--automation-id",
                fixture.automation_id,
                "--json",
                env=fixture.env(),
            )
            helper = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATE_SCRIPT),
                    "--repo-root",
                    str(fixture.repo_root),
                    "--roadmap-slug",
                    fixture.slug,
                    "--automation-id",
                    fixture.automation_id,
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=fixture.env(),
                check=False,
            )
            self.assertEqual(helper.returncode, 0, helper.stderr or helper.stdout)
            cli_report = json.loads(cli.stdout)
            helper_report = json.loads(helper.stdout)

            self.assertEqual(cli_report["command"], "validate")
            self.assertEqual(cli_report["cli_schema_version"], 1)
            self.assertEqual(cli_report["status"], "ok")
            self.assertEqual(cli_report["errors"], helper_report["errors"])
            self.assertEqual(cli_report["warnings"], helper_report["warnings"])
            self.assertEqual(cli_report["state_current_phase"], helper_report["state_current_phase"])

    def test_inspect_json_has_stable_cli_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True)

            proc = self.run_cli(
                "inspect",
                "--repo-root",
                str(fixture.repo_root),
                "--roadmap-slug",
                fixture.slug,
                "--automation-id",
                fixture.automation_id,
                "--json",
                env=fixture.env(),
            )
            report = json.loads(proc.stdout)

            self.assertEqual(report["command"], "inspect")
            self.assertEqual(report["cli_schema_version"], 1)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["current_phase"], "Phase 1 - Fixture")
            self.assertEqual(report["required_model"], "gpt-5.5")

    def test_scaffold_dry_run_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()

            proc = self.run_cli(
                "scaffold",
                "--repo-root",
                str(repo_root),
                "--roadmap-slug",
                "new-roadmap",
                "--automation-id",
                "new-roadmap-delivery",
                "--dry-run",
                "--json",
            )
            report = json.loads(proc.stdout)

            self.assertTrue(report["dry_run"])
            self.assertEqual(report["command"], "scaffold")
            self.assertIn(str(repo_root.resolve() / "automation" / "new_roadmap"), report["would_create"])
            self.assertFalse((repo_root / "automation" / "new_roadmap").exists())

    def test_package_dry_run_reports_codex_render_plan(self):
        proc = self.run_cli(
            "package",
            "--repo-root",
            str(REPO_ROOT),
            "--adapter",
            "codex",
            "--dry-run",
            "--json",
            allowed_returncodes=(0,),
        )
        report = json.loads(proc.stdout)

        self.assertTrue(report["dry_run"])
        self.assertEqual(report["command"], "package")
        self.assertEqual(report["adapter"], "codex")
        self.assertEqual(report["would_write"], str(REPO_ROOT / "skill" / "roadmap-delivery-skill"))
        self.assertIn(str(REPO_ROOT / "core" / "references"), report["would_read"])


if __name__ == "__main__":
    unittest.main()
