# Initialize a Hermes Job

[简体中文](../zh_CN/init-cron.md) | English

## Discover and Decide

1. Resolve one target: default home, explicit `HERMES_HOME`, or named profile. The global prefix is `hermes -p PROFILE cron ...`, not `hermes cron --profile ...`.
2. Through `terminal`, inspect `hermes cron create --help`, `hermes cron edit --help`, `hermes cron list --all`, and `hermes cron status` in that same scope. List includes disabled/completed candidates; preserve an existing matching ID instead of creating a duplicate. Repository authoring requires no live job inspection or mutation.
3. Confirm schedule, timezone, concrete delivery, failure delivery, mode, workdir, skills/tool access, catch-up, and acceptance criteria. Keep catch-up off and model/provider unpinned unless explicitly requested. Bare duration `30m` recurs; `in 30m` is once.
4. Select the matching language scene under `Hermes/{zh_CN,en_US}/cron-template/`. See [template guide](cron-template-guide.md) and [native inventory](native-parameters.md).

## Compile Without Deploying

From the repository root, using `terminal`:

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/en_US/cron-template/reminders/morning/morning.yaml --preview
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/en_US/cron-template/reminders/morning/morning.yaml --test --json
```

Inspect the full prompt, typed fields, scope, and destination. `--test` changes the emitted job to a paused local one-shot (`in 1m`, repeat one, catch-up false), not an automatic execution or cleanup. For normal deployment, set native `job.paused: true` and a reason in your scene before compiling. Do not pipe compiler output into a shell as an unattended installation step.

`--json` emits CLI argv. `--tool-json` emits `{name: cronjob_manage, arguments: {...}}` and must be dispatched in the intended profile's tool session. For configurations spanning both interfaces, use `--plan`: create paused through CLI, read the actual returned ID, bind the plan's ID placeholder, apply tool-only updates, read back every field, and resume only if authorized. A plan is not an executor; errors stop the sequence. See [editing](edit-cron.md) for clearing and mode changes.

## Install and Verify Only with Authorization

1. Review any co-located script; copy it explicitly into the target `$HERMES_HOME/scripts/aac/`. Check existing destination content before replacement, path confinement, dependencies, file permissions, and bytes. The compiler does not install anything. For Python dependencies, select an absolute Python interpreter only with user approval; shell scripts require bash. See [script/monitor installation](cron-template-guide.md).
2. Execute the reviewed paused create command/request once. Capture its returned ID, list/read back that exact ID, and verify it is disabled with the intended settings. Do not infer identity from a name.
3. If requested, explicitly `run` that ID, then inspect its durable run history and result. Check script/application access separately; a quiet success may be an intentional offline skip. A manual dispatch acknowledgment is not completion, and manual execution is not proof of automatic scheduling.
4. Resume only after acceptance and authorization. Read back enabled state, next run, and scheduler health. Do not start/restart/install gateway services unasked. A paused test canary is still runnable by an operator and is not an execution security boundary.
5. Report ID, target scope, verified fields and evidence, remaining prerequisites, and the agreed canary cleanup policy. Never promise automatic deletion.
