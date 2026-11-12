# Native parameter reference

[简体中文](../zh_CN/native-parameters.md) | English

The target installation's `hermes cron create --help` and `hermes cron edit --help` are authoritative; this table only maps template fields onto command flags and tool arguments.

## 1. Field table

| Scene `job` field | CLI flag | Tool argument | Type | Default | Notes |
|---|---|---|---|---|---|
| `schedule` | positional | `schedule` | string | required | `30m` interval, `in 30m` one-shot, `0 9 * * *` cron, `every monday 9am` |
| `name` | `--name` | `name` | string | none | `[AAC-Category]` prefix recommended; names are not unique and are not IDs |
| `deliver` | `--deliver` | `deliver` | string | creating chat | templates use `local`; external delivery needs separate approval |
| `failure_deliver` | `--failure-deliver` | `failure_deliver` | string | follows `deliver` | overrides failure notices only; `local` suppresses them |
| `repeat` | `--repeat` | `repeat` | integer | forever for recurring, once for one-shot | cap for one-shot jobs |
| `catch_up` | `--catch-up on\|off` | `catch_up` | boolean | config-dependent | templates use `false`; missed runs are skipped |
| `skills` | `--skill` (repeatable) | `skills` | list of strings | empty | `[]` clears on edit; CLI uses `--clear-skills` |
| `script` | `--script` | `script` | path | none | relative to `$HERMES_HOME/scripts/`; escapes and symlink escapes are rejected |
| `no_agent` | `--no-agent` | `no_agent` | boolean | `false` | requires `script`; incompatible with monitor |
| `monitor_script` | `--monitor-script` | `monitor` | path | none | mutually exclusive with `monitor_url` |
| `monitor_url` | `--monitor-url` | `monitor` | http(s) URL | none | mutually exclusive with `monitor_script` |
| `workdir` | `--workdir` | `workdir` | absolute path | none | injects context files and sets cwd |
| `timezone` | `--timezone` | `timezone` | IANA name | profile timezone | cron expression is read in that zone |
| `continuity` | `--continuity` / `--no-continuity` | `continuity` | boolean | `false` | injects this job's previous output; not persistent state |
| `paused` | `--paused` | `paused` | boolean | `false` | create disabled; resume with `hermes cron resume` |
| `paused_reason` | `--paused-reason` | `paused_reason` | string | none | requires `paused: true` |
| `pinned` | `--pin` / `--unpin` | `pinned` | boolean | `false` | locks the current main model; conflicts with `model` |
| `grace_minutes` | `--grace-minutes` | unsupported | integer 0–1440 | half the period, clamped 2–120 | catch-up window; `0` never catches up |
| `model` | `--model` | unsupported | string | follows cron/main model | pin a model only on request |
| `provider` | `--provider` | unsupported | string | follows model | must accompany `model` |
| `reasoning_effort` | `--reasoning-effort` | unsupported | enum | follows config | `none`/`minimal`/`low`/`medium`/`high`/`xhigh`/`max`/`ultra` |
| `interpreter` | `--interpreter` | unsupported | path | Hermes Python | `.py` scripts only; point at your own venv |
| `context_from` | unsupported | `context_from` | list of strings | empty | chains other jobs' output; tool lane only |
| `enabled_toolsets` | unsupported | `enabled_toolsets` | list of strings | all default tools | `[]` is an explicit zero-tool allowlist |
| `attach_to_session` | unsupported | `attach_to_session` | boolean | unset | continuable delivery; no effect with `deliver: local` |

## 2. Where each lane stops

- **CLI lane** (`hermes cron create/edit`) can set `model`, `provider`, `reasoning_effort`, `interpreter`, `grace_minutes`; it cannot set `context_from`, `enabled_toolsets`, `attach_to_session`.
- **Tool lane** (`cronjob_manage`) is the mirror image: it handles the last three and cannot set the first five. On the tool side `monitor_script` and `monitor_url` collapse into a single `monitor` field.
- Config that needs both lanes goes through `--plan`: create paused on the CLI, read back the real ID, bind it into the tool request, read the fields back, and resume only with approval.
- A field the chosen lane cannot express must fail loudly. `build-cron.py --tool-json` errors on CLI-only fields rather than dropping them.

## 3. Booleans and clearing

- `null` or omission means "leave unchanged".
- Clear strings with `''`; clear `skills` and `context_from` with `[]`.
- Mode switches need the explicit opposite: `--agent` to leave no-agent mode, `--no-continuity` to stop continuity, `--unpin` to release a model lock.
- `enabled_toolsets: []` means "no tools at all", which is not the same as "unset".

## 4. What the compiler rejects

Before emitting a command, `build-cron.py` rejects: unknown fields, booleans written as strings, lists written as scalars, `no_agent` without `script`, both monitor fields at once, a non-http(s) `monitor_url`, a `script` escaping `$HERMES_HOME/scripts`, `paused_reason` without `paused`, `model` together with `pinned`, `provider` without `model`, an out-of-range `reasoning_effort`, `grace_minutes` outside 0–1440, and duplicate YAML keys. Errors go to stderr only, leaving stdout empty so callers can branch on exit status.
