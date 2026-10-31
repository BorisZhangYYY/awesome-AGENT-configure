# OpenClaw Templates

> Workspace, scheduled-task, and context-injection templates for OpenClaw, where the Harness/Loop mechanisms live.

[简体中文](README.md) | English

## Template Types

| Type | Directory | Purpose |
|------|-----------|---------|
| Agent identity | `en_US/workspace_example/` (or `zh_CN/`) | `SOUL.md`, `AGENTS.md`, `USER.md`, `MEMORY.md`, `IDENTITY.md`, `HEARTBEAT.md` |
| Scheduled tasks | `en_US/cron-template/` (or `zh_CN/`) | Four scene categories (reminders, checks, projects, learning) plus the shared parent `template-cron.yaml` |
| Context injection | `en_US/hook-template/` (or `zh_CN/`) | Listens for `agent:bootstrap` and injects `context.md` at session startup |
| Skill tooling | `skills/aac-cron-manage/` | `build-cron.py`, `trigger.js`, and usage docs (shared, not split by language) |

## Scheduled Task Templates

Scenes are grouped by category under `cron-template/`:

| Category | Scenes |
|----------|--------|
| Reminders | Morning, noon, evening, custom reminders |
| Checks | Cron task health, Docker containers, workspace organization, custom checks |
| Projects | Feature development, maintenance sessions, custom projects (Loop mode) |
| Learning | Custom learning |

Every scene points to the parent template `template-cron.yaml` via `templateRef`. The parent template provides:

- **Harness**: time windows, deduplication, state files, delivery and trigger configuration.
- **Loop**: goals, milestones, state resumption, and auto-disable when the goal is reached.

Generate a cron command:

```bash
python3 OpenClaw/skills/aac-cron-manage/scripts/build-cron.py \
  OpenClaw/en_US/cron-template/reminders/morning/morning.yaml --preview
```

For the Chinese version, replace `en_US` with `zh_CN` in the path. Task names always use the `【AAC-` prefix; English templates use the categories `Reminder` / `Check` / `Project` / `Learn`.

## Workspace Templates

Copy the files from `en_US/workspace_example/` (or `zh_CN/`) into the OpenClaw workspace and adapt them:

- `SOUL.md`: persona and workspace management rules
- `AGENTS.md`: code of conduct and `## Tools` local environment notes
- `USER.md` / `MEMORY.md`: user profile and long-term memory skeleton
- `IDENTITY.md`: outward identity
- `HEARTBEAT.md`: heartbeat checklist

## Context Injection Templates

Copy `en_US/hook-template/` (or `zh_CN/`) into the OpenClaw hooks directory and edit `context.md` with the role and rules:

- `HOOK.md`: hook pack declaration and description
- `context.md`: content injected at every session startup
- `handler.js`: implementation that reads and injects the context

## Related Documentation

- [aac-cron-manage SKILL](skills/aac-cron-manage/SKILL.md)
- [Template parameter guide](skills/aac-cron-manage/references/en_US/cron-template-guide.md)
- [Trigger sandbox limitations](skills/aac-cron-manage/references/en_US/trigger-sandbox.md)
