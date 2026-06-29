---
name: migrate-cron
version: 1.0.0
description: AGENT 帮助用户将已有的 OpenClaw 定时任务按 awesome-AGENT-configure 模板规范进行改造和优化
aliases:
  - "migrate cron"
  - "迁移 cron"
  - "完善定时任务"
  - "改造 cron 任务"
required_tools:
  - shell
metadata:
  openclaw:
    requires:
      bins: ["python3", "openclaw"]
---

# migrate-cron

当用户已有 OpenClaw 定时任务，但配置不规范时，AGENT 使用本 skill 主动分析、改造、生成命令并执行。

## 何时触发

- 用户说"migrate cron"、"迁移 cron"、"完善定时任务"、"改造 cron 任务"
- 用户表达"帮我看看现有 cron 任务有没有问题"等类似意图
- `init-cron` 发现用户已有类似任务时切换到本 skill

## AGENT 执行流程

### 1. 列出当前 cron 任务

运行：

```bash
openclaw cron list
```

如果没有任务，告知用户并建议改用 `init-cron`：

> 检测到您还没有 cron 任务，建议先用 init-cron 创建第一个任务。

### 2. 让用户选择要迁移的任务

向用户展示当前所有任务列表，并询问：

> 您希望改造哪些任务？可以指定任务名、ID，或说"全部"。

**不要默认获取所有任务的详情**，只处理用户明确选择的任务。

如果用户说"全部"，才对所有任务执行后续步骤。

### 3. 获取选定任务的详情

对每个选定的任务运行：

```bash
openclaw cron info --id <job-id>
```

提取关键信息：
- name / description
- schedule（expr、timezone）
- session
- delivery mode
- model / thinking / tools
- lightContext
- timeout
- command 或 message 内容

### 4. 分析任务分类

根据任务名称、描述和实际行为判断分类：

| 分类 | 判断依据 |
|------|----------|
| 提醒 | 定时问候、固定格式、必须送达 |
| 巡检 | 检查状态、正常静默、异常告警 |
| 开发 | 推进项目、需要状态跟踪 |
| 学习 | 技术调研、知识积累 |

如果不确定，询问用户确认。

### 5. 检查不合理之处

对照 `OpenClaw/skills/SKILL-GUIDE.md` 中的推荐配置，检查每个选定任务：

#### 5.1 模型能力

- `thinking` 是否匹配任务复杂度？
- `model` 是否过度？
- `tools` 是否已限定？

#### 5.2 会话与投递

- `session` 是否为 `isolated`？
- `delivery` 模式是否合理？

#### 5.3 Harness 防护

- 是否缺少时间窗口？
- 是否缺少去重？
- `lightContext` 是否合适？

#### 5.4 准时性

- 提醒类是否未开启 `exact`？

### 6. 生成改造报告

为每个选定任务输出结构化的改造建议：

```markdown
## 任务：xxx

- 分类：提醒类
- 当前问题：
  1. thinking 未关闭，浪费 Token
  2. 缺少时间窗口，存在开机堆叠风险
  3. delivery 为 none，但提醒类应使用 announce
- 推荐配置：
  - JOB_NAME: 【AAC-提醒】早安
  - SESSION_TARGET: isolated
  - DELIVERY_MODE: announce
  - LIGHT_CONTEXT: "true"
  - THINKING: "off"
  - EXACT: "true"
  - TIMEOUT_SECONDS: "120"
```

**命名规范**：迁移后的任务名必须统一为 `【AAC-分类】任务名` 格式。如原任务名为 `早安`，迁移后变为 `【AAC-提醒】早安`。如果原任务名已有 `【AAC-` 前缀但分类错误，应一并修正。

### 7. 询问用户是否改造

向用户展示改造报告，并询问：

> 以上为选定任务的诊断结果。是否按推荐配置生成改造后的 YAML 并创建新任务？

### 8. 定位项目仓库（`AAC_REPO`）

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

### 9. 生成改造后的 YAML

用户确认后，为每个选定任务生成新的场景 YAML（放到运行时工作区，与项目源码分离）：

```bash
export AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
mkdir -p "$AAC_WORKSPACE/cron"
# YAML 文件路径：$AAC_WORKSPACE/cron/migrated-<job-name>.yaml
```

基于 `OpenClaw/template/reminders/custom.yaml` 或 `OpenClaw/template/checks/` 下对应分类的模板，填入推荐配置和原有任务的 schedule/内容。

**⚠️ 关键：必须修正 `templateRef` 为仓库绝对路径。** 模板源文件中的 `templateRef: "../template-cron.zh.yaml"` 是相对于仓库 `template/` 目录的路径，复制到 workspace 后无法解析。写入 YAML 时必须替换为：

```yaml
templateRef: "<AAC_REPO 的值>/OpenClaw/template/template-cron.zh.yaml"
```

其中 `<AAC_REPO 的值>` 使用上一步 `$AAC_REPO` 变量的实际路径（如 `/home/user/awesome-AGENT-configure`）。**禁止保留相对路径。**

### 10. 生成 OpenClaw 命令

运行：

```bash
export AAC_WORKSPACE="${AAC_WORKSPACE:-$HOME/.openclaw/workspace/awesome-AGENT-configure}"
python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/migrated-<job-name>.yaml"
```

### 11. 展示并请求确认

展示生成的命令，并说明改动后的效果：

> 以上为改造后的 `openclaw cron create` 命令。确认后我将创建新任务。旧任务不会自动删除，如需删除请单独告知。

### 12. 执行创建

用户确认后，执行生成的命令。

执行后验证：

```bash
openclaw cron list
```

并告知用户：
- 新任务已创建
- 旧任务 ID 未删除，如需删除可运行 `openclaw cron delete --id <old-job-id>`

## 关键原则

- **AGENT 主动诊断**：不是让用户自己对照文档检查
- **只处理用户选定的任务**：不要默认改造全部任务
- **先报告后执行**：改造前必须向用户展示诊断报告并获得确认
- **迁移后强制 AAC 命名**：所有改造后的任务名统一为 `【AAC-分类】任务名`
- **不删除旧任务**：只能建议用户手动删除
- **复杂任务分阶段**：开发/学习类任务不要一次性全改

