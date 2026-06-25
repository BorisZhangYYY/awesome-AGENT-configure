# Changelog

本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式，并采用 [Semantic Versioning](https://semver.org/lang/zh-CN/) 进行版本管理。

## [Unreleased]

### Added

- 新增 `AI-ProjConf/zh_CN/` 通用项目初始化模板目录，提供 `README.md`、`TODO.md`、`AGENT.md`、`CLAUDE.md`、`CHANGELOG.md` 的 example 模板。
- 新增 `OpenClaw/scripts/build-cron.py` 脚本，支持从场景 YAML 渲染生成 `openclaw cron create` 命令。
- 新增 `OpenClaw/conf/flags.yaml`，集中管理 OpenClaw 官方 CLI 参数映射及 boolean/enum 等特殊参数规则。
- 新增 `OpenClaw/conf/defaults.yaml`，管理官方参数与非官方扩展的默认变量值。
- 新增 `docs/OpenClaw/design-rationale.md`，解释开机堆叠问题与时间窗口、去重的必要性。
- 新增 `docs/OpenClaw/skill-creator.md`，记录 OpenClaw Skill 创建方式调研结果。
- 新增 `OpenClaw/skills/SKILL-GUIDE.md` 中“`openclaw cron edit` 支持矩阵”与“项目路径自动定位”章节，为 skill 执行提供统一参考。
- 新增 `OpenClaw/template/check/docker.yaml` Docker 容器/Compose 巡检场景，基于 `template-cron.zh.yaml` 并通过场景级 `template` 字段直接覆盖提示词。
- `OpenClaw/scripts/build-cron.py` 支持场景 YAML 通过顶层 `template` 字段覆盖模板文件的提示词。
- 新增 `OpenClaw/skills/init-cron/SKILL.md`，引导用户从零创建定时任务。
- 新增 `OpenClaw/skills/migrate-cron/SKILL.md`，帮助用户改造已有定时任务。
- `OpenClaw/template/template-cron.zh.yaml` 顶部注释增加 `{{WORKSPACE}}` 内置变量说明。

### Changed

- `OpenClaw/conf/defaults.yaml`：移除 `SESSION_TARGET: isolated` 默认值，改为在 `build-cron.py` 中按 `SESSION_TARGET > PERSISTENT_ID > isolated` 的优先级自动推断，避免 `PERSISTENT_ID` 被默认值覆盖。
- `OpenClaw/skills/init-cron/SKILL.md`、`OpenClaw/skills/migrate-cron/SKILL.md`、`OpenClaw/skills/edit-cron/SKILL.md`：
  - 不再使用 `/path/to/awesome-AGENT-configure` 占位符，统一按 `SKILL-GUIDE.md` 中的方法自动定位项目仓库（`AAC_REPO`）。
  - 明确区分项目仓库（`AAC_REPO`）与运行时配置目录（`AAC_WORKSPACE`，默认 `~/.openclaw/workspace/awesome-AGENT-configure`），二者完全分离。
  - `edit-cron` 更新流程改为优先使用 `openclaw cron edit <id>`（保留 job ID），仅在命令模式等 `edit` 不支持的场景下回退到 delete+create。
- `.gitignore`：增加 `__pycache__/`、`*.pyc`、`*.pyo` 忽略规则。
- `OpenClaw/template/template-cron.zh.yaml`：
  - 删除 `command.enabled`，遵循 OpenClaw 原生语义，`command.script` 非空时自动启用命令模式。
  - 删除 `timeWindow.timezone`，统一使用 `schedule.timezone`。
  - 明确 `message` 为官方 `--message` 参数映射，`template` 为生成 `message` 的提示词模板源。
  - 为未加引号的 YAML 占位符补充引号，修复 PyYAML 解析失败。
  - 顶部注释增加开机堆叠问题说明。
  - template 内将时间窗口和去重提炼为独立的【防护机制】结构性注释。
- `OpenClaw/conf/defaults.yaml`：增加 `THINKING: "off"` 默认值。
- `OpenClaw/template/reminders/*.yaml`：所有提醒场景增加 `THINKING: "off"` 和 `EXACT: "true"`。
- `README.md`：重构为目录导航结构，新增安装与依赖、项目结构、贡献指南等章节，修正章节标题笔误。
- `TODO.md`：精简为“待实现 / 已完成”两栏，按 P0~P3 优先级分组，删除历史已决策条目。
- `README.md`：补充项目结构、使用方法、设计原则和开机堆叠问题说明。
- `TODO.md`：关闭 `#3`/`#4`/`#7`/`#8`/`#10`。 

### Fixed

- 修正 `README.md` 项目结构中对 `AI-ProjConf/` 的描述，移除已删除的 `STATE` 引用。
- 删除 `AI-ProjConf/zh_CN/README.md.example` 中指向未提交 `CONTRIBUTING.md` 的“贡献指南”章节。
- 重命名 `AI-ProjConf/zh_CN/CHANGLOG.md.example` 为 `CHANGELOG.md.example`，修正拼写错误。
- 修复 `OpenClaw/scripts/build-cron.py` 中 `session:<id>` 持久会话逻辑：
  - 支持 `SESSION_TARGET: "session:my-id"` 直接生效。
  - 当仅提供 `PERSISTENT_ID` 时自动生成 `session:<id>`。
- 修复 `OpenClaw/scripts/build-cron.py` 对空列表/字典的处理：
  - `COMMAND_ARGV: []` / `{}` 不再渲染为字符串 `"[]"` / `"{}"`。
  - 非空列表/字典自动序列化为 JSON 字符串后传给 CLI。
- 修复 `build_persona_prompt` 在 `PERSONA_ROLE` 为空时生成病句“你是一个。”的问题，现在返回空字符串。
- 修复 `OpenClaw/conf/flags.yaml` 中 `delivery.mode: none` 不渲染任何 flag 的问题，改为渲染 `--no-deliver`。
- 修复 `OpenClaw/template/template-cron.zh.yaml` 中 `session:<id>` 注释与占位符混淆的问题。
- 修复 `OpenClaw/template/template-cron.zh.yaml` 中部分 `{{XXX}}` 占位符未加引号导致的 YAML 解析错误。

## [0.0.0] - 2026-06-21

### Added

- 项目初始化，提交基础目录结构与文档。
- 新增 `README.md`、`CLAUDE.md`、`AGENT.md`、`TODO.md`、`.gitignore`。
- 新增 `OpenClaw/template/template-cron.zh.yaml` 通用模板。
- 新增 `OpenClaw/template/reminders/` 下早安、午安、晚安、自定义提醒场景模板。
- 新增 `docs/OpenClaw/` 下架构、最佳实践、任务模板总览三篇文档。
- 新增 `.claude/skills/web-research/SKILL.md`。
