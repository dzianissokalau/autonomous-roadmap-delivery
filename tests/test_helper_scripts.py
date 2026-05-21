import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_ROOT = REPO_ROOT / "skill" / "autonomous-roadmap-delivery"
SKILL_ROOT = Path(os.environ.get("AUTONOMOUS_ROADMAP_SKILL_ROOT", DEFAULT_SKILL_ROOT)).expanduser()
INSPECT_SCRIPT = SKILL_ROOT / "scripts" / "inspect_delivery_state.py"
VALIDATE_SCRIPT = SKILL_ROOT / "scripts" / "validate_delivery_artifacts.py"


class DeliveryFixture:
    def __init__(
        self,
        tmpdir,
        *,
        slug="eval-fixture",
        automation_status="ACTIVE",
        current_phase="Phase 1 - Fixture",
        state_status="not_started",
        roadmap_status="In Progress",
        review_verdict="delivered",
        omit_review_dir=False,
        dirty_worktree=False,
        prompt_path="roadmaps/eval_fixture_roadmap.md",
        hard_stop_guard=True,
        state_layout="roadmaps",
    ):
        self.tmpdir = Path(tmpdir)
        self.repo_root = self.tmpdir / "repo"
        self.home = self.tmpdir / "home"
        self.slug = slug
        self.slug_dir = slug.replace("-", "_")
        self.automation_id = f"{slug}-delivery"
        self.repo_root.mkdir(parents=True)
        self.home.mkdir(parents=True)

        self._write_repo_files(
            current_phase=current_phase,
            state_status=state_status,
            roadmap_status=roadmap_status,
            review_verdict=review_verdict,
            omit_review_dir=omit_review_dir,
            state_layout=state_layout,
        )
        self._write_automation_config(
            automation_status=automation_status,
            prompt_path=prompt_path,
            hard_stop_guard=hard_stop_guard,
        )
        self._init_git()
        if dirty_worktree:
            (self.repo_root / "operator-notes.txt").write_text("unrelated local note\n", encoding="utf-8")

    def _write_repo_files(
        self,
        *,
        current_phase,
        state_status,
        roadmap_status,
        review_verdict,
        omit_review_dir,
        state_layout,
    ):
        roadmap_path = self.repo_root / "roadmaps" / "eval_fixture_roadmap.md"
        if state_layout == "root":
            state_dir = self.repo_root / "automation" / self.slug_dir
            review_prefix = f"automation/{self.slug_dir}/reviews"
        elif state_layout == "roadmaps":
            state_dir = self.repo_root / "roadmaps" / "automation" / self.slug_dir
            review_prefix = f"roadmaps/automation/{self.slug_dir}/reviews"
        else:
            raise ValueError(f"Unsupported state_layout: {state_layout}")
        self.state_dir = state_dir
        review_dir = state_dir / "reviews"
        roadmap_path.parent.mkdir(parents=True)
        state_dir.mkdir(parents=True)
        if not omit_review_dir:
            review_dir.mkdir(parents=True)

        roadmap_path.write_text(
            "\n".join(
                [
                    "# Eval Fixture Roadmap",
                    "",
                    f"Status: {roadmap_status}",
                    f"Current phase: {current_phase}",
                    "Last updated: 2026-05-21",
                    "Next action: Continue the fixture phase.",
                    "Blocked by: None",
                    "",
                    "## Phase 1 - Fixture",
                    "",
                    "Fixture body.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        state = {
            "roadmap": "roadmaps/eval_fixture_roadmap.md",
            "roadmap_slug": self.slug,
            "current_phase": current_phase,
            "branch": f"codex/{self.slug}-phase-1",
            "status": state_status,
            "review_iterations": 1,
            "max_review_iterations": 3,
            "last_review": {
                "file": f"{review_prefix}/{self.slug}-phase-1-review-iteration-1.md",
                "verdict": review_verdict,
            },
            "last_delivered_phase": None,
            "blocked_reason": None,
            "updated_at": "2026-05-21T00:00:00Z",
        }
        (state_dir / "delivery_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        (state_dir / "delivery_log.md").write_text("# Fixture Delivery Log\n", encoding="utf-8")
        if not omit_review_dir:
            (review_dir / f"{self.slug}-phase-1-review-iteration-1.md").write_text(
                "\n".join(
                    [
                        "# Phase 1 Review - Iteration 1",
                        "",
                        f"Verdict: {review_verdict}",
                        "",
                        "## Findings",
                        "",
                        "- Fixture review.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

    def _write_automation_config(self, *, automation_status, prompt_path, hard_stop_guard):
        automation_dir = self.home / ".codex" / "automations" / self.automation_id
        automation_dir.mkdir(parents=True)
        guard = ""
        if hard_stop_guard:
            guard = " If state is completed_pending_pause or all_phases_complete, do not start a new phase."
        prompt = f"Run the next safe step for `{prompt_path}`.{guard}"
        (automation_dir / "automation.toml").write_text(
            "\n".join(
                [
                    'id = "' + self.automation_id + '"',
                    f'prompt = {json.dumps(prompt)}',
                    f'status = "{automation_status}"',
                    'cwds = ["' + str(self.repo_root) + '"]',
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _init_git(self):
        subprocess.run(["git", "init", "-b", f"codex/{self.slug}-phase-1"], cwd=self.repo_root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "add", "."], cwd=self.repo_root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Fixture",
                "-c",
                "user.email=automation.invalid",
                "commit",
                "-m",
                "fixture",
            ],
            cwd=self.repo_root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def env(self):
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env["PYTHONPYCACHEPREFIX"] = str(self.tmpdir / "pycache")
        return env


class HelperScriptTests(unittest.TestCase):
    maxDiff = None

    def run_json(self, script, fixture, *extra_args, allowed_returncodes=(0,)):
        proc = subprocess.run(
            [
                "python3",
                str(script),
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

    def run_validate(self, fixture):
        return self.run_json(VALIDATE_SCRIPT, fixture, allowed_returncodes=(0, 1))

    def run_inspect(self, fixture):
        return self.run_json(INSPECT_SCRIPT, fixture)

    def warning_codes(self, report):
        return {item["code"] for item in report.get("warnings", [])}

    def error_codes(self, report):
        return {item["code"] for item in report.get("errors", [])}

    def test_clean_in_progress_fixture_passes_both_helpers(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp)

            inspect = self.run_inspect(fixture)
            validate = self.run_validate(fixture)

            self.assertEqual(inspect["current_phase"], "Phase 1 - Fixture")
            self.assertFalse(inspect["worktree_dirty"])
            self.assertEqual(inspect["warnings"], [])
            self.assertEqual(validate["errors"], [])
            self.assertEqual(validate["warnings"], [])

    def test_root_automation_layout_is_supported_by_both_helpers(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, state_layout="root")

            inspect = self.run_inspect(fixture)
            validate = self.run_validate(fixture)

            self.assertEqual(inspect["state_file"], str((fixture.state_dir / "delivery_state.json").resolve()))
            self.assertEqual(inspect["warnings"], [])
            self.assertEqual(validate["errors"], [])
            self.assertEqual(validate["warnings"], [])

    def test_stale_automation_prompt_path_is_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, prompt_path="roadmaps/missing_eval_fixture_roadmap.md")

            inspect = self.run_inspect(fixture)
            validate = self.run_validate(fixture)

            self.assertIn("stale_automation_roadmap_path", self.warning_codes(inspect))
            self.assertIn("stale_automation_roadmap_path", self.warning_codes(validate))
            self.assertEqual(validate["errors"], [])

    def test_completed_active_without_hard_stop_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(
                tmp,
                current_phase="Complete",
                state_status="completed",
                roadmap_status="Completed",
                hard_stop_guard=False,
            )

            validate = self.run_validate(fixture)

            self.assertIn("completed_state_active_automation", self.error_codes(validate))

    def test_missing_review_directory_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, omit_review_dir=True)

            validate = self.run_validate(fixture)

            self.assertIn("missing_review_dir", self.error_codes(validate))

    def test_invalid_review_verdict_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, review_verdict="approved")

            validate = self.run_validate(fixture)

            self.assertIn("invalid_review_verdict", self.error_codes(validate))

    def test_dirty_worktree_is_warning_not_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, dirty_worktree=True)

            inspect = self.run_inspect(fixture)
            validate = self.run_validate(fixture)

            self.assertTrue(inspect["worktree_dirty"])
            self.assertIn("worktree_dirty", self.warning_codes(inspect))
            self.assertIn("worktree_dirty", self.warning_codes(validate))
            self.assertEqual(validate["errors"], [])


if __name__ == "__main__":
    unittest.main()
