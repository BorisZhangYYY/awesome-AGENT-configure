---
name: aac-hermes-cron-manage
description: Create, verify, and update native Hermes cron templates.
version: 0.1.0
author: BorisZhangYYY, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, templates, harness, loop]
---

# AAC Hermes Cron Manager

[简体中文](SKILL.zh_CN.md) | English

Manage Hermes-native scheduled tasks from this repository's bilingual YAML templates. The compiler emits commands or requests; it never executes them or installs scripts. OpenClaw's independent skill is `aac-openclaw-cron-manage`; do not reuse its schema here.

## When to Use

- Initialize a reminder, check, learning routine, project Loop, script-only task, or change monitor.
- Edit, migrate, or refresh an existing Hermes job while preserving its immutable ID.
- Do not use for OpenClaw jobs, identity-file installation, or unapproved live scheduler/configuration changes.

## Prerequisites

Use Python 3 plus PyYAML, a checkout containing `Hermes/{zh_CN,en_US}/cron-template/`, and the target Hermes CLI. Resolve the intended home/profile before any installation. The compiler is `Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py`, relative to the repository root; use an absolute checkout path when installed elsewhere.

Read the target CLI help and public `tools/cronjob_tools.py::CRONJOB_SCHEMA` as text before promising field support. Do not import live Hermes modules to inspect a schema. No credentials belong in templates or emitted public examples.

## How to Run

Use `terminal` for the compiler and CLI; use `read_file`, `write_file`, `patch`, and `search_files` for template work. For a read-only preview from the repository root:

```python
terminal(command="python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py Hermes/en_US/cron-template/reminders/morning/morning.yaml --preview", timeout=60)
terminal(command="hermes cron create --help && hermes cron edit --help", timeout=60)
```

`--validate`, `--preview`, `--json`, `--tool-json`, `--plan`, `--catalog`, and `--check-cli` are inspection/output modes, not deployment. `--edit JOB_ID` emits an update, never a create. `--set KEY=YAML_VALUE` preserves booleans/lists. Choose either `--home PATH` or `--profile PROFILE`.

## Procedure

1. Resolve scope and inspect existing jobs via `hermes [-p PROFILE] cron list --all` and `status`. During repository-only development use help/source/fixtures, not live mutations. Record exact IDs, current policies, delivery, and permissions; names are not unique.
2. Read the matching guide: [initialize](references/en_US/init-cron.md), [edit](references/en_US/edit-cron.md), [migrate](references/en_US/migrate-cron.md), or [update templates](references/en_US/update-cron.md). Consult [template/Loop guide](references/en_US/cron-template-guide.md), [native fields](references/en_US/native-parameters.md), and [commands](references/en_US/commands.md).
3. Select a scene, fill generic variables, and inspect the complete prompt and typed job. Keep `catch_up: false`, explicit delivery, and unpinned models unless the user requests otherwise. Do not auto-commit/push, restart Docker, or alter gateway services.
4. Validate both the selected backend and runtime prerequisites. CLI cannot carry `context_from`, `enabled_toolsets`, or `attach_to_session`; public tools cannot carry explicit model/provider, reasoning, interpreter, or grace pins. Use `--plan` for mixed fields; stop on any unsupported option rather than dropping it.
5. Only after authorization, review/copy scripts into the target home's `scripts/`, create paused, and read back the exact returned ID. For mixed create plans, bind that real ID before tool updates; never execute an unresolved placeholder. For edits, preserve the ID and previous paused state. Stop the sequence on any failure.
6. Run only the authorized canary. `--test` merely emits a paused local one-shot, `in 1m`, repeat one, catch-up off; an explicit `run` is still required and automatic deletion is not guaranteed. Read the exact job and execution history before resuming or cleaning up.

## Pitfalls

- Every agent run is a fresh session: no current-chat context or autonomous clarification. The final response is delivered automatically; do not send it twice. `[SILENT]` alone means no report; `[CRON_FAILURE]` alone on line one declares failure.
- `no_agent: true` requires `script`, ignores prompt/skills, and uses no LLM. Empty stdout is quiet; nonzero exit/timeout fails. It cannot coexist with monitor mode. A pre-run script may use final-line JSON `{"wakeAgent": false}` to skip inference.
- A monitor runs its baseline on the first tick; unchanged exact-byte output suppresses the agent. Keep output stable. Scripts must resolve inside the target `$HERMES_HOME/scripts/`, including symlink targets.
- `null`/omission means no edit; `''` clears supported string fields, `skills: []` and `context_from: []` clear lists. `enabled_toolsets: []` means ZERO tools, not default tools. Change execution modes with explicit false/clear values.
- Loop needs a durable state file; `continuity` is only previous-output context. Auto-pause defaults off. Enable it only after paused creation, real-ID readback, and a same-ID `--edit` binding. Never select self by name or globally enable `cron.allow_agent_scheduling` just for this feature. Use the exact target home/profile for pause and readback; if unavailable, report completed-awaiting-operator-pause.
- Never edit native `jobs.json`, assume OpenClaw flags exist, or treat a successful compile/manual run as a hosted scheduled run.

## Verification

Read back the exact target after every authorized write: same ID, prompt, schedule/timezone, delivery/failure delivery, catch-up, skills, mode, script/monitor, tool restrictions, pin policy, and paused/enabled state. Separately verify installed bytes, script exit/stdout/stderr, run history, scheduler health, and an actual scheduled run if requested. Report verified work and remaining blockers; do not claim deployment from generated output.
