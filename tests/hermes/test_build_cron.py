"""Hermes compiler contracts; no running Hermes, network or model needed."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py"


class BuildCronTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="aac-hermes-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.template = self.root / "template.yaml"
        self.template.write_text(yaml.safe_dump({
            "version": 1,
            "variables": {"JOB_NAME": "AAC test", "SCHEDULE": "30m"},
            "job": {"name": "{{JOB_NAME}}", "schedule": "{{SCHEDULE}}",
                    "deliver": "local", "catch_up": False},
            "template": "Harness: verify evidence.\n{{SCENE_SPECIFIC_INSTRUCTIONS}}",
        }, allow_unicode=True), encoding="utf-8")
        self.scene = self.root / "scene.yaml"

    def run_build(self, job=None, variables=None, *flags):
        self.scene.write_text(yaml.safe_dump({
            "templateRef": "template.yaml", "job": job or {},
            "variables": {"SCENE_SPECIFIC_INSTRUCTIONS": "Do the task", **(variables or {})},
        }, allow_unicode=True), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(BUILDER), str(self.scene), "--home", str(self.home), *flags],
            capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def test_agent_scene_emits_native_argv_with_safe_defaults(self):
        result = self.run_build(None, {"JOB_NAME": "AAC quoted 'name'"}, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(result.stdout)
        self.assertEqual(argv[:6], ["env", f"HERMES_HOME={self.home}", "hermes", "cron", "create", "30m"])
        self.assertEqual(argv[argv.index("--name") + 1], "AAC quoted 'name'")
        self.assertEqual(argv[argv.index("--catch-up") + 1], "off")
        self.assertIn("Harness: verify evidence.", argv[6])
        self.assertIn("Do the task", argv[6])
        self.assertNotIn("--message", argv)

    def test_script_mode_has_no_agent_prompt(self):
        result = self.run_build({"no_agent": True, "script": "aac/check.py"}, None, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(result.stdout)
        self.assertIn("--no-agent", argv)
        self.assertEqual(argv[argv.index("--script") + 1], "aac/check.py")
        self.assertNotIn("Harness: verify evidence.", " ".join(argv))

    def test_edit_keeps_id_and_emits_false_and_clear_operations(self):
        result = self.run_build({"no_agent": False, "continuity": False, "pinned": False,
                                 "skills": [], "script": "", "model": ""}, None,
                                "--edit", "abc123abc123", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(result.stdout)
        self.assertEqual(argv[4:6], ["edit", "abc123abc123"])
        for flag in ("--agent", "--no-continuity", "--unpin", "--clear-skills"):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--script") + 1], "")
        self.assertNotIn("create", argv)

    def test_invalid_native_combinations_fail_without_partial_stdout(self):
        for job, error in [
            ({"no_agent": True}, "script"),
            ({"no_agent": True, "script": "ok.py", "monitor_url": "https://example.com"}, "monitor"),
            ({"monitor_script": "ok.py", "monitor_url": "https://example.com"}, "monitor"),
            ({"script": "../outside.py"}, "scripts"),
            ({"no_agent": "false"}, "boolean"),
            ({"catch_up": "off"}, "boolean"),
            ({"paused_reason": "not paused"}, "paused"),
            ({"tools": ["terminal"]}, "Unknown job"),
            ({"enabled_toolsets": "terminal"}, "list"),
            ({"reasoning_effort": "off"}, "reasoning_effort"),
            ({"grace_minutes": -1}, "grace_minutes"),
            ({"model": "test-model", "pinned": True}, "pinned"),
            ({"provider": "test-provider"}, "model"),
            ({"monitor_url": "file:///etc/hosts"}, "http"),
        ]:
            with self.subTest(job=job):
                result = self.run_build(job, None, "--json")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn(error, result.stderr)

    def test_duplicate_yaml_keys_are_rejected(self):
        self.scene.write_text("templateRef: template.yaml\njob:\n  no_agent: true\n  no_agent: false\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(BUILDER), str(self.scene), "--json"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Duplicate", result.stderr)

    def test_symlink_cannot_escape_target_scripts(self):
        (self.home / "scripts").mkdir()
        (self.home / "scripts/escape").symlink_to(self.root, target_is_directory=True)
        result = self.run_build({"script": "escape/task.py"}, None, "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scripts", result.stderr)


if __name__ == "__main__":
    unittest.main()
