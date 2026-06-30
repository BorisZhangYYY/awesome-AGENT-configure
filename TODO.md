# TODO

> 说明：
> - 优先级：P0 = 紧急，P1 = 重要，P2 = 一般，P3 = 低优先级
> - 状态：待实现 / 已完成
> - **已完成**的事项请先同步到 `CHANGELOG.md`，再从此处删除，保持文件精简。

## 待实现

### P1：

### P2：

- [ ] **模板链式继承**：场景文件支持多级 `templateRef`（如 `siyuan-cron-check → cron-check → template-cron.zh.yaml`），使定制版巡检在 AAC 升级标准 cron-check 时自动继承优化。当前只能全量复制 cron-check.yaml，升级时需手动合并。实现需考虑：多级 templateRef 链式解析、变量 merge 优先级（场景 > 中间模板 > 父模板 > defaults）、循环引用检测。

### P3：

- [ ] 缺少对 `OpenClaw/scripts/build-cron.py` 的单元测试，建议后续补充边界用例（空列表、空角色、session 拼接、嵌套变量等）。

## 已完成

- [x] 历史已完成事项已迁移至 `CHANGELOG.md`。

> 历史决策与已完成任务请查阅 `CHANGELOG.md`，本文件仅保留当前未办与刚办完的事项。
