# Hermes 身份、Cron 与 Loop 模板

> 身份文件、原生定时任务与有状态推进模板。仅生成配置，不自动安装、创建任务或修改运行中的 Hermes。

简体中文 | [English](README.en.md)

## 语言版本

| 版本 | 目录 |
|------|------|
| 简体中文 | `zh_CN/workspace-template/` |
| English | `en_US/workspace-template/` |

Cron 场景分别位于 `zh_CN/cron-template/` 与 `en_US/cron-template/`；共享技能为 [aac-hermes-cron-manage](skills/aac-hermes-cron-manage/SKILL.zh_CN.md)。Hermes 与 OpenClaw 的模板、编译器和技能独立，OpenClaw 使用 `aac-openclaw-cron-manage`，不能混用参数或静默标记。

## 文件职责

- `SOUL.md`：人格、交流方式与工作区管理约定；其中的目录分类与保留周期是本模板的约定，不代表框架强制要求，也不会自动创建目录或定时任务。
- `memories/USER.md`：用户画像和偏好，发布模板时只保留通用骨架或占位符。
- `memories/MEMORY.md`：长期保留的环境事实与约定，后续可由 Hermes 的 `memory` 工具维护。

## 身份模板使用方式

1. 确认目标 Hermes home：默认是 `~/.hermes/`；使用自定义 home 或 profile 时，以目标实例的 `$HERMES_HOME` 为准，不要覆盖其他 profile。
2. 备份目标文件，再按需将 `workspace-template/` 中的文件复制或合并到目标 home，保持相对路径不变。不要直接覆盖已经积累的用户画像和长期记忆。
3. 修改 `SOUL.md` 中的人格与工作区约定，填写 `memories/USER.md` 的名称、称呼、时区等信息；`Asia/Shanghai` 仅为示例时区。`memories/MEMORY.md` 留作长期记忆的初始骨架。
4. 开启新会话，使更新后的文件被加载。

目标路径分别为 `$HERMES_HOME/SOUL.md`、`$HERMES_HOME/memories/USER.md` 和 `$HERMES_HOME/memories/MEMORY.md`。`SOUL.md` 中的 `~/.hermes` 是默认 home 示例，使用其他 home 时请同步调整。

## Cron 快速开始

在仓库根目录执行；先安装 Python 3 与 PyYAML。下面只校验、预览，不执行生成的命令：

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/zh_CN/cron-template/reminders/morning/morning.yaml --validate
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/zh_CN/cron-template/reminders/morning/morning.yaml --preview
```

- 场景覆盖提醒、检查、学习、项目推进，以及 `scripts/script-only/` 与 `monitors/change-monitor/`。使用 `--set KEY=YAML_VALUE` 覆盖变量；`--home PATH` 或 `--profile PROFILE` 选择目标，不能同时使用。
- 默认输出 shell 命令；`--json` 输出 argv，`--tool-json` 输出公共工具请求，`--plan` 输出跨 CLI/工具的有序计划；均不执行。接口不能表达的非空字段会报错，不会静默丢弃。
- `--test` 生成暂停的一次性 `in 1m`、本地投递、`repeat: 1`、不补跑任务；需明确授权后执行 `run`，不承诺自动删除。脚本必须另行审阅并复制到目标 `$HERMES_HOME/scripts/aac/`，编译器不安装脚本。
- 新任务先创建暂停、读回真实 ID 和配置，再按授权测试及恢复；更新使用 `--edit JOB_ID` 保留 ID，不删除重建。原生 CLI 暂停/恢复是生命周期命令，不是 edit 的 `--paused` 参数。

## Harness 与 Loop

Harness 负责自包含任务、证据、权限边界与失败报告；Loop 每次推进一个可验证里程碑，并把进度写入独立状态文件。默认运行是新会话，没有当前聊天上下文；`continuity` 只注入上次输出，不代替持久状态。

`LOOP_MODE_ENABLED`、`LOOP_TASK_TYPE`、`LOOP_PROJECT_DIR`、`LOOP_STATE_FILE`、`LOOP_GOAL`、列表型 `LOOP_MILESTONES` 控制 Loop。`LOOP_AUTO_PAUSE: false`、`LOOP_JOB_ID: ''` 是安全默认值。自暂停必须先以关闭自暂停的方式创建暂停任务，读回真实 ID，再 `--edit` 同一 ID 注入绑定并显式启用自暂停，最后恢复；不得按名称猜任务。不要为了自暂停全局启用 `cron.allow_agent_scheduling`。

详见 [模板、脚本与 Loop](skills/aac-hermes-cron-manage/references/zh_CN/cron-template-guide.md)、[原生参数](skills/aac-hermes-cron-manage/references/zh_CN/native-parameters.md) 与 [命令和验收](skills/aac-hermes-cron-manage/references/zh_CN/commands.md)。

## 注意事项

- 不要把真实凭据、私人资料、聊天记录或实际运行中的记忆文件提交到公共仓库。
- 模板默认 `catch_up: false`；模型及 provider 仅按用户明确选择固定。Agent 无事输出 `[SILENT]`；失败首行独占 `[CRON_FAILURE]`。脚本空 stdout 静默，非零退出表示失败。
- 脚本模式 `no_agent` 不调用 AI，也不能与 monitor 同用；monitor 首次运行建立基线，后续 stdout 不变不唤醒 Agent，输出不能含时钟等不稳定数据。
- 不自动提交或推送 Git，不擅自启动 Docker 容器，不编辑原生 `jobs.json`，不自动重启 gateway。编写、预览和校验模板不代表已安装或已发生定时执行。

## 官方参考

- [文件职责与加载位置](https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what)
- [持久记忆](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- [原生 Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)；以目标安装的 `hermes cron create/edit --help` 与公共 `CRONJOB_SCHEMA` 核对选项。
