---
name: init-cron
version: 1.0.0
description: 认为某些任务可通过 cron 任务来实现时，AGENT 引导用户基于 awesome-AGENT-configure 模板创建合理的 OpenClaw 定时任务
triggers:
  - "init cron"
  - "初始化 cron"
  - "创建定时提醒"
  - "添加 cron 任务"
  - "新建定时任务"
required_tools:
  - shell
  - filesystem
metadata:
  openclaw:
    requires:
      bins: ["python3", "openclaw"]
---

# init-cron

当用户想要创建 OpenClaw 定时任务时，AGENT 使用本 skill 主动完成：选择模板、与用户交流确认配置、生成命令、执行创建。

## 何时触发

- 用户说"init cron"、"初始化 cron"、"创建定时提醒"、"添加 cron 任务"、"新建定时任务"
- 用户表达"我想加一个定时任务"等类似意图

## AGENT 执行流程

### 1. 询问用户任务意图

通过对话询问用户：

1. **任务分类**：提醒 / 巡检 / 项目 / 学习
2. **触发时间**：几点执行？是否每天？
3. **任务内容**：做什么？（如"早安问候"、"检查磁盘"、"生成日报"）
4. **是否需要送达**：必须送达（announce）还是正常静默（none）？

如果用户不确定，给出推荐：

| 分类 | 典型场景 |
|------|----------|
| 提醒 | 早安、午安、晚安、喝水提醒 |
| 巡检 | 磁盘检查、服务健康、容器状态 |
| 项目 | 功能开发、维护会话、代码重构 |
| 学习 | 技术调研、读书笔记、代码练习 |

### 2. 检查是否存在相关/类似任务

运行：

```bash
openclaw cron list
```

根据用户要创建的任务内容，判断现有任务中是否存在**相关或类似**的任务：

- **同名或同主题**：如用户要创建"早安提醒"，已存在"早安"相关任务
- **同分类同目标**：如用户要创建"磁盘巡检"，已存在"check-disk"任务
- **只是用户之前手动创建的不规范版本**

如果存在相关任务，告知用户并建议改用 `migrate-cron`：

> 检测到您已有一个类似任务「xxx」，但配置可能不够规范。建议先用 migrate-cron 对其进行改造，而不是新建一个重复任务。

如果不存在相关任务，继续创建流程。

### 3. 自动选择推荐配置

根据分类，从 `OpenClaw/skills/SKILL-GUIDE.md` 中取出推荐配置，自动填充到场景 YAML：

```yaml
variables:
  SESSION_TARGET: isolated
  DELIVERY_MODE: announce      # 巡检/学习类改为 none
  LIGHT_CONTEXT: "true"        # 开发/学习类改为 false
  THINKING: "off"              # 提醒/巡检 off；开发/学习 medium
  EXACT: "true"                # 提醒类 true，其他 false
  TIMEOUT_SECONDS: "120"       # 按分类调整
  TIME_WINDOW_ENABLED: "true"
  WINDOW_OUT_ACTION: NO_REPLY
  DEDUP_ENABLED: "true"        # 提醒类 true，其他按需
  PERSONA_MODE: inline
```

### 4. 询问用户必要变量

通过对话向用户确认或收集以下变量：

- `CATEGORY`：任务分类，决定 `【AAC-分类】` 前缀
- `TASK_NAME`：任务短名，如"早安"、"磁盘空间"
- `JOB_NAME`：由 AGENT 自动生成为 `【AAC-{{CATEGORY}}】{{TASK_NAME}}`
- `SCHEDULE_EXPR`：cron 表达式
- `TIMEZONE`：时区，默认 `Asia/Shanghai`
- `WINDOW_START` / `WINDOW_END`：时间窗口
- `SCENE_NAME` / `EMOJI` / `PERSONA_ROLE` / `TONE` / `REMARK`：提醒类内容
- 如果是 command 模式：`COMMAND_SCRIPT`、`COMMAND_CWD` 等

其他参数使用分类推荐值，如需修改再询问用户。

**命名强制规则**：所有通过本 skill 创建的任务，名称必须带有 `【AAC-分类】` 前缀。

### 5. 定位项目仓库（`AAC_REPO`）

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

### 6. 生成场景 YAML 文件

将收集到的变量写入运行时工作区（与项目源码分离）：

```bash
export AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
mkdir -p "$AAC_WORKSPACE/cron"
# YAML 文件路径：$AAC_WORKSPACE/cron/init-<job-name>.yaml
```

文件内容基于 `OpenClaw/template/reminders/custom-reminders.yaml`、`OpenClaw/template/learns/custom-learns.yaml`、`OpenClaw/template/projects/` 或 `OpenClaw/template/checks/` 下对应分类的模板。

**⚠️ 关键：必须修正 `templateRef` 为仓库绝对路径。** 模板源文件中的 `templateRef: "../template-cron.zh.yaml"` 是相对于仓库 `template/` 目录的路径，复制到 workspace 后无法解析。写入 YAML 时必须替换为：

```yaml
templateRef: "<AAC_REPO 的值>/OpenClaw/template/template-cron.zh.yaml"
```

其中 `<AAC_REPO 的值>` 使用上一步 `$AAC_REPO` 变量的实际路径（如 `/home/user/awesome-AGENT-configure`）。**禁止保留相对路径。**

### 7. 生成 OpenClaw 命令

运行：

```bash
export AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/init-<job-name>.yaml"
```

### 8. 向用户展示并请求确认

展示以下内容给用户：

- 生成的场景 YAML 路径
- 渲染后的 `openclaw cron create` 命令
- 关键配置说明（为什么这样配）

询问：

> 以上是生成的 cron 任务配置，请审阅。确认无误后回复"执行"，我将创建该任务。

### 9. 执行创建

用户确认后，执行生成的 `openclaw cron create` 命令。

执行后验证：

```bash
openclaw cron list
```

并告知用户创建结果。

## 关键原则

- **AGENT 主动做事**：不是让用户自己读文档、填 YAML、跑脚本
- **先推荐后确认**：自动给出合理默认值，用户只需确认或微调
- **解释配置原因**：每次给出推荐值时，简要说明为什么
- **避免重复任务**：发现类似任务时优先建议迁移改造
- **强制 AAC 命名**：所有创建的任务名必须带 `【AAC-分类】` 前缀
- **不擅自执行 push/delete 等危险操作**：创建前必须获得用户明确确认
