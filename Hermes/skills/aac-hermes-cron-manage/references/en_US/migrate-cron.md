# Migrate to Native Hermes Templates

[简体中文](../zh_CN/migrate-cron.md) | English

## Preserve Intent, Not Foreign Fields

Inventory the source job's exact identity, trigger, timezone, prompt, delivery, dependencies, skills/tools, missed-run policy, runtime state, and side effects. Read the target installation's help and public schema before mapping anything. Never import a foreign job object into Hermes's store or edit `jobs.json` directly.

| Source concept | Hermes mapping / boundary |
|---|---|
| Recurrence or delayed reminder | `schedule`; distinguish recurring `30m` from one-shot `in 30m` |
| Session targeting, main-session wake | No equivalent compiler field; Hermes agent runs are fresh sessions, not current-chat continuations |
| Message/payload | Self-contained `prompt`; skills are ordered supporting instructions |
| Announcement channel and recipient | Concrete `deliver` string; failure routing is separate `failure_deliver` |
| Model, thinking, fallback flags | User-approved CLI `model`/`provider` and `reasoning_effort` where appropriate; no invented generic fallback/timeout flags |
| Trigger JavaScript | Rewrite as an audited Hermes script or monitor if needed; QuickJS trigger code is not a Hermes trigger |
| Silence / explicit failure | Agent `[SILENT]`; first-line `[CRON_FAILURE]`; script empty stdout / nonzero exit |
| Persistent project Loop | Durable state file plus self-contained prompt, optional `continuity`; no claim of a persistent agent session |
| Automatic completion pause | Two-stage real-ID binding and explicit scoped permission; default operator pause |

OpenClaw's `--session`, `--wake`, `--message`, `--thinking`, `--timeout-seconds`, `--announce`, `--channel`, `--to`, `--delete-after-run`, `--trigger-script`, and `--fallbacks` are not Hermes create/edit flags. Do not translate tokens mechanically. The independent OpenClaw skill is `aac-openclaw-cron-manage`; do not alias it to this skill.

## Same-Framework Migration

For an existing job in the same Hermes home/profile, keep its immutable ID and use `--edit JOB_ID`. Record its prior pause state and all policies before changing it. Reconcile source/template defaults with runtime values explicitly: null omits an update, not a clear. Preserve model ownership and delivery, and use [edit semantics](edit-cron.md) for mode changes and list/string clears.

When moving to another home/profile, the destination has its own job store, skills, scripts, credentials, and gateway context. Create a new paused destination job and record the old-to-new ID mapping; never claim ID preservation across independent stores. Copy reviewed dependencies separately into the destination's confined `scripts/` tree. Rewrite `context_from` references only after reading real destination IDs. Do not copy credentials into templates or carry source absolute script paths into another home.

## Cut Over Without Double Execution

1. Build a template in the intended language, preview all typed fields, and choose CLI, tool, or `--plan` according to [native coverage](native-parameters.md). Compilation is offline output, not deployment.
2. With authorization, create the destination paused (or pause the existing same-ID job for migration). Keep Loop auto-pause off until the actual job ID is read back and bound with `--edit`.
3. Test script bytes, dependencies, application access, permissions, output, and concrete delivery separately. An explicit canary `run` can have real side effects even while paused; obtain consent.
4. Pause the old schedule at the approved cutover point, account for any live run (`cancel` only if authorized), and read back both scopes before resuming the destination. Keep rollback evidence; do not remove the source immediately.
5. Read back the exact destination ID/settings and the source's paused state. Verify next run and scheduler readiness; a manual result is not scheduled-run proof. Report which scope owns execution now and how rollback would work.

If a source requirement has no supported mapping, stop and ask rather than silently weaken it. Repository development does not authorize migration, gateway changes, cron creation, or live configuration edits.
