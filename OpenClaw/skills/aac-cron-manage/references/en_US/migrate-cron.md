# Migrate Cron Task Workflow

Convert an existing but non-compliant OpenClaw scheduled task into the AAC convention.

## When to Use

- The user already has manually created cron tasks
- `init-cron` finds a task with the same name/topic and switches to this workflow
- The user asks "check whether my existing tasks have problems"

## Steps

- **1. List tasks**: `openclaw cron list`
- **2. Choose tasks**: specified by the user, or "all"
- **3. Get details**: run `openclaw cron info --id <job-id>` for each task
- **4. Analyze the category**: judge from the name/description
  - Reminder → scheduled greeting, fixed format, must be delivered
  - Check → inspect status, silent when healthy, alert on anomalies
  - Project → advance a project, needs state tracking
  - Learning → technical research, knowledge accumulation
- **5. Diagnose problems**:
  - Does `thinking` match the complexity?
  - Is `session` set to `isolated`?
  - Is `delivery` reasonable?
  - Is a time window / deduplication missing?
  - Is `lightContext` appropriate?
  - Do reminder tasks have `exact` enabled?
- **6. Generate a report**:
  ```markdown
  ## Task: xxx
  - Category: reminder
  - Problems:
    1. thinking is not off; wastes tokens
    2. Missing time window
    3. delivery should be announce
  - Recommendations:
    - JOB_NAME: 【AAC-Reminder】Morning
    - SESSION_TARGET: isolated
    - DELIVERY_MODE: announce
  ```
- **7. User confirmation**: show the report and ask whether to migrate
- **8. Locate the repository**: same as the `init-cron` workflow
- **9. Generate YAML**: write to `$AAC_WORKSPACE/cron/migrated-<job-name>.yaml`
- **10. Render the command**: `build-cron.py --preview`
- **11. User confirmation**: show the command and ask whether to create
- **12. Execute create**: run after the user confirms
- **13. Verify**: `openclaw cron list`

## Naming Convention

After migration, names become `【AAC-Category】Task name`. Example: `Morning` → `【AAC-Reminder】Morning`. Old tasks are not deleted automatically.

## Safety Red Lines

- Do not migrate everything by default; only handle what the user selects
- Do not delete old tasks; only suggest that the user delete them manually
- Migrate complex tasks (project/learning) in stages
- Obtain user confirmation before creating
