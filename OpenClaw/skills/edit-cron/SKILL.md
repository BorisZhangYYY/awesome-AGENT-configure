---
name: edit-cron
version: 1.0.0
description: AGENT 帮助用户编辑已被 awesome-AGENT-configure 规范化后的 OpenClaw 定时任务
aliases:
  - "edit cron"
  - "修改 cron"
  - "编辑定时任务"
  - "更新 cron 任务"
required_tools:
  - shell
  - filesystem
metadata:
  openclaw:
    requires:
      bins: ["python3", "openclaw"]
---

# edit-cron

当用户想要修改一个**已经通过 awesome-AGENT-configure 模板创建**的 OpenClaw 定时任务时，AGENT 使用本 skill 编辑对应的场景 YAML、重新生成命令并更新任务。

## 何时触发

- 用户说"edit cron"、"修改 cron"、"编辑定时任务"、"更新 cron 任务"
- 用户表达"把早安提醒改到 7:30"、"调整巡检频率"等意图

## 前提条件

本 skill 只适用于**已按本项目规范创建**的任务，即存在对应的场景 YAML 文件：

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

### 2. 让用户选择要编辑的任务

向用户展示任务列表，并优先标识出名称带 `【AAC-` 前缀的任务：

> 以下是当前 cron 任务，带 `【AAC-` 前缀的是通过本模板规范化的任务，可直接编辑。您希望编辑哪个？

如果用户选择的任务名没有 `【AAC-` 前缀，告知用户：

> 该任务不是通过 awesome-AGENT-configure 模板创建的，建议先用 migrate-cron 改造后再编辑。

### 3. 查找对应的场景 YAML

根据任务名，在以下目录查找对应的 YAML 文件：

```bash
$AAC_WORKSPACE/cron/
# 默认 AAC_WORKSPACE = ~/.openclaw/workspace/awesome-AGENT-configure
```

文件名可能是：
- `init-<job-name>.yaml`
- `migrated-<job-name>.yaml`
- 用户手动命名的其他 yaml

如果找不到对应 YAML，告知用户：

> 未找到该任务对应的场景 YAML，可能不是通过本模板创建的。建议先用 migrate-cron 改造。

### 4. 读取并展示当前配置

读取 YAML 文件，向用户展示当前关键配置：

- 任务名称
- cron 表达式
- 时间窗口
- session / delivery / thinking / lightContext / exact
- 任务内容（如提醒类的 SCENE_NAME、REMARK 等）

### 5. 询问用户要修改的内容

通过对话询问用户：

> 您希望修改哪些配置？例如：触发时间、时间窗口、问候语、delivery 模式、thinking 级别等。

常见修改项：

| 修改意图 | 对应变量 |
|----------|----------|
| 改触发时间 | `SCHEDULE_EXPR` |
| 改时间窗口 | `WINDOW_START` / `WINDOW_END` |
| 改内容 | `SCENE_NAME` / `EMOJI` / `REMARK` / `TONE` |
| 改送达方式 | `DELIVERY_MODE` |
| 改模型能力 | `THINKING` / `MODEL` / `TOOLS` |
| 改超时 | `TIMEOUT_SECONDS` |
| 改执行脚本 | `COMMAND_SCRIPT` / `COMMAND_CWD` |

### 6. 修改场景 YAML

场景 YAML 位于运行时工作区（与项目源码分离）：

```bash
export AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
# YAML 文件路径：$AAC_WORKSPACE/cron/<job-name>.yaml
```

根据用户要求修改 YAML 文件中的变量值。

如果用户要修改的是分类相关的推荐配置（如从提醒类改成巡检类），需要参考 `OpenClaw/skills/SKILL-GUIDE.md` 调整整组参数。

### 6.5 定位项目仓库（`AAC_REPO`）

按照 `OpenClaw/skills/SKILL-GUIDE.md` 中“五、项目路径与运行时路径分离”的方法设置 `AAC_REPO`：

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

### 7. 重新生成 OpenClaw 命令

运行：

```bash
export AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/<job-name>.yaml"
```

得到 `openclaw cron create` 命令，用于审阅完整配置。

### 8. 选择更新方式并请求确认

OpenClaw 提供 `openclaw cron edit <job-id>` 来 patch 已有任务，**job ID 不变**。`edit` 支持 `--message`、`--cron`、`--name`、`--session`、`--thinking`、`--tools`、`--model`、`--tz`、`--announce`、`--no-deliver` 等常见字段，完整映射参见 `OpenClaw/skills/SKILL-GUIDE.md` 中的“四、`openclaw cron edit` 支持矩阵”。

- **Agent 模式任务**：优先使用 `openclaw cron edit <job-id>`，仅 patch 变更字段。
- **命令模式任务**：当前 `edit` 不支持 `--command`、`-command-argv` 等命令相关字段，只能先删除旧任务再创建新任务，job ID 会改变。

向用户展示：

- 修改前后的关键差异
- 将使用的更新方式（`edit` 还是 `delete+create`）
- 对应的命令

询问：

> 以上为更新后的配置。确认后我将执行更新。

### 9. 执行更新

#### 方式 A：Agent 模式且字段可被 `edit` 支持

```bash
openclaw cron edit <job-id> \
  --message "..." \
  --cron "..." \
  ...
```

#### 方式 B：命令模式或 `edit` 不支持相关字段

1. 删除旧任务：

```bash
openclaw cron rm <job-id>
```

2. 创建新任务：

```bash
openclaw cron create ...
```

验证：

```bash
openclaw cron list
```

并告知用户更新结果：

- 使用 `edit` 时，job ID 不变。
- 使用 delete+create 时，job ID 改变，旧运行历史不再关联。

## 关键原则

- **只编辑 AAC 规范化的任务**：通过 `【AAC-` 前缀识别，无对应 YAML 时转 migrate-cron
- **先展示再修改**：让用户清楚当前配置
- **明确变更差异**：修改前后对比展示
- **删除旧任务前必须确认**：这是破坏性操作
- **保留 YAML 文件**：修改后的 YAML 继续保存在 `$AAC_WORKSPACE/cron/`（默认 `~/.openclaw/workspace/awesome-AGENT-configure/cron/`）
- **编辑后名称仍保持 AAC 格式**：如修改分类，需同步更新 `【AAC-分类】` 前缀

