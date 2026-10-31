# AI-ProjConf

> A collection of project-initialization templates that set up AGENT collaboration conventions, task tracking, and documentation structure in one go.

[简体中文](README.md) | English

## Two Template Types

| Directory | Suitable for | Characteristics |
|-----------|--------------|-----------------|
| `en_US/single-repo/` | Independent developers / single-repository projects | The root is the git repository; convention files such as `CLAUDE.md` are version-controlled |
| `en_US/multi-repo/` | Large projects / microservice workspaces | The root is not version-controlled; each subdirectory is its own git repository; `CLAUDE.md` is a local work ledger |

The Chinese versions live in `zh_CN/single-repo/` and `zh_CN/multi-repo/` and mirror the English structure one-to-one.

## Template Contents

| File | Purpose |
|------|---------|
| `CLAUDE.md.example` | Project convention entry point: overview, architecture rules, environment index, task tracking, development and commit rules |
| `AGENTS.md.example` | AGENT entry file pointing to `CLAUDE.md` |
| `README.md.example` | Project README skeleton (single-repo) |
| `CHANGELOG.md.example` | Changelog skeleton following Keep a Changelog (single-repo) |
| `TODO.md.example` | Todo index; details live in `.project/` |
| `.docs/` | User-facing business and deployment documents |
| `.project/` | Internal repository development notes |
| `.project/env/` | Per-environment connection details: `test.md` / `uat.md` / `prd.md` |

## Task Tracking and Environment Configuration

- Create a `.project/YYYYMMDD-<topic>/` directory for each task and name the body after the topic.
- Merge follow-up work on the same topic into the existing directory; use numbered subdirectories such as `01-discussion` for steps.
- The root `TODO.md` is an index only: add a link line under "In Progress"; when done, move it to "Completed / Archived" with a `### ✅` prefix.
- Write environment connection details into `.project/env/` and register them in the "Environment Index" section of `CLAUDE.md`.

## Usage

Remove the `.example` suffix from the files in the matching directory, place them in your project root, and replace the `{{placeholders}}`.

```bash
cp AI-ProjConf/en_US/single-repo/CLAUDE.md.example /path/to/project/CLAUDE.md
```

## Language Versions

| Version | Directory |
|---------|-----------|
| 简体中文 | `zh_CN/` |
| English | `en_US/` |

Keep both languages in sync when adding or changing templates.
