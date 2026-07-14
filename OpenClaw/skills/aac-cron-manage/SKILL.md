---
name: aac-cron-manage
description: "Manage AAC-normalized OpenClaw cron tasks: create, edit, migrate, update, or remove."
---

# AAC Cron Manager

Manage awesome-AGENT-configure (AAC) normalized cron tasks. Only handles tasks with the `【AAC-` prefix.

## When to use

- User says "create cron", "add reminder", "new scheduled task"
- User says "edit cron", "modify cron task"
- User says "migrate cron", "upgrade cron task"
- User says "delete cron", "remove cron task"
- User says "sync cron to latest template"
- User says "test cron" (use `--test` flag)

## Hard rules

- Only manage tasks with `【AAC-` prefix in the name.
- All scene YAML files live in `~/.openclaw/workspace/awesome-AGENT-configure/cron/<task-name>/<task-name>.yaml`.
- Rendering goes through `OpenClaw/skills/aac-cron-manage/scripts/build-cron.py`.
- Templates are directory-based: `checks/docker-check/docker-check.yaml` + optional `docker-check.js`.
- Trigger logic is unified in `triggers/trigger.js` (time window + dedup). Scene-specific JS is auto-concatenated by `build-cron.py`.
- Always show config to user and get confirmation before executing.
- `--test` mode generates a one-off task with `【TEST】` prefix, skips window/dedup checks, and auto-deletes after run.

## Workflow selection

- **Create**: see `references/init-cron.md`
- **Edit**: see `references/edit-cron.md`
- **Migrate**: see `references/migrate-cron.md`
- **Sync to latest template**: see `references/update-cron.md`
- **Delete**: `openclaw cron rm <job-id>`
- **List installed**: `openclaw cron list`
- **List available templates**: `ls OpenClaw/template/*/*/` (from the AAC repo)

## Quick commands

- Render a scene YAML (normal):
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml"
  ```
- Render a scene YAML (test mode):
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml" \
    --test
  ```
- Locate AAC repo:
  ```bash
  export AAC_REPO=$(python3 -c "import os,sys; ...")
  ```
  Fallback order: `AAC_REPO` env → current directory → search under `$HOME`.

## Legacy variable cleanup

Do not use these in new YAMLs — they are handled by `triggers/trigger.js`:
- `TIME_WINDOW_ENABLED`
- `DEDUP_ENABLED`
- `WINDOW_OUT_ACTION`
- `TRIGGER_LIBRARY_PATH`

Instead, set `WINDOW_START`, `WINDOW_END`, `DEDUP_STATE_FILE`, `DEDUP_GRANULARITY` directly. `build-cron.py` injects them as environment variables into the trigger script.
