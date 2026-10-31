# Create Cron Task Workflow

Complete steps for creating a new AAC-normalized scheduled task.

## Prerequisites

- awesome-AGENT-configure cloned locally
- `python3` and the `openclaw` CLI available
- `AAC_REPO` environment variable set (optional but recommended)

## Steps

- **1. Ask intent**: confirm category (reminder/check/project/learning), trigger time, task content, and delivery method
- **2. Check duplicates**: run `openclaw cron list`; if a similar task exists, recommend the migration workflow instead
- **3. Choose a template**: pick from the directory-based templates
  - `OpenClaw/zh_CN/cron-template/reminders/morning/morning.yaml` (Chinese)
  - `OpenClaw/en_US/cron-template/reminders/morning/morning.yaml` (English)
  - `OpenClaw/zh_CN/cron-template/checks/docker-check/docker-check.yaml`
  - `OpenClaw/en_US/cron-template/checks/docker-check/docker-check.yaml`
  - and so on
- **4. Fill variables**: fill in category-recommended values automatically, then ask the user to confirm or tweak
  - `JOB_NAME` must use `【AAC-Category】Task name`
  - `SCHEDULE_EXPR`, `TIMEZONE`, `WINDOW_START`, `WINDOW_END`
  - `DEDUP_STATE_FILE`, `DEDUP_GRANULARITY`
- **5. Locate the repository**:
  ```bash
  export AAC_REPO=$(python3 -c "import os,sys; ...")
  ```
  Fallback order: environment variable → current directory → search under $HOME
- **6. Generate YAML**: write to `$AAC_WORKSPACE/cron/init-<job-name>/init-<job-name>.yaml`
  - Replace `templateRef` with the absolute path `<AAC_REPO>/OpenClaw/{zh_CN|en_US}/cron-template/template-cron.yaml`
- **7. Render the command**:
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/init-<job-name>/init-<job-name>.yaml"
  ```
- **8. User confirmation**: show the YAML path, rendered command, and key configuration notes
- **9. Execute create**: after the user confirms, run `openclaw cron create ...`
- **10. Verify**: `openclaw cron list` to confirm the task exists

## Test Mode

```bash
python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
  "$AAC_WORKSPACE/cron/init-<job-name>/init-<job-name>.yaml" \
  --test
```

Effects:
- The task name gets a `【TEST】` prefix
- Time window and deduplication are skipped
- `--delete-after-run` is appended (the task deletes itself after running)

## Time Window and Deduplication

- Do not use the `TIME_WINDOW_ENABLED` / `DEDUP_ENABLED` / `WINDOW_OUT_ACTION` variables
- All handling is done by `OpenClaw/skills/aac-cron-manage/scripts/trigger.js`
- `build-cron.py` automatically injects `WINDOW_START` / `WINDOW_END` / `DEDUP_STATE_FILE` / `DEDUP_GRANULARITY` as environment variables

## Safety Red Lines

- When a duplicate task is found, prefer migration over creating another copy
- Do not run dangerous operations such as push or delete without permission
- Obtain explicit user confirmation before creating
- Every task name must carry the `【AAC-Category】` prefix
