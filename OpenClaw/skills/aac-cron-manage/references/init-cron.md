# 创建 Cron 任务流程

新建 AAC 规范化定时任务的完整步骤。

## 前置条件

- awesome-AGENT-configure 项目已克隆到本地
- `python3` 和 `openclaw` CLI 可用
- 已设置 `AAC_REPO` 环境变量（可选，但推荐）

## 步骤

- **1. 询问意图**：确认分类（提醒/巡检/项目/学习）、触发时间、任务内容、送达方式
- **2. 检查重复**：运行 `openclaw cron list`，发现同类任务建议改用迁移流程
- **3. 选择模板**：从目录化模板中选取
  - `OpenClaw/template/reminders/morning/morning.yaml`
  - `OpenClaw/template/checks/docker-check/docker-check.yaml`
  - 等等
- **4. 填充变量**：自动填充分类推荐值，询问用户确认或微调
  - `JOB_NAME` 强制 `【AAC-分类】任务名`
  - `SCHEDULE_EXPR`、`TIMEZONE`、`WINDOW_START`、`WINDOW_END`
  - `DEDUP_STATE_FILE`、`DEDUP_GRANULARITY`
- **5. 定位仓库**：
  ```bash
  export AAC_REPO=$(python3 -c "import os,sys; ...")
  ```
  回退顺序：环境变量 → 当前目录 → $HOME 下搜索
- **6. 生成 YAML**：写入 `$AAC_WORKSPACE/cron/init-<job-name>.yaml`
  - `templateRef` 替换为绝对路径 `<AAC_REPO>/OpenClaw/template/template-cron.zh.yaml`
- **7. 渲染命令**：
  ```bash
  python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/init-<job-name>.yaml"
  ```
- **8. 用户确认**：展示 YAML 路径、渲染命令、关键配置说明
- **9. 执行创建**：用户确认后执行 `openclaw cron create ...`
- **10. 验证**：`openclaw cron list` 确认任务存在

## 测试模式

```bash
python3 "$AAC_REPO/OpenClaw/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/init-<job-name>.yaml" \
  --test
```

效果：
- 任务名加 `【TEST】` 前缀
- 跳过时间窗口和去重
- 追加 `--delete-after-run`（执行后自动删除）

## 时间窗口与去重说明

- 不再使用 `TIME_WINDOW_ENABLED` / `DEDUP_ENABLED` / `WINDOW_OUT_ACTION` 变量
- 统一由 `triggers/trigger.js` 处理
- `build-cron.py` 自动注入 `WINDOW_START` / `WINDOW_END` / `DEDUP_STATE_FILE` / `DEDUP_GRANULARITY` 为环境变量

## 安全红线

- 发现重复任务时优先建议迁移，不创建重复
- 不擅自执行 push / delete 等危险操作
- 创建前必须获得用户明确确认
- 所有任务名必须带 `【AAC-分类】` 前缀
