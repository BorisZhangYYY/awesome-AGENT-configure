# awesome-AGENT-configure

> 基于 AGENT 常见的 Cron 定时任务机制，结合 Harness 和 Loop 思想，打造一个**既自律，又准确，还可以自我提升的 AI AGENT**。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [适用场景](#适用场景)
- [快速开始](#快速开始)
  - [环境要求](#环境要求)
  - [安装](#安装)
  - [最小可运行示例](#最小可运行示例)
- [项目结构](#项目结构)
- [核心概念](#核心概念)
- [使用指南](#使用指南)
  - [生成 cron 命令](#生成-cron-命令)
  - [JSON 输出](#json-输出)
  - [自定义场景](#自定义场景)
- [配置说明](#配置说明)
- [路线图](#路线图)
- [贡献指南](#贡献指南)
- [常见问题](#常见问题)
- [支持与致谢](#支持与致谢)
- [许可证](#许可证)
- [相关链接](#相关链接)

---

## 项目简介

你在使用 OpenClaw、Hermes 等 AI AGENT 工具的时候，是否面临 workspace 杂乱、skills 冗杂、Heartbeat 与 Cron 效果不佳的情况？

通过本项目提供的模板，结合自身需求修改后将其应用在 AI AGENT 的 cron 机制内，即可通过严格的提示词系统（如状态机、时间窗口、效果评估等方式），让 AI AGENT 的 Cron 效果**可记录、可追踪、可推进**。

## 核心特性

- **Cron 模板化**：将通用约束沉淀在 `template-cron.zh.yaml`，场景文件只需填写变量。
- **Harness 与 Loop 机制**：通过时间窗口、去重、状态机等手段约束 AGENT 行为，提升稳定性。
- **构建期校验**：`build-cron.py` 在生成 CLI 命令时检测投递陷阱、注入时区偏移，减少运行期错误。
- **多框架扩展**：当前支持 OpenClaw，Hermes 与 Claude Code 模板持续补充中。

## 适用场景

- **定时提醒**：早安、午安、晚安、自定义提醒等个人助理场景。
- **环境巡检**：工作区整理、Docker 容器检查、Cron 任务健康检查。
- **项目维护**：功能开发、维护会话等需要 Loop 模式的长期任务。
- **自主学习**：让 AGENT 按固定节奏学习指定主题并记录进展。

## 快速开始

### 环境要求

- Python 3
- PyYAML（`pip install pyyaml`）

### 安装

```bash
pip install pyyaml
```

### 最小可运行示例

以早安提醒为例，生成并执行一条 OpenClaw cron 命令：

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/cron-template/reminders/morning/morning.yaml
```

输出示例：

```bash
openclaw \
  cron \
  create \
  '0 8 * * *' \
  --message \
  '...' \
  --name \
  '【AAC-提醒】 - 早安' \
  --tz \
  Asia/Shanghai \
  --announce \
  --best-effort-deliver \
  --session \
  isolated \
  --timeout-seconds \
  300 \
  --no-light-context \
  --thinking \
  off \
  --exact
```

## 项目结构

```
awesome-AGENT-configure/
├── AI-ProjConf/              # 通用项目初始化模板（README / TODO / AGENTS 等）
├── OpenClaw/
│   ├── conf/                 # OpenClaw 参数与 flag 配置
│   ├── cron-template/        # cron 场景模板，按类别分子目录
│   │   ├── checks/           # 巡检类模板
│   │   │   ├── cron-check/          # Cron 任务健康巡检
│   │   │   ├── custom-checks/       # 自定义巡检场景
│   │   │   ├── docker-check/        # Docker 容器/Compose 巡检
│   │   │   └── workspace-check/     # 工作区整理巡检
│   │   ├── projects/         # 项目类模板（Loop 方法，基于 template-cron.zh.yaml）
│   │   │   ├── custom-projects/     # 自定义项目场景
│   │   │   ├── feature/             # 功能开发场景
│   │   │   └── maintain/            # 维护会话场景
│   │   ├── learns/           # 学习类模板
│   │   │   └── custom-learns/     # AI 自我学习场景
│   │   ├── reminders/        # 提醒类模板
│   │   │   ├── morning/
│   │   │   ├── noon/
│   │   │   ├── evening/
│   │   │   └── custom-reminders/  # 自定义提醒场景
│   │   └── template-cron.zh.yaml  # 通用/Loop 统一父模板
│   ├── hook-template/        # 通用上下文注入模板
│   ├── skills/               # AAC cron 管理 skill（含 build-cron.py + trigger 模板）
│   └── workspace_example/    # OpenClaw workspace 配置示例
├── docs/                     # 项目文档
├── CHANGELOG.md
├── CLAUDE.md
├── README.md
└── TODO.md
```

## 核心概念

- **Cron**：基于 crontab 表达式的定时触发机制，决定任务何时运行。
- **Trigger**：OpenClaw 在 cron 触发后执行的 JavaScript 脚本，用于二次判断（如时间窗口、去重）。
- **Harness**：通过 Prompt 层的状态机、时间窗口、效果评估等手段，约束 AGENT 的执行行为。
- **Loop**：针对项目类任务，让 AGENT 在多次会话中持续推进，直至目标完成。
- **状态文件**：由 AGENT 自行维护的持久化记录，用于去重与进度追踪。

## 使用指南

### 生成 cron 命令

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/cron-template/reminders/morning/morning.yaml
```

### JSON 输出

如果需要程序化调用，可输出 JSON 数组：

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/cron-template/reminders/morning/morning.yaml --json
```

### 自定义场景

复制 `OpenClaw/cron-template/reminders/custom-reminders/custom-reminders.yaml`，修改 `variables` 中的值即可。

## 配置说明

- 场景配置：每个 `.yaml` 文件位于 `OpenClaw/cron-template/<类别>/<场景>/` 目录下。
- 通用约束：公共 Prompt 与变量定义在 `OpenClaw/cron-template/template-cron.zh.yaml`。
- 构建脚本：`OpenClaw/skills/aac-cron-manage/scripts/build-cron.py` 负责 YAML → CLI 翻译。
- 触发脚本：`OpenClaw/skills/aac-cron-manage/scripts/trigger.js` 为通用时间窗口检查脚本。

## 路线图

- [ ] 补充 Hermes 框架的 cron 模板与使用说明。
- [ ] 补充 Claude Code 框架的模板与使用说明。
- [ ] 完善 `docs/` 下的架构设计与最佳实践文档。
- [ ] 增加更多实用场景模板（如健康、阅读、代码审查等）。

## 贡献指南

欢迎提交 PR 与 Issue。

如果你有更多的实用模板，或者发现了项目中的错误与问题，欢迎在 PR 中补充，审核后会合并入代码库。

## 常见问题

### 可以直接使用这些模板吗？

可以。本项目为模板集合，可直接复制到自身项目或 AGENT workspace 中使用。

### 为什么 trigger.js 禁用 Node.js 模块？

OpenClaw Gateway 的 trigger 执行环境为 QuickJS-WASI 沙箱，禁止 `require`、`import`、Node 模块、网络、定时器等 API。时区换算由 `build-cron.py` 构建期注入 `AAC_TZ_OFFSET_MINUTES` 完成。

## 支持与致谢

- 问题反馈：请提交 [Issue](https://github.com/BorisZhangYYY/awesome-AGENT-configure/issues)。
- 致谢：感谢 OpenClaw 等 AGENT 框架提供的 Cron 与 Trigger 能力。

## 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 相关链接

- OpenClaw 官方文档：https://docs.openclaw.ai/
- Hermes 官方文档：https://hermes-agent.nousresearch.com/docs/
- Claude Code 官方文档：https://docs.claude.ai/
