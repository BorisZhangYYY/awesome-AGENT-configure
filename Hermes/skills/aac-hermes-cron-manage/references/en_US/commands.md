# Commands and acceptance

[简体中文](../zh_CN/commands.md) | English

Run everything inside the target `HERMES_HOME` or `hermes -p PROFILE` scope. `hermes cron` subcommands have no `--json`; read the text output of `list` and `runs` instead of inventing flags.

## 1. Read-only inspection

```bash
hermes cron list --all          # includes disabled and completed jobs
hermes cron status              # is the scheduler running, next tick
hermes cron runs --limit 20     # recent execution attempts
hermes cron runs <JOB_ID> --limit 5
hermes cron doctor              # common health problems
hermes cron incidents           # failure incidents, acknowledge individually
```

- Names are not unique; **IDs are**. Every `pause/resume/run/edit/remove` uses the ID you read back.
- When `list` shows nothing, check the scope first: default home, explicit `HERMES_HOME`, or a named profile.

## 2. Compiler output

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/en_US/cron-template/reminders/morning/morning.yaml --validate
python3 .../build-cron.py <scene> --preview     # rendered job and argv
python3 .../build-cron.py <scene> --json        # argv only
python3 .../build-cron.py <scene> --tool-json   # cronjob_manage request
python3 .../build-cron.py <scene> --plan        # ordered cross-lane plan
python3 .../build-cron.py <scene> --test        # paused one-shot 'in 1m' job
python3 .../build-cron.py --catalog             # every scene in this repository
python3 .../build-cron.py --check-cli           # read-only checks to run before deploying
```

`--home PATH` and `--profile PROFILE` are mutually exclusive; `--set KEY=YAML_VALUE` is repeatable for temporary overrides. Every mode prints only; nothing is executed.

## 3. Create

```bash
# review first
python3 .../build-cron.py <scene> --preview
# then run the reviewed command
env HERMES_HOME=$HOME/.hermes hermes cron create "0 8 * * *" "<rendered prompt>" \
  --name "[AAC-Reminder] Morning" --deliver local --catch-up off
```

- To stage a job, create it with `--paused --paused-reason "..."` and resume later.
- Immediately read back ID, name, schedule, delivery, and pause state with `hermes cron list --all`.

## 4. Edit, pause, resume, remove

```bash
hermes cron edit <JOB_ID> --schedule "0 9 * * *" --prompt "<new prompt>"
hermes cron pause <JOB_ID>
hermes cron resume <JOB_ID>
hermes cron run <JOB_ID>            # queues for the next tick; not an immediate completion
hermes cron cancel <JOB_ID>         # stops a live run, leaves the schedule alone
hermes cron remove <JOB_ID>
```

- Always update via `edit` to keep the ID; recreating loses run history and `context_from` references.
- Clearing: `--script ""`, `--workdir ""`, `--monitor-url ""`, `--clear-skills`; lists take `[]`.
- `pause` / `resume` are lifecycle commands, not substitutes for `edit --paused`.

## 5. Acceptance checklist

1. **Same ID**: identical before and after the edit, still visible in `list --all`.
2. **Fields**: read back schedule, timezone, delivery and failure delivery, catch-up, mode, script/monitor, tool limits, pause state.
3. **Script parity**: the file under `$HERMES_HOME/scripts/aac/` matches the repository copy byte for byte.
4. **Run history**: `runs <JOB_ID>` shows this attempt with the expected exit code and stdout/stderr.
5. **Scheduler health**: `status` is healthy and `doctor` reports nothing new.
6. **Real fire**: when it matters, wait for an actual tick to prove scheduled execution rather than a manual `run`.

If any item is missing, report "partially done" — never "live".

## 6. Common misreadings

| Observation | What it actually means |
|-------------|------------------------|
| Jobs listed but never firing | The scheduler is not running, or the job is paused |
| `run` succeeded | The job is queued for the next tick, not finished |
| The script works by hand | Says nothing about the scheduled path: env, cwd, and interpreter may differ |
| `[SILENT]` | The scene decided there was nothing to report, not a failure |
| `[CRON_FAILURE]` on the first line | The run failed; the rest explains the blocker |
| A report file exists | Disk write succeeded; it does not prove the conclusions |
