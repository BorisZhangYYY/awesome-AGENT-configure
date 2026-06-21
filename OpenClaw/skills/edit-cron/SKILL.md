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
~/.openclaw/workspace/awesome-AGENT-configure/cron/
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
~/.openclaw/workspace/awesome-AGENT-configure/cron/
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

根据用户要求修改 YAML 文件中的变量值。

如果用户要修改的是分类相关的推荐配置（如从提醒类改成巡检类），需要参考 `OpenClaw/skills/SKILL-GUIDE.md` 调整整组参数。

### 7. 重新生成 OpenClaw 命令

运行：

```bash
python3 /path/to/awesome-AGENT-configure/OpenClaw/scripts/build-cron.py ~/.openclaw/workspace/awesome-AGENT-configure/cron/<job-name>.yaml
```

### 8. 展示变更并请求确认

向用户展示：
- 修改前后的关键差异
- 新生成的 `openclaw cron create` 命令

询问：

> 以上为更新后的配置。确认后我将删除旧任务并创建新任务（OpenClaw 更新任务通常需要重新创建）。

### 9. 执行更新

用户确认后，执行以下操作：

1. 删除旧任务：

```bash
openclaw cron delete --id <old-job-id>
```

2. 创建新任务：

```bash
openclaw cron create ...
```

3. 验证：

```bash
openclaw cron list
```

并告知用户更新结果。

## 关键原则

- **只编辑 AAC 规范化的任务**：通过 `【AAC-` 前缀识别，无对应 YAML 时转 migrate-cron
- **先展示再修改**：让用户清楚当前配置
- **明确变更差异**：修改前后对比展示
- **删除旧任务前必须确认**：这是破坏性操作
- **保留 YAML 文件**：修改后的 YAML 继续保存在 `~/.openclaw/workspace/awesome-AGENT-configure/cron/`
- **编辑后名称仍保持 AAC 格式**：如修改分类，需同步更新 `【AAC-分类】` 前缀

