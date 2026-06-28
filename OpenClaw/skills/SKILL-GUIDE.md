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
- `【AAC-开发】补全登录功能`

**为什么要强制命名？**

- 一眼识别哪些任务按 AAC 规范创建
- `edit-cron` skill 可通过 `【AAC-` 前缀快速定位可编辑任务
- `migrate-cron` 迁移时统一重命名为 AAC 格式
- 避免用户手动创建的任务和 AAC 任务混淆

四类分类对应：

| 分类 | 前缀 | 示例 |
|------|------|------|
| 提醒 | `【AAC-提醒】` | `【AAC-提醒】早安` |
| 巡检 | `【AAC-巡检】` | `【AAC-巡检】磁盘空间` |
| 开发 | `【AAC-开发】` | `【AAC-开发】登录功能` |
| 学习 | `【AAC-学习】` | `【AAC-学习】RAG 调研` |

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
- `low`：简单巡检
- `medium`：开发、学习
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

**场景级 template 覆盖**

通用模板 `template-cron.zh.yaml` 提供了一份通用 `template`，包含时间窗口、去重、人设注入等通用机制。如果场景不是通用类型，可以在场景 YAML 中通过顶层 `template` 字段**完全覆盖**父模板的 `template`。

例如 `checks/docker.yaml`：

```yaml
template: |
  你是一名 Docker 容器巡检专家，负责检查本机 Docker 容器与 Compose 项目的健康状态。
  ...
```

如果需要复用父模板的通用机制，同时补充场景特定指令，可以使用 `{{SCENE_SPECIFIC_INSTRUCTIONS}}` 占位符。场景 YAML 通过 `SCENE_SPECIFIC_INSTRUCTIONS` 变量注入特定内容，例如 `reminders/morning.yaml`。

> ⚠️ 如果场景 YAML 不覆盖 `template`，且也不提供 `{{SCENE_SPECIFIC_INSTRUCTIONS}}`，最终 message 将只包含通用机制部分。

---

## 四、`openclaw cron edit` 支持矩阵

OpenClaw 官方 CLI **没有 `cron update` 子命令**，更新已有任务应使用：

```bash
openclaw cron edit <job-id> [选项]
```

`edit` 是 patch 语义：只修改指定的字段，未指定的字段保持原样，且 **job ID 不变**。

### 4.1 常用 `edit` 选项与模板变量对应

| 模板变量 | `edit` 选项 | 说明 |
|----------|-------------|------|
| `JOB_NAME` | `--name` | 修改任务名 |
| `SCHEDULE_EXPR`（cron 类型） | `--cron` | 修改 cron 表达式 |
| `TIMEZONE` | `--tz` | 修改时区 |
| `MESSAGE` | `--message` | 修改 Agent 模式提示词 |
| `SYSTEM_EVENT` | `--system-event` | 修改 systemEvent 载荷 |
| `SESSION_TARGET` | `--session` | 修改会话目标 |
| `MODEL` | `--model` | 修改模型覆盖 |
| `THINKING` | `--thinking` | 修改思考级别 |
| `TOOLS` | `--tools` | 修改工具白名单 |
| `DELIVERY_MODE: announce` | `--announce` | 启用 runner 兜底投递 |
| `DELIVERY_MODE: none` | `--no-deliver` | 禁用 runner 兜底投递 |
| `BEST_EFFORT: true` | `--best-effort-deliver` | 投递失败不导致任务失败 |
| `BEST_EFFORT: false` | `--no-best-effort-deliver` | 投递失败导致任务失败 |
| `LIGHT_CONTEXT: true` | `--light-context` | 轻量 bootstrap |
| `LIGHT_CONTEXT: false` | `--no-light-context` | 完整 bootstrap |
| `EXACT: true` | `--exact` | 禁用 stagger |
| `TIMEOUT_SECONDS` | `--timeout-seconds` | Agent 任务超时 |
| `CHANNEL` | `--channel` | 投递渠道 |
| `TO` | `--to` | 投递目标 |
| `STAGGER` | `--stagger` | 显式错峰窗口 |

### 4.2 哪些情况不能直接 `edit`

根据官方 CLI 帮助（`openclaw cron edit --help`），当前 `edit` **不支持** `--command`、`-command-argv`、`-command-cwd` 等命令模式字段。因此：

- **Agent 模式任务**：优先使用 `openclaw cron edit`，保留 job ID。
- **命令模式任务**：只能先 `openclaw cron rm <id>` 再 `openclaw cron create ...`，job ID 会改变。

### 4.3 `edit` 使用示例

```bash
# 修改消息和 cron 表达式，job ID 不变
openclaw cron edit abc123 \
  --message "新的提示词" \
  --cron "0 7 * * *" \
  --tz Asia/Shanghai
```

---

## 五、项目路径与运行时路径分离

本项目坚持“源码/模板”与“运行时配置”完全分离：

- **项目源码**（模板、脚本、skill 文档）在版本控制仓库中，位置由用户决定，例如 `/mnt/d/Study_Project/awesome-AGENT-configure`。
- **运行时配置**（生成的场景 YAML、状态文件）放到 OpenClaw workspace：`~/.openclaw/workspace/awesome-AGENT-configure/cron/`。

因此 skill 执行时需要区分两个路径：

| 变量 | 含义 | 示例 |
|------|------|------|
| `AAC_REPO` | 项目仓库根目录 | `/mnt/d/Study_Project/awesome-AGENT-configure` |
| `AAC_WORKSPACE` | 运行时配置根目录 | `~/.openclaw/workspace/awesome-AGENT-configure` |

### 5.1 定位项目仓库（`AAC_REPO`）

所有 skill 中不再使用 `/path/to/awesome-AGENT-configure` 占位符。AGENT 在执行涉及项目脚本的步骤前，应先定位项目根目录并保存到 `AAC_REPO`。

```bash
export AAC_REPO=$(python3 - <<'PY'
import os, sys

def locate_repo():
    # 1. 环境变量 AAC_REPO（用户显式设置，例如 /mnt/d/Study_Project/awesome-AGENT-configure）
    env = os.environ.get("AAC_REPO")
    if env and os.path.isfile(os.path.join(env, "OpenClaw/scripts/build-cron.py")):
        return env
    # 2. 当前工作目录
    cwd = os.getcwd()
    if os.path.isfile(os.path.join(cwd, "OpenClaw/scripts/build-cron.py")):
        return cwd
    # 3. 在 $HOME 下有限深度搜索
    home = os.path.expanduser("~")
    for root, dirs, _ in os.walk(home):
        if "awesome-AGENT-configure" in dirs:
            p = os.path.join(root, "awesome-AGENT-configure")
            if os.path.isfile(os.path.join(p, "OpenClaw/scripts/build-cron.py")):
                return p
        if root.count(os.sep) - home.count(os.sep) >= 4:
            del dirs[:]
    return ""

path = locate_repo()
if not path:
    print("ERROR: 未找到 awesome-AGENT-configure 项目路径，请先设置 AAC_REPO 环境变量", file=sys.stderr)
    sys.exit(1)
print(path)
PY
)
```

定位优先级：

1. 环境变量 `AAC_REPO`。
2. 当前工作目录（如果它就是项目根目录）。
3. `$HOME` 下前 4 层中名为 `awesome-AGENT-configure` 且包含 `OpenClaw/scripts/build-cron.py` 的目录。

### 5.2 运行时路径（`AAC_WORKSPACE`）

运行时生成的 YAML 和状态文件统一放在 OpenClaw workspace，与项目源码分离：

```bash
AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
mkdir -p "$AAC_WORKSPACE/cron"
```

### 5.3 使用方式

```bash
# 渲染生成命令
python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/init-<job-name>.yaml"
```

如果 `AAC_REPO` 定位失败，应停止执行并提示用户设置 `AAC_REPO` 环境变量。

---
