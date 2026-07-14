# TODO

> 说明：
> - 优先级：P0 = 紧急，P1 = 重要，P2 = 一般，P3 = 低优先级
> - 状态：待实现 / 已完成
> - **已完成**的事项请先同步到 `CHANGELOG.md`，再从此处删除，保持文件精简。

## 待实现

### P1：

- [x] **Cron Trigger 优化**：基于 OpenClaw 2026.7.1 新特性，将 AAC 模板从「固定轮询」升级为「条件触发」。详见 `plans/cron-trigger-optimization.md`。
  - ✅ Phase 1：template-cron.zh.yaml 新增 trigger 配置区块 + build-cron.py 支持
  - ✅ Phase 2：内置脚本库（trigger.js 统一时间窗口+去重，场景 JS 自动拼接）
  - ✅ Phase 3：场景模板目录化（docker-check / workspace-check 含专属 JS）
  - ✅ Phase 4：template-cron.zh.yaml 移除 Prompt 层时间窗口/去重逻辑，全面迁移至 trigger 脚本库
  - ✅ Phase 5：技能文档重构（4 个独立 skill 合并为 aac-cron-manage，SKILL-GUIDE.md 收归 references）

### P2：

- [ ] **模板链式继承**：场景文件支持多级 `templateRef`（如 `siyuan-cron-check → cron-check → template-cron.zh.yaml`），使定制版巡检在 AAC 升级标准 cron-check 时自动继承优化。当前只能全量复制 cron-check.yaml，升级时需手动合并。实现需考虑：多级 templateRef 链式解析、变量 merge 优先级（场景 > 中间模板 > 父模板 > defaults）、循环引用检测。

### P3：

- [ ] 缺少对 `OpenClaw/scripts/build-cron.py` 的单元测试，建议后续补充边界用例（空列表、空角色、session 拼接、嵌套变量等）。

## 已完成

- [x] 历史已完成事项已迁移至 `CHANGELOG.md`。

> 历史决策与已完成任务请查阅 `CHANGELOG.md`，本文件仅保留当前未办与刚办完的事项。
