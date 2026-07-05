# awesome-AGENT-configure

> 一套面向 OpenClaw、Hermes 等 AI AGENT 框架的**模板集合**，通过 Harness 与 Loop 机制让 AI AGENT 更加可控与可靠。

## 项目定位

本项目不是直接安装的软件，而是**可拿走的模板**：

1. **`{AGENT}/skills/`** 提供基础 Skill 模板（如创建 skill、管理 cron）。
2. **`{AGENT}/template/`** 提供通用配置模板（如 cron 父模板）。

你可以把 `skills/` 和 `template/` 中的模板复制到自己的项目中，结合需求改造后再使用。

## 目录说明

```text
awesome-AGENT-configure/
├── OpenClaw/
│   ├── skills/          # 基础 Skill 模板（aac-skill-manage、aac-cron-manage）
│   ├── scripts/         # 通用辅助脚本（如 aac-manage.sh）
│   ├── template/        # 通用 cron 父模板与场景模板
├── Claude Code/         # 未来开发
├── Hermes/              # 未来开发
├── CHANGELOG.md
├── CLAUDE.md
├── README.md
└── TODO.md
```

## 使用方式

### 1. 直接使用通用模板

以 OpenClaw 早安提醒为例：

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py OpenClaw/template/reminders/morning.yaml
```

### 2. 基于基础模板创建自己的场景

1. 从 `OpenClaw/skills/` 复制需要的基础 skill（`aac-skill-manage`、`aac-cron-manage`）。
2. 每个 skill 已自带 `scripts/`，注册到 OpenClaw workspace 后仍可独立运行。
3. 在运行时目录（默认 `~/.openclaw/workspace/awesome-AGENT-configure/cron/`）编写场景 YAML，`templateRef` 使用项目根目录的绝对路径。
4. 用本 skill 目录下的 `scripts/build-cron.py` 渲染生成 `openclaw cron create` 命令。

### 3. 管理 Skill 和 Cron

安装基础 skill：

```bash
./OpenClaw/scripts/aac-manage.sh install-skill aac-skill-manage aac-cron-manage
```

创建新 skill：

```bash
python3 OpenClaw/skills/aac-skill-manage/scripts/init_skill.py aac-<name> \
  --path OpenClaw/skills \
  --resources scripts
```

校验 skill：

```bash
python3 OpenClaw/skills/aac-skill-manage/scripts/quick_validate.py OpenClaw/skills/<name>
```

安装 cron 场景：

```bash
./OpenClaw/scripts/aac-manage.sh install-cron OpenClaw/template/reminders/morning.yaml
```

删除 cron：

```bash
./OpenClaw/scripts/aac-manage.sh remove-cron "【AAC-提醒】早安"
```

## 设计原则

- **模板化复用**：通用约束写在父模板中，场景文件只填变量。
- **Harness 防护**：通过时间窗口、单日去重、状态机等机制防止 cron 误触发与重复执行。
- **Loop 推进**：项目类任务使用状态机持续迭代，直到目标达成。
- **简约脚本**：`build-cron.py` 只做 YAML → CLI 的翻译，不嵌入业务逻辑；每个 cron skill 均自包含一份，避免注册后路径丢失。

## 链接

- OpenClaw 官方文档：https://docs.openclaw.ai/
- Hermes 官方文档：https://hermes-agent.nousresearch.com/docs
- Claude Code 官方文档：https://code.claude.com/docs
