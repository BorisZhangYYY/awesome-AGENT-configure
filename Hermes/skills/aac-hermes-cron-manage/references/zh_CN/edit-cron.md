# 编辑任务，保留身份

简体中文 | [English](../en_US/edit-cron.md)

## 写前读取

使用 `terminal`，始终带正确的 `hermes -p PROFILE cron ...` 前缀或显式 `HERMES_HOME`，读写不能跨 profile。先列表（`list --all` 或公共工具 `action: list`），选完整不可变 ID，记录原字段和启用状态。原生 CLI 可能支持名称解析，但本流程不依赖名称或 ID 前缀。CLI 显示不全时，可用公共工具列表补充读取；不要虚构 `list --json` 或 `get` 命令。

经授权后，在高风险模式/脚本/提示词迁移前暂停。暂停停止未来调度，不代替 `cancel` 停止当前运行。记录原状态，避免把本来暂停的任务恢复。除明确要求外，保留 ID、投递、补跑、skills、权限和模型策略。

## 编译相同 ID 的更新

在仓库根目录通过 `terminal` 执行：

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/zh_CN/cron-template/reminders/morning/morning.yaml \
  --edit JOB_ID --preview
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/zh_CN/cron-template/reminders/morning/morning.yaml \
  --edit JOB_ID --json
```

`JOB_ID` 必须替换为已验证的完整 ID。`--edit` 输出原生 `edit` 或工具 `action: update`，不会删建，并把 `LOOP_JOB_ID` 绑定为自身目标 ID。检查全部字段差异：完整场景可能覆盖的不止你想改的一项。单字段修复可直接使用稀疏原生 edit。

原生 `paused`、`paused_reason` 仅创建时可用，不是 edit 参数。普通编辑应移除场景级创建指令；编译器继承的 null 占位表示省略。使用明确的生命周期命令，或经审阅且包含生命周期步骤的 `--plan`，不要假定存在 `edit --paused`。`update` 请求不得携带创建专用字段。

## 省略、清空与模式切换

| 意图 | 原生 CLI / 公共工具 |
|---|---|
| 保持不变 | 省略；编译器 `null` 不输出 |
| 清空可选字符串 | 对支持字段传 `''`，如 script、monitor、workdir、timezone、失败投递；CLI 专用固定项也有文档化空串清空行为 |
| 替换/移除技能 | 重复 `--skill`、`--add-skill`、`--remove-skill` 或 `--clear-skills`；工具 `skills: []` 清空 |
| 删除上游上下文 | 工具 `context_from: []`；`continuity: false` 仅移除自身上下文 |
| 限制为无工具 | 工具 `enabled_toolsets: []` 是零工具，不是恢复默认 |
| 恢复 Agent 推理 | `--agent` / `no_agent: false` |
| 关闭连续输出上下文 | `--no-continuity` / `continuity: false` |
| 关闭可续聊投递 | 工具 `attach_to_session: false` |
| 释放模型锁定 | `--unpin` / `pinned: false`，仅用户明确要求时 |

null 或省略不会清除已有运行值，特别是模板默认 null 不能撤销原脚本、monitor、workdir 或模型固定。公共工具 `monitor: ''` 清空两个来源；CLI 切换脚本/URL 时必须显式清空旧来源。

下面为原生 CLI 模式切换的审阅示例，不代表获准执行：

```bash
hermes cron edit JOB_ID --agent --script '' --monitor-script aac/change-monitor.py
hermes cron edit JOB_ID --monitor-script '' --monitor-url '' --script aac/script-only.py --no-agent
hermes cron edit JOB_ID --monitor-script '' --monitor-url 'https://example.com/status'
```

切到 monitor 时必须显式关闭 `no_agent`；切到纯脚本时清空所有 monitor 来源。校验合并后的有效任务，不只是本次请求。`no_agent` 与 monitor 不能并存。

## 混合接口与读回

CLI 拒绝任何非 null 工具专有值，包括 `false`、`[]`；公共工具拒绝任何非 null CLI 专有值，包括 `''`。混合更新用 `--plan`。所有步骤必须指向同一不可变 ID 和范围，非明确要求不改变暂停状态，失败即停，恢复前读回结果。计划只描述操作，由操作员分别调用。

获授权编辑后按准确 ID 读回并比较所有请求字段、ID、启用状态和下次运行。按需运行获授权金丝雀并检查历史。任务仍阻塞时不能宣称修复，也不能因编译成功就恢复。参见 [命令与验收](commands.md)。
