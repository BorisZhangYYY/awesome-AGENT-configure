# awesome-AGENT-configure

> 基于 AGENT 常见的 Cron 定时任务机制，结合 Harness 和 Loop 思想，来打造一个**既自律，又准确，还可以自我提升的 AI AGENT**。

## 项目简介

你在使用 OpenClaw、Hermes 等 AI AGENT 工具的时候，是否面临 workspace 杂乱、skills 冗杂，Heartbeat 与 Cron 效果不佳的情况？通过本项目提供的模板，结合自身需求修改后将其应用在 AI AGENT 的 cron 机制内，即可通过严格的提示词系统，如状态机、时间窗口、效果评估等方式，让 AI AGENT 的 Cron 效果可记录、可追踪、可推进。

## 支持的模板

- **OpenClaw**：
  - 通用 cron 模板（`template-cron.zh.yaml`）：提醒、巡检、学习等单次任务，以及项目类 Loop 模式任务
  - 提醒类场景（morning / noon / evening / custom-reminders）
  - 巡检类场景（workspace-check / docker / cron-check）
  - 项目类场景（feature / maintain，启用 `LOOP_MODE_ENABLED`）
  - 学习类场景（custom-learns）
- **Hermes**：待补充
- **Claude Code**：待补充

> 如果你有更多的实用模板，或者是发现了项目中的一些错误与问题，欢迎在 PR 中补充，我会在审核后将其合并入代码库。

## 安装与依赖

本项目为模板集合，可直接复制使用。若需使用脚本生成 cron 命令，请确保环境满足：

- Python 3
- PyYAML（`pip install pyyaml`）

```bash
pip install pyyaml
```

## 使用方法

### 1. 生成 cron 命令

以早安提醒为例：

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py OpenClaw/cron-template/reminders/morning/morning.yaml
```

输出示例：

```bash
openclaw \
  cron \
  create \
  '0 8 * * *' \
  --message \
  '...' \
  --name \
  '【AAC-提醒】 - 早安' \
  --tz \
  Asia/Shanghai \
  --announce \
  --best-effort-deliver \
  --session \
  isolated \
  --timeout-seconds \
  300 \
  --no-light-context \
  --thinking \
  off \
  --exact
```

### 2. JSON 输出

如果需要程序化调用，可输出 JSON 数组：

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py OpenClaw/cron-template/reminders/morning/morning.yaml --json
```

### 3. 自定义场景

复制 `OpenClaw/cron-template/reminders/custom-reminders/custom-reminders.yaml`，修改 `variables` 中的值即可。

## 项目结构

```
awesome-AGENT-configure/
├── AI-ProjConf/              # 通用项目初始化模板（README / TODO / AGENT 等）
├── OpenClaw/
│   ├── conf/                 # OpenClaw 参数与 flag 配置
│   ├── cron-template/        # cron 场景模板，按类别分子目录
│   │   ├── checks/           # 巡检类模板
│   │   │   ├── cron-check.yaml      # Cron 任务健康巡检
│   │   │   ├── custom-checks.yaml   # 自定义巡检场景
│   │   │   ├── docker-check.yaml    # Docker 容器/Compose 巡检
│   │   │   └── workspace-check.yaml # 工作区整理巡检
│   │   ├── projects/         # 项目类模板（Loop 方法，基于 template-cron.zh.yaml）
│   │   │   ├── custom-projects.yaml  # 自定义项目场景
│   │   │   ├── feature.yaml          # 功能开发场景
│   │   │   └── maintain.yaml         # 维护会话场景
│   │   ├── learns/           # 学习类模板
│   │   │   └── custom-learns.yaml  # AI 自我学习场景
│   │   ├── reminders/        # 提醒类模板
│   │   │   └── custom-reminders.yaml  # 自定义提醒场景
│   │   └── template-cron.zh.yaml  # 通用/Loop 统一父模板
│   ├── hook-template/        # 通用上下文注入模板
│   └── skills/               # AAC cron 管理 skill（含 build-cron.py + trigger 模板）
├── CHANGELOG.md
├── CLAUDE.md
├── README.md
└── TODO.md
```

## 设计原则

- **官方参数映射为 `--` 命令行参数**：如 `--message`、`--command`、`--thinking`
- **非官方扩展通过 Prompt 实现 Harness/Loop**：如时间窗口、去重、人设配置
- **模板化复用**：通用约束写在 `template-cron.zh.yaml`，场景文件只填变量
- **简约脚本**：`build-cron.py` 只做 YAML → CLI 的翻译，不嵌入业务逻辑

## 链接

- OpenClaw 官方文档：https://docs.openclaw.ai/
- Hermes 官方文档：
- Claude Code 官方文档：
