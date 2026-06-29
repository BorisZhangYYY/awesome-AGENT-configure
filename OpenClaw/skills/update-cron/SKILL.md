---
name: update-cron
version: 1.0.0
description: 当 awesome-AGENT-configure 模板升级时，批量更新已有的 AAC 规范化 OpenClaw 定时任务，使其复用最新模板与 Harness/Loop 机制
aliases:
  - "update cron"
  - "升级 cron"
  - "同步定时任务"
  - "更新 AAC 任务"
required_tools:
  - shell
  - filesystem
metadata:
  openclaw:
    requires:
      bins: ["python3", "openclaw"]
---

# update-cron

当 `awesome-AGENT-configure` 项目的模板（`OpenClaw/template/template-cron.zh.yaml`、场景模板、`OpenClaw/conf/defaults.yaml` 等）发生升级后，AGENT 使用本 skill 帮助用户把已创建的 AAC 规范化任务同步到最新模板，**保留任务 ID 和核心配置**。

## 何时触发

- 用户说"update cron"、"升级 cron"、"同步定时任务"、"更新 AAC 任务"
- 用户表达"模板升级了，帮我更新已有 cron 任务"、"AAC 任务怎么同步最新模板"等意图
- 项目 `CHANGELOG.md` 中出现"Loop 机制更新"、"Harness 机制调整"等模板层改动后，主动建议用户同步

## 与 edit-cron 的区别

| Skill | 场景 | 用户操作 |
|-------|------|----------|
| `edit-cron` | 修改单个任务的配置（时间、内容、delivery 等） | 用户明确要改某个任务 |
| `update-cron` | 模板本身升级后，批量把旧任务复用新模板 | 用户要同步模板改进，任务配置不变 |

## 前提条件

本 skill 只适用于**已按本项目规范创建**的任务，即：

1. 任务名称带有 `【AAC-` 前缀
2. 存在对应的场景 YAML 文件：

```bash
$AAC_WORKSPACE/cron/
# 默认 AAC_WORKSPACE = ~/.openclaw/workspace/awesome-AGENT-configure
```

如果任务不是通过本项目创建的（没有对应 YAML），建议改用 `migrate-cron` skill。

## AGENT 执行流程

### 1. 列出当前 cron 任务

运行：

```bash
openclaw cron list
```

如果没有任务，告知用户：

> 当前没有 cron 任务。如需创建新任务，请使用 init-cron。

### 2. 筛选 AAC 规范化任务

从列表中筛选名称带 `【AAC-` 前缀的任务。向用户展示：

> 检测到以下 N 个通过 awesome-AGENT-configure 创建的任务，可以同步最新模板：
> - xxx
> - yyy
>
> 您希望同步哪些任务？可以指定任务名、ID，或说"全部"。

**不要默认更新全部任务**，只处理用户明确选择的任务。如果用户说"全部"，再对所有 AAC 任务执行后续步骤。

### 3. 定位项目仓库（`AAC_REPO`）

按照 `OpenClaw/skills/SKILL-GUIDE.md` 中"五、项目路径与运行时路径分离"的方法设置 `AAC_REPO`：

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

如果定位失败，停止执行并提示用户设置 `AAC_REPO` 环境变量。

### 4. 查找每个任务对应的场景 YAML

对每个选定任务，在 `$AAC_WORKSPACE/cron/` 下查找对应的 YAML 文件。常见文件名模式：

- `init-<job-name>.yaml`
- `migrated-<job-name>.yaml`
- 用户手动命名的 `<job-name>.yaml`

如果找不到对应 YAML，记录到"待人工处理"列表，继续处理其他任务。

### 5. 使用最新模板重新渲染

对每个找到 YAML 的任务，运行：

```bash
export AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/<job-name>.yaml" \
  --preview
```

这会渲染出基于最新模板的 `openclaw cron create` 命令和新的 `message`。

**注意**：渲染时如果 YAML 中使用了默认占位符（如 `DEV_PROJECT_DIR: /path/to/your/project`），`build-cron.py` 会报错并提示用户修改。此时应暂停，告知用户先通过 `edit-cron` 修正该任务的配置。

### 6. 获取任务 ID

运行：

```bash
openclaw cron list --format json
```

在 JSON 输出中精确匹配 `name` 等于该任务名称的条目，提取其 `id`。

如果无法找到任务 ID，记录到"待人工处理"列表，继续处理其他任务。

### 7. 选择更新方式

根据任务类型和字段支持情况选择更新方式（参考 `OpenClaw/skills/SKILL-GUIDE.md` 中的"四、`openclaw cron edit` 支持矩阵"）：

- **Agent 模式任务**（使用 `--message`）：优先使用 `openclaw cron edit <job-id>`，**保留 job ID**。
- **命令模式任务**（使用 `--command`）：当前 `edit` 不支持 `--command`、`-command-argv` 等命令相关字段，只能先删除旧任务再创建新任务，**job ID 会改变**。

### 8. 生成更新命令并请求确认

#### 方式 A：Agent 模式任务（推荐）

将 `build-cron.py` 生成的 `openclaw cron create` 命令替换为 `openclaw cron edit <job-id>`，保留所有 `--message`、`--cron`、`--tz`、`--session`、`--thinking`、`--tools`、`--model`、`--announce`/`--no-deliver` 等字段：

```bash
openclaw cron edit <job-id> \
  --message "<最新模板渲染后的 message>" \
  --cron "<SCHEDULE_EXPR>" \
  --tz "<TIMEZONE>" \
  ...
```

由于 `--message` 通常很长，如果命令行长度超出限制，可以改用 `--message-file <path>`（如果 OpenClaw CLI 支持）或将 message 写入临时文件后引用。若均不支持，则分段执行：先删除再创建（方式 B）。

#### 方式 B：命令模式任务 或 方式 A 不可行

1. 删除旧任务：

```bash
openclaw cron rm <job-id>
```

2. 创建新任务（使用 `build-cron.py` 生成的完整 `openclaw cron create` 命令）：

```bash
python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/<job-name>.yaml"
# 执行上面输出的命令
```

### 9. 向用户展示更新计划

汇总所有待更新任务，展示：

| 任务名 | 方式 | 是否保留 ID | 备注 |
|--------|------|-------------|------|
| xxx | edit | ✅ | Agent 模式 |
| yyy | rm+create | ❌ | 命令模式 |
| zzz | 跳过 | — | 未找到 YAML |

询问：

> 以上为同步计划。确认后我将执行更新。

### 10. 执行更新

用户确认后，按任务逐个执行。每个任务执行后验证：

```bash
openclaw cron list
```

并检查任务 ID 是否与预期一致。

### 11. 汇报结果

向用户汇报：

- 成功同步的任务数量
- 保留原 ID 的任务数量
- 需要重新创建（ID 改变）的任务数量
- 因缺少 YAML 或找不到 ID 而跳过的任务数量
- 跳过的原因

示例汇报：

```markdown
✅ 已同步 3 个 AAC 任务：
- 【AAC-提醒】早安（ID 保留：abc123）
- 【AAC-巡检】Docker 容器健康（ID 保留：def456）
- 【AAC-项目】MyProject 功能开发（ID 保留：ghi789）

⚠️ 跳过 1 个任务：
- 【AAC-学习】XXX：未找到对应场景 YAML，请手动检查 $AAC_WORKSPACE/cron/
```

## 关键原则

- **只更新 AAC 规范化任务**：通过 `【AAC-` 前缀识别，无对应 YAML 时跳过并提示
- **批量但不盲目**：列出后让用户选择，不默认更新全部
- **优先保留 job ID**：Agent 模式任务优先使用 `openclaw cron edit`
- **命令模式需重建**：提前告知用户 job ID 会改变
- **失败任务单独记录**：缺少 YAML、找不到 ID、渲染失败的任务不要阻断其他任务
- **同步后验证**：每个任务更新后检查 `openclaw cron list` 确认状态正常
- **不擅自执行删除/创建**：方式 B 必须先获得用户明确确认

## 注意事项

1. **模板升级可能改变 message 语义**：同步后建议观察一轮任务执行，确认行为符合预期。
2. **Loop 模式任务**：同步时会复用状态文件路径（`DEV_STATE_FILE`），历史状态不会丢失。
3. **避免在高峰时段批量更新**：防止任务因更新而触发状态变化或调度异常。
