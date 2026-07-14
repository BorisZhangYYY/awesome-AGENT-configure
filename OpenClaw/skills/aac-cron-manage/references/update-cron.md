# 同步 Cron 任务流程

模板升级后，将已有 AAC 任务同步到最新模板，保留核心配置和 job ID。

## 与编辑的区别

- `edit-cron`：修改单个任务的配置（时间、内容等）
- `update-cron`：模板本身升级后，批量复用新模板，任务配置不变

## 前提条件

- 任务名带 `【AAC-` 前缀
- 存在对应 YAML 文件于 `$AAC_WORKSPACE/cron/`

## 步骤

- **1. 列出任务**：`openclaw cron list`
- **2. 筛选 AAC 任务**：按 `【AAC-` 前缀筛选，展示列表
- **3. 用户选择**：指定任务名或 ID，或说"全部"
- **4. 定位仓库**：同 `init-cron` 流程
- **5. 查找 YAML**：在 `$AAC_WORKSPACE/cron/` 下搜索
- **6. 重新渲染**：
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<job-name>.yaml" \
    --preview
  ```
- **7. 获取 ID**：`openclaw cron list --format json`，匹配 `name`
- **8. 选择更新方式**：
  - Agent 模式：优先 `openclaw cron edit <job-id>`，保留 ID
  - 命令模式：只能 `rm` + `create`，ID 会变
- **9. 生成计划**：
  ```markdown
  | 任务名 | 方式 | 保留 ID | 备注 |
  | xxx | edit | ✅ | Agent 模式 |
  | yyy | rm+create | ❌ | 命令模式 |
  ```
- **10. 用户确认**：展示计划，询问是否执行
- **11. 执行更新**：逐个任务执行
- **12. 验证**：每个任务执行后 `openclaw cron list` 确认状态
- **13. 汇报结果**：
  - 成功同步数量
  - 保留原 ID 数量
  - ID 改变数量
  - 跳过数量及原因

## 注意事项

- 同步后建议观察一轮执行，确认行为符合预期
- Loop 模式任务同步时会复用状态文件路径，历史状态不丢失
- 避免在高峰时段批量更新
- 模板升级可能改变 message 语义，需留意
