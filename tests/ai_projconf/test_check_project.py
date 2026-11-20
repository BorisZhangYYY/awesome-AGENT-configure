"""Regression tests for the standalone project checker."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER = Path(__file__).resolve().parents[2] / "AI-ProjConf/scripts/check-project.py"


class ProjectCheckerTests(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def check(self, *args):
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root), *args],
            capture_output=True, text=True,
        )

    def init_backlog(self):
        self.write("backlog/config.yml", 'project_name: "Template fixture"\n')

    def test_backlog_without_legacy_index(self):
        self.init_backlog()
        self.write("backlog/tasks/task-1.md", "---\nid: TASK-1\nstatus: To Do\n---\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("INDEX.md", result.stdout)

    def test_backlog_checks_relative_links_with_spaces_and_parentheses(self):
        self.init_backlog()
        self.write("README.md", "[Guide](<backlog/docs/doc-1 - Runtime (local).md#setup>)\n")
        self.write("backlog/docs/doc-1 - Runtime (local).md", "[Evidence](résumé%20%231.txt)\n")
        self.write("backlog/docs/résumé #1.txt", "Evidence\n")
        result = self.check("--verbose")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("doc-1 - Runtime (local).md", result.stdout)
        self.assertIn("résumé #1.txt", result.stdout)

    def test_backlog_reports_broken_link(self):
        self.init_backlog()
        self.write("backlog/tasks/task-1.md", "[Evidence](missing.md)\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("broken link: backlog/tasks/task-1.md -> missing.md", result.stdout)

    def test_backlog_does_not_scan_history_or_nested_repositories(self):
        self.init_backlog()
        self.write(".project/INDEX.md", "[Old](missing.md)\n")
        self.write("backlog/archive/tasks/task-2.md", "[Old](missing.md)\n")
        self.write("service/README.md", "[Child](missing.md)\n")
        self.write("backlog/tasks/task-1.md", "[History](../archive/tasks/task-2.md)\n")
        result = self.check("--verbose")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("../archive/tasks/task-2.md", result.stdout)

    def test_legacy_still_requires_index(self):
        self.write(".docs/overview.md", "# Legacy doc\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing task register: .project/INDEX.md", result.stdout)

    def test_legacy_still_checks_owner_task(self):
        self.write(".project/INDEX.md", "---\nstatus: reference\nupdated_at: 2026-01-01\n---\n| S1 | Task |\n")
        self.write(".project/topic.md", "---\nstatus: reference\nowner_task: S2\nupdated_at: 2026-01-01\n---\n")
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("unregistered owner_task 'S2'", result.stdout)


if __name__ == "__main__":
    unittest.main()
