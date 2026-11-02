# awesome-AGENT-configure

> Harness 与 Loop 的 Agent 模板仓库：用约束让 AGENT 可靠，用循环让 AGENT 持续推进。

简体中文 | [English](README.en.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

提供 AI 项目规范、Agent 身份、定时任务与上下文注入四类模板，支持简体中文与英文，按需复制并替换 `{{PLACEHOLDER}}` 即可使用。

## AI 项目模板

为 AI 编程协作统一项目规范、任务跟踪和文档管理方式。

- **单仓库**：适用于独立项目，提供项目规范、Agent 引导、README、待办与变更日志骨架。
- **多仓库工作区**：适用于微服务等多仓库项目，在工作区集中维护协作规范与环境索引。
- **任务与文档分层**：待办索引与任务正文分离，区分使用文档、开发细则和环境配置，减少上下文冗余。

详见 [AI-ProjConf](AI-ProjConf/README.md)。

## Agent 身份模板

为 Hermes 与 OpenClaw 提供人格、用户画像和长期记忆的初始骨架。

- **人格与行为边界**：约定交流方式、工作习惯，以及私聊和群聊中的参与及隐私边界。
- **画像与记忆分工**：分开维护用户偏好与长期环境事实，避免信息混杂。
- **工作区管理**：按主题分类文件，将长内容外置，保持核心上下文简洁。

详见 [Hermes 工作区模板](Hermes/README.md)与 [OpenClaw 工作区模板](OpenClaw/README.md#工作区模板)。

## 定时任务模板

为 OpenClaw 提供提醒、巡检、项目推进和学习四类场景。

- **Harness 约束**：通过时间窗口、去重、状态记录与投递配置，约束任务执行行为。
- **Loop 推进**：按目标与里程碑持续推进，利用状态文件续传，并约定达成目标后自动停用。
- **构建工具**：`build-cron.py` 生成任务命令，支持预览与 JSON 输出，并校验投递配置、注入时区偏移。

详见 [OpenClaw 定时任务模板](OpenClaw/README.md#定时任务模板)。

## 上下文注入模板

通过 OpenClaw 的会话启动 Hook 注入角色与规则，让新会话获得统一的上下文。

- **集中维护**：在 `context.md` 中定义需要注入的内容。
- **启动时加载**：通过 `agent:bootstrap` 事件读取并注入，减少重复说明。

详见 [OpenClaw 上下文注入模板](OpenClaw/README.md#上下文注入模板)。

---

[MIT License](LICENSE)
