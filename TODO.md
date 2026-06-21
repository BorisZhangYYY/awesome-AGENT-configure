# TODO

## 待实现

### #1 补充非提醒类 OpenClaw 模板
当前项目只有提醒类场景模板，需要补充：
- 【巡检】类模板（如磁盘检查、服务健康检查）
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

### #5 完善状态文件 JSON 化方案
当前去重状态文件为纯文本日期格式，考虑升级为 JSON：
- 记录 `lastExecuted`、`executionCount`、`lastExitStatus`
- 在 Prompt 中处理文件读取失败的情况
- 评估是否需要新增辅助脚本

### #6 编写模板使用教程
- 在 README.md 或 docs/ 下补充更详细的教程
- 包含分类选择、参数调整、常见问题排查

### #7 Code Review 待修复问题
根据最近一次 review，需要修复以下问题：
- [ ] 修复 `build-cron.py` 中 `session:<id>` 逻辑永远不会触发的问题
  - `template-cron.zh.yaml` 中 `session:<id>` 是文档说明，用户实际会填 `SESSION_TARGET: "session:my-id"`
  - 建议：简化逻辑，直接渲染 `SESSION_TARGET`；或当 `PERSISTENT_ID` 非空时自动拼接
- [ ] 修复 `build-cron.py` 对空列表/字典的处理
  - `COMMAND_ARGV: []` 会渲染为字符串 `"[]"`
  - 建议：`is_empty` 增加对 `[]` / `{}` 的检测，或在文档中明确 JSON 字符串形式
- [ ] 修复 `build_persona_prompt` 空角色问题
  - `PERSONA_ROLE` 为空时返回"你是一个。"
  - 建议：返回空字符串或抛错
- [ ] 确认 OpenClaw 是否支持 `--no-light-context`
  - `context.lightContext` false 时当前渲染 `--no-light-context`
  - 如不支持，将 false_flag 改为 `null`
- [ ] 确认 OpenClaw 默认 delivery 模式是否即为 `none`
  - `delivery.mode: none` 当前不渲染任何 flag
- [ ] 评估 `render_template` 是否引入 Jinja2
  - 当前简单字符串替换无法处理变量值含 `{{` 或条件逻辑
- [ ] 更新 `CHANGELOG.md`
  - 补充 `edit-cron`、`SKILL-GUIDE.md`、AAC 命名规范、路径规范等最新变更
- [ ] 明确 skill 文档中项目路径的自动定位方式
  - 当前使用 `/path/to/awesome-AGENT-configure` 占位符
- [ ] 调研 OpenClaw 是否支持 `cron update`
  - `edit-cron` 当前采用 delete + create，会改变 job ID
- [ ] 优化 `template-cron.zh.yaml` 中 `session:<id>` 注释
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
