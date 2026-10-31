---
name: aac-cron-manage
description: "Manage AAC-normalized OpenClaw cron tasks: create, edit, migrate, update, or remove."
---

# AAC Cron Manager

English | [简体中文](SKILL.zh_CN.md)

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
- Templates are directory-based: `{zh_CN|en_US}/cron-template/checks/docker-check/docker-check.yaml`. (Scene-specific .js is currently unavailable; see the template comments.)
- Trigger logic is unified in `OpenClaw/skills/aac-cron-manage/scripts/trigger.js` (time window). Scene-specific JS is auto-concatenated by `build-cron.py`.
- Trigger scripts run in a QuickJS-WASI sandbox: pure ES2022 JS only — no `Intl`, no `require`/`import`, no `process`, no Node modules. See `references/en_US/trigger-sandbox.md` before touching any trigger code.
- Always show the configuration to the user and get confirmation before executing.
- `--test` mode generates a one-off task with a `【TEST】` prefix, skips window/dedup checks, and auto-deletes after running.

## Workflow selection

- **Create**: see `references/en_US/init-cron.md`
- **Edit**: see `references/en_US/edit-cron.md`
- **Migrate**: see `references/en_US/migrate-cron.md`
- **Sync to latest template**: see `references/en_US/update-cron.md`
- **Delete**: `openclaw cron rm <job-id>`
- **List installed**: `openclaw cron list`
- **List available templates**: `ls OpenClaw/{zh_CN,en_US}/cron-template/*/*/` (from the AAC repo)

## Quick commands

- Render a scene YAML (normal):
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml"
  ```
- Render a scene YAML as an argv array:
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml" --json
  ```
- Render a scene YAML as an **edit** command (keep the job id; do not create a new task):
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml" --edit <job-id> --json
  ```
- Render a scene YAML (test mode):
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<task-name>/<task-name>.yaml" \
    --test
  ```
- Locate the AAC repo:
  ```bash
  export AAC_REPO=$(python3 -c "import os,sys; ...")
  ```
  Fallback order: `AAC_REPO` env → current directory → search under `$HOME`.

## ⛔ Edit must use `--edit` or `--json`

`build-cron.py`'s default output uses **backslash line continuations**. Assembling an
`openclaw cron edit` command with string replacement silently fails: it actually runs
`openclaw cron create`, creates duplicate jobs, and may delete the copy that contains the
changes (incidents verified on 2026-10-19/21).

**Preferred**: `build-cron.py <yaml> --edit <job-id> --json` — directly generates
`openclaw cron edit <job-id> ...`, keeps the job id, updates the content in place, and
creates no new job (verified 2026-10-21).

**Fallback**: add `--json` to get the argv array and pass only `--message` for a minimal edit.

Neither option can be skipped: **after editing, verify that the live job's payload actually changed.**

## Legacy variable cleanup

Do not use these in new YAMLs — they are handled by `OpenClaw/skills/aac-cron-manage/scripts/trigger.js`:
- `TIME_WINDOW_ENABLED`
- `DEDUP_ENABLED`
- `WINDOW_OUT_ACTION`
- `TRIGGER_LIBRARY_PATH`

Instead, set `WINDOW_START`, `WINDOW_END`, `DEDUP_STATE_FILE`, `DEDUP_GRANULARITY` directly. `build-cron.py` injects them as environment variables into the trigger script.
