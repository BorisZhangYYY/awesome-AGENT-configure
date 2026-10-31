# Hermes Workspace Templates

> Starter templates for persona, user profile, and long-term memory. Hermes cron configuration is not included.

[简体中文](README.md) | English

## Language Versions

| Version | Directory |
|---------|-----------|
| 简体中文 | `zh_CN/workspace-template/` |
| English | `en_US/workspace-template/` |

## File Responsibilities

- `SOUL.md`: persona, communication style, and workspace management conventions. The directory categories and retention periods are conventions of this template, not framework requirements; nothing creates directories or scheduled tasks automatically.
- `memories/USER.md`: user profile and preferences. Published templates should contain only a generic skeleton or placeholders.
- `memories/MEMORY.md`: long-lived environment facts and conventions, which Hermes's `memory` tool can maintain later.

## Usage

1. Confirm the target Hermes home: the default is `~/.hermes/`; when using a custom home or profile, follow that instance's `$HERMES_HOME` and do not overwrite other profiles.
2. Back up the target files, then copy or merge the files from `workspace-template/` into the target home as needed, preserving relative paths. Do not overwrite an accumulated user profile or long-term memory.
3. Edit the persona and workspace conventions in `SOUL.md`; fill in the name, preferred name, and timezone in `memories/USER.md` (`Asia/Shanghai` is only an example). Leave `memories/MEMORY.md` as the initial long-term memory skeleton.
4. Start a new session so the updated files are loaded.

The target paths are `$HERMES_HOME/SOUL.md`, `$HERMES_HOME/memories/USER.md`, and `$HERMES_HOME/memories/MEMORY.md`. `~/.hermes` in `SOUL.md` is the default-home example; adjust it when using another home.

## Notes

- Do not commit real credentials, private material, chat logs, or live memory files to a public repository.
- These are file templates; no change to a running Hermes configuration is required.

## Official References

- [Which file does what](https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what)
- [Persistent memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory)
