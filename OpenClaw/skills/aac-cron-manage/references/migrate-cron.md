# 迁移 Cron 任务流程

将已有但配置不规范的 OpenClaw 定时任务改造为 AAC 规范。

## 何时触发

- 用户已有手动创建的 cron 任务
- `init-cron` 发现同名/同主题任务时切换
- 用户说"帮我看看现有任务有没有问题"

## 步骤

- **1. 列出任务**：`openclaw cron list`
- **2. 选择任务**：用户指定，或说"全部"
- **3. 获取详情**：对每个任务运行 `openclaw cron info --id <job-id>`
- **4. 分析分类**：根据名称/描述判断
  - 提醒 → 定时问候、固定格式、必须送达
  - 巡检 → 检查状态、正常静默、异常告警
  - 开发 → 推进项目、需要状态跟踪
  - 学习 → 技术调研、知识积累
- **5. 诊断问题**：
  - `thinking` 是否匹配复杂度
  - `session` 是否为 `isolated`
  - `delivery` 是否合理
  - 是否缺少时间窗口 / 去重
  - `lightContext` 是否合适
  - 提醒类是否未开启 `exact`
- **6. 生成报告**：
  ```markdown
  ## 任务：xxx
  - 分类：提醒类
  - 问题：
    1. thinking 未关闭，浪费 Token
    2. 缺少时间窗口
    3. delivery 应为 announce
  - 推荐：
    - JOB_NAME: 【AAC-提醒】早安
    - SESSION_TARGET: isolated
    - DELIVERY_MODE: announce
  ```
- **7. 用户确认**：展示报告，询问是否改造
- **8. 定位仓库**：同 `init-cron` 流程
- **9. 生成 YAML**：写入 `$AAC_WORKSPACE/cron/migrated-<job-name>.yaml`
- **10. 渲染命令**：`build-cron.py --preview`
- **11. 用户确认**：展示命令，询问是否创建
- **12. 执行创建**：用户确认后执行
- **13. 验证**：`openclaw cron list`

## 命名规范

迁移后统一为 `【AAC-分类】任务名`。原 `早安` → `【AAC-提醒】早安`。旧任务不自动删除。

## 安全红线

- 不默认改造全部，只处理用户选定的
- 不删除旧任务，只能建议用户手动删除
- 复杂任务（开发/学习）分阶段改造
- 创建前必须获得用户确认
