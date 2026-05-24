import json
import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    from tests.test_helper_scripts import DeliveryFixture, REPO_ROOT, VALIDATE_SCRIPT
except ModuleNotFoundError:  # pragma: no cover - unittest discover import style
    from test_helper_scripts import DeliveryFixture, REPO_ROOT, VALIDATE_SCRIPT


class SchemaValidationTests(unittest.TestCase):
    maxDiff = None

    def run_validate(self, fixture, *extra_args, allowed_returncodes=(0, 1)):
        proc = subprocess.run(
            [
                "python3",
                str(VALIDATE_SCRIPT),
                "--repo-root",
                str(fixture.repo_root),
                "--roadmap-slug",
                fixture.slug,
                "--automation-id",
                fixture.automation_id,
                "--json",
                *extra_args,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=fixture.env(),
            check=False,
        )
        self.assertIn(proc.returncode, allowed_returncodes, proc.stderr or proc.stdout)
        return json.loads(proc.stdout)

    def warning_codes(self, report):
        return {item["code"] for item in report.get("warnings", [])}

    def error_codes(self, report):
        return {item["code"] for item in report.get("errors", [])}

    def test_schema_files_are_present_and_valid_json(self):
        schema_dir = REPO_ROOT / "schemas"

        for filename in (
            "delivery_state.schema.json",
            "phase_model_policy.schema.json",
            "review_artifact.schema.json",
            "automation_run_log.schema.json",
        ):
            with self.subTest(filename=filename):
                path = schema_dir / filename
                self.assertTrue(path.exists(), path)
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_valid_versioned_artifacts_pass_schema_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True)

            validate = self.run_validate(fixture)

            self.assertEqual(validate["errors"], [])
            self.assertNotIn("legacy_delivery_state_schema_version", self.warning_codes(validate))
            self.assertEqual(validate["schema_validation"]["delivery_state"]["schema_version"], 1)

    def test_legacy_state_without_schema_version_passes_with_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True, state_schema_version=None)

            validate = self.run_validate(fixture)

            self.assertEqual(validate["errors"], [])
            self.assertIn("legacy_delivery_state_schema_version", self.warning_codes(validate))
            self.assertEqual(validate["schema_validation"]["delivery_state"]["mode"], "compatibility")

    def test_invalid_state_schema_version_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True, state_schema_version=2)

            validate = self.run_validate(fixture)

            self.assertIn("invalid_delivery_state_schema_version", self.error_codes(validate))

    def test_state_schema_type_violation_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True)
            state_path = fixture.state_dir / "delivery_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["review_iterations"] = "one"
            state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

            validate = self.run_validate(fixture)

            self.assertIn("delivery_state_schema_error", self.error_codes(validate))

    def test_run_log_entries_are_schema_validated_line_by_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True, run_log_text='{"timestamp": "2026-05-21T00:00:00Z"}\n')

            validate = self.run_validate(fixture)

            self.assertIn("automation_run_log_schema_error", self.error_codes(validate))

    def test_review_artifact_schema_checks_required_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True)
            review_path = fixture.state_dir / "reviews" / f"{fixture.slug}-phase-1-review-iteration-1.md"
            review_path.write_text(
                "\n".join(
                    [
                        "# Broken Review",
                        "",
                        "## Findings",
                        "",
                        "- Missing metadata.",
                        "",
                        "## Verdict",
                        "",
                        "delivered",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            validate = self.run_validate(fixture)

            self.assertIn("review_artifact_schema_error", self.error_codes(validate))


if __name__ == "__main__":
    unittest.main()
