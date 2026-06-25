# awesome-AGENT-configure

> 基于 AGENT 常见的 Cron 定时任务机制，结合 Harness 和 Loop 思想，来打造一个**既自律，又准确，还可以自我提升的 AI AGENT**。

## 目录

- [项目简介](#项目简介)
- [支持的模板](#支持的模板)
- [安装与依赖](#安装与依赖)
- [使用方法](#使用方法)
  - [1. 生成 cron 命令](#1-生成-cron-命令)
  - [2. JSON 输出](#2-json-输出)
  - [3. 自定义场景](#3-自定义场景)
- [项目结构](#项目结构)
- [设计原则](#设计原则)
- [链接](#链接)

## 项目简介

你在使用 OpenClaw、Hermes 等 AI AGENT 工具的时候，是否面临 workspace 杂乱、skills 冗杂，Heartbeat 与 Cron 效果不佳的情况？通过本项目提供的模板，结合自身需求修改后将其应用在 AI AGENT 的 cron 机制内，即可通过严格的提示词系统，如状态机、时间窗口、效果评估等方式，让 AI AGENT 的 Cron 效果可记录、可追踪、可推进。

## 支持的模板

- **OpenClaw**：通用 cron 模板 + 提醒类场景 + 生成器脚本
- **Hermes**：待补充
- **Claude Code**：待补充

> 如果你有更多的实用模板，或者是发现了项目中的一些错误与问题，欢迎在 PR 中补充，我会在审核后将其合并入代码库。

## 安装与依赖

本项目为模板集合，可直接复制使用。若需使用脚本生成 cron 命令，请确保环境满足：

- Python 3

无需额外安装第三方依赖。

## 使用方法

### 1. 生成 cron 命令

以早安提醒为例：

```bash
python3 OpenClaw/scripts/build-cron.py OpenClaw/template/reminders/morning.yaml
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
python3 OpenClaw/scripts/build-cron.py OpenClaw/template/reminders/morning.yaml --json
```

### 3. 自定义场景

复制 `OpenClaw/template/reminders/custom.yaml`，修改 `variables` 中的值即可。

## 项目结构

```
awesome-AGENT-configure/
├── AI-ProjConf/              # 通用项目初始化模板（README / TODO / AGENT 等）
├── OpenClaw/
│   ├── conf/                 # OpenClaw 参数与 flag 配置
│   ├── scripts/              # 模板生成与辅助脚本
│   ├── skills/               # 方便管理 AAC cron 封装的 skills
│   └── template/             # cron 场景模板，按类别分子目录
│       ├── check/            # 巡检类模板
│       └── reminders/        # 提醒类模板
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
