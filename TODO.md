# TODO

> 说明：
> - 优先级：P0 = 紧急，P1 = 重要，P2 = 一般，P3 = 低优先级
> - 状态：待实现 / 已完成
> - **已完成**的事项请先同步到 `CHANGELOG.md`，再从此处删除，保持文件精简。

## 待实现

### P1：

- [ ] 补充非提醒类 OpenClaw 模板
  - 当前项目已有提醒类场景模板，以及巡检类 Docker 容器健康检查模板（`OpenClaw/template/checks/docker.yaml`）。
  - 仍需补充：
    - 【巡检】类其他模板（如服务健康检查、SSL 证书、磁盘空间）
    - 【开发】类模板（含状态机设计）
    - 【学习】类模板（含选题引擎、产出要求）
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

- [ ] `OpenClaw/template/checks/docker.yaml` 直接调用 `docker` 命令，要求 OpenClaw runner 所在环境具备 Docker CLI 及相应权限，需在文档中说明。

- [ ] `OpenClaw/template/template-cron.zh.yaml` 默认提示词仍为提醒类内容，未覆盖 `template` 的场景会生成问候语，需在文档中提醒贡献者注意。

- [ ] 缺少对 `OpenClaw/scripts/build-cron.py` 的单元测试，建议后续补充边界用例（空列表、空角色、session 拼接等）。

- [ ] `OpenClaw/scripts/build-cron.py` 的 `render_template` 多轮替换存在两个边界问题
  - 问题 1：若变量值本身包含 `{{KEY}}` 字符串，后续轮次可能误将其当作占位符再次替换。
  - 问题 2：5 轮替换后若仍有未解析占位符残留，函数直接返回，未抛出异常或告警，导致 `{{XXX}}` 进入最终 message。
  - 方向：方案一仅增加残留占位符检查；方案二改为正则一次性替换原占位符，避免扫描本轮新插入文本。

- [ ] `OpenClaw/scripts/build-cron.py` 的 `is_empty` 与 `parse_bool` 对数字/字符串 `0` 语义不一致
  - `is_empty(0)` 返回 False（会写入命令），`parse_bool("0")` 返回 False（会触发 false_flag）。
  - 边界场景如 `TIMEOUT_SECONDS=0` 可能产生不可预期的行为，需统一语义。

- [ ] `OpenClaw/template/checks/cron-check.yaml` 重试方案未提醒备份原任务配置
  - 当前建议通过 `openclaw cron rm <旧ID>` 后重新 `openclaw cron create ... --wake now` 来重试，会导致 job ID 改变。
  - 需提醒用户在删除前导出/备份原任务完整配置，避免丢失 schedule、delivery 等参数。

### P3：

- [ ] skill 文档中的项目自动定位脚本在 `$HOME` 较大时仍可能较慢，生产使用建议优先配置 `AAC_REPO` 环境变量。

- [ ] `OpenClaw/template/checks/docker.yaml` 中日志检查 `--tail` 行数、关键字等写死在 prompt 里，后续如需复用建议抽成变量。

- [ ] `OpenClaw/conf/flags.yaml` 中 `delivery.mode: none` 映射为 `--no-deliver` 基于 OpenClaw 2026.6.9 验证，旧版本可能不支持，需确认兼容性。

- [ ] `OpenClaw/skills/SKILL-GUIDE.md` 任务分类从 7 类缩减为 4 类后缺少迁移说明
  - 删除的【汇报】【整理】【系统】三类未说明如何映射到新的【提醒/巡检/开发/学习】。
  - 需在文档中增加一句映射建议，方便用户归类原有任务。

- [ ] `OpenClaw/workspace_example/SOUL.md.example` 目录拆分缺少迁移说明
  - 旧规范将 IDENTITY.md 引用资源放在 `assets/`，新规范拆分为 `avatars/`（OpenClaw 形象）和 `assets/`（用户资源）。
  - 需说明已按旧规范存放的头像如何迁移到 `avatars/`。

- [ ] `OpenClaw/template/checks/workspace-check.yaml` 未处理旧规范中头像在 `assets/` 的情况
  - 当前整理逻辑会把旧规范中放在 `assets/` 的头像当作用户资源处理，未识别为需要迁移到 `avatars/` 的文件。
  - 需补充旧规范到新规范的迁移规则。

- [ ] `OpenClaw/scripts/build-cron.py` 的 `build_command` 函数存在未使用的 `scene` 和 `template` 参数
  - 函数签名中 `scene` 与 `template` 未被使用，需确认是否删除或改为后续扩展预留。

## 已完成

- [x] 历史已完成事项已迁移至 `CHANGELOG.md`。

> 历史决策与已完成任务请查阅 `CHANGELOG.md`，本文件仅保留当前未办与刚办完的事项。
