# 命令与验收

简体中文 | [English](../en_US/commands.md)

所有命令都在目标 `HERMES_HOME` 或 `hermes -p PROFILE` 作用域内执行。`hermes cron` 子命令没有 `--json`，需要结构化数据时读 `runs` / `list` 的文本输出，不要臆造参数。

## 1. 只读盘点

```bash
hermes cron list --all          # 含停用与已完成任务
hermes cron status              # 调度器是否在跑、下次 tick
hermes cron runs --limit 20     # 最近的运行记录
hermes cron runs <JOB_ID> --limit 5
hermes cron doctor              # 常见健康问题
hermes cron incidents           # 失败事件，可单独确认
```

- 名称不唯一，**ID 才唯一**；任何 `pause/resume/run/edit/remove` 都要用读回来的真实 ID。
- `list` 里看不到任务时先确认作用域：默认 home、显式 `HERMES_HOME`、还是某个 profile。

## 2. 编译器输出

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/zh_CN/cron-template/reminders/morning/morning.yaml --validate
python3 .../build-cron.py <场景> --preview          # 渲染后的 job 与 argv
python3 .../build-cron.py <场景> --json             # 只要 argv
python3 .../build-cron.py <场景> --tool-json        # cronjob_manage 请求
python3 .../build-cron.py <场景> --plan             # 跨通道有序计划
python3 .../build-cron.py <场景> --test             # 暂停的 in 1m 一次性任务
python3 .../build-cron.py --catalog                 # 列出仓库内全部场景
python3 .../build-cron.py --check-cli               # 打印上线前该跑的只读检查
```

`--home PATH` 与 `--profile PROFILE` 二选一；`--set KEY=YAML_VALUE` 可重复，用于临时替换变量。所有模式都只打印，不执行。

## 3. 创建

```bash
# 先看一遍
python3 .../build-cron.py <场景> --preview
# 再执行（人工审阅后）
env HERMES_HOME=$HOME/.hermes hermes cron create "0 8 * * *" "<渲染后的提示词>" \
  --name "【AAC-提醒】早安" --deliver local --catch-up off
```

- 需要先停用、之后再恢复的，创建时加 `--paused --paused-reason "..."`。
- 创建后立刻 `hermes cron list --all` 读回 ID、名称、调度、投递与暂停状态。

## 4. 编辑、暂停、恢复、删除

```bash
hermes cron edit <JOB_ID> --schedule "0 9 * * *" --prompt "<新提示词>"
hermes cron pause <JOB_ID>
hermes cron resume <JOB_ID>
hermes cron run <JOB_ID>            # 下一次 tick 触发，不等于立即执行完成
hermes cron cancel <JOB_ID>         # 停止正在跑的运行，不动调度
hermes cron remove <JOB_ID>
```

- 更新一律用 `edit` 保留 ID，不删除重建；ID 变了会丢掉运行历史与 `context_from` 引用。
- 清空字段：`--script ""`、`--workdir ""`、`--monitor-url ""`、`--clear-skills`；列表用 `[]`。
- `pause` / `resume` 是生命周期命令，不是 `edit --paused` 的替代。

## 5. 验收清单

1. **同一 ID**：编辑前后 ID 一致，`list --all` 能查到。
2. **字段到位**：调度、时区、投递与失败投递、补跑、模式、脚本/monitor、工具限制、暂停状态逐项读回。
3. **脚本一致**：目标 `$HERMES_HOME/scripts/aac/` 内文件与仓库副本字节一致。
4. **运行记录**：`runs <JOB_ID>` 有本次记录，退出码与 stdout/stderr 符合预期。
5. **调度健康**：`status` 正常，`doctor` 无新增问题。
6. **真实触发**：需要时等一个真实 tick，确认自动调度而非仅手动 `run`。

以上任一项缺失，都只能报「部分完成」，不能说「已上线」。

## 6. 常见误判

| 现象 | 实际含义 |
|------|----------|
| `list` 里有任务但从不执行 | 调度器没在跑，或任务处于暂停 |
| `run` 成功 | 只是排入了下一次 tick，不代表已经跑完 |
| 脚本手动执行正常 | 不证明定时路径可用：环境变量、cwd、解释器都可能不同 |
| `[SILENT]` | 场景判定无事可报，不是失败 |
| `[CRON_FAILURE]` 首行 | 任务执行失败，后面是阻塞原因 |
| 报告文件存在 | 只证明写盘成功，不证明结论正确 |
