# awesome-AGENT-configure

> Harness 与 Loop 的 Agent 模板仓库：用约束让 AGENT 可靠，用循环让 AGENT 持续推进。

简体中文 | [English](README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 目录

- [项目简介](#项目简介)
- [模板总览](#模板总览)
- [核心特性](#核心特性)
- [快速开始](#快速开始)
  - [AI 项目模板](#ai-项目模板最常用)
  - [Agent 身份模板](#agent-身份模板)
  - [定时任务模板](#定时任务模板)
  - [上下文注入模板](#上下文注入模板)
- [核心概念](#核心概念)
- [使用指南](#使用指南)
  - [语言版本](#语言版本)
  - [占位符与模板](#占位符与模板)
  - [构建期校验](#构建期校验)
- [路线图](#路线图)
- [贡献指南](#贡献指南)
- [常见问题](#常见问题)
- [许可证](#许可证)
- [相关链接](#相关链接)

---

## 项目简介

使用 OpenClaw、Hermes 等 AI AGENT 工具时，真正决定效果的往往不是模型本身，而是围绕它的约束与推进机制：

- **Harness（约束）**：时间窗口、去重、状态机、效果评估，让 AGENT 的行为可预测、可追踪。
- **Loop（循环）**：目标、里程碑、状态续传、自动停用，让 AGENT 在多次会话中持续推进，直至完成。

本仓库把这些机制沉淀为可直接复制的模板，按使用场景分为四类：AI 项目模板、Agent 身份模板、定时任务模板、上下文注入模板。

## 模板总览

| 类型 | 模板 | 解决什么问题 | 语言 |
|------|------|--------------|------|
| **AI 项目模板** | AI-ProjConf：single-repo / multi-repo | 项目规范、任务跟踪、环境索引、文档分层 | zh_CN / en_US |
| **Agent 身份模板** | Hermes / OpenClaw workspace | 人格、用户画像、长期记忆、群聊边界 | zh_CN / en_US |
| **定时任务模板** | OpenClaw cron：提醒 / 巡检 / 项目 / 学习 | 时间窗口、去重、状态机；Loop 里程碑与自动停用 | zh_CN / en_US |
| **上下文注入模板** | OpenClaw hook-template | 会话启动时注入角色与规则 | zh_CN / en_US |

## 核心特性

- **Harness 约束**：把时间窗口、去重、状态机、效果评估写进模板，减少运行期漂移。
- **Loop 推进**：项目类任务按里程碑推进，状态可续传，达成目标后自动停用。
- **AI 项目规范**：`CLAUDE.md` / `AGENTS.md` / `TODO.md` / `CHANGELOG.md` 一套对齐，覆盖 single-repo 与 multi-repo。
- **占位符化**：所有模板使用 `{{PLACEHOLDER}}`，复制后替换即可。
- **构建期校验**：`build-cron.py` 在生成命令时校验投递陷阱、注入时区偏移。
- **中英双语**：README 与全部模板提供 `zh_CN` / `en_US` 两个版本。

## 快速开始

### AI 项目模板（最常用）

选择与项目形态匹配的目录：

| 形态 | 目录 | 适用场景 |
|------|------|----------|
| 单仓库 | `AI-ProjConf/zh_CN/single-repo/`（或 `en_US/`） | 独立开发者；根目录即 git 仓库 |
| 微服务工作区 | `AI-ProjConf/zh_CN/multi-repo/`（或 `en_US/`） | 根目录不做版本控制；子目录为独立 git 仓库 |

将 `.example` 文件复制到项目根目录并去掉后缀，替换占位符：

```bash
cp AI-ProjConf/zh_CN/single-repo/CLAUDE.md.example /path/to/project/CLAUDE.md
```

模板约定：

- `.docs/`：面向使用者的业务/部署文档
- `.project/`：仓库内部开发细则
- `.project/env/`：按环境拆分的连接信息（`test.md` / `uat.md` / `prd.md`）
- `.project/YYYYMMDD-主题/`：任务正文；根 `TODO.md` 只做索引

### Agent 身份模板

- **Hermes**：将 `Hermes/zh_CN/workspace-template/`（或 `en_US/`）中的 `SOUL.md` 与 `memories/*.md` 备份后合并到 `$HERMES_HOME`。
- **OpenClaw**：将 `OpenClaw/zh_CN/workspace_example/`（或 `en_US/`）中的文件复制到 OpenClaw workspace，按需修改。

### 定时任务模板

以早安提醒为例：

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/zh_CN/cron-template/reminders/morning/morning.yaml
```

常用参数：

```bash
# 预览渲染后的 message 与命令
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/zh_CN/cron-template/reminders/morning/morning.yaml --preview

# 输出 JSON 数组，便于程序化调用
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/zh_CN/cron-template/reminders/morning/morning.yaml --json
```

英文版本将路径中的 `zh_CN` 换成 `en_US`。

### 上下文注入模板

将 `OpenClaw/zh_CN/hook-template/`（或 `en_US/`）复制到 OpenClaw hooks 目录，编辑 `context.md` 填写角色与规则。

## 核心概念

- **Harness**：约束 AGENT 行为的 Prompt 层机制，如时间窗口、去重、状态机、效果评估。
- **Loop**：让 AGENT 跨会话持续推进的机制，如目标、里程碑、状态文件、自动停用。
- **Cron**：基于 crontab 表达式的定时触发。
- **Trigger**：cron 触发后执行的 JavaScript 二次判断（时间窗口、去重）。
- **状态文件**：AGENT 自行维护的持久化记录，用于去重与续传。
- **身份文件**：`SOUL.md` / `USER.md` / `MEMORY.md` 等，定义 AGENT 的人格与记忆。

## 使用指南

### 语言版本

- 中文：`README.md`、`*/zh_CN/`
- English：`README.en.md`、`*/en_US/`
- 两套模板与 README 需同步维护；新增模板时同时补齐两种语言。

### 占位符与模板

- 模板变量仅使用大写字母、数字和下划线（`[A-Z][A-Z0-9_]*`）。
- 场景 YAML 通过 `templateRef` 指向父模板；场景变量覆盖父模板默认值。
- 英文场景通过 `LOCALE: "en_US"` 生成英文人设提示词；中文场景默认为 `zh_CN`。
- Cron 任务名强制使用 `【AAC-分类】任务名`；英文模板的分类为 `Reminder` / `Check` / `Project` / `Learn`，前缀 `【AAC-` 固定。

### 构建期校验

`build-cron.py` 会：

- 检测 `DELIVERY_MODE=announce + CHANNEL=last + isolated` 的投递陷阱；
- 注入时区偏移 `AAC_TZ_OFFSET_MINUTES`，避免 trigger 沙箱内使用 `Intl`；
- 对 Loop 变量做前置校验。

## 路线图

- [ ] 补充 Claude Code 框架的项目模板。
- [ ] 补充更多实用场景模板。

## 贡献指南

欢迎提交 PR 与 Issue。

如果你有更多的实用模板，或者发现了项目中的错误与问题，欢迎在 PR 中补充，审核后会合并入代码库。

## 常见问题

### 可以直接使用这些模板吗？

可以。本项目为模板集合，可直接复制到自身项目或 AGENT workspace 中使用。

### 为什么 trigger.js 禁用 Node.js 模块？

OpenClaw Gateway 的 trigger 执行环境为 QuickJS-WASI 沙箱，禁止 `require`、`import`、Node 模块、网络、定时器等 API。时区换算由 `build-cron.py` 构建期注入 `AAC_TZ_OFFSET_MINUTES` 完成。

### 中文版和英文版内容不一致怎么办？

以中文版为准，并欢迎提交 PR 同步英文版。

## 许可证

本项目采用 [MIT](LICENSE) 许可证。

## 相关链接

- OpenClaw 官方文档：https://docs.openclaw.ai/
- Hermes 官方文档：https://hermes-agent.nousresearch.com/docs/
- Claude Code 官方文档：https://docs.claude.ai/
