# TODO

## 待讨论/待决策

### #3 message 与 template 的关系
- 当前设计：`template` 字段写完整 Prompt，`message: "{{MESSAGE}}"` 作为占位符，由生成器将渲染后的 `template` 内容填入 `MESSAGE`
- 备选方案：直接删除 `message` 字段，生成器将渲染后的 `template` 作为 `--message` 的值
- 决策：待讨论

### #4 command.enabled 非官方抽象
- 当前设计：`command.enabled` 是模板层开关，决定是否渲染 `--command`
- OpenClaw 原生语义：只要存在 `--command` 参数即启用命令模式
- 建议：删除 `command.enabled`，改为 `command.script` 非空时自动启用
- 决策：待讨论

### #7 timeWindow.timezone 与 schedule.timezone 重复
- `timeWindow` 是【非官方】扩展，其 timezone 通常与 `schedule.timezone` 一致
- 建议：`timeWindow` 中不再单独配置 timezone，统一使用 `schedule.timezone`
- 决策：待讨论

## 待实现

### #8 明确 {{WORKSPACE}} 变量来源
- `deduplication.stateFile` 等字段中使用了 `{{WORKSPACE}}`
- 需要明确该变量是由生成器注入，还是要求场景文件显式定义
- 状态：待实现

### #10 补充 OpenClaw 模板生成器脚本
- `OpenClaw/scripts/` 目录为空
- 需要实现 `render-template.py`（或类似脚本），将 YAML 模板 + 场景变量渲染为 `openclaw cron add` 命令
- 状态：待实现
