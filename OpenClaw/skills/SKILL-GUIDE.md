# OpenClaw Cron 模板参数指南

> 本文档系统介绍 `awesome-AGENT-configure` 中 OpenClaw Cron 模板支持的所有参数，以及不同任务类型的推荐配置。

---

## 一、核心概念

### 1.1 官方参数 vs 非官方扩展

| 类型 | 来源 | 传递方式 |
|------|------|----------|
| 官方参数 | OpenClaw 原生 CLI 参数 | 渲染为 `openclaw cron create` 的 `--xxx` 参数 |
| 非官方扩展 | 本模板为了 Harness/Loop 增加的抽象 | 渲染进 `--message` 的 Prompt 中，由 Agent 执行 |

### 1.2 模板渲染流程

```
场景 YAML + 通用模板 ──▶ build-cron.py ──▶ openclaw cron create --message "..." --xxx ...
```

### 1.3 命名规范

被 awesome-AGENT-configure（AAC）规范化过的 cron 任务，名称必须遵循：

```
【AAC-分类】任务名
```

例如：
- `【AAC-提醒】早安`
- `【AAC-巡检】磁盘空间`
- `【AAC-汇报】日报`
- `【AAC-开发】补全登录功能`

**为什么要强制命名？**

- 一眼识别哪些任务按 AAC 规范创建
- `edit-cron` skill 可通过 `【AAC-` 前缀快速定位可编辑任务
- `migrate-cron` 迁移时统一重命名为 AAC 格式
- 避免用户手动创建的任务和 AAC 任务混淆

七类分类对应：

| 分类 | 前缀 | 示例 |
|------|------|------|
| 提醒 | `【AAC-提醒】` | `【AAC-提醒】早安` |
| 巡检 | `【AAC-巡检】` | `【AAC-巡检】磁盘空间` |
| 汇报 | `【AAC-汇报】` | `【AAC-汇报】日报` |
| 开发 | `【AAC-开发】` | `【AAC-开发】登录功能` |
| 学习 | `【AAC-学习】` | `【AAC-学习】RAG 调研` |
| 整理 | `【AAC-整理】` | `【AAC-整理】归档日志` |
| 系统 | `【AAC-系统】` | `【AAC-系统】Token 监控` |

---

## 二、官方参数详解

### 2.1 基础信息

| YAML 字段 | CLI 参数 | 说明 | 推荐值 |
|-----------|----------|------|--------|
| `name` | `--name` | 任务名称 | `【分类】任务名` |
| `message` | `--message` | Agent 模式下的提示词 | 由 `template` 渲染生成 |
| `systemEvent` | `--system-event` | main 模式下的系统事件 | 需要静默触发时用 |

### 2.2 调度配置

| YAML 字段 | CLI 参数 | 说明 | 示例 |
|-----------|----------|------|------|
| `schedule.type` | 位置参数类型 | `at` / `every` / `cron` | `cron` |
| `schedule.expr` | 位置参数 | cron 表达式 / 间隔 / 相对时间 | `0 8 * * *` |
| `schedule.timezone` | `--tz` | 时区 | `Asia/Shanghai` |

### 2.3 投递配置

| YAML 字段 | CLI 参数 | 说明 | 推荐值 |
|-----------|----------|------|--------|
| `delivery.mode` | `--announce` / `--webhook` / 无 | 投递模式 | 提醒类 `announce`，巡检类 `none` |
| `delivery.channel` | `--channel` | 目标平台 | `telegram` / `slack` / `discord` |
| `delivery.to` | `--to` | 接收目标 | 群聊/频道 ID |
| `delivery.threadId` | `--thread-id` | Telegram topic ID | 论坛话题 ID |
| `delivery.webhookUrl` | `--webhook` | webhook URL | webhook 模式必填 |
| `delivery.bestEffort` | `--best-effort-deliver` / `--no-best-effort-deliver` | 投递失败是否导致任务失败 | 提醒类 `true` |

**delivery.mode 说明：**

- `announce`：Agent 没发，Runner 兜底发。适合必须送达的提醒。
- `webhook`：POST 到 URL。适合集成外部系统。
- `none`：无 Runner 兜底。适合巡检类（正常时静默）。

### 2.4 会话配置

| YAML 字段 | CLI 参数 | 说明 | 推荐值 |
|-----------|----------|------|--------|
| `session.target` | `--session` | 执行会话 | 绝大多数用 `isolated` |
| `session.persistentId` | `--session` | 持久命名会话 ID | 需要历史积累时用 `session:xxx` |
| `session.timeoutSeconds` | `--timeout-seconds` | 超时时间 | 提醒 120s，开发 4h |

**session.target 选择：**

- `isolated`：独立会话，不污染主会话。**绝大多数任务推荐。**
- `main`：主会话，适合需要立即打扰用户的提醒。
- `current`：当前会话，适合上下文感知的循环任务。
- `session:<id>`：持久命名会话，适合需要历史积累的流程。

### 2.5 Agent 配置

| YAML 字段 | CLI 参数 | 说明 | 推荐值 |
|-----------|----------|------|--------|
| `agent.agentId` | `--agent` | 绑定特定 agent | 默认不填 |
| `agent.model` | `--model` | 模型覆盖 | 按任务复杂度选择 |
| `agent.thinking` | `--thinking` | 思考级别 | 提醒类 `off`，开发类 `medium/high` |
| `agent.tools` | `--tools` | 限制作业可用工具 | 按任务需求限定 |

**thinking 推荐：**

- `off`：问候、提醒、固定格式输出
- `low`：简单巡检、汇报
- `medium`：开发、学习、整理
- `high`：复杂分析、代码审查

**tools 推荐：**

- 提醒类：`exec,read`（时间窗口检查、去重检查）
- 巡检类：`exec,read,write`（执行脚本、读取日志、写入报告）
- 开发类：`exec,read,write,edit,bash`（完整工具集）

### 2.6 命令模式

| YAML 字段 | CLI 参数 | 说明 | 示例 |
|-----------|----------|------|------|
| `command.script` | `--command` | 执行的脚本 | `scripts/check-disk.sh` |
| `command.cwd` | `--command-cwd` | 工作目录 | `/srv/app` |
| `command.argv` | `--command-argv` | 精确参数数组（避免 shell 转义） | `["node","scripts/export.mjs"]` |
| `command.input` | `--command-input` | 标准输入 | JSON 字符串 |
| `command.env` | `--command-env` | 环境变量 | `KEY=VALUE` |
| `command.noOutputTimeoutSeconds` | `--no-output-timeout-seconds` | 无输出超时 | `30` |
| `command.outputMaxBytes` | `--output-max-bytes` | 输出上限 | `65536` |

**命令模式适用场景：**

- 纯脚本巡检
- 数据导出
- 不需要 Agent 推理的确定性任务

### 2.7 上下文配置

| YAML 字段 | CLI 参数 | 说明 | 推荐值 |
|-----------|----------|------|--------|
| `context.lightContext` | `--light-context` / `--no-light-context` | 是否跳过 workspace bootstrap | 巡检/提醒 `true`，开发 `false` |

### 2.8 高级选项

| YAML 字段 | CLI 参数 | 说明 | 推荐值 |
|-----------|----------|------|--------|
| `advanced.disabled` | `--disabled` | 创建后默认禁用 | 调试时用 |
| `advanced.deleteAfterRun` | `--delete-after-run` | 成功后删除 | 一次性任务 |
| `advanced.keepAfterRun` | `--keep-after-run` | 成功后保留 | 默认 |
| `advanced.wake` | `--wake` | 立即执行或等下次心跳 | `now` / `next-heartbeat` |
| `advanced.exact` | `--exact` | 禁用自动 stagger | 提醒类 `true` |
| `advanced.stagger` | `--stagger` | 显式错峰窗口 | `30s` |

---

## 三、非官方扩展详解

这些字段不会变成 `--xxx` 参数，而是渲染进 `message` 里，由 Agent 在运行时执行。

### 3.1 时间窗口 `timeWindow`

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `enabled` | 是否启用 | `true` |
| `start` | 窗口开始时间 | 场景定义 |
| `end` | 窗口结束时间 | 场景定义 |
| `action` | 窗口外行为 | `NO_REPLY` |

**为什么需要：** 防止 OpenClaw gateway 重启后补发任务导致非时段执行（开机堆叠）。

### 3.2 去重 `deduplication`

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `enabled` | 是否启用 | `true` |
| `stateFile` | 状态文件路径 | `{{WORKSPACE}}/.state/reminder-xxx.txt` |

**为什么需要：** 防止同一任务在开机堆叠时被重复执行。

### 3.3 人设 `persona`

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `mode` | `inline` / `file` | `inline` |
| `file` | 外部人设文件路径 | 空 |
| `role` | inline 模式角色描述 | 场景定义 |

### 3.4 模板 `template`

整个 Prompt 的模板源。场景变量会替换其中的 `{{XXX}}` 占位符。

---
