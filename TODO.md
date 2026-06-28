# TODO

> 说明：
> - 优先级：P0 = 紧急，P1 = 重要，P2 = 一般，P3 = 低优先级
> - 状态：待实现 / 已完成
> - **已完成**的事项请先同步到 `CHANGELOG.md`，再从此处删除，保持文件精简。

## 待实现

### P1：

### P2：

- [ ] `OpenClaw/scripts/build-cron.py` 新增场景级 `template` 覆盖能力，但 `SKILL-GUIDE.md` 和 `template-cron.zh.yaml` 注释中尚未说明该用法。

- [ ] `OpenClaw/template/checks/cron-check.yaml` 重试方案未提醒备份原任务配置
  - 当前建议通过 `openclaw cron rm <旧ID>` 后重新 `openclaw cron create ... --wake now` 来重试，会导致 job ID 改变。
  - 需提醒用户在删除前导出/备份原任务完整配置，避免丢失 schedule、delivery 等参数。

### P3：

- [ ] 缺少对 `OpenClaw/scripts/build-cron.py` 的单元测试，建议后续补充边界用例（空列表、空角色、session 拼接、嵌套变量等）。

- [ ] `OpenClaw/scripts/build-cron.py` 的 `build_command` 函数存在未使用的 `scene` 和 `template` 参数
  - 函数签名中 `scene` 与 `template` 未被使用，需确认是否删除或改为后续扩展预留。

## 已完成

- [x] 历史已完成事项已迁移至 `CHANGELOG.md`。

> 历史决策与已完成任务请查阅 `CHANGELOG.md`，本文件仅保留当前未办与刚办完的事项。
