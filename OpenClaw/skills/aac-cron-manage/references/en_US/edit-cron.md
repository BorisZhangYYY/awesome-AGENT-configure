# Edit Cron Task Workflow

Modify a scheduled task that was created under AAC conventions.

## Prerequisites

- The task name carries the `【AAC-` prefix
- A corresponding scene YAML exists at `$AAC_WORKSPACE/cron/<job-name>.yaml`
- If no YAML exists, prefer the migration workflow instead

## Steps

- **1. List tasks**: `openclaw cron list`; identify tasks with the `【AAC-` prefix first
- **2. Choose a task**: the user specifies a task name or ID
- **3. Find the YAML**: search under `$AAC_WORKSPACE/cron/`
- **4. Show the configuration**: read the YAML and show key fields (name, schedule, window, delivery, thinking, tools)
- **5. Ask what to change**: common edits:
  - Trigger time → `SCHEDULE_EXPR`
  - Time window → `WINDOW_START` / `WINDOW_END`
  - Content → `SCENE_NAME` / `EMOJI` / `REMARK`
  - Delivery method → `DELIVERY_MODE`
  - Model capability → `THINKING` / `MODEL` / `TOOLS`
  - Timeout → `TIMEOUT_SECONDS`
- **6. Edit the YAML**: update the corresponding variable values
- **7. Render again**:
  ```bash
  # Recommended: --edit <job-id> directly generates an `openclaw cron edit <job-id> ...` command
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<job-name>.yaml" --edit <job-id> --json
  ```
  `--edit` mode: the positional argument is the job id (not the cron expression), the cron expression goes through `--cron`,
  and every other flag matches create. **Run the command directly to update in place; it does not create a new job.**

  If the old script has no `--edit`, fall back to taking only `--message` for a minimal edit:
  ```bash
  python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
    "$AAC_WORKSPACE/cron/<job-name>.yaml" --json
  ```
  The output is an argv array (JSON); take the `--message` value directly.
  ⛔ **Never do string replacement on the default output** (see "Forbidden Approach" below).
- **8. Choose the update method**:
  - Agent mode (uses `--message`): prefer `openclaw cron edit <job-id>` to keep the ID
  - Command mode (uses `--command`): `edit` is unsupported; only `rm` + `create`, and the ID changes
- **9. User confirmation**: show the before/after diff, update method, and the exact command
- **10. Execute the update**:
  - Method A (recommended): render with `--edit <job-id>` and run it directly
    ```bash
    python3 "$AAC_REPO/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py" \
      "$AAC_WORKSPACE/cron/<job-name>.yaml" --edit <job-id> --json > /tmp/edit-argv.json
    python3 -c "import json,subprocess; subprocess.run(json.load(open('/tmp/edit-argv.json')))"
    ```
    (Verified on 2026-10-21: job id preserved, content updated in place, no duplicate created.)

  - Method A' (old-script fallback): pass only `--message`; all other fields stay as they are on the live job
    ```python
    import json, subprocess
    arr = json.loads(subprocess.run(
        ['python3', f'{AAC_REPO}/OpenClaw/skills/aac-cron-manage/scripts/build-cron.py', yaml, '--json'],
        capture_output=True, text=True).stdout)
    msg = arr[arr.index('--message') + 1]
    subprocess.run(['openclaw', 'cron', 'edit', job_id, '--message', msg])
    ```
  - Method A' (when other fields must change): rebuild from the argv flags, and **each flag may appear only once**.
    Verified `openclaw cron edit` supports `--name`, `--description`, `--tz`, `--session`, `--light-context`,
    `--announce`, `--best-effort-deliver`, `--channel`, `--to`, `--timeout-seconds`, `--agent`, `--model`,
    `--fallbacks`, `--thinking`, `--tools`, `--trigger-script`, and more.
    ⚠️ **Do not pass the create positional argument (cron expression) into edit** — edit's positional argument is the job id.
  - Method B: `openclaw cron rm <job-id>` + `openclaw cron create ...`
- **11. Verify (cannot be skipped)**: confirm the live job's payload **actually changed**:
  ```bash
  openclaw cron list --json | python3 -c "
  import json,sys
  d=json.load(sys.stdin)
  for j in d['jobs']:
      if j['id']=='<job-id>':
          m=(j.get('payload') or {}).get('message','')
          print(j['id'][:8], j['name'], 'len=', len(m))
          print('contains new marker:', 'YOUR_NEW_MARKER' in m)
  "
  ```
  Also confirm the total job count did not increase (no accidental duplicate was created).

## ⛔ Forbidden Approach (incident verified on 2026-10-21)

**Never** take `build-cron.py`'s default output and do string replacement to assemble an edit command:

```python
# ❌ Never do this
edit_cmd = output.replace('openclaw cron create', 'openclaw cron edit <id>', 1)
```

Why (repeated failures on 2026-10-19/21 produced 4 duplicate jobs and deleted the copy that had the changes):

1. The default output uses **backslash line continuations**: `openclaw \⏎  cron \⏎  create \⏎  '15 7 * * *' ...`.
   The string `'openclaw cron create'` **does not match** (there are `\\\n  ` sequences in between), so the replace silently fails.
2. The failed replace means the command that actually runs is `openclaw cron create` → one more job every time.
3. Worse: the "new job with the changes" is then deleted as a duplicate, leaving the old-content job, so the changes never take effect.

**Symptom**: after an edit, `openclaw cron list` shows two jobs with the same name, and the new one is `idle` (never ran).

**Correct approach**: use `--json` to get the argv array and build the edit command as in Method A above.

**Another pitfall**: when rebuilding flags from argv, if the same flag appears twice (e.g. duplicate `--agent`),
commander treats the later flag's value as an extra positional argument and reports
`Too many arguments for this command`. Deduplicate by flag name before assembling.
Verified: `openclaw cron edit <id> --agent --agent main` always fails; `openclaw cron edit <id> --agent main` works.

**Another pitfall: edit really overwrites; do not use it for flag experiments**

`openclaw cron edit <id> --message "x"` **immediately overwrites the live job's message with "x"**.
**Do not experiment on production jobs** when verifying flag behavior — back up the message first:

```python
msg = (job['payload'] or {}).get('message') or ''
open('/tmp/msg-backup.txt','w').write(msg)   # restore after experimenting
```

## Safety Red Lines

- Confirm before deleting an old task (destructive operation)
- Keep the updated YAML under `$AAC_WORKSPACE/cron/`
- Keep the name in AAC format after editing
- Prefer `edit` to preserve the job ID and avoid losing state
- **After an edit, verify the payload actually changed** (step 11); do not trust the command's return code alone
- **Confirm the content before deleting a "duplicate" job**: compare both payloads with `--json`; the one being deleted may be the one with the changes
- Always add `--json` when rendering commands
