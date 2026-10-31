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

## Purpose

This hook pack automatically injects the role/identity description from `context.md` into the bootstrap context every time an Agent session starts (the `agent:bootstrap` event), so the Agent carries that role in every session.

**Difference from workspace file injection**:
- Workspace files (SOUL.md, AGENTS.md, etc.) are **persistent** and stay in effect once replaced
- A hook pack is **additive** and does not modify the user's existing workspace files
- Suitable for plugin/subproject scenarios where the user's main workspace does not need to know about the plugin role

## Configuration

1. Edit `context.md` with the plugin-specific role description
2. Adjust the injection position in `handler.js` if needed (default: after the system message)
3. Install the hook: copy this directory into the OpenClaw hooks directory

## Dependencies

- The OpenClaw framework with hook support
