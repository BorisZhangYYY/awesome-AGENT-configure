# Updating and migrating templates

[简体中文](../zh_CN/update-cron.md) | English

Upgrading a template and upgrading a live job are different operations: editing repository files changes no job; editing a job must keep its ID and pause state.

## 1. Upgrade the repository template

1. Change `template-cron.yaml` or a scene YAML without altering the three top-level keys or the variable names.
2. Change both locales together; variable sets, placeholder sets, and `job` keys must stay identical.
3. Validate everything:

```bash
for f in $(find Hermes/zh_CN/cron-template Hermes/en_US/cron-template -name "*.yaml" \
  ! -name "template-cron.yaml"); do
  python3 Hermes/skills/aac-hermes-cron-manage/scripts/build-cron.py "$f" --validate
done
python3 -m unittest discover -s tests/hermes
```

4. If the change affects every job (for example the shared constraints), state the blast radius in the commit message.

## 2. Apply the new template to an existing job

```bash
# 1) locate the job: only the ID is unique
hermes cron list --all
# 2) generate an update that keeps the ID
python3 .../build-cron.py Hermes/zh_CN/cron-template/checks/docker-check/docker-check.yaml \
  --edit <JOB_ID> --preview
# 3) run the reviewed command
env HERMES_HOME=$HOME/.hermes hermes cron edit <JOB_ID> --schedule "0 */6 * * *" --prompt "..."
# 4) read back
hermes cron runs <JOB_ID> --limit 5
```

- `edit` changes only the fields you pass; clear a field explicitly with `''` or `[]` (`--clear-skills` on the CLI).
- A paused job stays paused through `edit`; do not slip a `resume` into an upgrade.
- Turning a one-shot into a recurring job (or back) is a rebuild: create the new job, verify it, then remove the old one.
- Capture `list --all` and `runs` before and after as change evidence.

## 3. Migrating from OpenClaw

The parameters do not carry over:

| OpenClaw | Native Hermes |
|---|---|
| `trigger.js` time windows and dedup | no trigger; use `catch_up` and `grace_minutes` |
| single `message` text | `prompt` plus `skills` |
| scene-level `template` override | scenes override only `variables` and `job` |
| no native monitor | `monitor_script` / `monitor_url` (mutually exclusive) |

Migration order: rewrite the scene for Hermes → `--validate` → create paused → verify with a manual `run` → resume and watch one real period → only then disable the OpenClaw job. Never run both.

## 4. Rollback

1. `hermes cron edit <JOB_ID> --prompt "<previous prompt>"` restores the wording; field-level rollback changes only the differing fields.
2. Script rollback: swap the file under `$HERMES_HOME/scripts/aac/` back to the previous bytes, then `run` once to confirm.
3. Template rollback goes through Git: `git revert` the commit, recompile, and diff the `--preview` output.
4. After any rollback, read back ID, fields, and run history instead of trusting memory.

## 5. Disabling and cleanup

- Pausing: `hermes cron pause <JOB_ID>` keeps the history.
- Retiring: pause first, observe for a while, then `remove`. Removal drops the history and cannot be undone from `list`.
- Jobs produced by `--test` only fire when explicitly run and are never deleted automatically; remove them yourself when done.
