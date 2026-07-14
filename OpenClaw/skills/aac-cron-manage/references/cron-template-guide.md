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
- `【AAC-项目】补全登录功能`

**为什么要强制命名？**

- 一眼识别哪些任务按 AAC 规范创建
- `edit-cron` / `update-cron` skill 可通过 `【AAC-` 前缀快速定位可编辑/可同步的任务
- `migrate-cron` 迁移时统一重命名为 AAC 格式
- 避免用户手动创建的任务和 AAC 任务混淆

四类分类对应：

| 分类 | 前缀 | 示例 |
|------|------|------|
| 提醒 | `【AAC-提醒】` | `【AAC-提醒】早安` |
| 巡检 | `【AAC-巡检】` | `【AAC-巡检】磁盘空间` |
| 项目 | `【AAC-项目】` | `【AAC-项目】登录功能` |
| 学习 | `【AAC-学习】` | `【AAC-学习】RAG 调研` |

### 1.4 模板类型

| 模板 | 路径 | 适用场景 | 核心机制 |
|------|------|----------|----------|
| **统一父模板** | `template-cron.zh.yaml` | 提醒、巡检、学习、项目 | Harness（时间窗口 + 去重）+ 可选 Loop（状态驱动 + 里程碑） |

> **关键区别**：`template-cron.zh.yaml` 是所有场景的统一父模板。当 `LOOP_MODE_ENABLED` 为 `true` 时进入 Loop 模式，支持状态续传、目标/里程碑和到达目标后自动停用 cron。

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
| `context.lightContext` | `--light-context` / `--no-light-context` | 是否跳过 workspace bootstrap | 巡检/提醒 `true`，开发/整理 `false` |

**`lightContext` 含义：**
- `true`（`--light-context`）：**不加载** AGENTS.md/SOUL.md/IDENTITY.md 等系统文件，节省 Token。适合简单提醒、巡检等无需读取系统文件的任务。
- `false`（`--no-light-context`）：**完整加载**所有 bootstrap 文件。审查/整理/开发类任务必须设为 `false`，因为任务需要读取这些文件的内容。

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

**禁止场景级 template 覆盖**

为确保时间窗口、去重等非官方 Harness 机制对所有场景一致生效，**场景 YAML 不允许直接定义顶层 `template` 字段**。所有场景的 prompt 都基于 `template-cron.zh.yaml` 中的通用 `template`。

场景特定内容必须通过 `{{SCENE_SPECIFIC_INSTRUCTIONS}}` 占位符注入，由场景 YAML 的 `SCENE_SPECIFIC_INSTRUCTIONS` 变量提供。例如 `reminders/morning.yaml`：

```yaml
variables:
  SCENE_SPECIFIC_INSTRUCTIONS: |
    你负责在合适的时间给主人送上早安提醒。
    ...
```

> ⚠️ 如果场景 YAML 直接定义顶层 `template` 字段，`build-cron.py` 会报错。

**通用 `template` 已包含的机制**

- `{{PERSONA_PROMPT}}`：人设注入
- 时间窗口检查（基于 `TIME_WINDOW_ENABLED` / `WINDOW_START` / `WINDOW_END` / `WINDOW_OUT_ACTION`）
- 单日/单次去重（基于 `DEDUP_ENABLED` / `DEDUP_STATE_FILE`，日期由 Agent 运行时通过 `exec date` 获取）
- 执行后去重状态写入（基于 `DEDUP_ENABLED` / `DEDUP_STATE_FILE`，日期由 Agent 运行时通过 `exec date` 获取）

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
    if env and os.path.isfile(os.path.join(env, "OpenClaw/skills/aac-cron-manage/scripts/build-cron.py")):
        return env
    # 2. 当前工作目录
    cwd = os.getcwd()
    if os.path.isfile(os.path.join(cwd, "OpenClaw/skills/aac-cron-manage/scripts/build-cron.py")):
        return cwd
    # 3. 在 $HOME 下有限深度搜索
    home = os.path.expanduser("~")
    for root, dirs, _ in os.walk(home):
        if "awesome-AGENT-configure" in dirs:
            p = os.path.join(root, "awesome-AGENT-configure")
            if os.path.isfile(os.path.join(p, "OpenClaw/skills/aac-cron-manage/scripts/build-cron.py")):
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
3. `$HOME` 下前 4 层中名为 `awesome-AGENT-configure` 且包含 `OpenClaw/skills/aac-cron-manage/scripts/build-cron.py` 的目录。

### 5.2 运行时路径（`AAC_WORKSPACE`）

运行时生成的 YAML 和状态文件统一放在 OpenClaw workspace，与项目源码分离：

```bash
AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
mkdir -p "$AAC_WORKSPACE/cron"
```

### 5.3 使用方式

```bash
# 渲染生成命令
python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/init-<job-name>/init-<job-name>.yaml"
```

如果 `AAC_REPO` 定位失败，应停止执行并提示用户设置 `AAC_REPO` 环境变量。

---

## 六、开发迭代模板（Loop 方法）

### 6.1 什么是 Loop 方法

Loop 方法是一种**状态驱动的增量迭代开发模式**，核心思想：

1. **状态续传**：通过 `.state/session.json` 记录进度，跨会话保持连续性
2. **清单驱动**：START 清单（启动时）和 EXIT 清单（退出时）确保每次会话质量
3. **增量迭代**：每次只做一小块，积累到完整功能
4. **自动恢复**：根据状态自动判断是「领新任务」「续传」还是「解阻塞」

### 6.2 与通用 Cron 模板的区别

| 维度 | 通用 Cron（提醒/巡检） | 开发迭代（Loop） |
|------|------------------------|------------------|
| **执行模式** | 单次执行，结束即完 | 循环迭代，状态续传 |
| **状态管理** | 无（或简单去重） | 有（session.json 完整状态机） |
| **清单机制** | 无 | START / EXIT 双清单 |
| **超时时间** | 短（2-5 分钟） | 长（2-4 小时） |
| **lightContext** | 通常为 `true` | 必须为 `false`（需系统文件） |
| **thinking** | 通常为 `off` | 通常为 `medium/high` |
| **单日去重** | 通常启用 | 通常禁用（一天可多次迭代） |

### 6.3 状态机

```
+--------+     领新任务      +-------------+
| ready  | ----------------> | in_progress |
+--------+                   +-------------+
       ^                            | 完成/部分完成
       |                            v
       +-----------------------+ 遇到阻塞
                                 +---------+
                                 | blocked | ——→ 限时解阻塞（≤15min）
                                 +---------+      超时则保持 blocked
```

### 6.4 开发迭代的三阶段

#### PHASE 1：START — 会话启动

**必须执行**：
1. 读取状态文件（`session.json`）
2. 读取项目 TODO.md
3. 读取最近 git 提交历史
4. 判断会话类型（ready / in_progress / blocked）
5. 加载开发上下文（代码、测试、文档）

#### PHASE 2：DEV — 执行开发任务

**核心开发工作**：
1. 按当前任务执行编码
2. 遵守最少改动原则和验证闭环
3. 运行测试验证

#### PHASE 3：EXIT — 会话退出

**必须执行**：
1. 代码收尾（语法检查、测试、git diff）
2. 安全审查（无 API Key、无私人路径）
3. Git 提交（**不 push**，遵守安全红线）
4. 更新状态文件（status、next_step、tech_debt）
5. 更新 TODO.md
6. 汇报（如配置了投递）

### 6.5 项目场景文件示例

#### 功能开发（`projects/feature.yaml`）

```yaml
templateRef: "../template-cron.zh.yaml"

variables:
  # 启用 Loop 模式
  LOOP_MODE_ENABLED: "true"

  JOB_NAME: "【AAC-项目】XXX 功能开发"
  SCHEDULE_EXPR: "0 10 * * 1-5"  # 工作日上午 10 点
  TIMEZONE: "Asia/Shanghai"
  WINDOW_START: "09:00"
  WINDOW_END: "12:00"

  DEV_PROJECT_NAME: "MyProject"
  DEV_PROJECT_DIR: "/path/to/project"
  DEV_PHASE: "Phase 1"
  DEV_BRANCH: "dev/main"
  DEV_STATE_FILE: "{{DEV_PROJECT_DIR}}/.state/dev-session.json"
  DEV_TEST_PATTERN: "test_*.py"
  # Git 提交前缀（常见：feat/fix/refactor/maint/docs/test/chore）
  DEV_COMMIT_PREFIX: "feat"
  # 项目文档目录
  DEV_DOCS_DIR: "{{DEV_PROJECT_DIR}}/docs"

  # 目标与里程碑
  DEV_GOAL: "完成 XXX 功能的开发与测试"
  DEV_MILESTONES: '["里程碑 1：基础模块", "里程碑 2：核心逻辑", "里程碑 3：集成测试与文档"]'
  DEV_CURRENT_MILESTONE: "里程碑 1：基础模块"
  DEV_AUTO_DISABLE_ON_GOAL_REACHED: "true"

  # 核心：定义具体开发指令
  DEV_TASK_INSTRUCTIONS: |
    ### 当前任务：实现 XXX 功能
    
    步骤：
    1. ...
    2. ...
    3. ...
    
    验收标准：
    - 测试全部通过
    - 代码符合项目规范

  # 项目类配置
  LIGHT_CONTEXT: "false"
  THINKING: "medium"
  TOOLS: "exec,read,write,edit,bash"
  TIMEOUT_SECONDS: "14400"  # 4 小时
  SESSION_TARGET: "isolated"

  # 通常不需要单日去重
  DEDUP_ENABLED: "false"
  DEDUP_STATE_FILE: "{{WORKSPACE}}/.state/dev-feature-dedup.txt"
```

#### 维护会话（`projects/maintain.yaml`）

```yaml
templateRef: "../template-cron.zh.yaml"

variables:
  # 启用 Loop 模式
  LOOP_MODE_ENABLED: "true"

  JOB_NAME: "【AAC-项目】XXX 维护会话"
  SCHEDULE_EXPR: "0 15 * * 1-5"  # 工作日下午 3 点

  DEV_PROJECT_NAME: "MyProject"
  DEV_PROJECT_DIR: "/path/to/project"
  DEV_PHASE: "维护"
  DEV_BRANCH: "main"
  DEV_STATE_FILE: "{{DEV_PROJECT_DIR}}/.state/dev-maintain-session.json"
  # Git 提交前缀（常见：feat/fix/refactor/maint/docs/test/chore）
  DEV_COMMIT_PREFIX: "maint"
  # 项目文档目录
  DEV_DOCS_DIR: "{{DEV_PROJECT_DIR}}/docs"

  # 目标与里程碑
  DEV_GOAL: "完成本轮维护周期"
  DEV_MILESTONES: '["测试回归", "健康检查", "债务处理", "依赖与文档同步"]'
  DEV_CURRENT_MILESTONE: "测试回归"
  DEV_AUTO_DISABLE_ON_GOAL_REACHED: "false"

  DEV_TASK_INSTRUCTIONS: |
    ### 维护标准流程
    1. 运行全部测试
    2. 代码健康检查
    3. 技术债务处理
    4. 依赖检查
    5. 文档同步
```

### 6.6 推荐配置速查表

| 配置项 | 功能开发 | 维护会话 | 重构任务 |
|--------|----------|----------|----------|
| `SCHEDULE_EXPR` | `0 10 * * 1-5` | `0 15 * * 1-5` | `0 10 * * 1,3,5` |
| `TIMEOUT_SECONDS` | `14400` (4h) | `7200` (2h) | `10800` (3h) |
| `THINKING` | `medium` | `medium` | `high` |
| `LIGHT_CONTEXT` | `false` | `false` | `false` |
| `DEDUP_ENABLED` | `false` | `false` | `false` |
| `TOOLS` | `exec,read,write,edit` | `exec,read,write,edit` | `exec,read,write,edit` |
| `DEV_COMMIT_PREFIX` | `feat` | `maint` | `refactor` |

### 6.7 状态文件格式

开发迭代模板依赖的状态文件（`session.json`）标准格式：

```json
{
  "status": "ready | in_progress | blocked | completed | goal_reached",
  "current_card": "任务标识（如 P4-T1）",
  "last_session": "2026-06-29T10:00:00+08:00",
  "next_step": "具体、可执行的下一步",
  "blockers": ["阻塞项描述"],
  "tech_debt": ["债务描述"],
  "test_coverage": "208/208 全部通过",
  "goal": "总体目标描述",
  "milestones": ["里程碑 1", "里程碑 2", "里程碑 3"],
  "current_milestone_index": 0,
  "dev_log": [
    {
      "time": "2026-06-29T10:00:00+08:00",
      "task": "P4-T1",
      "summary": "完成了 xxx",
      "tests": "通过",
      "commit": "abc1234"
    }
  ]
}
```

### 6.8 安全红线（开发模板特有）

1. **不自动 push**：模板只执行 `git commit`，`git push` 必须人工审核后执行
2. **敏感信息检查**：EXIT 阶段必须检查 API Key、token、私人路径
3. **变更范围确认**：`git diff` 确认无意外文件被修改
4. **测试通过才能提交**：未通过测试的代码不提交（或明确标记为 WIP）

---
