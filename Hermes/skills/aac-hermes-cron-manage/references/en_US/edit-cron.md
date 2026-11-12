# Edit Without Replacing Identity

[简体中文](../zh_CN/edit-cron.md) | English

## Read Before Writing

Use `terminal` with the correct `hermes -p PROFILE cron ...` prefix or explicit `HERMES_HOME`; never mix profiles between read and write. List first (`list --all`, or public tool `action: list`), select the full immutable ID, and record the existing fields and enabled state. Native CLI may resolve names, but this workflow never relies on names or ID prefixes. Public tool listing is useful when CLI display omits a requested field; do not invent `list --json` or `get` commands.

Pause before a risky mode/script/prompt migration if authorized. Pausing prevents future scheduling; it does not replace `cancel` for a live run. Record the prior state so an already-paused job is not accidentally resumed. Preserve the job's ID, delivery, catch-up, skills, permissions, and model policy unless changes are requested.

## Compile a Same-ID Update

Use `terminal` from the repository root:

```bash
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/en_US/cron-template/reminders/morning/morning.yaml \
  --edit JOB_ID --preview
python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py \
  Hermes/en_US/cron-template/reminders/morning/morning.yaml \
  --edit JOB_ID --json
```

`JOB_ID` is a placeholder for the exact verified ID. `--edit` emits native `edit` or tool `action: update`, not delete/create, and binds `LOOP_JOB_ID` to its own target ID. Inspect the full field diff: a fully populated scene can replace more than the one field you intended. Use a sparse native edit for a single-field repair when appropriate.

`paused` and `paused_reason` are create-only native fields, not edit flags. Remove scene-level create directives for a normal edit; compiler-inherited null placeholders mean omit. Use explicit lifecycle commands, or a reviewed `--plan` that contains lifecycle steps, rather than pretending `edit --paused` exists. Never send create-only fields in an `update` request.

## Omission, Clears, and Mode Changes

| Intent | Native CLI / public tool |
|---|---|
| Leave unchanged | Omit; compiler `null` emits nothing |
| Clear optional string | Pass `''` for supported fields such as script, monitor, workdir, timezone, failure delivery; CLI-only pins also have documented empty-string clears |
| Replace/remove skills | Repeat `--skill`, `--add-skill`, `--remove-skill`, or `--clear-skills`; tool `skills: []` clears |
| Remove upstream context | Tool `context_from: []`; `continuity: false` only removes self context |
| Restrict to no tools | Tool `enabled_toolsets: []` is ZERO tools, not a reset to defaults |
| Resume agent inference | `--agent` / `no_agent: false` |
| Disable continuity | `--no-continuity` / `continuity: false` |
| Disable continuable delivery | Tool `attach_to_session: false` |
| Release model lock | `--unpin` / `pinned: false`, only on explicit user instruction |

A null or omitted field does not clear an existing runtime value. In particular, default template nulls cannot undo a previous script, monitor, workdir, or pin. Public tool `monitor: ''` clears both monitor sources; CLI must explicitly clear the old source when switching script/URL transports.

Native CLI mode-transition examples below are output for review, not authorization to execute:

```bash
hermes cron edit JOB_ID --agent --script '' --monitor-script aac/change-monitor.py
hermes cron edit JOB_ID --monitor-script '' --monitor-url '' --script aac/script-only.py --no-agent
hermes cron edit JOB_ID --monitor-script '' --monitor-url 'https://example.com/status'
```

When moving to monitor mode, explicitly disable `no_agent`; when moving to script-only, clear every monitor source. Check the merged effective job, not just the update payload. `no_agent` and a monitor are incompatible.

## Mixed Interfaces and Readback

CLI rejects every non-null tool-only value, even `false` or `[]`; the public tool rejects every non-null CLI-only value, even `''`. Use `--plan` for mixed updates. All steps must target the same immutable ID and scope, preserve paused state unless intentionally changed, stop on errors, and read back the result before any resume. A plan only describes operations; the operator dispatches them separately.

After an authorized edit, list/read that exact job and compare every requested field, the ID, enabled state, and next run. Run an authorized canary and check history as needed. Do not call a job repaired while it remains blocked, or resume it merely because compilation succeeded. See [commands and acceptance](commands.md).
