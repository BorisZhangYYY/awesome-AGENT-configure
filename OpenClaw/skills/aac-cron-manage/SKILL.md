---
name: aac-cron-manage
description: "在 OpenClaw 中创建、编辑、迁移或删除 AAC 规范化定时任务时使用。"
---

# AAC Cron 管理器

管理 awesome-AGENT-configure（AAC）项目规范化的 OpenClaw 定时任务。

## 何时使用

- 用户说"创建 cron"、"添加定时任务"、"新建提醒"
- 用户说"编辑 cron"、"修改定时任务"
- 用户说"迁移 cron"、"改造定时任务"
- 用户说"删除 cron"、"移除定时任务"

## 核心规则

- 只管理按 AAC 规范创建的任务，名称带 `【AAC-` 前缀。
- 所有场景 YAML 保存在运行时目录：`~/.openclaw/workspace/awesome-AGENT-configure/cron/`。
- cron 的渲染通过 `aac-cron-manage/scripts/build-cron.py` 完成。
- 创建/编辑/迁移前先向用户展示配置，获得确认后再执行。

## 命令对应

| 用户意图 | 执行命令 |
|----------|----------|
| 创建 cron | `OpenClaw/scripts/aac-manage.sh install-cron OpenClaw/template/<category>/<scene>.yaml` |
| 编辑 cron | 修改 `$AAC_WORKSPACE/cron/<job-name>.yaml`，然后 `OpenClaw/scripts/aac-manage.sh install-cron <scene-yaml>`（方式见下方说明） |
| 迁移 cron | 获取现有任务信息，生成 AAC 规范 YAML，再 `install-cron` |
| 删除 cron | `OpenClaw/scripts/aac-manage.sh remove-cron "【AAC-分类】任务名"` |
| 列出可安装场景 | `OpenClaw/scripts/aac-manage.sh list-crons` |
| 列出已安装 cron | `OpenClaw/scripts/aac-manage.sh list-installed-crons` |
| 安装所有 cron | `OpenClaw/scripts/aac-manage.sh install-all-crons` |
| 删除所有 AAC cron | `OpenClaw/scripts/aac-manage.sh remove-all-crons` |

## 创建 cron 流程

1. 询问用户任务分类、触发时间、内容、送达方式。
2. 检查是否已有相似任务，有则建议迁移。
3. 选择对应模板，填充变量，任务名强制 `【AAC-分类】任务名`。
4. 将 YAML 写入 `$AAC_WORKSPACE/cron/init-<job-name>.yaml`。
5. 修正 `templateRef` 为 AAC 项目模板的绝对路径。
6. 调用 `build-cron.py` 渲染并执行 `openclaw cron create`。

## 编辑 cron 流程

1. 列出当前 cron 任务，优先标识 `【AAC-` 前缀任务。
2. 读取对应场景 YAML，展示当前配置。
3. 询问用户修改项，更新 YAML。
4. 重新渲染命令：
   - Agent 模式字段优先用 `openclaw cron edit <job-id>`（保留 ID）。
   - 命令模式或不支持字段，先 `rm` 再 `create`（ID 改变）。
5. 展示变更差异，确认后执行。

## 迁移 cron 流程

1. 列出任务，让用户选择要迁移的。
2. 对每个任务运行 `openclaw cron get --id <job-id>`。
3. 判断分类，对照 AAC 规范生成诊断报告。
4. 用户确认后，生成 `migrated-<job-name>.yaml`。
5. 调用 `install-cron` 创建新任务，旧任务不自动删除。

## 删除 cron 流程

1. 确认要删除的任务名称或 ID。
2. 调用 `remove-cron`。
3. 汇报删除结果。

<!-- AAC_ORIGIN: skill=aac-cron-manage | generated=2026-07-05T00:00:00Z | category=cron -->
