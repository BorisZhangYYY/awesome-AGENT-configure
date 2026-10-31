# OpenClaw Trigger Sandbox Limitations

> This document is a **hard constraint** for developing AAC cron trigger scripts.
> Read it before modifying `scripts/trigger.js` or adding a scene `.js`.

## Sandbox Environment

OpenClaw Gateway (2026.7.1+) evaluates `--trigger-script` in a **code-mode sandbox**:

- Engine: **QuickJS-WASI** (isolated environment, no ICU data)
- Language: ES2022 pure JavaScript (TypeScript is transpiled)
- Entry point: the script's top level `return`s an object; `{ fire: true }` runs the task, `{ fire: false }` skips it

## Forbidden APIs

| API | Status | Consequence | Alternative |
|-----|--------|-------------|-------------|
| `Intl.*` (DateTimeFormat, etc.) | ❌ No ICU | `ReferenceError: Intl is not defined` | Inject `AAC_TZ_OFFSET_MINUTES` at build time and use pure Date offset arithmetic |
| `require()` / `import` | ❌ Statically rejected | `ToolInputError: code mode module access is disabled` | None; do not depend on any module |
| `fs` / `path` / `child_process` / `os` | ❌ Modules disabled | Same as above | Move file/process work into the Agent Prompt (exec/read/write tools) |
| `process` global | ❌ Undefined | `ReferenceError: process is not defined` | Configuration is injected by build-cron.py as `const` constants |
| `fetch` / network APIs | ❌ Undefined | `ReferenceError` | Move network checks into the Agent Prompt |
| `setTimeout` / `setInterval` | ❌ Undefined | `ReferenceError` | Triggers must return synchronously |

## Available APIs

- ES2022 language features: `Date` / `Math` / `JSON` / `String` / `Array` / `Object` / template literals / destructuring, etc.
- Top-level `return` (a code-mode feature)

## Correct Timezone Conversion

IANA timezone conversion needs a tz database, which is **impossible inside the sandbox**. AAC's approach:

1. `build-cron.py` uses Python `zoneinfo` at build time to compute the timezone's current UTC offset;
2. It injects a constant `const AAC_TZ_OFFSET_MINUTES = 480;` (Asia/Shanghai in this example);
3. trigger.js does pure Date arithmetic: `new Date(Date.now() + offset * 60000)` and then reads with `getUTC*()`.

> ⚠️ **Daylight saving warning**: the offset is frozen at build time. Timezones with DST (e.g. America/New_York) need the task rebuilt after a transition to refresh the offset; timezones without DST (e.g. Asia/Shanghai) remain valid permanently.
> When `AAC_TZ_OFFSET_MINUTES` is not injected, trigger.js falls back to the Gateway host's local time.

## Failure Symptoms and Troubleshooting

Using a forbidden API in the sandbox makes **trigger evaluation fail outright**:

```text
status: error (Nx)
last error: cron trigger evaluation failed (internal_error): ReferenceError: ...
```

The Agent session **never starts** — no report, no notification, no deduplication marker; only the cron error count grows.

Troubleshooting commands:

```bash
openclaw cron list                          # check the status column
openclaw cron show <job-id>                 # check last error
```

## Historical Incidents

- **2026-07-15**: trigger.js used `require('fs')` for deduplication → all task evaluations failed. Fix: move deduplication into the Agent Prompt.
- **2026-07-19**: trigger.js used `Intl.DateTimeFormat` for timezone conversion → three check tasks all failed evaluation (error 4x~7x). Fix: inject the UTC offset at build time.

## Development Red Lines

1. **Only pure ES2022 JS is allowed** — before finishing, ask yourself: would this code run in a browser `vm` environment without ICU?
2. **Test every new API before using it**: verify trigger evaluation with `openclaw cron run --wait <job-id>`.
3. **Inject configuration at build time**: use a `const XXX = ...;` preamble; never probe the environment at runtime.
4. **File/network/process needs → move them into the Agent Prompt**; triggers only make a lightweight fire/skip decision.
