# 初始化 Hermes 任务

简体中文 | [English](../en_US/init-cron.md)

## 发现与决策

1. 确认唯一目标：默认 home、显式 `HERMES_HOME` 或命名 profile。全局前缀是 `hermes -p PROFILE cron ...`，不是 `hermes cron --profile ...`。
2. 使用 `terminal` 在同一范围检查 `hermes cron create --help`、`hermes cron edit --help`、`hermes cron list --all`、`hermes cron status`。包括停用/已完成任务，存在匹配任务时保留原 ID，不重复创建。仅编写仓库模板不需要读取或修改线上任务。
3. 确认调度、时区、明确投递、失败投递、模式、workdir、skills/工具权限、补跑和验收条件。默认关闭补跑，不固定 model/provider，除非用户明确要求。`30m` 为周期，`in 30m` 为一次。
4. 选择 `Hermes/{zh_CN,en_US}/cron-template/` 中对应语言场景，参考 [模板指南](cron-template-guide.md) 与 [原生参数](native-parameters.md)。

## 只编译，不部署

在仓库根目录通过 `terminal` 执行：

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/zh_CN/cron-template/reminders/morning/morning.yaml --preview
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/zh_CN/cron-template/reminders/morning/morning.yaml --test --json
```

检查完整提示词、带类型字段、目标范围和投递地址。`--test` 只把输出任务变为暂停、本地投递的一次性任务（`in 1m`、一次、不补跑），不自动执行或清理。普通部署应先在场景中设置原生 `job.paused: true` 及原因再编译。不要把编译输出直接通过管道交给 shell 自动安装。

`--json` 输出 CLI argv；`--tool-json` 输出 `{name: cronjob_manage, arguments: {...}}`，必须在目标 profile 的工具会话调用。跨接口配置用 `--plan`：CLI 暂停创建，读取实际返回 ID，绑定计划的 ID 占位符，再应用工具专有更新、读回所有字段，只有获授权才能恢复。计划不是执行器，任一步失败即停止。清空与模式切换参见 [编辑指南](edit-cron.md)。

## 仅在授权后安装和验证

1. 审阅场景同目录脚本，显式复制到目标 `$HERMES_HOME/scripts/aac/`。替换前查看目标已有内容，检查路径约束、依赖、文件权限与字节一致性。编译器不会安装文件。Python 依赖需要的绝对解释器应获用户批准；Shell 脚本需要 bash。参见 [脚本/monitor 安装](cron-template-guide.md)。
2. 将审阅后的暂停创建命令/请求执行一次，记录返回 ID，按准确 ID 列表/读回，确认停用且字段正确。不得用名称推断身份。
3. 如需测试，显式 `run` 该 ID，再查看持久运行历史和结果。脚本/目标应用访问单独验收，安静成功可能只是离线跳过。分发受理不是完成，手动运行也不证明自动调度。
4. 验收和授权后才恢复，读回启用状态、下次时间和调度器健康。不擅自启动/重启/安装 gateway 服务。暂停的测试任务仍可被操作员运行，不是执行安全隔离。
5. 报告 ID、目标范围、字段与证据、剩余前提，以及约定的测试任务清理方式。不承诺自动删除。
