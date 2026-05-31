import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build_adapters.py"
DIST_ROOT = REPO_ROOT / "dist" / "claude"
HOOK_CONFIG = DIST_ROOT / "hooks" / "hooks.json"
HOOK_SCRIPT = DIST_ROOT / "hooks" / "roadmap_delivery_safety.py"


class ClaudeHookTests(unittest.TestCase):
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
        return json.loads(proc.stdout)

    def run_hook(self, mode, payload, *, cwd=REPO_ROOT):
        proc = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT), mode],
            cwd=cwd,
            input=json.dumps(payload),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        if not proc.stdout.strip():
            return None
        return json.loads(proc.stdout)

    def test_hook_config_is_generated_with_supported_events(self):
        report = self.run_build_check()
        files = {item["path"]: item for item in report["reports"][0]["files"]}

        self.assertIn("hooks/hooks.json", files)
        self.assertIn("hooks/roadmap_delivery_safety.py", files)
        self.assertEqual(files["hooks/roadmap_delivery_safety.py"]["mode"], "0755")

        config = json.loads(HOOK_CONFIG.read_text(encoding="utf-8"))
        self.assertIn("Roadmap Delivery safety hooks", config["description"])
        self.assertEqual(
            set(config["hooks"]),
            {"PreToolUse", "UserPromptSubmit", "Stop"},
        )
        pre_tool = config["hooks"]["PreToolUse"][0]
        self.assertEqual(pre_tool["matcher"], "Bash")
        handler = pre_tool["hooks"][0]
        self.assertEqual(handler["type"], "command")
        self.assertEqual(handler["command"], "python3")
        self.assertEqual(handler["args"][0], "${CLAUDE_PLUGIN_ROOT}/hooks/roadmap_delivery_safety.py")
        self.assertEqual(handler["args"][1], "guard-bash")

    def test_bash_guard_asks_before_destructive_git(self):
        output = self.run_hook(
            "guard-bash",
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "git reset --hard HEAD~1"},
            },
        )

        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "ask")
        self.assertIn("destructive git reset", decision["permissionDecisionReason"])
        self.assertIn("explicit human approval", decision["permissionDecisionReason"])

    def test_bash_guard_asks_before_broad_staging(self):
        output = self.run_hook(
            "guard-bash",
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "git add . && git commit -m hooks"},
            },
        )

        decision = output["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "ask")
        self.assertIn("broad git staging", decision["permissionDecisionReason"])
        self.assertIn("explicit phase-owned paths", decision["permissionDecisionReason"])

    def test_bash_guard_allows_safe_validation_commands_to_continue(self):
        output = self.run_hook(
            "guard-bash",
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -m unittest discover -s tests -v"},
            },
        )

        self.assertIsNone(output)

    def test_prompt_hook_adds_blocked_remediation_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_dir = root / "automation" / "demo-roadmap"
            state_dir.mkdir(parents=True)
            (state_dir / "delivery_state.json").write_text(
                json.dumps(
                    {
                        "roadmap": "roadmaps/demo.md",
                        "roadmap_slug": "demo-roadmap",
                        "status": "blocked",
                        "blocked_reason": "review verdict missing",
                    }
                ),
                encoding="utf-8",
            )

            output = self.run_hook(
                "remind-prompt",
                {
                    "hook_event_name": "UserPromptSubmit",
                    "cwd": str(root),
                    "prompt": "Run the next safe phase-gated delivery step for roadmaps/demo.md",
                },
            )

        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Blocked Remediation Mode", context)
        self.assertIn("review verdict missing", context)

    def test_prompt_hook_blocks_completed_phase_delivery_prompt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_dir = root / "automation" / "demo-roadmap"
            state_dir.mkdir(parents=True)
            (state_dir / "delivery_state.json").write_text(
                json.dumps(
                    {
                        "roadmap": "roadmaps/demo.md",
                        "roadmap_slug": "demo-roadmap",
                        "status": "completed",
                        "all_phases_complete": True,
                    }
                ),
                encoding="utf-8",
            )

            output = self.run_hook(
                "remind-prompt",
                {
                    "hook_event_name": "UserPromptSubmit",
                    "cwd": str(root),
                    "prompt": "Deliver phase work for demo-roadmap",
                },
            )

        self.assertEqual(output["decision"], "block")
        self.assertIn("hard stop", output["reason"])
        self.assertIn("Do not start phase work", output["reason"])

    def test_prompt_hook_adds_privacy_reminder_for_publication_terms(self):
        output = self.run_hook(
            "remind-prompt",
            {
                "hook_event_name": "UserPromptSubmit",
                "cwd": str(REPO_ROOT),
                "prompt": "Publish the package release",
            },
        )

        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("privacy reminder", context)
        self.assertIn("explicit human approval", context)

    def test_stop_hook_blocks_unverified_delivery_claim(self):
        output = self.run_hook(
            "guard-stop",
            {
                "hook_event_name": "Stop",
                "last_assistant_message": "Phase 5 delivered.",
            },
        )

        self.assertEqual(output["decision"], "block")
        self.assertIn("verification evidence", output["reason"])
        self.assertIn("delivered review verdict", output["reason"])

    def test_stop_hook_allows_reviewed_and_verified_delivery_summary(self):
        output = self.run_hook(
            "guard-stop",
            {
                "hook_event_name": "Stop",
                "last_assistant_message": (
                    "Phase 5 delivered. Verification passed and review verdict: delivered."
                ),
            },
        )

        self.assertIsNone(output)

    def test_stop_hook_does_not_repeat_active_stop_block(self):
        output = self.run_hook(
            "guard-stop",
            {
                "hook_event_name": "Stop",
                "stop_hook_active": True,
                "last_assistant_message": "Phase 5 delivered.",
            },
        )

        self.assertIsNone(output)


if __name__ == "__main__":
    unittest.main()
