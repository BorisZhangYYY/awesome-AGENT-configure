# awesome-AGENT-configure

> An Agent template repository for Harness and Loop: constrain the agent to make it reliable, loop it to make it persistent.

[简体中文](README.md) | English

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Overview](#overview)
- [Template Overview](#template-overview)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
  - [AI Project Templates](#ai-project-templates-most-used)
  - [Agent Identity Templates](#agent-identity-templates)
  - [Scheduled Task Templates](#scheduled-task-templates)
  - [Context Injection Templates](#context-injection-templates)
- [Core Concepts](#core-concepts)
- [Usage Guide](#usage-guide)
  - [Language Versions](#language-versions)
  - [Placeholders and Templates](#placeholders-and-templates)
  - [Build-Time Validation](#build-time-validation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [FAQ](#faq)
- [License](#license)
- [Related Links](#related-links)

---

## Overview

With AI AGENT tools such as OpenClaw and Hermes, the result is often decided not by the model alone but by the constraints and progress mechanisms around it:

- **Harness (constraint)**: time windows, deduplication, state machines, and effect evaluation make AGENT behavior predictable and traceable.
- **Loop (iteration)**: goals, milestones, state resumption, and auto-disable let the AGENT keep advancing across sessions until the work is done.

This repository distills those mechanisms into copy-ready templates in four categories: AI project templates, agent identity templates, scheduled task templates, and context injection templates.

## Template Overview

| Type | Template | Problem it solves | Languages |
|------|----------|-------------------|-----------|
| **AI project templates** | AI-ProjConf: single-repo / multi-repo | Project conventions, task tracking, environment index, documentation layering | zh_CN / en_US |
| **Agent identity templates** | Hermes / OpenClaw workspace | Persona, user profile, long-term memory, group-chat boundaries | zh_CN / en_US |
| **Scheduled task templates** | OpenClaw cron: reminders / checks / projects / learning | Time windows, deduplication, state machines; Loop milestones and auto-disable | zh_CN / en_US |
| **Context injection templates** | OpenClaw hook-template | Inject roles and rules at session startup | zh_CN / en_US |

## Key Features

- **Harness constraints**: time windows, deduplication, state machines, and effect evaluation live in the templates, reducing runtime drift.
- **Loop progress**: project tasks advance by milestone, resume from state, and disable themselves when the goal is reached.
- **AI project conventions**: aligned `CLAUDE.md` / `AGENTS.md` / `TODO.md` / `CHANGELOG.md` for both single-repo and multi-repo layouts.
- **Placeholder-driven**: every template uses `{{PLACEHOLDER}}`; copy and replace.
- **Build-time validation**: `build-cron.py` checks delivery pitfalls and injects timezone offsets when generating commands.
- **Bilingual**: all READMEs and templates ship in `zh_CN` and `en_US`.

## Getting Started

### AI Project Templates (most used)

Pick the directory that matches your project:

| Layout | Directory | Suitable for |
|--------|-----------|--------------|
| Single repository | `AI-ProjConf/en_US/single-repo/` (or `zh_CN/`) | Independent developers; the root is the git repository |
| Microservice workspace | `AI-ProjConf/en_US/multi-repo/` (or `zh_CN/`) | The root is not version-controlled; each subdirectory is its own git repository |

Copy the `.example` files into your project root, drop the suffix, and replace the placeholders:

```bash
cp AI-ProjConf/en_US/single-repo/CLAUDE.md.example /path/to/project/CLAUDE.md
```

Template conventions:

- `.docs/`: user-facing business and deployment documents
- `.project/`: internal development notes
- `.project/env/`: per-environment connection details (`test.md` / `uat.md` / `prd.md`)
- `.project/YYYYMMDD-topic/`: task bodies; the root `TODO.md` is only an index

### Agent Identity Templates

- **Hermes**: back up and merge `SOUL.md` and `memories/*.md` from `Hermes/en_US/workspace-template/` (or `zh_CN/`) into `$HERMES_HOME`.
- **OpenClaw**: copy the files from `OpenClaw/en_US/workspace_example/` (or `zh_CN/`) into the OpenClaw workspace and adapt them.

### Scheduled Task Templates

Using the morning reminder as an example:

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/en_US/cron-template/reminders/morning/morning.yaml
```

Common flags:

```bash
# Preview the rendered message and command
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/en_US/cron-template/reminders/morning/morning.yaml --preview

# Output a JSON array for programmatic use
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/en_US/cron-template/reminders/morning/morning.yaml --json
```

For the Chinese version, replace `en_US` with `zh_CN` in the path.

### Context Injection Templates

Copy `OpenClaw/en_US/hook-template/` (or `zh_CN/`) into the OpenClaw hooks directory and edit `context.md` with the role and rules.

## Core Concepts

- **Harness**: prompt-layer mechanisms that constrain AGENT behavior, such as time windows, deduplication, state machines, and effect evaluation.
- **Loop**: mechanisms that let an AGENT advance across sessions, such as goals, milestones, state files, and auto-disable.
- **Cron**: schedule triggering based on crontab expressions.
- **Trigger**: a JavaScript check (time window, deduplication) that runs after a cron schedule fires.
- **State file**: a persistent record maintained by the AGENT for deduplication and resumption.
- **Identity files**: `SOUL.md` / `USER.md` / `MEMORY.md`, which define the AGENT's persona and memory.

## Usage Guide

### Language Versions

- Chinese: `README.md`, `*/zh_CN/`
- English: `README.en.md`, `*/en_US/`
- Keep both template sets and READMEs in sync; add both languages when adding a new template.

### Placeholders and Templates

- Template variables use uppercase letters, digits, and underscores only (`[A-Z][A-Z0-9_]*`).
- A scene YAML points to its parent template via `templateRef`; scene variables override parent defaults.
- English scenes set `LOCALE: "en_US"` to generate an English persona prompt; Chinese scenes default to `zh_CN`.
- Cron task names follow `【AAC-Category】Task name`; English templates use `Reminder` / `Check` / `Project` / `Learn`, while the `【AAC-` prefix stays fixed.

### Build-Time Validation

`build-cron.py`:

- detects the `DELIVERY_MODE=announce + CHANNEL=last + isolated` delivery pitfall;
- injects the timezone offset `AAC_TZ_OFFSET_MINUTES` so the trigger sandbox never needs `Intl`;
- validates Loop variables up front.

## Roadmap

- [ ] Add project templates for the Claude Code framework.
- [ ] Add more practical scene templates.

## Contributing

PRs and Issues are welcome.

If you have a useful template or have found a problem, open a PR; it will be reviewed and merged.

## FAQ

### Can I use these templates directly?

Yes. This repository is a template collection; copy what you need into your project or AGENT workspace.

### Why does trigger.js avoid Node.js modules?

OpenClaw Gateway runs triggers in a QuickJS-WASI sandbox that forbids `require`, `import`, Node modules, networking, timers, and similar APIs. `build-cron.py` computes the timezone offset at build time and injects `AAC_TZ_OFFSET_MINUTES`.

### What if the Chinese and English versions disagree?

The Chinese version is authoritative; PRs that sync the English version are welcome.

## License

This project is licensed under [MIT](LICENSE).

## Related Links

- OpenClaw documentation: https://docs.openclaw.ai/
- Hermes documentation: https://hermes-agent.nousresearch.com/docs/
- Claude Code documentation: https://docs.claude.ai/
