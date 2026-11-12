---
name: aac-hermes-cron-manage
description: Create, verify, and update native Hermes cron templates.
version: 0.1.0
author: BorisZhangYYY, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, templates, harness, loop]
---

# AAC Hermes Cron 管理

简体中文 | [English](SKILL.md)

使用仓库的双语 YAML 模板管理 Hermes 原生定时任务。编译器只输出命令或请求，不执行、不安装脚本。OpenClaw 的独立技能是 `aac-openclaw-cron-manage`，其配置结构不能直接套用。

## 何时使用

- 初始化提醒、巡检、学习、项目 Loop、纯脚本任务或变更监控。
- 编辑、迁移、升级已有 Hermes 任务，同时保留不可变 ID。
- 不用于 OpenClaw 任务、身份文件安装或未经授权的线上调度器/配置改动。

## 前置条件

需要 Python 3、PyYAML、包含 `Hermes/{zh_CN,en_US}/cron-template/` 的仓库，以及目标 Hermes CLI。安装前先确认目标 home/profile。编译器的仓库相对路径是 `Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py`；技能安装到别处时应使用仓库绝对路径。

承诺参数支持前，阅读目标 CLI help 与公共 `tools/cronjob_tools.py::CRONJOB_SCHEMA` 的文本，不为查看 schema 导入线上 Hermes 模块。模板及公开输出不得包含凭据。

## 运行方式

编译器和 CLI 使用 `terminal`；模板使用 `read_file`、`write_file`、`patch`、`search_files`。在仓库根目录只读预览：

```python
terminal(command="python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py Hermes/zh_CN/cron-template/reminders/morning/morning.yaml --preview", timeout=60)
terminal(command="hermes cron create --help && hermes cron edit --help", timeout=60)
```

`--validate`、`--preview`、`--json`、`--tool-json`、`--plan`、`--catalog`、`--check-cli` 是检查/输出模式，不部署。`--edit JOB_ID` 只生成更新，不创建。`--set KEY=YAML_VALUE` 保留布尔值和列表类型。`--home PATH` 与 `--profile PROFILE` 二选一。

## 操作流程

1. 确认范围，通过 `hermes [-p PROFILE] cron list --all` 和 `status` 检查已有任务。仅开发仓库时使用 help/源码/测试夹具，不改线上状态。记录真实 ID、现有策略、投递和权限；名称不唯一。
2. 阅读对应指南：[初始化](references/zh_CN/init-cron.md)、[编辑](references/zh_CN/edit-cron.md)、[迁移](references/zh_CN/migrate-cron.md) 或 [模板升级](references/zh_CN/update-cron.md)。按需查看 [模板与 Loop](references/zh_CN/cron-template-guide.md)、[原生参数](references/zh_CN/native-parameters.md)、[命令](references/zh_CN/commands.md)。
3. 选场景、填写通用变量，检查完整提示词和带类型 job。除非用户要求，保持 `catch_up: false`、明确投递、不固定模型。不自动提交/推送、不启动 Docker、不改 gateway 服务。
4. 校验所选后端与运行前提。CLI 不能携带 `context_from`、`enabled_toolsets`、`attach_to_session`；公共工具不能携带显式 model/provider、reasoning、interpreter、grace 固定项。混合配置使用 `--plan`；任何不支持的参数都必须报错，不得丢弃。
5. 仅获授权后审阅并复制脚本到目标 home 的 `scripts/`，创建暂停任务，读回真实 ID。混合创建计划必须先绑定实际 ID，才能执行工具更新；不得执行未解析占位符。编辑保留 ID 和原暂停状态，任何一步失败都停止后续步骤。
6. 只执行获授权的金丝雀测试。`--test` 仅输出暂停、本地投递、`in 1m`、一次、不补跑的任务，仍需显式 `run`，不保证自动删除。恢复或清理前读回同一任务及运行历史。

## 易错点

- 每次 Agent 运行都是新会话，没有当前聊天上下文，不能自主追问。最终回复由系统投递，不要重复发消息。无报告时只输出 `[SILENT]`；声明失败时首行独占 `[CRON_FAILURE]`。
- `no_agent: true` 必须有 `script`，忽略 prompt/skills，不调用 LLM。空 stdout 静默，非零退出或超时失败；不能与 monitor 同用。前置脚本可用最后一行 JSON `{"wakeAgent": false}` 跳过推理。
- monitor 首次 tick 执行建立基线，之后字节完全不变才抑制 Agent。输出必须稳定。脚本及符号链接最终目标必须位于目标 `$HERMES_HOME/scripts/` 内。
- `null`/省略表示不修改；支持的字符串用 `''` 清空，`skills: []`、`context_from: []` 清空列表。`enabled_toolsets: []` 表示零工具，不是默认工具。模式切换必须显式 false/清空旧值。
- Loop 必须有持久状态文件，`continuity` 只提供上次输出。自动暂停默认关闭；先暂停创建、读回真实 ID，再通过相同 ID 的 `--edit` 绑定后启用。不得按名称找自己，不得仅为此全局启用 `cron.allow_agent_scheduling`。暂停和读回必须指定正确 home/profile；不可用时报告已完成、等待操作员暂停。
- 不编辑原生 `jobs.json`，不假定 OpenClaw 参数存在，不把编译成功/手动执行等同于宿主定时执行。

## 验证

每次获授权写入后读回准确目标：同一 ID、prompt、调度/时区、正常与失败投递、补跑策略、skills、运行模式、脚本/monitor、工具限制、模型固定策略、暂停/启用状态。另行验证脚本安装字节、退出码/stdout/stderr、运行历史、调度器健康；需要时验证真实定时运行。只报告已验证结果和阻塞，生成输出不等于部署。
