# Template and Loop guide

[简体中文](../zh_CN/cron-template-guide.md) | English

The template has two layers: `Hermes/{zh_CN,en_US}/cron-template/template-cron.yaml` (shared constraints) and the scene YAMLs (task instruction plus variables). Scenes describe only their own job; anything repeated stays in the parent template.

## 1. Layout

```
Hermes/en_US/cron-template/
├── template-cron.yaml              # parent: variable defaults, native job defaults, Harness and Loop sections
├── reminders/<name>/<name>.yaml    # personalized reminders, agent mode
├── checks/<name>/<name>.yaml       # read-only checks, daily report
├── projects/<name>/<name>.yaml     # Loop work, paused by default
├── learns/<name>/<name>.yaml       # study cadence, notes
├── scripts/script-only/            # no_agent script job, runnable script included
└── monitors/change-monitor/        # monitor_script change detection, script and source included
```

A scene file has exactly three top-level keys: `templateRef`, `variables`, `job`. `templateRef` must be `"../../template-cron.yaml"`, resolved from the scene directory.

## 2. Variables and placeholders

- Placeholders use `{{UPPER_SNAKE_CASE}}` and are replaced by value: lists and mappings render as JSON, booleans as `true` / `false`.
- An undefined variable is an error; it is never rendered as an empty string or left in place.
- Variables may reference other variables; cycles are rejected.
- Precedence: `--set KEY=YAML_VALUE`, then scene `variables`, then parent defaults.
- `HERMES_HOME` is injected by the compiler; never define it in a scene.

## 3. Conditionals

The parent template supports nestable conditionals:

```yaml
{{#if LOOP_MODE_ENABLED}}
rendered only for Loop scenes
{{#if LOOP_AUTO_PAUSE}}
rendered only when self-pause is on
{{/if}}
{{/if}}
```

Truthiness follows YAML: `false`, `""`, `0`, and `[]` are false. An unclosed `{{#if}}` fails the build.

## 4. The Harness section

The shared constraints are the floor for every scene; editing them changes every job's behaviour:

- Fresh session: no chat context, no questions, self-contained output.
- Evidence first: cite only what this run actually read; state gaps.
- Authorization: no Git commit or push, no container lifecycle changes, no Hermes config or jobs.json edits, no dependency installs.
- Output is the delivery: the final response goes to local delivery; do not call an external sender.
- Reports: `{{HERMES_HOME}}/docs/reports/<topic>/<YYYY-MM-DD>.md`, appended on repeat runs.
- Failure wording: `[SILENT]` when idle, `[CRON_FAILURE]` alone on the first line when blocked.

After changing this section, run `python3 -m unittest discover -s tests/hermes` and read one `--preview` end to end.

## 5. Loop mode

A Loop scene describes its work with five variables: `LOOP_TASK_TYPE`, `LOOP_GOAL`, `LOOP_MILESTONES` (at least three), `LOOP_PROJECT_DIR`, `LOOP_STATE_FILE`. The template then adds these rules:

1. Read the state file first; create it when missing.
2. Advance one verifiable milestone per run, write the state back, then report.
3. Completion needs evidence, never "attempted".
4. A corrupt state file is rebuilt with a state-loss event recorded.
5. When all milestones are done, recommend stopping the job; never rewrite the schedule.
6. Two runs without progress must report the blocker.

`LOOP_AUTO_PAUSE` and `LOOP_JOB_ID` are the self-pause switch and binding, defaulting to `false` and an empty string. Bind by creating paused, reading back the real ID, then editing that same ID; never guess a job by name.

## 6. Scripts and monitors

- Scripts must live inside the target `$HERMES_HOME/scripts/`, symlink targets included; the compiler rejects `..` escapes and links pointing outside.
- The compiler only prints commands; it copies nothing. Review the file, then install it as `$HERMES_HOME/scripts/aac/<name>` with identical bytes.
- `no_agent` requires `script`, ignores the prompt and skills, and delivers stdout verbatim: empty means silence, a non-zero exit means failure.
- `monitor_script` and `monitor_url` are mutually exclusive and neither works with `no_agent`; monitor output must be stable or every tick looks changed.
- For third-party dependencies point `interpreter` at a venv Python instead of touching the system interpreter.

## 7. Adding a scene

1. Create `Hermes/{zh_CN,en_US}/cron-template/<category>/<name>/` with a same-named YAML in both locales.
2. Keep `templateRef`, `variables`, `job`; use upper-case variable names and keep both locales' variable and placeholder sets identical.
3. Always state `deliver: local` and `catch_up: false`; add `paused: true` with `paused_reason` when the job must not run yet.
4. Run `build-cron.py <scene> --validate`, then read `--preview` yourself.
5. Register the scene in `SCENES` inside `tests/hermes/test_scenes.py`, add its assertions, and run the full suite.

## 8. Anti-patterns

| Practice | Consequence |
|----------|-------------|
| Duplicating the shared constraints inside a scene | Two sources drift; one edit misses the other |
| Writing `{{lower_case}}` or empty `{{ }}` | Renders nonsense without failing; tests catch it |
| Shipping only one locale | Variable/placeholder parity fails |
| Putting credentials, real IDs, or internal hosts in a template | Templates land in a public repository |
| Letting the compiler execute or install | Breaks the print-only contract and the audit trail |
