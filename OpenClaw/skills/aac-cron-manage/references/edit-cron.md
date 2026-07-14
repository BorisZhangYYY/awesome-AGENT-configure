# 编辑 Cron 任务流程

修改已按 AAC 规范创建的定时任务。

## 前提条件

- 任务名带 `【AAC-` 前缀
- 存在对应场景 YAML 文件于 `$AAC_WORKSPACE/cron/<job-name>.yaml`
- 无 YAML 时建议改用迁移流程

## 步骤

- **1. 列出任务**：`openclaw cron list`，优先标识 `【AAC-` 前缀
- **2. 选择任务**：用户指定任务名或 ID
- **3. 查找 YAML**：在 `$AAC_WORKSPACE/cron/` 下搜索
- **4. 展示配置**：读取 YAML 并展示关键字段（名称、schedule、窗口、delivery、thinking、tools）
- **5. 询问修改**：常见修改项：
  - 触发时间 → `SCHEDULE_EXPR`
  - 时间窗口 → `WINDOW_START` / `WINDOW_END`
  - 内容 → `SCENE_NAME` / `EMOJI` / `REMARK`
  - 送达方式 → `DELIVERY_MODE`
  - 模型能力 → `THINKING` / `MODEL` / `TOOLS`
  - 超时 → `TIMEOUT_SECONDS`
- **6. 修改 YAML**：更新对应变量值
- **7. 重新渲染**：
  ```bash
  python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<job-name>.yaml"
  ```
- **8. 选择更新方式**：
  - Agent 模式（用 `--message`）：优先 `openclaw cron edit <job-id>`，保留 ID
  - 命令模式（用 `--command`）：不支持 `edit`，只能 `rm` + `create`，ID 会变
- **9. 用户确认**：展示修改前后差异、更新方式、对应命令
- **10. 执行更新**：
  - 方式 A：`openclaw cron edit <job-id> --message "..." --cron "..." ...`
  - 方式 B：`openclaw cron rm <job-id>` + `openclaw cron create ...`
- **11. 验证**：`openclaw cron list` 确认状态

## 安全红线

- 删除旧任务前必须确认（破坏性操作）
- 保留修改后的 YAML 文件于 `$AAC_WORKSPACE/cron/`
- 修改后名称仍保持 AAC 格式
- 优先使用 `edit` 保留 job ID，避免状态丢失
