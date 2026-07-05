# Changelog

本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式，并采用 [Semantic Versioning](https://semver.org/lang/zh-CN/) 进行版本管理。

## [Unreleased]

### Added

- 新增 `OpenClaw/scripts/aac-manage.sh` 管理脚本，支持安装/删除 AAC skill 与 cron，支持单个与批量操作。
- 所有 cron skill（init-cron、edit-cron、migrate-cron、update-cron）均自包含 `scripts/build-cron.py`，避免注册到 OpenClaw workspace 后路径丢失。

### Changed

- `OpenClaw/skills/` 下 skill 重构为两个管理器：`aac-skill-manage`（管理 skill）和 `aac-cron-manage`（管理 cron）。
- 删除旧的 `aac-create-skill`、`aac-init-cron`、`aac-edit-cron`、`aac-migrate-cron`、`aac-update-cron`。
- `README.md` 更新为模板项目新定位，并同步 skill 名称与脚本用法。
- `README.md` 补充 Hermes 与 Claude Code 官方文档链接。

### Fixed

- `README.md` 示例命令从已删除的 `init-cron` 路径修正为 `aac-cron-manage`。
- `aac-manage.sh` 全局选项解析改为 nameref 数组传递，避免含空格参数被错误拆分。
- `aac-manage.sh` `install-cron` 多文件安装时错误信息使用当前 `$src` 而非 `$1`。
- `aac-manage.sh` `install-cron` 的 `templateRef` 正则同时支持带引号与不带引号两种写法。
- `aac-cron-manage/SKILL.md` 迁移流程中 `openclaw cron info` 修正为 `openclaw cron get`。
- `build-cron.py` 根据 `SCHEDULE_TYPE` 选择 `--cron`（位置参数）、`--at` 或 `--every`，不再把 at/every 表达式误当 cron 位置参数。
- `build-cron.py` `delivery.mode=webhook` 不再生成裸 `--webhook` 标志，改为校验 `WEBHOOK_URL` 后由 `delivery.webhookUrl` 生成 `--webhook <url>`。
- `build-cron.py` 增加 `DELETE_AFTER_RUN` 与 `KEEP_AFTER_RUN` 互斥校验。
- `quick_validate.py` 补充 OpenClaw 官方可选 frontmatter 键：`disable-model-invocation`、`command-dispatch`、`command-tool`、`command-arg-mode`。