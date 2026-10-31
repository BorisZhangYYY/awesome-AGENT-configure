# OpenClaw 模板

> OpenClaw 的工作区、定时任务与上下文注入模板，是 Harness / Loop 机制的主要落点。

简体中文 | [English](README.en.md)

## 模板类型

| 类型 | 目录 | 用途 |
|------|------|------|
| Agent 身份模板 | `zh_CN/workspace_example/`（或 `en_US/`） | `SOUL.md`、`AGENTS.md`、`USER.md`、`MEMORY.md`、`IDENTITY.md`、`HEARTBEAT.md` |
| 定时任务模板 | `zh_CN/cron-template/`（或 `en_US/`） | 提醒、巡检、项目、学习四类场景 + 统一父模板 `template-cron.yaml` |
| 上下文注入模板 | `zh_CN/hook-template/`（或 `en_US/`） | 监听 `agent:bootstrap`，在会话启动时注入 `context.md` |
| 技能工具 | `skills/aac-cron-manage/` | `build-cron.py`、`trigger.js` 与使用文档（共享，不按语言拆分） |

## 定时任务模板

场景按类别放在 `cron-template/` 下：

| 类别 | 场景 |
|------|------|
| 提醒 | 早安、午安、晚安、自定义提醒 |
| 巡检 | Cron 任务健康、Docker 容器、工作区整理、自定义巡检 |
| 项目 | 功能开发、维护会话、自定义项目（Loop 模式） |
| 学习 | 自定义学习 |

所有场景通过 `templateRef` 指向父模板 `template-cron.yaml`。父模板提供：

- **Harness**：时间窗口、去重、状态文件、投递与触发配置。
- **Loop**：目标、里程碑、状态续传、到达目标后自动停用。

生成 cron 命令：

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/zh_CN/cron-template/reminders/morning/morning.yaml --preview
```

英文模板将路径中的 `zh_CN` 换成 `en_US`。任务名固定使用 `【AAC-` 前缀；英文模板的分类为 `Reminder` / `Check` / `Project` / `Learn`。

## 工作区模板

将 `zh_CN/workspace_example/`（或 `en_US/`）中的文件复制到 OpenClaw workspace，按需修改：

- `SOUL.md`：人格与工作区管理规范
- `AGENTS.md`：行为准则与 `## Tools` 本地环境笔记
- `USER.md` / `MEMORY.md`：用户画像与长期记忆骨架
- `IDENTITY.md`：外在身份
- `HEARTBEAT.md`：心跳检查清单

## 上下文注入模板

将 `zh_CN/hook-template/`（或 `en_US/`）复制到 OpenClaw hooks 目录，编辑 `context.md` 填写角色与规则：

- `HOOK.md`：hook pack 声明与说明
- `context.md`：每次会话启动时注入的内容
- `handler.js`：读取并注入上下文的实现

## 相关文档

- [aac-cron-manage SKILL（中文）](skills/aac-cron-manage/SKILL.zh_CN.md)
- [模板参数指南](skills/aac-cron-manage/references/zh_CN/cron-template-guide.md)
- [Trigger 沙箱限制](skills/aac-cron-manage/references/zh_CN/trigger-sandbox.md)
