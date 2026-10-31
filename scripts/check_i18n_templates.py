#!/usr/bin/env python3
"""中英文模板一致性校验。

检查项：
  1. zh_CN / en_US 文件集合一致（忽略构建产物 trigger.js）
  2. Cron 父模板 YAML 结构一致
  3. Cron 场景变量键一致（英文允许 LOCALE / LOOP_TASK_TYPE 两个本地化变量）
  4. 对应 YAML 的 {{占位符}} 集合一致
  5. 场景 templateRef 指向的父模板真实存在

用法：
    python3 scripts/check_i18n_templates.py            # 全部检查
    python3 scripts/check_i18n_templates.py --verbose  # 打印通过项

退出码：0 = 全部通过；1 = 有失败项。
"""

from __future__ import annotations

import argparse
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IGNORED_NAMES = {"trigger.js", ".DS_Store"}
# 英文模板在语言层面新增的变量，不要求中文模板同步。
EN_ONLY_VARS = {"LOCALE", "LOOP_TASK_TYPE"}
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}")


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def iter_files(root: str) -> list[str]:
    """ Returns files under root, relative to root, excluding build artifacts. """
    result: list[str] = []
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(files):
            if name in IGNORED_NAMES:
                continue
            result.append(os.path.relpath(os.path.join(base, name), root))
    return result


def load_yaml(path: str):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def shape(value):
    """Returns a structural signature that ignores scalar text."""
    if isinstance(value, dict):
        return {key: shape(item) for key, item in sorted(value.items())}
    if isinstance(value, list):
        return [shape(value[0])] if value else []
    return type(value).__name__


def yaml_variables(path: str) -> set[str]:
    data = load_yaml(path)
    return set((data.get("variables") or {}).keys())


class Result:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def fail(self, message: str) -> None:
        self.failures.append(message)


def check_file_sets(result: Result, verbose: bool) -> None:
    pairs = [
        ("AI-ProjConf", "zh_CN", "en_US"),
        ("Hermes", "zh_CN", "en_US"),
        ("OpenClaw", "zh_CN", "en_US"),
        ("OpenClaw/skills/aac-cron-manage/references", "zh_CN", "en_US"),
    ]
    for base, zh, en in pairs:
        zh_root = os.path.join(ROOT, base, zh)
        en_root = os.path.join(ROOT, base, en)
        if not os.path.isdir(zh_root) or not os.path.isdir(en_root):
            result.fail(f"缺少语言目录：{rel(zh_root)} 或 {rel(en_root)}")
            continue
        zh_files = set(iter_files(zh_root))
        en_files = set(iter_files(en_root))
        for missing in sorted(zh_files - en_files):
            result.fail(f"{base}: en_US 缺少 {missing}")
        for extra in sorted(en_files - zh_files):
            result.fail(f"{base}: zh_CN 缺少 {extra}")
        if verbose and zh_files == en_files:
            print(f"  OK   {base}: {len(zh_files)} 个文件镜像一致")


def check_cron_templates(result: Result, verbose: bool) -> None:
    zh_root = os.path.join(ROOT, "OpenClaw/zh_CN/cron-template")
    en_root = os.path.join(ROOT, "OpenClaw/en_US/cron-template")
    zh_scenes = {
        p for p in iter_files(zh_root)
        if p.endswith((".yaml", ".yml")) and os.path.basename(p) != "template-cron.yaml"
    }
    en_scenes = {
        p for p in iter_files(en_root)
        if p.endswith((".yaml", ".yml")) and os.path.basename(p) != "template-cron.yaml"
    }

    for missing in sorted(zh_scenes - en_scenes):
        result.fail(f"cron 场景 en_US 缺少 {missing}")
    for extra in sorted(en_scenes - zh_scenes):
        result.fail(f"cron 场景 zh_CN 缺少 {extra}")

    zh_parent = os.path.join(zh_root, "template-cron.yaml")
    en_parent = os.path.join(en_root, "template-cron.yaml")
    if not (os.path.isfile(zh_parent) and os.path.isfile(en_parent)):
        result.fail("缺少 cron 父模板 template-cron.yaml")
    else:
        if shape(load_yaml(zh_parent)) != shape(load_yaml(en_parent)):
            result.fail("cron 父模板 YAML 结构不一致")
        elif verbose:
            print("  OK   cron 父模板 YAML 结构一致")

    for scene in sorted(zh_scenes & en_scenes):
        zh_path = os.path.join(zh_root, scene)
        en_path = os.path.join(en_root, scene)
        zh_vars = yaml_variables(zh_path)
        en_vars = yaml_variables(en_path)
        extra = en_vars - zh_vars - EN_ONLY_VARS
        missing = zh_vars - en_vars
        if extra:
            result.fail(f"{scene}: en_US 多出变量 {sorted(extra)}")
        if missing:
            result.fail(f"{scene}: en_US 缺少变量 {sorted(missing)}")

        zh_text = open(zh_path, encoding="utf-8").read()
        en_text = open(en_path, encoding="utf-8").read()
        zh_tokens = set(PLACEHOLDER_RE.findall(zh_text))
        en_tokens = set(PLACEHOLDER_RE.findall(en_text))
        if zh_tokens != en_tokens:
            result.fail(
                f"{scene}: 占位符不一致 "
                f"(zh-only={sorted(zh_tokens - en_tokens)}, en-only={sorted(en_tokens - zh_tokens)})"
            )
        elif verbose:
            print(f"  OK   {scene}: 变量与占位符一致")

    for lang, root, scenes in (("zh_CN", zh_root, zh_scenes), ("en_US", en_root, en_scenes)):
        for scene in sorted(scenes):
            path = os.path.join(root, scene)
            ref = (load_yaml(path).get("templateRef") or "").strip()
            if not ref:
                result.fail(f"{lang}/{scene}: 缺少 templateRef")
                continue
            target = ref if os.path.isabs(ref) else os.path.normpath(os.path.join(os.path.dirname(path), ref))
            if not os.path.isfile(target):
                result.fail(f"{lang}/{scene}: templateRef 指向不存在的文件 {ref}")


def main() -> int:
    parser = argparse.ArgumentParser(description="中英文模板一致性校验")
    parser.add_argument("--verbose", action="store_true", help="打印通过项")
    args = parser.parse_args()

    result = Result()
    check_file_sets(result, args.verbose)
    check_cron_templates(result, args.verbose)

    print("=" * 60)
    if result.failures:
        print(f"❌ 模板一致性检查未通过：{len(result.failures)} 项失败")
        for failure in result.failures:
            print(f"  ✗ {failure}")
        return 1
    print("✅ 模板一致性检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
