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
| `.project/INDEX.md.example` | Task register: single source of truth with stable IDs, assignee, closing conditions, evidence paths, and document lifecycle |
| `.project/rules/workflow.md.example` | Workflow playbook: new task / stopping halfway / interruption / resuming, plus team conventions and opening prompts |
| `scripts/check-project.py` | Shared state checker for all four templates (not an `.example`; copy it into the project alongside the templates) |
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
- One fact, one place: environments, versions, quotas, conclusions, and task status appear only in the file that defines them; rewrite the original sentence and never append "update" sections.
- Body documents carry YAML front matter with `status` (`active` / `reference` / `superseded` / `evidence` / `archived`), `owner_task`, and `updated_at`; retired documents add `superseded_by`.

## Task Tracking and Environment Configuration

- Create a `.project/YYYYMMDD-<topic>/` directory for each task and name the body after the topic; merge follow-up work on the same topic into the existing directory using numbered subdirectories such as `01-discussion`.
- Status, dependencies, assignee, closing conditions, evidence, current stage, and blockers are all registered in the [Task Register](en_US/multi-repo/.project/INDEX.md.example) (stage group headings / Notes column / `blocked` rows), one stable ID per task, with large stages broken into subtask chains. **Which rows this round covers comes from the session instruction and is never written into a shared file.**
- **Entry protocol**: read `INDEX.md` and run `python3 scripts/check-project.py` before work; with an explicit ID list touch only those rows, without one take the rows that are `active` and assigned to you. Treat only `status: active` documents as execution input, and never start a task from "pending confirmation / not implemented" found in `superseded`, `archived`, or `evidence` documents or in session memory.
- **Working as a team**: one row, one assignee — claiming a row means putting your name in it; commit right after editing and commit only your own rows; on handover change the assignee and write the break point in Notes. The playbook is [workflow.md](en_US/multi-repo/.project/rules/workflow.md.example).
- Rewrite the original register row and its `updated_at` on every status change; mark a task `done` only when evidence exists and the closing condition is met, and remove links and references when removing a conclusion. See [check-project.py](scripts/check-project.py).
- Write environment details into `.docs/01-environments/` and register them in the "Environment Index" of `CLAUDE.md`; register existing environments only — no files or placeholder content for missing ones.

## Usage

Remove the `.example` suffix from the files in the matching directory, place them in your project root, and replace the `{{placeholders}}`. The checker is shared by all four templates, so copy it into the project's `scripts/` directory separately.

```bash
cp AI-ProjConf/en_US/single-repo/CLAUDE.md.example /path/to/project/CLAUDE.md
cp AI-ProjConf/scripts/check-project.py /path/to/project/scripts/check-project.py
```

Drop the `.example` suffix from `.project/rules/workflow.md.example` into `.project/rules/workflow.md`: it is the human-facing playbook.

## Language Versions

| Version | Directory |
|---------|-----------|
| 简体中文 | `zh_CN/` |
| English | `en_US/` |

Keep both languages in sync when adding or changing templates.
