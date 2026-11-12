"""Offline scenario acceptance tests; run with stdlib unittest (existing PyYAML dependency)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCENES = {
    "reminders": ("morning", "noon", "evening", "custom-reminders"),
    "checks": ("docker-check", "cron-check", "workspace-check", "custom-checks"),
    "projects": ("feature", "maintain", "custom-projects"),
    "learns": ("custom-learns",),
    "scripts": ("script-only",),
    "monitors": ("change-monitor",),
}
NATIVE_FIELDS = set("schedule name deliver failure_deliver repeat catch_up skills script no_agent "
                    "monitor_script monitor_url workdir model provider pinned reasoning_effort "
                    "interpreter timezone grace_minutes continuity paused paused_reason context_from "
                    "enabled_toolsets attach_to_session".split())
BASE_VARIABLES = set("JOB_NAME SCHEDULE DELIVER LOCALE SCENE_SPECIFIC_INSTRUCTIONS "
                     "LOOP_MODE_ENABLED LOOP_TASK_TYPE LOOP_PROJECT_DIR LOOP_STATE_FILE "
                     "LOOP_GOAL LOOP_MILESTONES LOOP_AUTO_PAUSE LOOP_JOB_ID HERMES_HOME".split())
PLACEHOLDER = re.compile(r"\{\{\s*([A-Z][A-Z0-9_]*)\s*\}\}")


def scene_path(locale, category, name):
    return ROOT / "Hermes" / locale / "cron-template" / category / name / (name + ".yaml")


class SceneTests(unittest.TestCase):
    def load_scene(self, locale, category, name):
        path = scene_path(locale, category, name)
        self.assertTrue(path.is_file(), f"Missing bilingual scenario: {path.relative_to(ROOT)}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)
        return path, data

    def all_scenes(self):
        for locale in ("zh_CN", "en_US"):
            for category, names in SCENES.items():
                for name in names:
                    yield locale, category, name

    def test_complete_bilingual_inventory(self):
        for locale in ("zh_CN", "en_US"):
            expected = {f"{category}/{name}/{name}.yaml"
                        for category, names in SCENES.items() for name in names}
            base = ROOT / "Hermes" / locale / "cron-template"
            actual = {str(p.relative_to(base)) for category in SCENES
                      for p in (base / category).rglob("*.yaml")}
            self.assertEqual(expected, actual, f"Incomplete {locale} scene inventory")

    def test_native_schema_explicit_local_delivery_and_uppercase_variables(self):
        for locale, category, name in self.all_scenes():
            with self.subTest(locale=locale, scene=name):
                _, data = self.load_scene(locale, category, name)
                self.assertEqual(set(data), {"templateRef", "variables", "job"})
                self.assertEqual(data["templateRef"], "../../template-cron.yaml")
                variables, job = data["variables"], data["job"]
                self.assertIsInstance(variables, dict)
                self.assertTrue(all(re.fullmatch(r"[A-Z][A-Z0-9_]*", key) for key in variables))
                self.assertEqual(variables["LOCALE"], locale)
                self.assertEqual(variables["DELIVER"], "local")
                self.assertIsInstance(variables["SCENE_SPECIFIC_INSTRUCTIONS"], str)
                self.assertTrue(variables["SCENE_SPECIFIC_INSTRUCTIONS"].strip())
                self.assertIsInstance(job, dict)
                self.assertLessEqual(set(job), NATIVE_FIELDS)
                self.assertEqual(job["deliver"], "local")
                self.assertIs(job["catch_up"], False)
                self.assertEqual(job["schedule"], "{{SCHEDULE}}")
                self.assertEqual(job["name"], "{{JOB_NAME}}")
                self.assertNotIn(None, job.values())
                for key in ("skills", "context_from", "enabled_toolsets"):
                    if key in job:
                        self.assertIsInstance(job[key], list)
                for key in ("catch_up", "no_agent", "continuity", "paused", "pinned"):
                    if key in job:
                        self.assertIsInstance(job[key], bool)
                text = json.dumps(data, ensure_ascii=False)
                self.assertLessEqual(set(PLACEHOLDER.findall(text)), set(variables) | BASE_VARIABLES)
                self.assertNotRegex(text, r"\{\{[^{}]*[a-z][^{}]*\}\}")

    def test_i18n_variable_placeholder_and_job_key_parity(self):
        for category, names in SCENES.items():
            for name in names:
                with self.subTest(scene=name):
                    _, zh = self.load_scene("zh_CN", category, name)
                    _, en = self.load_scene("en_US", category, name)
                    self.assertEqual(set(zh["variables"]), set(en["variables"]))
                    self.assertEqual(set(zh["job"]), set(en["job"]))
                    self.assertEqual(set(PLACEHOLDER.findall(json.dumps(zh))),
                                     set(PLACEHOLDER.findall(json.dumps(en))))
                    self.assertNotRegex(json.dumps(en, ensure_ascii=False), r"[\u4e00-\u9fff]")

    def test_no_legacy_commands_or_unapproved_docker_recovery(self):
        for locale, category, name in self.all_scenes():
            with self.subTest(locale=locale, scene=name):
                path, data = self.load_scene(locale, category, name)
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"(?i)openclaw|NO_REPLY|git\s+add\s+(?:-A|\.)")
                if name == "docker-check":
                    self.assertNotRegex(text, r"docker\s+(?:compose\s+.*\s+up|start|restart|rm|system\s+prune)\b")
                    self.assertRegex(text, r"read-only|只读")
                    self.assertRegex(text, r"explicit.*approval|明确.*授权")
                    self.assertIn("[SILENT]", text)
                    self.assertIn("[CRON_FAILURE]", text)
                if category == "projects":
                    self.assertRegex(text, r"explicit.*approval|明确.*授权")
                    self.assertRegex(text, r"user changes|用户.*改动")

    def test_projects_use_typed_loop_and_are_paused_until_configured(self):
        for locale in ("zh_CN", "en_US"):
            state_files = []
            for name in SCENES["projects"]:
                with self.subTest(locale=locale, scene=name):
                    _, data = self.load_scene(locale, "projects", name)
                    variables, job = data["variables"], data["job"]
                    self.assertIs(variables["LOOP_MODE_ENABLED"], True)
                    self.assertIs(variables["LOOP_AUTO_PAUSE"], False)
                    self.assertEqual(variables["LOOP_PROJECT_DIR"], "/path/to/your/project")
                    self.assertTrue(variables["LOOP_TASK_TYPE"])
                    self.assertTrue(variables["LOOP_GOAL"])
                    self.assertIsInstance(variables["LOOP_MILESTONES"], list)
                    self.assertGreaterEqual(len(variables["LOOP_MILESTONES"]), 3)
                    self.assertTrue(all(isinstance(item, str) and item for item in variables["LOOP_MILESTONES"]))
                    self.assertEqual(variables["LOOP_STATE_FILE"], "{{LOOP_PROJECT_DIR}}/.state/" + name + ".json")
                    state_files.append(variables["LOOP_STATE_FILE"])
                    self.assertEqual(job["workdir"], "{{LOOP_PROJECT_DIR}}")
                    self.assertIs(job["continuity"], True)
                    self.assertIs(job["paused"], True)
                    self.assertTrue(job["paused_reason"])
            self.assertEqual(len(state_files), len(set(state_files)))

    def test_reminder_timing_personalization_and_reports(self):
        schedules = {"morning": "0 8 * * *", "noon": "0 12 * * *",
                     "evening": "0 22 * * *", "custom-reminders": "0 9 * * *"}
        for locale in ("zh_CN", "en_US"):
            for name, schedule in schedules.items():
                _, data = self.load_scene(locale, "reminders", name)
                self.assertEqual(data["variables"]["SCHEDULE"], schedule)
                self.assertIn("{{TONE}}", data["variables"]["SCENE_SPECIFIC_INSTRUCTIONS"])
                self.assertIn("{{REMARK}}", data["variables"]["SCENE_SPECIFIC_INSTRUCTIONS"])
                self.assertIn("date", data["variables"]["SCENE_SPECIFIC_INSTRUCTIONS"])
                self.assertIs(data["job"].get("no_agent", False), False)
            for category in ("checks", "projects", "learns"):
                for name in SCENES[category]:
                    path, _ = self.load_scene(locale, category, name)
                    text = path.read_text(encoding="utf-8")
                    self.assertIn("{{HERMES_HOME}}/docs/reports/", text)
                    self.assertIn("<YYYY-MM-DD>.md", text)
            path, _ = self.load_scene(locale, "checks", "cron-check")
            text = path.read_text(encoding="utf-8")
            for command in ("hermes cron list", "hermes cron status", "hermes cron runs", "hermes cron doctor"):
                self.assertIn(command, text)
            self.assertNotIn("--json", text)
            self.assertNotIn("hermes cron run ", text)

    def test_script_only_runs_without_model_network_or_business_mutation(self):
        for locale in ("zh_CN", "en_US"):
            with self.subTest(locale=locale):
                path, data = self.load_scene(locale, "scripts", "script-only")
                self.assertEqual(data["job"]["script"], "aac/script-only.py")
                self.assertIs(data["job"]["no_agent"], True)
                self.assertNotIn("model", data["job"])
                self.assertIn("$HERMES_HOME/scripts/aac/", path.read_text(encoding="utf-8"))
                script = path.with_suffix(".py")
                self.assertTrue(script.is_file())
                before = {p.name: p.read_bytes() for p in script.parent.iterdir() if p.is_file()}
                first = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=10)
                second = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=10)
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(first.stdout, second.stdout)
                self.assertEqual(json.loads(first.stdout)["status"], "ok")
                self.assertEqual(before, {p.name: p.read_bytes() for p in script.parent.iterdir() if p.is_file()})
                with tempfile.TemporaryDirectory(prefix="aac-script-", dir=Path.home() / ".hermes/cache/scratch") as temp:
                    target = Path(temp) / "invalid.py"
                    target.write_text("def invalid(\n", encoding="utf-8")
                    failed = subprocess.run([sys.executable, str(script), "--target", str(target)],
                                            capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, "")
                    missing = subprocess.run([sys.executable, str(script), "--target", str(target) + ".missing"],
                                             capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(missing.returncode, 0)

    def test_monitor_native_path_stable_output_and_change_detection(self):
        for locale in ("zh_CN", "en_US"):
            with self.subTest(locale=locale):
                path, data = self.load_scene(locale, "monitors", "change-monitor")
                self.assertEqual(data["job"]["monitor_script"], "aac/change-monitor.py")
                self.assertIs(data["job"].get("no_agent", False), False)
                self.assertNotIn("monitor_url", data["job"])
                self.assertIn("--monitor-url", path.read_text(encoding="utf-8"))
                self.assertIn("$HERMES_HOME/scripts/aac/", path.read_text(encoding="utf-8"))
                source = path.parent / "monitor-source.txt"
                script = path.with_suffix(".py")
                self.assertTrue(source.is_file())
                self.assertTrue(script.is_file())
                with tempfile.TemporaryDirectory(prefix="aac-monitor-", dir=Path.home() / ".hermes/cache/scratch") as temp:
                    target = Path(temp)
                    shutil.copy2(script, target / script.name)
                    shutil.copy2(source, target / source.name)
                    def run():
                        return subprocess.run([sys.executable, str(target / script.name)],
                                              capture_output=True, text=True, timeout=10)
                    first, second = run(), run()
                    self.assertEqual(first.returncode, 0, first.stderr)
                    self.assertEqual(second.returncode, 0, second.stderr)
                    self.assertEqual(first.stdout, second.stdout)
                    self.assertEqual(json.loads(first.stdout)["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
                    self.assertNotRegex(first.stdout.lower(), r"timestamp|generated_at|checked_at")
                    (target / source.name).write_text("changed\n", encoding="utf-8")
                    changed = run()
                    self.assertEqual(changed.returncode, 0, changed.stderr)
                    self.assertNotEqual(first.stdout, changed.stdout)
                    (target / source.name).unlink()
                    failed = run()
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, "")


if __name__ == "__main__":
    unittest.main()
