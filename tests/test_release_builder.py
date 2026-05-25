import hashlib
import json
import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
