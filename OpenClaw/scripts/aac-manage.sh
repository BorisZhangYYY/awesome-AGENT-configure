#!/usr/bin/env bash
# AAC 管理脚本
# 一键安装/删除 AAC skill 和 cron，支持单个与批量操作。

set -euo pipefail

AacManageVersion="0.1.0"

# ===== 默认路径 =====
# AAC_REPO：AAC 项目根目录；未设置时自动定位。
# OPENCLAW_WORKSPACE：OpenClaw workspace 根目录。
# AAC_WORKSPACE：AAC 运行时配置目录（场景 YAML、状态文件等）。
AAC_REPO="${AAC_REPO:-}"
OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
AAC_WORKSPACE="${AAC_WORKSPACE:-$OPENCLAW_WORKSPACE/awesome-AGENT-configure}"

SKILLS_SRC="OpenClaw/skills"
SKILLS_DST="$OPENCLAW_WORKSPACE/skills"
CRON_SRC="OpenClaw/template"
CRON_DST="$AAC_WORKSPACE/cron"
BUILD_CRON="$SKILLS_SRC/aac-cron-manage/scripts/build-cron.py"


usage() {
    cat <<EOF
AAC 管理脚本 v$AacManageVersion

用法: aac-manage.sh <命令> [参数]

Skill 管理：
  list-skills                         列出 AAC 仓库中可安装的 skill
  list-installed-skills               列出已安装到 OpenClaw workspace 的 skill
  install-skill  <name> [name...]     安装指定 skill
  remove-skill   <name> [name...]     删除指定 skill
  install-all-skills                  安装所有 AAC skill
  remove-all-skills                   删除所有已安装的 AAC skill

Cron 管理：
  list-crons                          列出 AAC 仓库中可安装的 cron 场景
  list-installed-crons                列出当前 OpenClaw cron 任务
  install-cron   <scene-yaml>         安装指定 cron 场景
  remove-cron    <job-name>          删除指定 cron 任务（按名称匹配）
  install-all-crons                   安装所有 AAC cron 场景
  remove-all-crons                    删除所有 AAC cron 任务（按名称前缀匹配）

全局选项（需放在命令前）：
  --repo <path>         显式指定 AAC 项目根目录
  --workspace <path>    显式指定 OpenClaw workspace 目录

示例：
  aac-manage.sh install-skill aac-skill-manage aac-cron-manage
  aac-manage.sh install-cron OpenClaw/template/reminders/morning.yaml
  aac-manage.sh remove-cron "【AAC-提醒】早安"
EOF
}


# ===== 路径定位 =====

locate_repo() {
    local marker="OpenClaw/skills/aac-cron-manage/scripts/build-cron.py"

    if [[ -n "$AAC_REPO" ]]; then
        if [[ -f "$AAC_REPO/$marker" ]]; then
            echo "$AAC_REPO"
            return
        fi
        echo "错误：AAC_REPO 指向的目录缺少 $marker" >&2
        exit 1
    fi

    # 从当前目录向上搜索
    local dir
    dir="$(pwd)"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/$marker" ]]; then
            echo "$dir"
            return
        fi
        dir="$(dirname "$dir")"
    done

    # 在 $HOME 下有限深度搜索
    python3 - <<'PY'
import os, sys

def locate():
    home = os.path.expanduser("~")
    marker = "OpenClaw/skills/aac-cron-manage/scripts/build-cron.py"
    for root, dirs, _ in os.walk(home):
        p = os.path.join(root, "awesome-AGENT-configure")
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, marker)):
            return p
        depth = root.count(os.sep) - home.count(os.sep)
        if depth >= 4:
            del dirs[:]
    return ""

path = locate()
if not path:
    print("错误：未找到 AAC 项目路径，请设置 AAC_REPO 环境变量或使用 --repo", file=sys.stderr)
    sys.exit(1)
print(path)
PY
}


# ===== 通用工具 =====

ensure_dir() {
    mkdir -p "$1"
}

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "错误：缺少必要命令 '$1'" >&2
        exit 1
    fi
}


# ===== Skill 管理 =====

list_skills() {
    local repo
    repo="$(locate_repo)"
    find "$repo/$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
}

list_installed_skills() {
    if [[ ! -d "$SKILLS_DST" ]]; then
        echo "（尚未安装任何 skill）"
        return
    fi
    find "$SKILLS_DST" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
}

install_skill() {
    local repo
    repo="$(locate_repo)"
    ensure_dir "$SKILLS_DST"

    for name in "$@"; do
        local src="$repo/$SKILLS_SRC/$name"
        local dst="$SKILLS_DST/$name"
        if [[ ! -d "$src" ]]; then
            echo "错误：skill 不存在：$name" >&2
            exit 1
        fi
        if [[ -d "$dst" ]]; then
            echo "已存在，覆盖安装：$name"
            rm -rf "$dst"
        else
            echo "安装 skill：$name"
        fi
        cp -r "$src" "$dst"
    done
}

remove_skill() {
    for name in "$@"; do
        local dst="$SKILLS_DST/$name"
        if [[ ! -d "$dst" ]]; then
            echo "未安装，跳过：$name"
            continue
        fi
        echo "删除 skill：$name"
        rm -rf "$dst"
    done
}

install_all_skills() {
    local repo
    repo="$(locate_repo)"
    local names
    names="$(find "$repo/$SKILLS_SRC" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)"
    if [[ -z "$names" ]]; then
        echo "没有可安装的 skill"
        return
    fi
    # shellcheck disable=SC2086
    install_skill $names
}

remove_all_skills() {
    if [[ ! -d "$SKILLS_DST" ]]; then
        echo "没有已安装的 skill"
        return
    fi
    local names
    names="$(find "$SKILLS_DST" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)"
    if [[ -z "$names" ]]; then
        echo "没有已安装的 skill"
        return
    fi
    # shellcheck disable=SC2086
    remove_skill $names
}


# ===== Cron 管理 =====

list_crons() {
    local repo
    repo="$(locate_repo)"
    find "$repo/$CRON_SRC" -name "*.yaml" -type f ! -name "template-cron.zh.yaml" | sort
}

list_installed_crons() {
    if ! command -v openclaw >/dev/null 2>&1; then
        echo "错误：未找到 openclaw 命令" >&2
        exit 1
    fi
    openclaw cron list
}

install_cron() {
    local repo
    repo="$(locate_repo)"
    ensure_dir "$CRON_DST"

    for src in "$@"; do
        if [[ ! -f "$src" ]]; then
            # 尝试基于 repo 的相对路径
            src="$repo/$src"
        fi
        if [[ ! -f "$src" ]]; then
            echo "错误：场景 YAML 不存在：$src" >&2
            exit 1
        fi

        local name
        name="$(basename "$src")"
        local dst="$CRON_DST/$name"

        echo "安装 cron 场景：$name"
        cp "$src" "$dst"

        # 修正 templateRef 为绝对路径
        python3 - <<PY
import re
from pathlib import Path

src_path = Path("$src").resolve()
dst_path = Path("$dst").resolve()
repo_path = Path("$repo").resolve()
template_path = (repo_path / "OpenClaw/template/template-cron.zh.yaml").resolve()

text = dst_path.read_text(encoding="utf-8")
# 匹配 templateRef: "..." 或 templateRef: '...'
text = re.sub(
    r"^(templateRef:\s*)['\"]?([^'\"\s]+)['\"]?",
    lambda m: f'{m.group(1)}"{template_path}"',
    text,
    flags=re.MULTILINE,
)
dst_path.write_text(text, encoding="utf-8")
PY

        # 渲染并执行 openclaw cron create
        local cmd
        cmd="$(python3 "$repo/$BUILD_CRON" "$dst")"
        echo "执行："
        echo "$cmd"
        eval "$cmd"
    done
}

remove_cron() {
    require_cmd openclaw
    for pattern in "$@"; do
        echo "查找 cron 任务：$pattern"
        local job_id
        job_id="$(python3 - <<PY
import json, subprocess, sys
pattern = """$pattern"""
try:
    result = subprocess.run(
        ["openclaw", "cron", "list", "--format", "json"],
        capture_output=True, text=True, check=True
    )
    jobs = json.loads(result.stdout)
    for job in jobs:
        if job.get("name") == pattern or job.get("id") == pattern:
            print(job.get("id"))
            sys.exit(0)
    sys.exit(1)
except Exception as e:
    print(f"查找失败: {e}", file=sys.stderr)
    sys.exit(1)
PY
)"
        if [[ -z "$job_id" ]]; then
            echo "未找到：$pattern"
            continue
        fi
        echo "删除 cron 任务：$pattern (ID: $job_id)"
        openclaw cron rm "$job_id"
    done
}

install_all_crons() {
    local repo
    repo="$(locate_repo)"
    local scenes
    scenes="$(find "$repo/$CRON_SRC" -name "*.yaml" -type f ! -name "template-cron.zh.yaml" | sort)"
    if [[ -z "$scenes" ]]; then
        echo "没有可安装的 cron 场景"
        return
    fi
    # shellcheck disable=SC2086
    install_cron $scenes
}

remove_all_crons() {
    require_cmd openclaw
    echo "删除所有 AAC cron 任务..."
    python3 - <<PY
import json, subprocess, sys

try:
    result = subprocess.run(
        ["openclaw", "cron", "list", "--format", "json"],
        capture_output=True, text=True, check=True
    )
    jobs = json.loads(result.stdout)
    removed = 0
    for job in jobs:
        name = job.get("name", "")
        if name.startswith("【AAC-"):
            job_id = job.get("id")
            print(f"删除：{name} (ID: {job_id})")
            subprocess.run(["openclaw", "cron", "rm", job_id], check=True)
            removed += 1
    if removed == 0:
        print("没有 AAC cron 任务需要删除")
    else:
        print(f"共删除 {removed} 个 AAC cron 任务")
except Exception as e:
    print(f"错误：{e}", file=sys.stderr)
    sys.exit(1)
PY
}


# ===== 参数解析 =====

parse_global_options() {
    # $1 为输出数组的 nameref 名称
    local -n _remaining="$1"
    shift

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --repo)
                AAC_REPO="$2"
                shift 2
                ;;
            --workspace)
                OPENCLAW_WORKSPACE="$2"
                AAC_WORKSPACE="$OPENCLAW_WORKSPACE/awesome-AGENT-configure"
                SKILLS_DST="$OPENCLAW_WORKSPACE/skills"
                CRON_DST="$AAC_WORKSPACE/cron"
                shift 2
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
    _remaining=("$@")
}


# ===== 主入口 =====

main() {
    require_cmd python3

    local -a argv=()
    parse_global_options argv "$@"

    if [[ ${#argv[@]} -eq 0 ]]; then
        usage
        exit 1
    fi

    local cmd="${argv[0]}"
    local -a rest=("${argv[@]:1}")

    case "$cmd" in
        list-skills)            list_skills ;;
        list-installed-skills)  list_installed_skills ;;
        install-skill)          install_skill "${rest[@]}" ;;
        remove-skill)           remove_skill "${rest[@]}" ;;
        install-all-skills)     install_all_skills ;;
        remove-all-skills)      remove_all_skills ;;
        list-crons)             list_crons ;;
        list-installed-crons)   list_installed_crons ;;
        install-cron)           install_cron "${rest[@]}" ;;
        remove-cron)            remove_cron "${rest[@]}" ;;
        install-all-crons)      install_all_crons ;;
        remove-all-crons)       remove_all_crons ;;
        *)
            echo "错误：未知命令 '$cmd'" >&2
            usage >&2
            exit 1
            ;;
    esac
}

main "$@"
