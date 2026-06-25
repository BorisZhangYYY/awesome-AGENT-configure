# TODO

> 说明：
> - 优先级：P0 = 紧急，P1 = 重要，P2 = 一般，P3 = 低优先级
> - 状态：待实现 / 已完成
> - **已完成**的事项请先同步到 `CHANGELOG.md`，再从此处删除，保持文件精简。

## 待实现

### P1：

- [ ] 补充非提醒类 OpenClaw 模板
  - 当前项目已有提醒类场景模板，以及巡检类 Docker 容器健康检查模板（`OpenClaw/template/check/docker.yaml`）。
  - 仍需补充：
    - 【巡检】类其他模板（如服务健康检查、SSL 证书、磁盘空间）
    - 【汇报】类模板（如日报、数据汇总）
    - 【开发】类模板（含状态机设计）
    - 【学习】类模板（含选题引擎、产出要求）
    - 【整理】类模板（含原子性步骤、幂等执行）
    - 【系统】类模板（含审计、Token 监控）
  - 验收标准：每类至少提供一个可直接运行的场景 YAML，并在 `SKILL-GUIDE.md` 中说明使用方式。

- [ ] 验证 OpenClaw skill 实际使用效果
  - 在真实 OpenClaw 环境中测试 `init-cron` skill
  - 在真实 OpenClaw 环境中测试 `migrate-cron` skill
  - 在真实 OpenClaw 环境中测试 `edit-cron` skill
  - 根据测试结果调整 skill 的 prompt 和流程
  - 验收标准：三个 skill 均能在真实环境中完成至少一次端到端验证，并形成测试记录。

### P2：

- [ ] 补充 Hermes 框架模板
  - 调研 Hermes 官方 cron 机制
  - 设计 Hermes 通用模板和场景示例
  - 验收标准：提供 Hermes 通用模板文件与至少一个场景示例。

- [ ] 补充 Claude Code 框架模板
  - 调研 Claude Code 的 cron / scheduled tasks 能力
  - 设计 Claude Code 通用模板和场景示例
  - 验收标准：提供 Claude Code 通用模板文件与至少一个场景示例。

- [ ] `OpenClaw/scripts/build-cron.py` 的 `add_flag` 对 list/dict 统一 JSON 序列化，未来若 `COMMAND_ENV` 等字段需要非 JSON 格式，需单独处理。

- [ ] `OpenClaw/scripts/build-cron.py` 新增场景级 `template` 覆盖能力，但 `SKILL-GUIDE.md` 和 `template-cron.zh.yaml` 注释中尚未说明该用法。

- [ ] `OpenClaw/template/check/docker.yaml` 直接调用 `docker` 命令，要求 OpenClaw runner 所在环境具备 Docker CLI 及相应权限，需在文档中说明。

- [ ] `OpenClaw/template/template-cron.zh.yaml` 默认提示词仍为提醒类内容，未覆盖 `template` 的场景会生成问候语，需在文档中提醒贡献者注意。

- [ ] 缺少对 `OpenClaw/scripts/build-cron.py` 的单元测试，建议后续补充边界用例（空列表、空角色、session 拼接等）。

### P3：

- [ ] skill 文档中的项目自动定位脚本在 `$HOME` 较大时仍可能较慢，生产使用建议优先配置 `AAC_REPO` 环境变量。

- [ ] `OpenClaw/template/check/docker.yaml` 中日志检查时间 `--since 10m`、关键字等写死在 prompt 里，后续如需复用建议抽成变量。

- [ ] `OpenClaw/conf/flags.yaml` 中 `delivery.mode: none` 映射为 `--no-deliver` 基于 OpenClaw 2026.6.9 验证，旧版本可能不支持，需确认兼容性。

## 已完成

- [x] 历史已完成事项已迁移至 `CHANGELOG.md`。

> 历史决策与已完成任务请查阅 `CHANGELOG.md`，本文件仅保留当前未办与刚办完的事项。
