# awesome-AGENT-configure

> An Agent template repository for Harness and Loop: constrain the agent to make it reliable, loop it to make it persistent.

[简体中文](README.md) | English

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Four template categories cover AI project conventions, agent identity, scheduled tasks, and context injection. Available in Simplified Chinese and English; copy what you need and replace `{{PLACEHOLDER}}` values.

## AI Project Templates

Align project conventions, task tracking, and documentation for AI-assisted development.

- **Backlog.md**: one template for single- and multi-repository projects, with CLI-managed tasks, shared docs, and milestones.
- **Legacy templates**: separate single- and multi-repository variants that track work in `.project/` and keep shared docs in `.docs/` without requiring Backlog.md.

See [AI-ProjConf](AI-ProjConf/README.en.md).

## Agent Identity Templates

Persona, user profile, and long-term memory scaffolds for Hermes and OpenClaw.

- **Persona and boundaries**: define communication style, work habits, participation, and privacy boundaries for private and group chats.
- **Profiles and memory**: keep user preferences separate from long-term environment facts.
- **Workspace organization**: categorize files by topic and move lengthy content out of core context files.

See [Hermes workspace templates](Hermes/README.en.md) and [OpenClaw workspace templates](OpenClaw/README.en.md#workspace-templates).

## Scheduled Task Templates

Reminder, check, project, and learning scenarios for OpenClaw.

- **Harness constraints**: time windows, deduplication, state records, and delivery configuration guide task execution.
- **Loop progress**: goals and milestones guide continued work, with state files for resumption and instructions to disable tasks once goals are met.
- **Build tooling**: `build-cron.py` generates task commands with preview and JSON output, validates delivery configuration, and injects timezone offsets.

See [OpenClaw scheduled task templates](OpenClaw/README.en.md#scheduled-task-templates).

## Context Injection Templates

Inject roles and rules through OpenClaw's session-start hook so new sessions receive consistent context.

- **Centralized content**: define what to inject in `context.md`.
- **Startup loading**: read and inject content on `agent:bootstrap`, reducing repeated instructions.

See [OpenClaw context injection templates](OpenClaw/README.en.md#context-injection-templates).

## Acknowledgments

Thanks to these projects and their maintainers for the tools and ideas behind these templates:

- [Backlog.md](https://backlog.md/): task, documentation, and milestone management for the AI project template. [CLI reference](https://github.com/MrLesk/Backlog.md/blob/main/CLI-INSTRUCTIONS.md)
- [OpenClaw](https://openclaw.ai/): the framework behind the workspace, scheduled task, and context injection templates. [Official docs](https://docs.openclaw.ai/)
- [Claude Code](https://claude.com/product/claude-code): the source of the project-level `CLAUDE.md` convention. [Official docs](https://code.claude.com/docs/en/overview)
- [Hermes Agent](https://hermes-agent.nousresearch.com/): the framework behind the workspace identity, user profile, and memory templates. [Official docs](https://hermes-agent.nousresearch.com/docs)

---

[MIT License](LICENSE)
