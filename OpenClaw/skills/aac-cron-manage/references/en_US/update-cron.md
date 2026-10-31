# Sync Cron Task Workflow

After a template upgrade, sync existing AAC tasks to the latest template while keeping the core configuration and job ID.

## Difference from Editing

- `edit-cron`: change the configuration of a single task (time, content, etc.)
- `update-cron`: after the template itself is upgraded, reuse the new template in bulk while task configuration stays the same

## Prerequisites

- The task name carries the `【AAC-` prefix
- A corresponding YAML file exists under `$AAC_WORKSPACE/cron/`

## Steps

- **1. List tasks**: `openclaw cron list`
- **2. Filter AAC tasks**: filter by the `【AAC-` prefix and show the list
- **3. User selection**: specify a task name or ID, or "all"
- **4. Locate the repository**: same as the `init-cron` workflow
- **5. Find the YAML**: search under `$AAC_WORKSPACE/cron/`
- **6. Render again**:
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<job-name>.yaml" \
    --preview
  ```
- **7. Get the ID**: `openclaw cron list --format json`, matching by `name`
- **8. Choose the update method**:
  - Agent mode: prefer `openclaw cron edit <job-id>` to keep the ID
  - Command mode: only `rm` + `create`; the ID changes
- **9. Generate a plan**:
  ```markdown
  | Task name | Method | Keeps ID | Notes |
  | xxx | edit | ✅ | Agent mode |
  | yyy | rm+create | ❌ | Command mode |
  ```
- **10. User confirmation**: show the plan and ask whether to execute
- **11. Execute updates**: process each task one by one
- **12. Verify**: run `openclaw cron list` after each task to confirm its status
- **13. Report results**:
  - Number synced successfully
  - Number that kept the original ID
  - Number whose ID changed
  - Number skipped and why

## Notes

- After syncing, watch one run to confirm the behavior matches expectations
- Loop-mode tasks reuse their state file path when synced, so historical state is not lost
- Avoid bulk updates during peak hours
- Template upgrades can change the semantics of the message; pay attention
