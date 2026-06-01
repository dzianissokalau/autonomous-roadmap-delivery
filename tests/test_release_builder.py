import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReleaseBuilderTests(unittest.TestCase):
    maxDiff = None

    def test_build_release_checksum_file_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "dist"
            proc = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_release.py",
                    "--output-dir",
                    str(output_dir),
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
            self.assertEqual(report["adapter_check"]["status"], "passed")
            self.assertEqual(report["codex_artifact_validation"]["status"], "passed")
            self.assertEqual(report["claude_artifact_validation"]["status"], "passed")
            self.assertEqual(report["generic_artifact_validation"]["status"], "passed")

            artifact_kinds = {item["kind"] for item in report["artifacts"]}
            self.assertEqual(
                artifact_kinds,
                {
                    "source_archive",
                    "codex_skill_package",
                    "claude_plugin_package",
                    "schema_bundle",
                    "cli_source_package",
                    "generic_markdown_pack",
                    "release_manifest",
                    "checksums",
                },
            )
            checksum_artifact = next(item for item in report["artifacts"] if item["kind"] == "checksums")
            checksum_path = Path(checksum_artifact["path"])

            self.assertTrue(checksum_path.is_file())
            expected = {
                item["filename"]: item["sha256"]
                for item in report["artifacts"]
                if item["kind"] != "checksums"
            }
            observed = {}
            for line in checksum_path.read_text(encoding="utf-8").splitlines():
                digest, filename = line.split("  ", 1)
                artifact_path = output_dir / filename
                self.assertTrue(artifact_path.is_file(), filename)
                observed[filename] = digest
                actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                self.assertEqual(actual, digest)

            self.assertEqual(observed, expected)

    def test_build_release_contains_multi_host_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "dist"
            proc = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_release.py",
                    "--output-dir",
                    str(output_dir),
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
            artifacts = {item["kind"]: Path(item["path"]) for item in report["artifacts"]}

            with tarfile.open(artifacts["claude_plugin_package"], "r:gz") as archive:
                names = set(archive.getnames())
            self.assertIn(
                "roadmap-delivery-claude-plugin-0.1.0/.claude-plugin/plugin.json",
                names,
            )
            self.assertIn(
                "roadmap-delivery-claude-plugin-0.1.0/skills/roadmap-delivery-skill/SKILL.md",
                names,
            )
            self.assertIn("roadmap-delivery-claude-plugin-0.1.0/agents/reviewer.md", names)
            self.assertIn("roadmap-delivery-claude-plugin-0.1.0/hooks/hooks.json", names)

            with tarfile.open(artifacts["generic_markdown_pack"], "r:gz") as archive:
                names = set(archive.getnames())
            self.assertIn("roadmap-delivery-generic-markdown-pack-0.1.0/README.md", names)
            self.assertIn(
                "roadmap-delivery-generic-markdown-pack-0.1.0/workflow/phase-loop.md",
                names,
            )
            self.assertIn(
                "roadmap-delivery-generic-markdown-pack-0.1.0/schemas/delivery_state.schema.json",
                names,
            )

            manifest = json.loads((output_dir / "roadmap-delivery-0.1.0-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["compatibility"]["supported_host_packages"], ["codex", "claude"])
            self.assertEqual(manifest["compatibility"]["claude_plugin_path"], "dist/claude")


if __name__ == "__main__":
    unittest.main()
