import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL_ROOT = REPO_ROOT / "skill" / "roadmap-delivery-skill"
SKILL_ROOT = Path(
    os.environ.get(
        "ROADMAP_DELIVERY_SKILL_ROOT",
        os.environ.get("AUTONOMOUS_ROADMAP_SKILL_ROOT", DEFAULT_SKILL_ROOT),
    )
).expanduser()
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
        blocked_remediation_guard=True,
        state_layout="roadmaps",
        write_automation_config=True,
        write_model_policy=False,
        policy_text=None,
        policy_model="gpt-5.5",
        policy_reasoning="xhigh",
        automation_model="gpt-5.5",
        automation_reasoning="xhigh",
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
            write_model_policy=write_model_policy,
            policy_text=policy_text,
            policy_model=policy_model,
            policy_reasoning=policy_reasoning,
        )
        if write_automation_config:
            self._write_automation_config(
                automation_status=automation_status,
                prompt_path=prompt_path,
                hard_stop_guard=hard_stop_guard,
                blocked_remediation_guard=blocked_remediation_guard,
                automation_model=automation_model,
                automation_reasoning=automation_reasoning,
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
        write_model_policy,
        policy_text,
        policy_model,
        policy_reasoning,
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
            "last_blocker_repair": None,
            "required_model": policy_model if write_model_policy else None,
            "required_reasoning_effort": policy_reasoning if write_model_policy else None,
            "configured_automation_model": policy_model if write_model_policy else None,
            "configured_automation_reasoning_effort": policy_reasoning if write_model_policy else None,
            "run_count": 1 if write_model_policy else 0,
            "stalled_run_count": 0,
            "max_stalled_runs": 3,
            "last_progress_signature": "fixture" if write_model_policy else None,
            "last_progress_at": "2026-05-21T00:00:00Z" if write_model_policy else None,
            "last_operator_alert": None,
            "updated_at": "2026-05-21T00:00:00Z",
        }
        (state_dir / "delivery_state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
        (state_dir / "delivery_log.md").write_text("# Fixture Delivery Log\n", encoding="utf-8")
        if write_model_policy:
            if policy_text is None:
                policy = {
                    "schema_version": 1,
                    "max_stalled_runs": 3,
                    "notification": {"mode": "alert_file", "fallback": "alert_file"},
                    "defaults": {"model": policy_model, "reasoning_effort": policy_reasoning},
                    "phases": {
                        "1": {"model": policy_model, "reasoning_effort": policy_reasoning},
                        "finalization": {"model": policy_model, "reasoning_effort": policy_reasoning},
                    },
                }
                policy_text = json.dumps(policy, indent=2)
            (state_dir / "phase_model_policy.json").write_text(policy_text, encoding="utf-8")
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

    def _write_automation_config(
        self,
        *,
        automation_status,
        prompt_path,
        hard_stop_guard,
        blocked_remediation_guard,
        automation_model,
        automation_reasoning,
    ):
        automation_dir = self.home / ".codex" / "automations" / self.automation_id
        automation_dir.mkdir(parents=True)
        guard = ""
        if hard_stop_guard:
            guard = " If state is completed_pending_pause or all_phases_complete, do not start a new phase."
        blocked_guard = ""
        if blocked_remediation_guard:
            blocked_guard = " If status is blocked, enter Blocked Remediation Mode, repair local blockers before advance, and only then resume."
        prompt = f"Run the next safe step for `{prompt_path}`.{guard}{blocked_guard}"
        (automation_dir / "automation.toml").write_text(
            "\n".join(
                [
                    'id = "' + self.automation_id + '"',
                    f'prompt = {json.dumps(prompt)}',
                    f'status = "{automation_status}"',
                    f'model = "{automation_model}"',
                    f'reasoning_effort = "{automation_reasoning}"',
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

    def run_validate(self, fixture, *extra_args, allowed_returncodes=(0, 1)):
        return self.run_json(VALIDATE_SCRIPT, fixture, *extra_args, allowed_returncodes=allowed_returncodes)

    def run_validate_proc(self, fixture, *extra_args):
        return subprocess.run(
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
            self.assertTrue(validate["blocked_remediation_guard"])

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

    def test_missing_automation_config_is_warning_for_both_helpers(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_automation_config=False)

            inspect = self.run_inspect(fixture)
            validate = self.run_validate(fixture)

            self.assertIn("missing_automation_config", self.warning_codes(inspect))
            self.assertIn("missing_automation_config", self.warning_codes(validate))
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

    def test_branch_mismatch_warnings_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, current_phase="Phase 2 - Fixture")

            validate = self.run_validate(fixture)

            self.assertIn("state_branch_name_mismatch", self.warning_codes(validate))
            self.assertIn("current_branch_name_mismatch", self.warning_codes(validate))
            self.assertEqual(validate["errors"], [])

    def test_missing_state_file_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp)
            (fixture.state_dir / "delivery_state.json").unlink()

            validate = self.run_validate(fixture)

            self.assertIn("missing_state_file", self.error_codes(validate))

    def test_invalid_state_json_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp)
            (fixture.state_dir / "delivery_state.json").write_text("{not valid json\n", encoding="utf-8")

            validate = self.run_validate(fixture)

            self.assertIn("invalid_state_json", self.error_codes(validate))

    def test_strict_mode_allows_named_warning_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_automation_config=False)

            strict = self.run_validate_proc(fixture, "--strict")
            allowed = self.run_validate_proc(fixture, "--strict", "--allow-warning", "missing_automation_config")

            self.assertEqual(strict.returncode, 1, strict.stdout)
            self.assertEqual(allowed.returncode, 0, allowed.stderr or allowed.stdout)

    def test_model_policy_match_reports_model_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(tmp, write_model_policy=True)

            inspect = self.run_inspect(fixture)
            validate = self.run_validate(fixture)

            self.assertEqual(validate["errors"], [])
            self.assertEqual(validate["warnings"], [])
            self.assertEqual(validate["model_policy"]["required_model"], "gpt-5.5")
            self.assertEqual(validate["model_policy"]["configured_model"], "gpt-5.5")
            self.assertFalse(validate["model_policy"]["model_mismatch"])
            self.assertEqual(inspect["required_model"], "gpt-5.5")
            self.assertEqual(inspect["configured_automation_model"], "gpt-5.5")
            self.assertFalse(inspect["model_mismatch"])
            self.assertEqual(inspect["stalled_run_count"], 0)

    def test_model_policy_mismatch_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(
                tmp,
                write_model_policy=True,
                policy_model="gpt-5.5",
                automation_model="gpt-5.4",
            )

            validate = self.run_validate(fixture)

            self.assertIn("automation_model_mismatch", self.error_codes(validate))
            self.assertTrue(validate["model_policy"]["model_mismatch"])

    def test_invalid_model_policy_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(
                tmp,
                write_model_policy=True,
                policy_text='{"schema_version": 1, "max_stalled_runs": 0, "notification": {"mode": "mystery"}, "defaults": {"model": "gpt-5.5", "reasoning_effort": "giant"}, "phases": {}}',
            )

            validate = self.run_validate(fixture)

            codes = self.error_codes(validate)
            self.assertIn("invalid_max_stalled_runs", codes)
            self.assertIn("invalid_notification_mode", codes)
            self.assertIn("invalid_default_reasoning_effort", codes)

    def test_blocked_active_without_remediation_guard_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = DeliveryFixture(
                tmp,
                state_status="blocked",
                review_verdict="blocked",
                blocked_remediation_guard=False,
            )

            validate = self.run_validate(fixture)

            self.assertIn("blocked_state_active_without_remediation_guard", self.error_codes(validate))
            self.assertIn("automation_prompt_missing_blocked_remediation_guard", self.warning_codes(validate))


if __name__ == "__main__":
    unittest.main()
