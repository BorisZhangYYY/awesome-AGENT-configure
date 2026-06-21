# Changelog

本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式，并采用 [Semantic Versioning](https://semver.org/lang/zh-CN/) 进行版本管理。

## [Unreleased]

### Added

- 新增 `OpenClaw/scripts/build-cron.py` 脚本，支持从场景 YAML 渲染生成 `openclaw cron create` 命令。
- 新增 `OpenClaw/conf/flags.yaml`，集中管理 OpenClaw 官方 CLI 参数映射及 boolean/enum 等特殊参数规则。
- 新增 `OpenClaw/conf/defaults.yaml`，管理官方参数与非官方扩展的默认变量值。
- 新增 `docs/OpenClaw/design-rationale.md`，解释开机堆叠问题与时间窗口、去重的必要性。
- 新增 `docs/OpenClaw/skill-creator.md`，记录 OpenClaw Skill 创建方式调研结果。
- 新增 `OpenClaw/skills/init-cron/SKILL.md`，引导用户从零创建定时任务。
- 新增 `OpenClaw/skills/migrate-cron/SKILL.md`，帮助用户改造已有定时任务。
- `OpenClaw/template/template-cron.zh.yaml` 顶部注释增加 `{{WORKSPACE}}` 内置变量说明。

### Changed

- `OpenClaw/template/template-cron.zh.yaml`：
  - 删除 `command.enabled`，遵循 OpenClaw 原生语义，`command.script` 非空时自动启用命令模式。
  - 删除 `timeWindow.timezone`，统一使用 `schedule.timezone`。
  - 明确 `message` 为官方 `--message` 参数映射，`template` 为生成 `message` 的提示词模板源。
  - 为未加引号的 YAML 占位符补充引号，修复 PyYAML 解析失败。
  - 顶部注释增加开机堆叠问题说明。
  - template 内将时间窗口和去重提炼为独立的【防护机制】结构性注释。
- `OpenClaw/conf/defaults.yaml`：增加 `THINKING: "off"` 默认值。
- `OpenClaw/template/reminders/*.yaml`：所有提醒场景增加 `THINKING: "off"` 和 `EXACT: "true"`。
- `README.md`：补充项目结构、使用方法、设计原则和开机堆叠问题说明。
- `TODO.md`：关闭 `#3`/`#4`/`#7`/`#8`/`#10`。 

### Fixed

- 修复 `OpenClaw/template/template-cron.zh.yaml` 中部分 `{{XXX}}` 占位符未加引号导致的 YAML 解析错误。

## [0.0.0] - 2026-06-21

### Added

- 项目初始化，提交基础目录结构与文档。
- 新增 `README.md`、`CLAUDE.md`、`AGENT.md`、`TODO.md`、`.gitignore`。
- 新增 `OpenClaw/template/template-cron.zh.yaml` 通用模板。
- 新增 `OpenClaw/template/reminders/` 下早安、午安、晚安、自定义提醒场景模板。
- 新增 `docs/OpenClaw/` 下架构、最佳实践、任务模板总览三篇文档。
- 新增 `.claude/skills/web-research/SKILL.md`。
