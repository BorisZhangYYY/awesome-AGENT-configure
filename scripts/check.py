#!/usr/bin/env python3
"""AAC 仓库发版前自检。

检查项：
  1. YAML 可解析
  2. Python / Shell 语法
  3. cron 模板渲染（build-cron.py）
  4. Markdown 格式（尾随空格 / 未闭合代码块）
  5. CHANGELOG 结构（Unreleased 段 + 版本头格式）

用法：
    python3 scripts/check.py            # 全部检查
    python3 scripts/check.py --verbose  # 打印每项明细

退出码：0 = 全部通过；1 = 有失败项。
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_CRON = "OpenClaw/skills/aac-cron-manage/scripts/build-cron.py"
TEMPLATE_ROOT = "OpenClaw/cron-template"
SKIP_TEMPLATE = "template-cron.zh.yaml"

# 设计上就以占位符形式提供的模板：DEV_PROJECT_DIR 必须由使用者填写。
# 这类模板渲染失败属预期行为，不计为错误。
PLACEHOLDER_OK = (
    "DEV_PROJECT_DIR 仍是默认占位符",
)


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def iter_files(pattern: str) -> list[str]:
    return sorted(
        p for p in glob.glob(os.path.join(ROOT, pattern), recursive=True)
        if ".git/" not in p
    )


class Result:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.skips: list[str] = []
        self.notes: list[str] = []

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def skip(self, msg: str) -> None:
        self.skips.append(msg)


def check_yaml(r: Result, verbose: bool) -> None:
    try:
        import yaml
    except ImportError:
        r.notes.append("YAML 检查跳过：PyYAML 未安装")
        return

    for path in iter_files("**/*.yaml") + iter_files("**/*.yml"):
        try:
            list(yaml.safe_load_all(open(path, encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001
            r.fail(f"YAML 解析失败 {rel(path)}: {exc}")
        else:
            if verbose:
                print(f"  OK   {rel(path)}")


def check_python_and_shell(r: Result, verbose: bool) -> None:
    for path in iter_files("**/*.py"):
        proc = subprocess.run(
            [sys.executable, "-m", "py_compile", path],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            r.fail(f"Python 语法错误 {rel(path)}: {proc.stderr.strip()}")
        else:
            if verbose:
                print(f"  OK   {rel(path)}")

    for path in iter_files("**/*.sh"):
        proc = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
        if proc.returncode != 0:
            r.fail(f"Shell 语法错误 {rel(path)}: {proc.stderr.strip()}")
        else:
            if verbose:
                print(f"  OK   {rel(path)}")


def check_template_render(r: Result, verbose: bool) -> None:
    scenes = [
        p for p in iter_files(f"{TEMPLATE_ROOT}/**/*.yaml")
        if os.path.basename(p) != SKIP_TEMPLATE
    ]

    for path in scenes:
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, BUILD_CRON), path, "--preview"],
            capture_output=True, text=True, cwd=ROOT,
        )
        if proc.returncode == 0:
            if verbose:
                print(f"  OK   {rel(path)}")
            continue

        stderr = (proc.stderr + proc.stdout).strip()
        if any(token in stderr for token in PLACEHOLDER_OK):
            r.skip(f"占位符模板（需使用者填写）{rel(path)}")
        else:
            r.fail(f"模板渲染失败 {rel(path)}: {stderr.splitlines()[-1] if stderr else '未知错误'}")


def check_markdown(r: Result, verbose: bool) -> None:
    for path in iter_files("**/*.md"):
        lines = open(path, encoding="utf-8").read().split("\n")

        # 跳过 YAML 块标量（| 或 >）内部：那里的缩进与尾随空格有意义
        block_indent: int | None = None
        trailing: list[int] = []
        for idx, line in enumerate(lines, 1):
            if block_indent is not None:
                if line.strip() and (len(line) - len(line.lstrip())) <= block_indent:
                    block_indent = None
                else:
                    continue
            if re.search(r":\s*[|>][-+]?\s*$", line):
                block_indent = len(line) - len(line.lstrip())
                continue
            if line != line.rstrip():
                trailing.append(idx)

        fences = sum(1 for ln in lines if ln.strip().startswith("```"))
        problems = []
        if trailing:
            problems.append(f"尾随空格 {len(trailing)} 行 (首: {trailing[0]})")
        if fences % 2:
            problems.append(f"代码块未闭合 ({fences} 个 ```)")

        if problems:
            r.fail(f"MD 格式 {rel(path)}: {'; '.join(problems)}")
        else:
            if verbose:
                print(f"  OK   {rel(path)}")


def check_changelog(r: Result, verbose: bool) -> None:
    path = os.path.join(ROOT, "CHANGELOG.md")
    if not os.path.exists(path):
        r.fail("CHANGELOG.md 不存在")
        return

    text = open(path, encoding="utf-8").read()

    if not re.search(r"^## \[Unreleased\]", text, re.M):
        r.fail("CHANGELOG 缺少 `## [Unreleased]` 段")

    # 版本头：## [x.y.z] - YYYY-MM-DD
    version_headers = re.findall(r"^## \[([^\]]+)\]", text, re.M)
    released = [v for v in version_headers if v.lower() != "unreleased"]
    if not released:
        r.fail("CHANGELOG 没有任何已发布版本段")

    for v in released:
        if not re.fullmatch(r"\d+\.\d+\.\d+", v):
            r.fail(f"CHANGELOG 版本号格式异常：`[{v}]`（应为 x.y.z）")

    # 已发布版本段必须带日期
    for line in text.split("\n"):
        m = re.match(r"^## \[(\d+\.\d+\.\d+)\](.*)$", line)
        if m and not re.match(r"^ - \d{4}-\d{2}-\d{2}\s*$", m.group(2)):
            r.fail(f"CHANGELOG 版本 `{m.group(1)}` 缺少日期（应为 `## [{m.group(1)}] - YYYY-MM-DD`）")

    if verbose and not r.failures:
        print(f"  OK   CHANGELOG.md（已发布 {len(released)} 个版本）")


def main() -> int:
    parser = argparse.ArgumentParser(description="AAC 仓库发版前自检")
    parser.add_argument("--verbose", "-v", action="store_true", help="打印每项明细")
    args = parser.parse_args()

    r = Result()
    sections = [
        ("YAML 解析", check_yaml),
        ("Python / Shell 语法", check_python_and_shell),
        ("cron 模板渲染", check_template_render),
        ("Markdown 格式", check_markdown),
        ("CHANGELOG 结构", check_changelog),
    ]

    for title, func in sections:
        if args.verbose:
            print(f"\n[{title}]")
        func(r, args.verbose)

    print("\n" + "=" * 60)
    if r.skips:
        print(f"豁免 {len(r.skips)} 项（设计如此）：")
        for s in r.skips:
            print(f"  ~ {s}")
    for note in r.notes:
        print(f"  ! {note}")

    if r.failures:
        print(f"\n❌ 检查未通过：{len(r.failures)} 项失败")
        for f in r.failures:
            print(f"  ✗ {f}")
        return 1

    print("\n✅ 全部检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
