---
name: "{{PLUGIN_NAME}}"
version: "{{PLUGIN_VERSION}}"
description: "{{PLUGIN_DESCRIPTION}}"
author: "{{PLUGIN_AUTHOR}}"
events:
  - agent:bootstrap
files:
  - handler.js
  - context.md
---

# {{PLUGIN_NAME}}

{{PLUGIN_DESCRIPTION}}

## 用途

本 hook pack 在每次 Agent 会话启动（`agent:bootstrap` 事件）时，自动将 `context.md` 中的角色/身份描述注入到 bootstrap 上下文中，使 Agent 在每次会话中都携带特定角色设定。

**与工作区文件注入的区别**：
- 工作区文件（SOUL.md、AGENTS.md 等）是**持久**的，替换后会一直生效
- hook pack 是**追加**式的，不修改用户已有的工作区文件
- 适合插件/子项目场景，用户主工作区不需要感知插件角色

## 配置

1. 编辑 `context.md`，填写插件专属的角色描述
2. 根据需要修改 `handler.js` 中的注入位置（默认为系统提示词末尾）
3. 安装 hook：将本目录复制到 OpenClaw hooks 目录

## 依赖

- OpenClaw 框架，支持 hook 机制
