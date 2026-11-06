"""Regression coverage for the repository's OpenClaw skill identity.

Run with: python3 -m unittest discover -s tests/openclaw -v
Only repository source is scanned; ignored generated artifacts are not inputs.
"""

from pathlib import Path
import re
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
OLD_NAME = "aac-cron-manage"
NEW_NAME = "aac-openclaw-cron-manage"
SKILL = ROOT / "OpenClaw" / "skills" / NEW_NAME


class OpenClawSkillIdentityTests(unittest.TestCase):
    def test_skill_directory_and_bilingual_frontmatter_match(self):
        self.assertTrue(SKILL.is_dir(), f"Missing skill directory: {SKILL}")
        self.assertFalse((SKILL.parent / OLD_NAME).exists())
        for filename in ("SKILL.md", "SKILL.zh_CN.md"):
            with self.subTest(filename=filename):
                content = (SKILL / filename).read_text(encoding="utf-8")
                frontmatter = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
                self.assertIsNotNone(frontmatter, "Missing YAML frontmatter")
                self.assertRegex(
                    frontmatter.group(1), rf"(?m)^name: {re.escape(NEW_NAME)}$"
                )

    def test_active_sources_do_not_reference_old_skill_identity(self):
        # Include untracked source so a directory move is testable before staging.
        # Outside a git checkout (exported snapshots) fall back to a filesystem scan.
        candidates = self._git_listed_sources()
        violations = []
        for relative in candidates:
            path = ROOT / relative
            # Historical changelogs and build/documentation artifacts are not active.
            if path.name == "CHANGELOG.md" or set(Path(relative).parts) & {
                "docs", "build", "dist", "__pycache__",
            }:
                continue
            if not path.is_file():
                continue  # Deleted paths remain in the index until staging.
            if OLD_NAME in relative:
                violations.append(f"Old skill path: {relative}")
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if OLD_NAME in line:
                    violations.append(f"{relative}:{number}: {line}")
        self.assertEqual([], violations, "Old active references:\n" + "\n".join(violations))

    @staticmethod
    def _git_listed_sources() -> list[str]:
        try:
            result = subprocess.run(
                [
                    "git", "ls-files", "--cached", "--others", "--exclude-standard",
                    "-z", "--", "OpenClaw", "CLAUDE.md",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError):
            found = [ROOT / "CLAUDE.md"]
            for path in (ROOT / "OpenClaw").rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    found.append(path)
            return sorted(str(path.relative_to(ROOT)) for path in found)
        return sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})


if __name__ == "__main__":
    unittest.main()