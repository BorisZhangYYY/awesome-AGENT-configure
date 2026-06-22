# TODO

## 待实现

### #1 补充非提醒类 OpenClaw 模板
当前项目已有提醒类场景模板，以及巡检类 Docker 容器健康检查模板（`OpenClaw/template/check/docker.yaml`）。仍需补充：
- 【巡检】类其他模板（如服务健康检查、SSL 证书、磁盘空间）
- 【汇报】类模板（如日报、数据汇总）
- 【开发】类模板（含状态机设计）
- 【学习】类模板（含选题引擎、产出要求）
- 【整理】类模板（含原子性步骤、幂等执行）
- 【系统】类模板（含审计、Token 监控）

### #2 验证 OpenClaw skill 实际使用效果
- 在真实 OpenClaw 环境中测试 `init-cron` skill
- 在真实 OpenClaw 环境中测试 `migrate-cron` skill
- 在真实 OpenClaw 环境中测试 `edit-cron` skill
- 根据测试结果调整 skill 的 prompt 和流程

### #3 补充 Hermes 框架模板
- 调研 Hermes 官方 cron 机制
- 设计 Hermes 通用模板和场景示例

### #4 补充 Claude Code 框架模板
- 调研 Claude Code 的 cron / scheduled tasks 能力
- 设计 Claude Code 通用模板和场景示例

### #5 完善状态文件 JSON 化方案（已决策：保持纯文本）

当前去重状态文件为纯文本日期格式，考虑升级为 JSON：
- 记录 `lastExecuted`、`executionCount`、`lastExitStatus`
- 在 Prompt 中处理文件读取失败的情况
- 评估是否需要新增辅助脚本

**决策**：提醒类任务当前不需要更复杂的状态，保持纯文本日期格式。未来若扩展到巡检/开发等需要失败重试、执行次数统计的场景，再重新评估 JSON 化。

### #6 编写模板使用教程（已决策：由 SKILL-GUIDE.md 覆盖）

- 在 README.md 或 docs/ 下补充更详细的教程
- 包含分类选择、参数调整、常见问题排查

**决策**：`OpenClaw/skills/SKILL-GUIDE.md` 已包含参数详解、`openclaw cron edit` 支持矩阵、项目路径定位等使用指导，暂不再单独编写教程。后续如用户反馈指引不足，再在 README 中补充快速开始。

### #7 Code Review 待修复问题
根据最近一次 review，需要修复以下问题：
- [x] 修复 `build-cron.py` 中 `session:<id>` 逻辑永远不会触发的问题
  - `template-cron.zh.yaml` 中 `session:<id>` 是文档说明，用户实际会填 `SESSION_TARGET: "session:my-id"`
  - 建议：简化逻辑，直接渲染 `SESSION_TARGET`；或当 `PERSISTENT_ID` 非空时自动拼接
- [x] 修复 `build-cron.py` 对空列表/字典的处理
  - `COMMAND_ARGV: []` 会渲染为字符串 `"[]"`
  - 建议：`is_empty` 增加对 `[]` / `{}` 的检测，或在文档中明确 JSON 字符串形式
- [x] 修复 `build_persona_prompt` 空角色问题
  - `PERSONA_ROLE` 为空时返回"你是一个。"
  - 建议：返回空字符串或抛错
- [x] 确认 OpenClaw 是否支持 `--no-light-context`
  - `context.lightContext` false 时当前渲染 `--no-light-context`
  - 如不支持，将 false_flag 改为 `null`
- [x] 确认 OpenClaw 默认 delivery 模式是否即为 `none`
  - `delivery.mode: none` 当前不渲染任何 flag
- [x] 评估 `render_template` 是否引入 Jinja2
  - 结论：暂不引入。当前模板简单，简单字符串替换足够；Jinja2 会增加学习成本。
- [x] 更新 `CHANGELOG.md`
  - 补充 `edit-cron`、`SKILL-GUIDE.md`、AAC 命名规范、路径规范等最新变更
- [x] 明确 skill 文档中项目路径的自动定位方式
  - 当前使用 `/path/to/awesome-AGENT-configure` 占位符
- [x] 调研 OpenClaw 是否支持 `cron update`
  - `edit-cron` 当前采用 delete + create，会改变 job ID
- [x] 优化 `template-cron.zh.yaml` 中 `session:<id>` 注释
  - 避免与占位符混淆

## 已决策/已完成

- ✅ message 与 template 的关系：`message` 是官方 `--message` 映射，`template` 生成其内容
- ✅ command.enabled 删除，按 `command.script` 非空自动启用
- ✅ timeWindow.timezone 删除，统一使用 `schedule.timezone`
- ✅ `{{WORKSPACE}}` 默认 `~/.openclaw/workspace`，由生成器注入
- ✅ OpenClaw 模板生成器 `build-cron.py` 已完成
- ✅ 开机堆叠防护机制已在模板和文档中显性化
- ✅ 提醒类默认 `THINKING: off`、`EXACT: true`
- ✅ `init-cron` / `migrate-cron` / `edit-cron` skill 初版已完成（待实际验证）
- ✅ skill 生成的场景 YAML 统一存放路径：`~/.openclaw/workspace/awesome-AGENT-configure/cron/`
- ✅ AAC 命名规范：被规范化任务统一命名为 `【AAC-分类】任务名`
- ✅ 项目仓库与运行时配置完全分离：`AAC_REPO` 指向源码仓库，`AAC_WORKSPACE` 指向运行时配置（默认 `~/.openclaw/workspace/awesome-AGENT-configure`）
- ✅ 状态文件格式决策：保持纯文本日期格式，暂不做 JSON 化（提醒类任务不需要更复杂的状态）
- ✅ 教程决策：`OpenClaw/skills/SKILL-GUIDE.md` 已覆盖参数指南与使用方式，暂不再单独编写教程
- ✅ 模板引擎决策：暂不引入 Jinja2，保持简单字符串替换

## 近期改动注意事项

本次 review 发现以下需要后续关注或改进的点：

- [ ] `OpenClaw/scripts/build-cron.py` 的 `add_flag` 对 list/dict 统一 JSON 序列化，未来若 `COMMAND_ENV` 等字段需要非 JSON 格式，需单独处理。
- [ ] `OpenClaw/scripts/build-cron.py` 新增场景级 `template` 覆盖能力，但 `SKILL-GUIDE.md` 和 `template-cron.zh.yaml` 注释中尚未说明该用法。
- [ ] skill 文档中的项目自动定位脚本在 `$HOME` 较大时仍可能较慢，生产使用建议优先配置 `AAC_REPO` 环境变量。
- [ ] `OpenClaw/template/check/docker.yaml` 直接调用 `docker` 命令，要求 OpenClaw runner 所在环境具备 Docker CLI 及相应权限。
- [ ] `OpenClaw/template/check/docker.yaml` 中日志检查时间 `--since 10m`、关键字等写死在 prompt 里，后续如需复用建议抽成变量。
- [ ] `OpenClaw/conf/flags.yaml` 中 `delivery.mode: none` 映射为 `--no-deliver` 基于 OpenClaw 2026.6.9 验证，旧版本可能不支持。
- [ ] `OpenClaw/template/template-cron.zh.yaml` 默认提示词仍为提醒类内容，未覆盖 `template` 的场景会生成问候语，需在文档中提醒贡献者注意。
- [ ] 缺少对 `OpenClaw/scripts/build-cron.py` 的单元测试，建议后续补充边界用例（空列表、空角色、session 拼接等）。
