# 模板与 Loop 指南

简体中文 | [English](../en_US/cron-template-guide.md)

模板分两层：`Hermes/{zh_CN,en_US}/cron-template/template-cron.yaml`（共享约束）与各场景 YAML（业务指令 + 变量）。场景只写自己关心的事，重复的约束一律留在父模板。

## 1. 文件结构

```
Hermes/zh_CN/cron-template/
├── template-cron.yaml              # 父模板：变量默认值、原生 job 默认值、Harness 与 Loop 段落
├── reminders/<name>/<name>.yaml    # 个性化提醒，Agent 模式
├── checks/<name>/<name>.yaml       # 只读巡检，写日报告
├── projects/<name>/<name>.yaml     # Loop 推进，默认 paused
├── learns/<name>/<name>.yaml       # 学习推进，写笔记
├── scripts/script-only/            # no_agent 纯脚本，附可执行脚本
└── monitors/change-monitor/        # monitor_script 变更监控，附脚本与监控源
```

场景文件固定三个顶层键：`templateRef`、`variables`、`job`。`templateRef` 必须是 `"../../template-cron.yaml"`，相对场景目录解析。

## 2. 变量与占位符

- 占位符写作 `{{UPPER_SNAKE_CASE}}`，不区分类型，渲染时按值替换；列表与字典按 JSON 渲染，布尔渲染为 `true` / `false`。
- 未定义的变量直接报错，**不会**渲染成空串或原样保留。
- 变量可嵌套：变量值里可以再引用其他变量，循环引用会被拒绝。
- 命令行的 `--set KEY=YAML_VALUE` 覆盖优先级最高，其次是场景 `variables`，最后是父模板默认值。
- `HERMES_HOME` 由编译器注入，不要在场景里定义它。

## 3. 条件块

父模板支持一层可嵌套的条件块：

```yaml
{{#if LOOP_MODE_ENABLED}}
这一段只在 Loop 场景渲染
{{#if LOOP_AUTO_PAUSE}}
这一段只在自暂停开启时渲染
{{/if}}
{{/if}}
```

条件按 YAML 真值判断：`false`、`""`、`0`、`[]` 都为假。未闭合的 `{{#if}}` 会直接报错。

## 4. Harness 段落

父模板的「统一约束」是所有场景共享的底线，改动它等于改所有任务的行为：

- 新会话前提：没有聊天上下文，不能提问，输出必须自足。
- 取证要求：只引用本次实际读到的内容，缺失就说明缺失。
- 授权边界：不提交/推送 Git，不启停容器，不改 Hermes 配置与 jobs.json，不装依赖。
- 输出即交付：最终回复就是本地投递内容，不再调用外部发送工具。
- 报告位置：`{{HERMES_HOME}}/docs/reports/<主题>/<YYYY-MM-DD>.md`，同日追加。
- 失败表述：无事输出 `[SILENT]`；失败时首行独占 `[CRON_FAILURE]`。

调整这些条款时，先跑 `python3 -m unittest discover -s tests/hermes`，再抽查一个场景的 `--preview`。

## 5. Loop 模式

Loop 场景用五个变量描述任务：`LOOP_TASK_TYPE`、`LOOP_GOAL`、`LOOP_MILESTONES`（至少三项）、`LOOP_PROJECT_DIR`、`LOOP_STATE_FILE`。父模板会追加这些规则：

1. 先读状态文件，缺失则创建。
2. 每次只推进一个可验证里程碑，完成后写回状态，再报告进度。
3. 完成以证据为准，不以「已尝试」为准。
4. 状态损坏时重建并记录状态丢失事件。
5. 全部完成后建议停止任务，不自行改调度。
6. 连续两轮无进展时报告阻塞。

`LOOP_AUTO_PAUSE` 与 `LOOP_JOB_ID` 是自暂停开关与绑定 ID，默认 `false` 与空串。绑定必须先暂停创建、读回真实 ID、再 `--edit` 同一 ID 注入，不允许按名称猜任务。

## 6. 脚本与 monitor

- 脚本必须位于目标 `$HERMES_HOME/scripts/` 内，符号链接的最终目标也要落在其中；编译器会拒绝 `..` 越界与指向外部的链接。
- 编译器只生成命令，**不复制文件**。审阅后按 `$HERMES_HOME/scripts/aac/<文件名>` 手动安装，并保持字节一致。
- `no_agent` 必须有 `script`，忽略提示词与 skills，stdout 直接投递；空 stdout 视为静默，非零退出视为失败。
- `monitor_script` 与 `monitor_url` 互斥，且都不能与 `no_agent` 同用；监控输出必须稳定，否则每 tick 都被判定为变化。
- 需要第三方依赖时用 `interpreter` 指向自建 venv 的 Python，别改系统解释器。

## 7. 新增一个场景

1. 在 `Hermes/{zh_CN,en_US}/cron-template/<类别>/<name>/` 建同名 YAML，中英各一份。
2. 顶层只写 `templateRef`、`variables`、`job`；变量名全大写，中英变量集合与占位符集合必须一致。
3. `job` 里至少显式写 `deliver: local` 与 `catch_up: false`；不需要跑的任务加 `paused: true` 与 `paused_reason`。
4. 跑 `build-cron.py <场景> --validate`，再跑 `--preview` 人工读一遍提示词。
5. 在 `tests/hermes/test_scenes.py` 的 `SCENES` 里登记，补该场景的验收断言，跑全量测试。

## 8. 不要做的事

| 做法 | 后果 |
|------|------|
| 在场景里重复父模板的统一约束 | 两处措辞漂移，改一处漏一处 |
| 用 `{{小写}}` 或 `{{ }}` 空占位 | 渲染不报错但输出错乱，测试会拦 |
| 只写中英其中一份 | 变量/占位符对不齐，`test_i18n_variable_placeholder_and_job_key_parity` 失败 |
| 把凭据、真实 ID、内部地址写进模板 | 模板会进公开仓库 |
| 让编译器顺手执行或安装 | 与「只输出」的契约冲突，审计无法复现 |
