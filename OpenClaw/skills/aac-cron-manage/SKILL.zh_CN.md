---
name: aac-cron-manage
description: "Manage AAC-normalized OpenClaw cron tasks: create, edit, migrate, update, or remove."
---

# AAC Cron Manager

[English](SKILL.md) | 简体中文

管理 awesome-AGENT-configure（AAC）规范化的 cron 任务。只处理名称带 `【AAC-` 前缀的任务。

## 何时使用

- 用户说「创建 cron」「添加提醒」「新建定时任务」
- 用户说「编辑 cron」「修改定时任务」
- 用户说「迁移 cron」「升级定时任务」
- 用户说「删除 cron」「移除定时任务」
- 用户说「同步 cron 到最新模板」
- 用户说「测试 cron」（使用 `--test` 参数）

## 硬性规则

- 只管理名称带 `【AAC-` 前缀的任务。
- 所有场景 YAML 位于 `~/.openclaw/workspace/awesome-AGENT-configure/cron/<task-name>/<task-name>.yaml`。
- 渲染统一走 `OpenClaw/skills/aac-cron-manage/scripts/build-cron.py`。
- 模板按目录组织：`{zh_CN|en_US}/cron-template/checks/docker-check/docker-check.yaml`（场景专属 .js 暂不可用，见模板注释）。
- Trigger 逻辑统一在 `OpenClaw/skills/aac-cron-manage/scripts/trigger.js`（时间窗口）。场景 JS 由 `build-cron.py` 自动拼接。
- Trigger 脚本运行在 QuickJS-WASI 沙箱：仅允许 ES2022 纯 JS —— 禁用 `Intl`、`require`/`import`、`process`、Node 模块。修改任何 trigger 代码前先阅读 `references/zh_CN/trigger-sandbox.md`。
- 执行前必须向用户展示配置并获得确认。
- `--test` 模式生成带 `【TEST】` 前缀的一次性任务，跳过时间窗口与去重检查，执行后自动删除。

## 流程选择

- **创建**：见 `references/zh_CN/init-cron.md`
- **编辑**：见 `references/zh_CN/edit-cron.md`
- **迁移**：见 `references/zh_CN/migrate-cron.md`
- **同步到最新模板**：见 `references/zh_CN/update-cron.md`
- **删除**：`openclaw cron rm <job-id>`
- **列出已安装任务**：`openclaw cron list`
- **列出可用模板**：`ls OpenClaw/{zh_CN,en_US}/cron-template/*/*/`（在 AAC 仓库根目录执行）

## 常用命令

- 渲染场景 YAML（普通）：
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml"
  ```
- 将场景 YAML 渲染为 argv 数组：
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml" --json
  ```
- 将场景 YAML 渲染为 **edit** 命令（保留 job id，不新建任务）：
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml" --edit <job-id> --json
  ```
- 渲染场景 YAML（测试模式）：
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml" \
    --test
  ```
- 定位 AAC 仓库：
  ```bash
  export AAC_REPO=$(python3 -c "import os,sys; ...")
  ```
  回退顺序：`AAC_REPO` 环境变量 → 当前目录 → `$HOME` 下搜索。

## ⛔ Edit 时必须用 `--edit` 或 `--json`

`build-cron.py` 的默认输出是**反斜杠续行**格式。用字符串替换拼 `openclaw cron edit` 会静默失败，
实际执行成 `openclaw cron create` → 产生重复 job，还可能误删带改动的副本（2026-10-19/21 实测事故）。

**首选**：`build-cron.py <yaml> --edit <job-id> --json` —— 直接生成 `openclaw cron edit <job-id> ...`，
保留 job id、原地更新内容、不新建 job（2026-10-21 实测通过）。

**次选**：加 `--json` 拿 argv 数组，只传 `--message` 做最小编辑。

两者都不可省略：**edit 后必须核对 live job 的 payload 真的变了**。

## 遗留变量清理

新 YAML 中不要使用以下变量 —— 它们已由 `OpenClaw/skills/aac-cron-manage/scripts/trigger.js` 处理：
- `TIME_WINDOW_ENABLED`
- `DEDUP_ENABLED`
- `WINDOW_OUT_ACTION`
- `TRIGGER_LIBRARY_PATH`

请直接设置 `WINDOW_START`、`WINDOW_END`、`DEDUP_STATE_FILE`、`DEDUP_GRANULARITY`。`build-cron.py` 会将它们作为环境变量注入 trigger 脚本。
