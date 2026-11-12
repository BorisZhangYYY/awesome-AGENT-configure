# awesome-AGENT-configure

> An Agent template repository for Harness and Loop: constrain the agent to make it reliable, loop it to make it persistent.

[简体中文](README.md) | English

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Four template categories cover AI project conventions, agent identity, scheduled tasks, and context injection. Available in Simplified Chinese and English; copy what you need and replace `{{PLACEHOLDER}}` values.

## AI Project Templates

Align project conventions, task tracking, and documentation for AI-assisted development.

- **Single repository**: project conventions, agent guidance, and README, task index, and changelog scaffolds for standalone projects.
- **Multi-repository workspace**: shared collaboration rules and an environment index for microservices and other multi-repo projects.
- **Task and documentation layers**: separate task indexes from detailed notes, and user guides from development rules and environment configuration, keeping context lean.

See [AI-ProjConf](AI-ProjConf/README.en.md).

## Agent Identity Templates

Persona, user profile, and long-term memory scaffolds for Hermes and OpenClaw.

- **Persona and boundaries**: define communication style, work habits, participation, and privacy boundaries for private and group chats.
- **Profiles and memory**: keep user preferences separate from long-term environment facts.
- **Workspace organization**: categorize files by topic and move lengthy content out of core context files.

See [Hermes workspace templates](Hermes/README.en.md) and [OpenClaw workspace templates](OpenClaw/README.en.md#workspace-templates).

## Scheduled Task Templates

Independent reminder, check, project, learning, script-only, and change-monitor scenarios for OpenClaw and Hermes; their parameters and compilers are not interchangeable.

- **Harness constraints**: one shared premise (fresh session, evidence first, authorization boundary) plus consistent `[SILENT]` and `[CRON_FAILURE]` wording.
- **Loop progress**: goals and milestones drive one verifiable step per run, with progress in a dedicated state file and no automatic self-pause by default.
- **Build tooling**: each `build-cron.py` only prints reviewable commands or requests — never executes or installs — with validate, preview, JSON, tool-request, plan, and one-shot test modes.

See [Hermes scheduled task templates](Hermes/README.en.md#cron-quick-start) and [OpenClaw scheduled task templates](OpenClaw/README.en.md#scheduled-task-templates).

## Context Injection Templates

Inject roles and rules through OpenClaw's session-start hook so new sessions receive consistent context.

- **Centralized content**: define what to inject in `context.md`.
- **Startup loading**: read and inject content on `agent:bootstrap`, reducing repeated instructions.

See [OpenClaw context injection templates](OpenClaw/README.en.md#context-injection-templates).

---

[MIT License](LICENSE)
