import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_adapters.py"


class GenericAdapterPackageTests(unittest.TestCase):
    maxDiff = None

    def run_build(self, *args):
        proc = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT), "--repo-root", str(REPO_ROOT), *args, "--json"],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        report = json.loads(proc.stdout)
        self.assertEqual(report["adapters"], ["generic"])
        generic = report["reports"][0]
        self.assertEqual(generic["adapter"], "generic")
        return report, generic

    def test_render_only_package_includes_policy_schemas_and_workflow(self):
        report, generic = self.run_build("--adapter", "generic", "--check")

        self.assertEqual(report["status"], "ok")
        self.assertEqual(generic["status"], "ok")
        self.assertEqual(generic["check_mode"], "render_only")
        self.assertFalse(generic["output_committed"])
        self.assertEqual(generic["capability_file"], "host-capabilities/generic.yaml")
        self.assertEqual(generic["diffs"], [])
        self.assertEqual(generic["errors"], [])

        paths = {item["path"] for item in generic["files"]}
        self.assertIn("schemas/approval_policy.schema.json", paths)
        self.assertIn("schemas/phase_model_policy.schema.json", paths)
        self.assertIn("schemas/automation_run_log.schema.json", paths)
        self.assertIn("workflow/model-policy-and-stall-control.md", paths)
        self.assertIn("workflow/phase-loop.md", paths)
        self.assertIn("capabilities/generic.yaml", paths)

    def test_written_generic_pack_documents_policy_fallbacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, generic = self.run_build("--adapter", "generic", "--write", "--output-root", tmp)
            output_root = Path(tmp) / "generic"
            self.assertTrue(output_root.is_dir())

            corpus_parts = []
            for item in generic["files"]:
                path = output_root / item["path"]
                try:
                    corpus_parts.append(path.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    continue
            corpus = "\n".join(corpus_parts).lower()

        for term in (
            "approval_policy.json",
            "`allowed`",
            "`forbidden`",
            "adaptive_model_policy",
            "run quality",
            "pause_automation_on_completion",
            "pause_automation_on_stall",
            "completed_pending_pause",
            "runner readback",
            "local alert",
        ):
            with self.subTest(term=term):
                self.assertIn(term.lower(), corpus)

    def test_generic_pack_does_not_claim_concrete_host_runtime_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_build("--adapter", "generic", "--write", "--output-root", tmp)
            output_root = Path(tmp) / "generic"
            corpus = "\n".join(
                path.read_text(encoding="utf-8")
                for path in sorted(output_root.rglob("*"))
                if path.is_file() and path.suffix in {".md", ".yaml", ".json"}
            )

        self.assertIn("not a supported runtime integration", corpus)
        self.assertNotIn("~/.codex", corpus)
        self.assertNotIn("/.codex/", corpus)
        self.assertNotIn("Claude Code loading is required", corpus)


if __name__ == "__main__":
    unittest.main()
