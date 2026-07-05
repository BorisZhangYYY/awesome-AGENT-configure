---
name: aac-skill-manage
description: "在 OpenClaw workspace 中安装、删除、列出或创建 AAC skill 时使用。"
---

# AAC Skill 管理器

管理 awesome-AGENT-configure（AAC）项目中的 skill，包括创建新 skill 和向 OpenClaw workspace 安装/卸载 skill。

## 何时使用

- 用户说"安装 skill"、"删除 skill"、"列出 skill"
- 用户说"创建 skill"、"新建 skill"
- 用户想把自己写的 skill 同步到 OpenClaw workspace

## 核心规则

- 所有 AAC skill 名称以 `aac-` 开头。
- 创建 skill 时，源文件先生成在 AAC 项目 `OpenClaw/skills/` 下。
- 安装/卸载通过 `OpenClaw/scripts/aac-manage.sh` 脚本执行。
- 不要直接手动复制目录，统一走脚本，便于后续扩展。

## 命令对应

| 用户意图 | 执行命令 |
|----------|----------|
| 创建 skill | `python3 OpenClaw/skills/aac-skill-manage/scripts/init_skill.py aac-<name> --path OpenClaw/skills --resources scripts` |
| 安装 skill | `OpenClaw/scripts/aac-manage.sh install-skill <name>` |
| 删除 skill | `OpenClaw/scripts/aac-manage.sh remove-skill <name>` |
| 列出可安装 skill | `OpenClaw/scripts/aac-manage.sh list-skills` |
| 列出已安装 skill | `OpenClaw/scripts/aac-manage.sh list-installed-skills` |
| 安装所有 skill | `OpenClaw/scripts/aac-manage.sh install-all-skills` |
| 删除所有 skill | `OpenClaw/scripts/aac-manage.sh remove-all-skills` |

## 创建 skill 流程

1. 询问用户 skill 用途和触发条件。
2. 运行 `init_skill.py` 生成 `aac-<name>/SKILL.md` 和 `scripts/`。
3. 引导用户补全 `SKILL.md` 中的 TODO。
4. 用 `quick_validate.py` 校验 frontmatter 和 AAC_ORIGIN 标记。
5. 用户确认后，调用 `install-skill` 安装到 workspace。

## 安装/删除流程

1. 确认目标 skill 名称。
2. 调用对应 `aac-manage.sh` 命令。
3. 向用户汇报结果。

<!-- AAC_ORIGIN: skill=aac-skill-manage | generated=2026-07-05T00:00:00Z | category=management -->
