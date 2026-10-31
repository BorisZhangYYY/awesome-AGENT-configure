#!/usr/bin/env python3
"""中英文文档一致性校验。

检查项：
  1. README / SKILL 中英文配对文件存在
  2. references/zh_CN 与 references/en_US 文件集合一致
  3. 配对文档的标题数量、代码块数量一致
  4. 配对文档的相对链接都能解析
  5. 英文文档不残留中文（语言切换标签与行内代码除外）

用法：
    python3 scripts/check_i18n_docs.py            # 全部检查
    python3 scripts/check_i18n_docs.py --verbose  # 打印通过项

退出码：0 = 全部通过；1 = 有失败项。
"""

from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CJK_RE = re.compile(r"[一-鿿]")
HEADING_RE = re.compile(r"^#{1,6} ", re.MULTILINE)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
FENCE_RE = re.compile(r"^```", re.MULTILINE)
# 英文文档中允许出现的中文：语言切换标签。
ALLOWED_CJK = {"简体中文"}


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def strip_code(text: str) -> str:
    """Removes fenced code blocks and inline code spans before the CJK check."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return INLINE_CODE_RE.sub("", text)


class Result:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)


def check_relative_links(result: Result, path: str) -> None:
    base = os.path.dirname(path)
    for match in LINK_RE.finditer(read(path)):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        relative = target.split("#", maxsplit=1)[0]
        if not relative:
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, relative))):
            result.fail(f"{rel(path)}: 链接指向不存在的文件 {target}")


def check_pair(result: Result, zh_path: str, en_path: str, verbose: bool) -> None:
    if not os.path.isfile(zh_path):
        result.fail(f"缺少中文文档 {rel(zh_path)}")
        return
    if not os.path.isfile(en_path):
        result.fail(f"缺少英文文档 {rel(en_path)}")
        return

    zh_text = read(zh_path)
    en_text = read(en_path)

    zh_headings = len(HEADING_RE.findall(zh_text))
    en_headings = len(HEADING_RE.findall(en_text))
    if zh_headings != en_headings:
        result.fail(f"{rel(en_path)}: 标题数量 {en_headings}，中文版为 {zh_headings}")

    zh_fences = len(FENCE_RE.findall(zh_text))
    en_fences = len(FENCE_RE.findall(en_text))
    if zh_fences != en_fences:
        result.fail(f"{rel(en_path)}: 代码块标记数 {en_fences}，中文版为 {zh_fences}")

    check_relative_links(result, zh_path)
    check_relative_links(result, en_path)

    leaked: list[str] = []
    for line_no, line in enumerate(en_text.splitlines(), start=1):
        cleaned = strip_code(line)
        plain = cleaned
        for allowed in ALLOWED_CJK:
            plain = plain.replace(allowed, "")
        if CJK_RE.search(plain):
            leaked.append(f"第 {line_no} 行：{line.strip()[:80]}")
    if leaked:
        result.fail(f"{rel(en_path)}: 英文文档残留中文 {len(leaked)} 处（首：{leaked[0]}）")

    if verbose and not leaked:
        print(f"  OK   {rel(zh_path)} ↔ {rel(en_path)}")


def check_reference_dirs(result: Result, verbose: bool) -> None:
    zh_root = os.path.join(ROOT, "OpenClaw/skills/aac-cron-manage/references/zh_CN")
    en_root = os.path.join(ROOT, "OpenClaw/skills/aac-cron-manage/references/en_US")
    if not os.path.isdir(zh_root) or not os.path.isdir(en_root):
        result.fail("缺少 references/zh_CN 或 references/en_US")
        return

    zh_files = {name for name in os.listdir(zh_root) if name.endswith(".md")}
    en_files = {name for name in os.listdir(en_root) if name.endswith(".md")}
    for missing in sorted(zh_files - en_files):
        result.fail(f"references: en_US 缺少 {missing}")
    for extra in sorted(en_files - zh_files):
        result.fail(f"references: zh_CN 缺少 {extra}")
    for name in sorted(zh_files & en_files):
        check_pair(
            result,
            os.path.join(zh_root, name),
            os.path.join(en_root, name),
            verbose,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="中英文文档一致性校验")
    parser.add_argument("--verbose", action="store_true", help="打印通过项")
    args = parser.parse_args()

    result = Result()
    pairs = [
        ("README.md", "README.en.md"),
        ("AI-ProjConf/README.md", "AI-ProjConf/README.en.md"),
        ("Hermes/README.md", "Hermes/README.en.md"),
        ("OpenClaw/README.md", "OpenClaw/README.en.md"),
        (
            "OpenClaw/skills/aac-cron-manage/SKILL.zh_CN.md",
            "OpenClaw/skills/aac-cron-manage/SKILL.md",
        ),
    ]
    for zh, en in pairs:
        check_pair(result, os.path.join(ROOT, zh), os.path.join(ROOT, en), args.verbose)

    check_reference_dirs(result, args.verbose)

    print("=" * 60)
    if result.failures:
        print(f"❌ 文档一致性检查未通过：{len(result.failures)} 项失败")
        for failure in result.failures:
            print(f"  ✗ {failure}")
        return 1
    print("✅ 文档一致性检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
