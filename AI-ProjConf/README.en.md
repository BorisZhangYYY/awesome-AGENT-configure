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
| `CLAUDE.md.example` | Project convention entry point: overview, documentation rules, environment index, task tracking, development and commit rules |
| `AGENTS.md.example` | AGENT entry file pointing to `CLAUDE.md` |
| `README.md.example` | Project README skeleton (single-repo) |
| `CHANGELOG.md.example` | Changelog skeleton following Keep a Changelog (single-repo) |
| `TODO.md.example` | Todo index; details live in `.project/` |
| `.docs/` | Shared material reused across tasks: environment notes, feature lists, data-reporting/API specs, resource inventories, acceptance reports |
| `.docs/README.md.example` | Shared-material index entry point: numbering convention and category table |
| `.docs/01-environments/` | Fixed numbered slot for `test.md` / `uat.md` / `prd.md`; create files only for environments that exist |
| `.project/` | Workspace: requirement discussions, designs, demo and verification runs, debugging, Q&A, plans and retrospectives |

## Shared Material vs. Workspace

| Area | What goes there | Naming |
|------|-----------------|--------|
| `.docs/` | Stable material a second task will reuse (including environment and access details) | Numbered top-level categories `01-environments/` (fixed), `02-category/`, ...; `00-` reserved for overview; no date directories inside |
| `.project/` | Content that only serves one work episode | `YYYYMMDD-<topic>/`, with `01-discussion/` subdirectories for steps |

- The number only controls ordering: append new categories at the end of the numbering, never renumber or reuse a removed number.
- Keep each shared document and its attachments in one place; `.project/` topic directories link to them with relative paths instead of copying.
- When several versions of a document exist, keep only the latest and record the version in the filename or the body.
- `single-repo/` and `multi-repo/` share the same `.docs` numbering and `.project` topic conventions.

## Task Tracking and Environment Configuration

- Create a `.project/YYYYMMDD-<topic>/` directory for each task and name the body after the topic.
- Merge follow-up work on the same topic into the existing directory; use numbered subdirectories such as `01-discussion` for steps.
- The root `TODO.md` is an index only: add a link line under "In Progress"; when done, move it to "Completed / Archived" with a `### ✅` prefix.
- Write environment details into `.docs/01-environments/` and register them in the "Environment Index" of `CLAUDE.md`; register existing environments only — no files or placeholder content for missing ones.

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
