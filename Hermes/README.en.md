# Hermes Identity, Cron, and Loop Templates

> Identity files, native scheduled tasks, and stateful progress templates. Compilation does not install files, create jobs, or change a running Hermes instance.

[简体中文](README.md) | English

## Language Versions

| Version | Directory |
|---------|-----------|
| Chinese | `zh_CN/workspace-template/` |
| English | `en_US/workspace-template/` |

Cron scenes live in `zh_CN/cron-template/` and `en_US/cron-template/`; the shared skill is [aac-hermes-cron-manage](skills/aac-hermes-cron-manage/SKILL.md). Hermes and OpenClaw have independent templates, compilers, and skills; OpenClaw uses `aac-openclaw-cron-manage`. Do not interchange flags or silence tokens.

## File Responsibilities

- `SOUL.md`: persona, communication style, and workspace management conventions. The directory categories and retention periods are conventions of this template, not framework requirements; nothing creates directories or scheduled tasks automatically.
- `memories/USER.md`: user profile and preferences. Published templates should contain only a generic skeleton or placeholders.
- `memories/MEMORY.md`: long-lived environment facts and conventions, which Hermes's `memory` tool can maintain later.

## Identity Template Usage

1. Confirm the target Hermes home: the default is `~/.hermes/`; when using a custom home or profile, follow that instance's `$HERMES_HOME` and do not overwrite other profiles.
2. Back up the target files, then copy or merge the files from `workspace-template/` into the target home as needed, preserving relative paths. Do not overwrite an accumulated user profile or long-term memory.
3. Edit the persona and workspace conventions in `SOUL.md`; fill in the name, preferred name, and timezone in `memories/USER.md` (`Asia/Shanghai` is only an example). Leave `memories/MEMORY.md` as the initial long-term memory skeleton.
4. Start a new session so the updated files are loaded.

The target paths are `$HERMES_HOME/SOUL.md`, `$HERMES_HOME/memories/USER.md`, and `$HERMES_HOME/memories/MEMORY.md`. `~/.hermes` in `SOUL.md` is the default-home example; adjust it when using another home.

## Cron Quick Start

Run from the repository root with Python 3 and PyYAML installed. These commands validate and preview only; they do not execute the generated command:

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/en_US/cron-template/reminders/morning/morning.yaml --validate
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/en_US/cron-template/reminders/morning/morning.yaml --preview
```

- Scenes cover reminders, checks, learning, project progress, `scripts/script-only/`, and `monitors/change-monitor/`. Override variables with `--set KEY=YAML_VALUE`; select a target with either `--home PATH` or `--profile PROFILE`, never both.
- Default output is a shell command; `--json` emits argv, `--tool-json` a public tool request, and `--plan` ordered CLI/tool steps. Nothing executes. Non-null fields unsupported by the selected interface fail rather than disappear.
- `--test` generates a paused, local, one-shot `in 1m` job with `repeat: 1` and catch-up off. Explicit authorization and `run` are required; automatic deletion is not promised. Review and copy scripts separately into the target `$HERMES_HOME/scripts/aac/`; the compiler does not install them.
- Create paused, read back the real ID and settings, then test and resume as authorized. Update with `--edit JOB_ID` to preserve identity, never delete/recreate. Native CLI pause/resume are lifecycle commands, not an edit `--paused` flag.

## Harness and Loop

Harness supplies self-contained instructions, evidence, permission boundaries, and failure reporting. Loop advances one verifiable milestone per run and saves progress in a separate state file. Each default run starts a fresh session with no current-chat context; `continuity` injects previous output, not persistent structured state.

Configure Loop with `LOOP_MODE_ENABLED`, `LOOP_TASK_TYPE`, `LOOP_PROJECT_DIR`, `LOOP_STATE_FILE`, `LOOP_GOAL`, and list-valued `LOOP_MILESTONES`. Safe defaults are `LOOP_AUTO_PAUSE: false` and `LOOP_JOB_ID: ''`. For self-pause, first create paused with auto-pause off, read the real ID, use `--edit` on that same ID to bind it and explicitly enable auto-pause, then resume. Never discover a target by name. Do not globally enable `cron.allow_agent_scheduling` merely for self-pause.

See [templates, scripts, and Loop](skills/aac-hermes-cron-manage/references/en_US/cron-template-guide.md), [native parameters](skills/aac-hermes-cron-manage/references/en_US/native-parameters.md), and [commands and acceptance](skills/aac-hermes-cron-manage/references/en_US/commands.md).

## Notes

- Do not commit real credentials, private material, chat logs, or live memory files to a public repository.
- Templates default to `catch_up: false`; model/provider pins require an explicit user choice. An agent with nothing to report returns `[SILENT]`; failures put `[CRON_FAILURE]` alone on the first line. Empty script stdout is quiet; a nonzero exit means failure.
- `no_agent` uses no AI and cannot coexist with a monitor. A monitor's first tick establishes a baseline; subsequent identical stdout suppresses the agent. Do not put clock values or other unstable data in monitor output.
- No automatic Git commit/push, Docker startup, raw `jobs.json` edits, or gateway restart. Authoring, previewing, and validating templates does not prove installation or a scheduled execution.

## Official References

- [Which file does what](https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what)
- [Persistent memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
- [Native cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron); reconcile options with the target installation's `hermes cron create/edit --help` and public `CRONJOB_SCHEMA`.
