# TODO

> 说明：
> - 优先级：P0 = 紧急，P1 = 重要，P2 = 一般，P3 = 低优先级
> - 状态：待实现 / 已完成
> - **已完成**的事项需同步到 `CHANGELOG.md`

## 待实现

### P0：

- [x] 实现 OpenClaw 的一个脚本，aac-manage.sh，可以一键安装 AAC 的 skill、cron，或者一键删除 AAC 的 skill、cron，也支持部分安装和删除，总之就是一个管理效果。
- [ ] {{任务 2}}

### P1：

- [ ] 设计决策：`template-cron.zh.yaml` 中 `persona.file` 与 `context.lightContext: true` 的组合冲突
  - 问题：`lightContext: true` 会跳过 workspace bootstrap 文件（SOUL.md / IDENTITY.md 等）的注入，而 `persona.file` 通常正是引用这些文件；组合使用时 Agent 可能拿不到人设内容。
  - 可选方案：
    1. 在 `build-cron.py` 中增加校验：当 `PERSONA_MODE=file` 且 `LIGHT_CONTEXT=true` 时抛出错误或警告；
    2. 在模板注释中明确说明该组合的风险，由场景文件自行规避；
    3. 调整 `PERSONA_PROMPT` 渲染逻辑，在 lightContext 模式下主动读取 `persona.file` 内容并注入到 message 中。
  - 需要用户确认采用哪种方案后再实现。

### P2：

- [ ] {{任务 4}}

### P3：

- [ ] {{任务 5}}

## 已完成

- [x] {{已完成任务 1}}
- [x] {{已完成任务 2}}
