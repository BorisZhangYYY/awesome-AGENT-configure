#!/usr/bin/env python3
"""Check the project task register and document lifecycle.

Run at the start of each agent session and before commits:

    python3 scripts/check-project.py
    python3 scripts/check-project.py --root /path/to/project --max-age 14 --verbose

Checks:
  1. relative Markdown links resolve
  2. body documents declare front matter: status / owner_task / updated_at
  3. status is one of the allowed lifecycle values
  4. superseded documents declare an existing superseded_by target
  5. active documents were refreshed within --max-age days
  6. owner_task IDs are registered in .project/INDEX.md
  7. configured key facts appear only in their defining file

Exit code: 0 = clean, 1 = findings. Warnings do not fail the run.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import sys

# --- Configuration ---------------------------------------------------------
# Every option a project may want to change is listed here.
REGISTER = ".project/INDEX.md"          # single source of truth for task status
DOC_ROOTS = (".project", ".docs")       # directories whose .md files need front matter
VALID_STATUS = ("active", "reference", "superseded", "evidence", "archived")
DEFAULT_MAX_AGE = 14                    # days before an active doc is called stale
# Stable facts -> the one file allowed to state them. Extend per project, e.g.
# KEY_FACTS = {"64C128G": ".docs/01-environments/test.md"}
KEY_FACTS = {}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".idea", ".vscode", "venv"}
# Indexes and playbooks are not task bodies, so they do not need owner_task.
INDEX_FILES = {REGISTER, ".docs/README.md", ".project/README.md"}
NO_OWNER_TASK_PREFIXES = (".project/rules/",)
# A second status table inside body docs is what lets stale conclusions survive.
SECOND_STATUS_RE = re.compile(
    r"^(#{1,6}\s*(当前状态|current status)|>\s*状态[:：])", re.I | re.M
)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
ID_RE = re.compile(r"^\|\s*([A-Za-z][A-Za-z0-9_.-]*)\s*\|", re.M)

# ---------------------------------------------------------------------------


def rel(root: str, path: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def iter_markdown(root: str):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".git")]
        for name in sorted(files):
            if name.endswith(".md"):
                yield os.path.join(base, name)


def front_matter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fields = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")
    return fields


def registered_ids(text: str) -> set[str]:
    return set(ID_RE.findall(text)) - {"ID"}


# --- Checks ---------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check project task register and document lifecycle"
    )
    parser.add_argument("--root", default=".", help="project root (default: .)")
    parser.add_argument(
        "--max-age", type=int, default=DEFAULT_MAX_AGE,
        help="days an active document may go unrefreshed (default: 14)",
    )
    parser.add_argument("--verbose", action="store_true", help="print passing items")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    failures: list[str] = []
    warnings: list[str] = []
    today = datetime.date.today()

    register_path = os.path.join(root, REGISTER)
    if not os.path.isfile(register_path):
        print(f"FAIL missing task register: {REGISTER}")
        print("     Create it from .project/INDEX.md.example before starting work.")
        return 1
    register_text = open(register_path, encoding="utf-8").read()

    ids = registered_ids(register_text)
    all_md = list(iter_markdown(root))
    body_docs = [p for p in all_md if rel(root, p).startswith(DOC_ROOTS)]

    for path in all_md:
        name = rel(root, path)
        text = open(path, encoding="utf-8", errors="ignore").read()

        for link in LINK_RE.findall(text):
            target = link.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(resolved):
                failures.append(f"broken link: {name} -> {target}")
            elif args.verbose:
                print(f"  OK   link {name} -> {target}")

        if path not in body_docs:
            continue

        fm = front_matter(text)
        if fm is None:
            failures.append(f"missing front matter: {name}")
            continue

        status = fm.get("status", "")
        if status not in VALID_STATUS:
            failures.append(
                f"invalid status {status!r}: {name} (allowed: {', '.join(VALID_STATUS)})"
            )

        updated = fm.get("updated_at", "")
        try:
            age = (today - datetime.date.fromisoformat(updated)).days
        except ValueError:
            failures.append(f"invalid updated_at {updated!r}: {name} (expected YYYY-MM-DD)")
            age = None
        if status == "active" and age is not None and age > args.max_age:
            warnings.append(f"stale active document: {name} ({age} days since {updated})")

        if status == "superseded":
            target = fm.get("superseded_by", "")
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), target)) if target else ""
            if not target or not os.path.exists(resolved):
                failures.append(f"superseded without valid superseded_by: {name}")

        exempt = name in INDEX_FILES or name.startswith(NO_OWNER_TASK_PREFIXES)
        if not exempt:
            owner = fm.get("owner_task", "")
            if not owner:
                failures.append(f"missing owner_task: {name}")
            elif ids and owner not in ids:
                failures.append(f"unregistered owner_task {owner!r}: {name}")
            if SECOND_STATUS_RE.search(text):
                warnings.append(
                    f"second status source in body: {name} (status belongs in {REGISTER})"
                )

        if args.verbose:
            print(f"  OK   front matter {name} (status={status})")

    for fact, defining in KEY_FACTS.items():
        owner_path = os.path.abspath(os.path.join(root, defining))
        for path in all_md:
            if os.path.abspath(path) == owner_path:
                continue
            if fact in open(path, encoding="utf-8", errors="ignore").read():
                warnings.append(
                    f"key fact {fact!r} repeated in {rel(root, path)}; "
                    f"define it only in {defining}"
                )

    for line in warnings:
        print(f"WARN {line}")
    for line in failures:
        print(f"FAIL {line}")
    print("=" * 60)
    print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
