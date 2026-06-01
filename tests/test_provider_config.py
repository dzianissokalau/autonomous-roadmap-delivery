import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from roadmap_delivery.validation import validate_json_schema


PROVIDER_CONFIG = REPO_ROOT / "config" / "providers.example.yaml"
PROVIDER_SCHEMA = REPO_ROOT / "schemas" / "provider_config.schema.json"
PHASE_POLICY = REPO_ROOT / "automation" / "multi-host-adapter-and-claude-plugin" / "phase_model_policy.json"
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_adapters.py"
CODEX_REFERENCE = REPO_ROOT / "skill" / "roadmap-delivery-skill" / "references" / "model-policy-and-stall-control.md"
CLAUDE_REFERENCE = (
    REPO_ROOT
    / "dist"
    / "claude"
    / "skills"
    / "roadmap-delivery-skill"
    / "references"
    / "model-policy-and-stall-control.md"
)
CLAUDE_README = REPO_ROOT / "dist" / "claude" / "README.md"


class ProviderConfigTests(unittest.TestCase):
    maxDiff = None

    def load_example(self):
        return json.loads(PROVIDER_CONFIG.read_text(encoding="utf-8"))

    def load_schema(self):
        return json.loads(PROVIDER_SCHEMA.read_text(encoding="utf-8"))

    def schema_errors(self, config):
        return validate_json_schema(config, self.load_schema())

    def test_example_provider_config_validates_against_schema(self):
        config = self.load_example()

        self.assertEqual(self.schema_errors(config), [])

    def test_required_roles_map_to_phase_model_policy_and_codex_runner_fields(self):
        config = self.load_example()
        phase_policy = json.loads(PHASE_POLICY.read_text(encoding="utf-8"))
        expected_roles = {"executor", "reviewer", "inspector", "finalizer", "repairer"}

        self.assertEqual(set(config["roles"]), expected_roles)
        self.assertEqual(set(config["policies"]["high_reasoning"]["roles"]), {"executor", "reviewer", "finalizer", "repairer"})
        self.assertEqual(config["policies"]["low_cost"]["roles"], ["inspector"])

        for role_name, role in config["roles"].items():
            with self.subTest(role=role_name):
                self.assertEqual(role["phase_model_policy"]["model_field"], "model")
                self.assertEqual(role["phase_model_policy"]["reasoning_effort_field"], "reasoning_effort")
                codex = role["providers"]["codex"]
                self.assertEqual(codex["provider"], "codex")
                self.assertTrue(codex["supports_reasoning_effort"])
                self.assertEqual(codex["config_fields"]["model"], "model")
                self.assertEqual(codex["config_fields"]["reasoning_effort"], "reasoning_effort")

        executor_codex = config["roles"]["executor"]["providers"]["codex"]
        self.assertEqual(executor_codex["model"], phase_policy["defaults"]["model"])
        self.assertEqual(executor_codex["reasoning_effort"], phase_policy["defaults"]["reasoning_effort"])

    def test_claude_mapping_declares_no_reasoning_effort_control(self):
        config = self.load_example()

        for role_name, role in config["roles"].items():
            claude = role["providers"]["claude"]
            with self.subTest(role=role_name):
                self.assertEqual(claude["provider"], "claude")
                self.assertFalse(claude["supports_reasoning_effort"])
                self.assertNotIn("reasoning_effort", claude)
                self.assertEqual(claude["config_fields"], {"model": "model"})

    def test_schema_rejects_missing_provider_model(self):
        config = self.load_example()
        broken = copy.deepcopy(config)
        del broken["roles"]["executor"]["providers"]["codex"]["model"]

        errors = self.schema_errors(broken)

        self.assertTrue(any("missing required property 'model'" in error for error in errors), errors)

    def test_schema_rejects_invalid_reasoning_effort(self):
        config = self.load_example()
        broken = copy.deepcopy(config)
        broken["roles"]["inspector"]["providers"]["codex"]["reasoning_effort"] = "tiny"

        errors = self.schema_errors(broken)

        self.assertTrue(any("value 'tiny' is not one of" in error for error in errors), errors)

    def test_generated_adapters_render_provider_role_guidance(self):
        proc = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT), "--repo-root", str(REPO_ROOT), "--check", "--json"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

        codex_reference = CODEX_REFERENCE.read_text(encoding="utf-8")
        claude_reference = CLAUDE_REFERENCE.read_text(encoding="utf-8")
        claude_readme = CLAUDE_README.read_text(encoding="utf-8")

        for text in (codex_reference, claude_reference):
            normalized = " ".join(text.split())
            with self.subTest(reference=text[:40]):
                self.assertIn("provider-role config", text)
                self.assertIn("config/providers.example.yaml", text)
                self.assertIn("schemas/provider_config.schema.json", text)
                self.assertIn("does not prove the active runner", normalized)

        self.assertIn("provider-neutral model-role guidance", claude_readme)
        self.assertIn("Live Claude Code loading remains an optional maintainer", claude_readme)


if __name__ == "__main__":
    unittest.main()
