# Changelog

本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式，并采用 [Semantic Versioning](https://semver.org/lang/zh-CN/) 进行版本管理。

## [Unreleased]

### Added

- **Trigger 架构重构**：`triggers/trigger.js` 成为唯一通用脚本（时间窗口 + 去重），场景专属 JS（如 `docker-check.js`）自动拼接。`build-cron.py` 新增 `--test` 参数，生成一次性测试任务（跳过窗口/去重，执行后自动删除）。
- **模板目录化**：所有场景模板从单文件迁移为目录结构（如 `checks/docker-check/docker-check.yaml` + `docker-check.js`），`templateRef` 从 `../` 改为 `../../`。
- **Skill 架构重构**：4 个独立 project skill（init-cron / edit-cron / migrate-cron / update-cron）合并为 `aac-cron-manage`，SKILL-GUIDE.md 收归 `references/cron-template-guide.md`。
- `OpenClaw/skills/aac-cron-manage/` 目录建立，与 workspace skill 结构保持一致。

### Changed

- `build-cron.py` 重构 `add_trigger()`：自动检测场景目录下是否有同名 `.js` 文件，有则拼接 `trigger.js + 场景 JS`，无则直接 `return checkTimeWindowAndDedup()`。
- `build-cron.py` 移除 `TRIGGER_LIBRARY_PATH` / `TRIGGER_LIBRARY_ENV_INJECT` / `TRIGGER_SCRIPT` 支持，改为直接读取 `triggers/trigger.js` + 自动检测场景 `.js`。
- `build-cron.py` 移除 `TIME_WINDOW_ENABLED` / `DEDUP_ENABLED` / `WINDOW_OUT_ACTION` 默认值。
- `template-cron.zh.yaml` 移除 `timeWindow.enabled` / `deduplication.enabled` 字段，仅保留 `start` / `end` / `stateFile` / `granularity`。
- `template-cron.zh.yaml` 更新 trigger 区块注释，说明新架构（trigger.js 通用 + 场景 JS 可选拼接）。
- 所有场景模板移除 `TRIGGER_LIBRARY_PATH` 和 `DEDUP_ENABLED` / `TIME_WINDOW_ENABLED` 变量。

### Removed

- `OpenClaw/triggers/` 下旧脚本：`docker_status.js` / `git_changed.js` / `file_changed.js` / `http_changed.js` / `time_window.js`，功能已合并入 `trigger.js` 或场景专属 `.js`。
- `OpenClaw/skills/init-cron/` / `edit-cron/` / `migrate-cron/` / `update-cron/` 独立目录，内容已合并入 `aac-cron-manage/references/`。
- `OpenClaw/skills/aac-skill-manage/` 空目录（项目无其他 skill 需管理）。
- 旧单文件模板：`checks/cron-check.yaml` / `docker-check.yaml` / `workspace-check.yaml` 等（已目录化）。

### Added

- **Trigger 脚本库化**：`build-cron.py` 新增 `TRIGGER_LIBRARY_PATH` 和 `TRIGGER_LIBRARY_ENV_INJECT` 支持，自动从 `OpenClaw/triggers/` 读取库脚本并注入环境变量（`AAC_TIMEZONE`、`AAC_WINDOW_START`、`AAC_DEDUP_FILE` 等），实现脚本复用与任务隔离。
- `OpenClaw/template/reminders/{morning,noon,evening,custom-reminders}.yaml` 新增 `TRIGGER_ENABLED: "true"` + `TRIGGER_LIBRARY_PATH: "OpenClaw/triggers/time_window.js"`，将时间窗口与去重逻辑从 Prompt 迁移至 trigger 脚本。
- `OpenClaw/template/checks/cron-check.yaml` 新增 `TRIGGER_ENABLED: "true"` + `TRIGGER_LIBRARY_PATH: "OpenClaw/triggers/time_window.js"`，将时间窗口与去重逻辑从 Prompt 迁移至 trigger 脚本。
- `OpenClaw/template/checks/docker-check.yaml` 改用 `TRIGGER_LIBRARY_PATH: "OpenClaw/triggers/docker_status.js"` 替代内联 `TRIGGER_SCRIPT`，新增 `DOCKER_STATE_FILE` 变量实现任务级状态文件隔离。
- `OpenClaw/template/checks/workspace-check.yaml` 改用 `TRIGGER_LIBRARY_PATH: "OpenClaw/triggers/git_changed.js"` 替代内联 `TRIGGER_SCRIPT`，新增 `GIT_DIR` / `GIT_STATE_FILE` 变量实现任务级状态文件隔离。
- `OpenClaw/template/checks/custom-checks.yaml` 新增 `TRIGGER_ENABLED: "true"` + `TRIGGER_LIBRARY_PATH: "OpenClaw/triggers/time_window.js"` 示例配置。

### Changed

- `OpenClaw/template/template-cron.zh.yaml`：移除 Prompt 层【防护机制 1：时间窗口】和【防护机制 2：去重】指令块，以及"执行后去重"块。时间窗口与去重由 trigger 脚本或 YAML 配置层统一管理，不再在 message 中重复描述。保留 YAML `timeWindow` / `deduplication` 配置区作为 trigger 环境变量来源。
- `OpenClaw/template/template-cron.zh.yaml` 顶部注释更新为"时间窗口、去重与 trigger 的关系"，明确 trigger 脚本为推荐实现方式，Prompt 层仅作向后兼容。
- `OpenClaw/template/template-cron.zh.yaml` trigger 区块注释更新，说明 trigger 脚本库（`time_window.js` / `docker_status.js` 等）的推荐用法。
- `OpenClaw/scripts/build-cron.py` `add_trigger()` 重构为支持 `TRIGGER_LIBRARY_PATH`，新增 `build_trigger_from_library()` 函数负责读取库脚本、注入环境变量、生成复合脚本。
- `OpenClaw/template/checks/docker-check.yaml` 移除冗余 `WINDOW_START` / `WINDOW_END` / `DEDUP_ENABLED` / `DEDUP_STATE_FILE` 变量（docker_status.js 不依赖时间窗口和去重）。
- `OpenClaw/template/checks/workspace-check.yaml` 移除冗余 `WINDOW_START` / `WINDOW_END` / `DEDUP_ENABLED` / `DEDUP_STATE_FILE` 变量（git_changed.js 自身实现 commit 去重，时间窗口由 cron 调度保证）。

### Removed

- `OpenClaw/template/template-cron.zh.yaml` 中 Prompt 层的【防护机制 1：时间窗口】和【防护机制 2：去重】完整指令块（约 40 行），以及【执行后去重】块（约 3 行）。

### Added

- **OpenClaw 2026.7.1+ trigger 支持**：`template-cron.zh.yaml` 新增 `trigger` 配置区块，`build-cron.py` 支持 `--trigger-script` / `--trigger-once` 参数渲染，默认 `TRIGGER_ENABLED: "false"` 保持向后兼容。
- 新增 `OpenClaw/triggers/` 内置脚本库：提供 `time_window.js`（时间窗口+去重）、`docker_status.js`（容器状态变化）、`file_changed.js`（文件修改时间）、`http_changed.js`（HTTP 响应变化）、`git_changed.js`（git 新 commit）5 个通用 trigger 脚本。
- `OpenClaw/template/checks/docker-check.yaml` 新增 `TRIGGER_ENABLED: "true"` 配置，使用 `docker_status.js` 逻辑，仅在容器状态变化时唤醒 Agent。
- `OpenClaw/template/checks/workspace-check.yaml` 新增 `TRIGGER_ENABLED: "true"` 配置，使用 `git_changed.js` 逻辑，仅在工作区有 git 变化时唤醒 Agent。
- `OpenClaw/scripts/build-cron.py` 新增 `add_trigger()` 函数：将 `TRIGGER_SCRIPT` 写入 `~/.openclaw/workspace/.aac-triggers/{job_name}.trigger.js` 并添加 `--trigger-script` 参数。

- `OpenClaw/scripts/build-cron.py` 重构为完全自包含的独立脚本：内嵌 `DEFAULTS` 和 `FLAGS` 常量，零外部文件依赖，可直接拷贝到任意项目使用。
- `OpenClaw/scripts/build-cron.py` 新增 `{{#IF VAR}}...{{#ELSE}}...{{/IF}}` 条件块引擎，支持模板按变量值分支渲染。
- `OpenClaw/scripts/build-cron.py` 新增 `<!-- AAC_ORIGIN: ... -->` 起源标记注入机制，即使 cron 被大幅定制化（改名、改结构）也能通过 message 追溯上游模板来源。
- `OpenClaw/template/template-cron.zh.yaml` 新增 `DEDUP_GRANULARITY` 去重粒度配置，支持 `daily`（默认，向后兼容）/ `half-day`（上午/下午）/ `hourly` / `per-run`（永不去重）四种模式。
- `OpenClaw/template/template-cron.zh.yaml` 新增 `LOOP_TASK_TYPE` 变量，替换模板中硬编码的"推进软件开发项目"文本，使 Loop 模式适用于任意领域。
- `OpenClaw/template/template-cron.zh.yaml` 新增 `LOOP_EXEC_INSTRUCTIONS` 变量：非空时完全替换 PHASE 2 默认开发流程（git log、py_compile、pytest 等），仅保留状态机管理、里程碑判定、自动停用等核心 Loop 架构。
- `OpenClaw/template/template-cron.zh.yaml` 新增 `LOOP_STATE_SCHEMA` 变量：非空时将自定义字段 merge 到状态文件 schema 中，使 Loop 状态文件不再局限于 `tech_debt`/`test_coverage` 等开发专用字段。
- 新增 `OpenClaw/hook-pack/` 通用上下文注入模板（`HOOK.md`、`handler.js`、`context.md`），支持插件/子项目通过 `agent:bootstrap` 事件注入任意上下文（角色、规则、工作流、状态约定等），无需修改用户工作区文件。

- 将 Loop 开发迭代逻辑合并入 `OpenClaw/template/template-cron.zh.yaml`，新增 `LOOP_MODE_ENABLED` 开关，支持目标（`DEV_GOAL`）、里程碑（`DEV_MILESTONES`）、当前里程碑（`DEV_CURRENT_MILESTONE`）和到达目标后自动停用 cron（`DEV_AUTO_DISABLE_ON_GOAL_REACHED`）。
- 新增 `OpenClaw/template/checks/custom-checks.yaml` 通用巡检场景模板，便于用户快速创建自定义巡检任务。
- 新增 `OpenClaw/template/projects/custom-projects.yaml` 通用项目场景模板，支持基于 Loop 方法的任意项目任务。
- 新增 `OpenClaw/skills/update-cron/SKILL.md`，用于在 AAC 模板升级后批量同步已有 AAC 规范化定时任务。
- `OpenClaw/scripts/build-cron.py` 增加 Loop 模式前置校验：验证 `LOOP_MODE_ENABLED` 为合法布尔字符串、`TIMEOUT_SECONDS` 为正整数、`DEV_PROJECT_DIR` 不是默认占位符、`DEV_MILESTONES` 为合法 JSON 数组，防止无效配置生成 cron 命令。
- `OpenClaw/scripts/build-cron.py` 在渲染前统一展开变量中的嵌套占位符（如 `SCHEDULE_EXPR: "{{CUSTOM_SCHEDULE_EXPR}}"`），修复命令参数未解析的问题。
- `OpenClaw/conf/defaults.yaml` 增加 `SCENE_SPECIFIC_INSTRUCTIONS` 默认值。
- `OpenClaw/scripts/build-cron.py` 增加渲染后未解析大写模板占位符警告，防止未定义变量泄漏到 cron message。
- 新增 `AI-ProjConf/zh_CN/` 通用项目初始化模板目录，提供 `README.md`、`TODO.md`、`AGENT.md`、`CLAUDE.md`、`CHANGELOG.md` 的 example 模板。
- 新增 `OpenClaw/scripts/build-cron.py` 脚本，支持从场景 YAML 渲染生成 `openclaw cron create` 命令。
- 新增 `OpenClaw/conf/flags.yaml`，集中管理 OpenClaw 官方 CLI 参数映射及 boolean/enum 等特殊参数规则。
- 新增 `OpenClaw/conf/defaults.yaml`，管理官方参数与非官方扩展的默认变量值。
- 新增 `docs/OpenClaw/design-rationale.md`，解释开机堆叠问题与时间窗口、去重的必要性。
- 新增 `docs/OpenClaw/skill-creator.md`，记录 OpenClaw Skill 创建方式调研结果。
- 新增 `OpenClaw/skills/SKILL-GUIDE.md` 中“`openclaw cron edit` 支持矩阵”与“项目路径自动定位”章节，为 skill 执行提供统一参考。
- 新增 `OpenClaw/template/check/docker.yaml` Docker 容器/Compose 巡检场景，基于 `template-cron.zh.yaml` 并通过场景级 `template` 字段直接覆盖提示词。
- `OpenClaw/scripts/build-cron.py` 支持场景 YAML 通过顶层 `template` 字段覆盖模板文件的提示词。
- 新增 `OpenClaw/skills/init-cron/SKILL.md`，引导用户从零创建定时任务。
- 新增 `OpenClaw/skills/migrate-cron/SKILL.md`，帮助用户改造已有定时任务。
- `OpenClaw/template/template-cron.zh.yaml` 顶部注释增加 `{{WORKSPACE}}` 内置变量说明。

### Changed

- `OpenClaw/template/template-cron.zh.yaml` Loop 模式通用化：移除硬编码的"推进软件开发项目"及 git log/py_compile/pytest 等开发专属步骤；状态机核心架构保留，业务执行阶段通过 `LOOP_EXEC_INSTRUCTIONS` 可完全自定义；状态文件 schema 通过 `LOOP_STATE_SCHEMA` 可扩展自定义字段。
- `OpenClaw/template/template-cron.zh.yaml` 去重机制升级：从单一 `date +%Y-%m-%d` 升级为粒度可配（`daily`/`half-day`/`hourly`/`per-run`），通过 `DEDUP_GRANULARITY` 控制。
- `OpenClaw/template/template-cron.zh.yaml` PHASE 1/2/3 重组：PHASE 1（状态机核心 + 状态文件管理）→ PHASE 2（可替换业务执行，通过 `{{#IF LOOP_EXEC_INSTRUCTIONS}}` 分支）→ PHASE 3（退出管理核心：里程碑判定 + 状态更新 + 汇报 + 自动停用）。
- `OpenClaw/scripts/build-cron.py` 管线重排：结构标记处理（`{{#LOOP_ONLY}}`、`{{#IF}}` 等）先于变量替换执行，消除用户内容中 `{{#IF}}` 等字面量被误解析为模板指令的安全风险。
- `CLAUDE.md` 新增模板变量命名规范：仅使用大写字母、数字和下划线，禁止连字符。

- 将 `OpenClaw/template/checks/docker.yaml` 重命名为 `OpenClaw/template/checks/docker-check.yaml`，与类别内其他巡检模板命名风格保持一致。
- `OpenClaw/template/template-cron.zh.yaml`：
  - 移除状态机中不可达的 `completed` 状态，状态现在为 `ready` | `in_progress` | `blocked` | `goal_reached`，并同步更新状态机转换图。
  - 增强 PHASE 3.4 里程碑完成判定，要求同时满足代码已提交、语法检查通过、测试通过、TODO.md 对应项已标记完成、git 无未提交重要变更。
  - 增强 PHASE 3.8 自动停用 cron 逻辑，优先使用状态文件中记录的 `cron_job_id`，失败后回退到按任务名从 `openclaw cron list --format json` 查找，并增加失败处理说明。
  - PHASE 1.2 增加写入状态文件前 `mkdir -p` 步骤；PHASE 1.6 增加读取架构文档前 `mkdir -p {{DEV_DOCS_DIR}}` 步骤。
- 删除独立的 `OpenClaw/template/template-dev.zh.yaml`，其 Loop 逻辑已合并至 `template-cron.zh.yaml`。
- 将提醒类自定义模板从 `OpenClaw/template/reminders/custom.yaml` 重命名为 `OpenClaw/template/reminders/custom-reminders.yaml`，并补充默认示例值。
- `OpenClaw/template/template-cron.zh.yaml` 增加 Loop 模式支持，同时完整保留所有 OpenClaw 官方参数字段（systemEvent、command、keepAfterRun、stagger、webhookUrl、failureDestination 等），确保所有场景基于同一父模板。
- `OpenClaw/conf/defaults.yaml`：新增 Loop 模式相关默认值（`LOOP_MODE_ENABLED`、`DEV_*` 系列变量）。
- `OpenClaw/scripts/build-cron.py`：将 `WORKSPACE` 展开为绝对路径（`os.path.abspath(os.path.expanduser(...))`）。
- `OpenClaw/conf/defaults.yaml`：移除 `SESSION_TARGET: isolated` 默认值，改为在 `build-cron.py` 中按 `SESSION_TARGET > PERSISTENT_ID > isolated` 的优先级自动推断，避免 `PERSISTENT_ID` 被默认值覆盖。
- `OpenClaw/skills/init-cron/SKILL.md`、`OpenClaw/skills/migrate-cron/SKILL.md`、`OpenClaw/skills/edit-cron/SKILL.md`：
  - 不再使用 `/path/to/awesome-AGENT-configure` 占位符，统一按 `SKILL-GUIDE.md` 中的方法自动定位项目仓库（`AAC_REPO`）。
  - 明确区分项目仓库（`AAC_REPO`）与运行时配置目录（`AAC_WORKSPACE`，默认 `~/.openclaw/workspace/awesome-AGENT-configure`），二者完全分离。
  - `edit-cron` 更新流程改为优先使用 `openclaw cron edit <id>`（保留 job ID），仅在命令模式等 `edit` 不支持的场景下回退到 delete+create。
- `.gitignore`：增加 `__pycache__/`、`*.pyc`、`*.pyo` 忽略规则。
- `OpenClaw/template/template-cron.zh.yaml`：
  - 删除 `command.enabled`，遵循 OpenClaw 原生语义，`command.script` 非空时自动启用命令模式。
  - 删除 `timeWindow.timezone`，统一使用 `schedule.timezone`。
  - 明确 `message` 为官方 `--message` 参数映射，`template` 为生成 `message` 的提示词模板源。
  - 为未加引号的 YAML 占位符补充引号，修复 PyYAML 解析失败。
  - 顶部注释增加开机堆叠问题说明。
  - template 内将时间窗口和去重提炼为独立的【防护机制】结构性注释。
- `OpenClaw/conf/defaults.yaml`：增加 `THINKING: "off"` 默认值。
- `OpenClaw/template/reminders/*.yaml`：所有提醒场景增加 `THINKING: "off"` 和 `EXACT: "true"`。
- `README.md`：重构为目录导航结构，新增安装与依赖、项目结构、贡献指南等章节，修正章节标题笔误。
- `TODO.md`：精简为“待实现 / 已完成”两栏，按 P0~P3 优先级分组，删除历史已决策条目。
- `README.md`：补充项目结构、使用方法、设计原则和开机堆叠问题说明。
- `TODO.md`：关闭 `#3`/`#4`/`#7`/`#8`/`#10`。 
- `OpenClaw/skills/SKILL-GUIDE.md`、`init-cron/SKILL.md`、`migrate-cron/SKILL.md`：将任务分类从 7 类（提醒/巡检/汇报/开发/学习/整理/系统）精简为 4 类（提醒/巡检/开发/学习）。
- `OpenClaw/skills/init-cron/SKILL.md`、`migrate-cron/SKILL.md`：调整步骤顺序，先定位项目仓库（`AAC_REPO`）再生成场景 YAML，并明确要求将 `templateRef` 修正为仓库绝对路径。
- `OpenClaw/workspace_example/SOUL.md.example`：调整目录结构规范，将 IDENTITY.md 引用资源从 `assets/` 拆分为 `avatars/`，用户资源仍放 `assets/`，并增加 `.trash` 回收站规范。
- `OpenClaw/template/template-cron.zh.yaml` 及 `OpenClaw/template/checks/*.yaml`：将 `TIME_WINDOW_ENABLED`、`WINDOW_OUT_ACTION`、`DEDUP_ENABLED` 等非官方配置变量注入 prompt，避免硬配置与 prompt 行为脱节。
- `OpenClaw/template/template-cron.zh.yaml`：将默认 `template` 改为通用版本，移除提醒类特定内容，仅保留 persona、时间窗口、去重等通用 Harness 机制；新增 `{{SCENE_SPECIFIC_INSTRUCTIONS}}` 占位符由场景 YAML 注入场景特定指令。
- `OpenClaw/template/reminders/*.yaml` 及 `OpenClaw/template/checks/*.yaml`：将业务特定 prompt 从顶层 `template` 字段迁移到 `SCENE_SPECIFIC_INSTRUCTIONS` 变量，统一由父模板控制 Harness 机制。
- `OpenClaw/skills/SKILL-GUIDE.md` 及 `OpenClaw/template/template-cron.zh.yaml`：明确禁止场景 YAML 通过顶层 `template` 字段覆盖父模板，确保时间窗口、去重等非官方机制对所有场景生效。

### Removed

- 删除 `OpenClaw/conf/defaults.yaml` 和 `OpenClaw/conf/flags.yaml`：`build-cron.py` 已将所有默认值和 CLI 参数映射内嵌为 `DEFAULTS`/`FLAGS` 常量，实现完全自包含。

### Fixed

- `OpenClaw/template/template-cron.zh.yaml`：在 Loop 模式状态文件初始化步骤（PHASE 1.1）增加"状态文件冲突"警告，明确提示"每个 Loop 任务必须使用独立的状态文件"，防止用户将多个任务配置为共用同一个 `DEV_STATE_FILE` 导致状态互相覆盖、里程碑错乱。
- `OpenClaw/template/projects/feature.yaml`、`OpenClaw/template/projects/maintain.yaml`：在 `DEV_STATE_FILE` 变量注释中同步增加冲突警告，并建议使用不同文件名（如 `dev-session.json` / `maintain-session.json`）。
- `OpenClaw/scripts/build-cron.py` `apply_conditional_blocks()` truthiness 检查修复：`"false"`/`"0"`/`"[]"`/`"{}"` 等字符串字面量现正确判定为假。
- `OpenClaw/scripts/build-cron.py` `inject_origin_tag()` 修复 HTML 注释注入风险：对 `CATEGORY`/`JOB_NAME` 中的 `-->` 序列做 sanitize（替换为 `-- >`）。
- `OpenClaw/scripts/build-cron.py` `substitute_variables()` 修复列表/字典值的序列化：使用 `json.dumps()` 替代 `str()`，确保 JSON 代码块合法性。
- `OpenClaw/scripts/build-cron.py` `build_persona_prompt()` 修复 `PERSONA_MODE` 为空或 YAML `null` 时静默丢失人设的问题，现正确回退到模板默认值 `"inline"`。
- `OpenClaw/scripts/build-cron.py` 消除 `resolve_variables()` 冗余调用：变量解析仅在 `main()` 中执行一次，`render_message()` 内不再重复扫描。
- `OpenClaw/scripts/build-cron.py` 未解析标记检查扩展为同时检测变量占位符（`{{XXX}}`）和控制标记（`{{#IF}}`/`{{/IF}}` 等），防止模板语法错误静默泄漏。
- `OpenClaw/scripts/build-cron.py` `inject_origin_tag()` 新增 `now` 参数，支持测试注入固定时间戳以实现可复现输出。
- `TODO.md` 修复重复的 `### P2：` 标题。
- `OpenClaw/skills/update-cron/SKILL.md` 更新过时的 `defaults.yaml` 引用为 `build-cron.py` 中的 `DEFAULTS`/`FLAGS` 常量。

- 修复 `OpenClaw/template/reminders/{morning,noon,evening,custom-reminders}.yaml`、`OpenClaw/template/checks/{cron-check,docker,workspace-check}.yaml` 中残留的 `{{DATE_TODAY}}` / `{{TIME_NOW}}` / `{{WEEKDAY}}` 占位符，改为由 Agent 执行时通过 `exec date` 获取当前日期/时间。
- `OpenClaw/template/projects/feature.yaml`、`OpenClaw/template/projects/maintain.yaml`：补充 `DEV_DOCS_DIR` 变量，明确 TODO.md、CHANGELOG.md、架构文档等路径；扩展 `DEV_COMMIT_PREFIX` 注释，包含 `docs`/`test`/`chore` 等常见前缀。
- `OpenClaw/conf/defaults.yaml`：补充 `DEV_DOCS_DIR` 默认值；修复之前误删的 `PERSONA_MODE` 和 `WORKSPACE` 默认值。
- 修复 `OpenClaw/template/template-cron.zh.yaml` 中 Loop 模式分支的未定义占位符泄漏问题：移除 `{{DEV_COMMIT_MESSAGE}}`、`{{DATE_TODAY}}`、`{{TIME_NOW}}` 以及状态字段（`{{current_card}}`、`{{status}}` 等）的直接模板引用，改为从状态文件中读取后填入。
- 修复 `OpenClaw/template/projects/maintain.yaml` 中项目特定值（`Siyuan-RAG Companion`、`/mnt/d/Study_Project/siyuan-rag-companion` 等）违反通用化原则的问题，统一替换为占位符。
- 修复 `OpenClaw/template/projects/maintain.yaml` 缺少 `DEDUP_STATE_FILE` 导致 `{{DEDUP_STATE_FILE}}` 泄漏的问题。
- 修复 `CLAUDE.md` 中 `CHANGLOG.md` 拼写错误，统一为 `CHANGELOG.md`。
- 修复 `README.md` 中“无需额外安装第三方依赖”的错误说明，补充 PyYAML 依赖。
- 修复 `OpenClaw/skills/SKILL-GUIDE.md` 仍引用已移除的 `DATE_TODAY` 以及旧 `dev/` 路径的问题。
- 修正 `README.md` 项目结构中对 `AI-ProjConf/` 的描述，移除已删除的 `STATE` 引用。
- 删除 `AI-ProjConf/zh_CN/README.md.example` 中指向未提交 `CONTRIBUTING.md` 的“贡献指南”章节。
- 重命名 `AI-ProjConf/zh_CN/CHANGLOG.md.example` 为 `CHANGELOG.md.example`，修正拼写错误。
- 修复 `OpenClaw/scripts/build-cron.py` 中 `session:<id>` 持久会话逻辑：
  - 支持 `SESSION_TARGET: "session:my-id"` 直接生效。
  - 当仅提供 `PERSISTENT_ID` 时自动生成 `session:<id>`。
- 修复 `OpenClaw/scripts/build-cron.py` 对空列表/字典的处理：
  - `COMMAND_ARGV: []` / `{}` 不再渲染为字符串 `"[]"` / `"{}"`。
  - 非空列表/字典自动序列化为 JSON 字符串后传给 CLI。
- 修复 `build_persona_prompt` 在 `PERSONA_ROLE` 为空时生成病句“你是一个。”的问题，现在返回空字符串。
- 修复 `OpenClaw/conf/flags.yaml` 中 `delivery.mode: none` 不渲染任何 flag 的问题，改为渲染 `--no-deliver`。
- 修复 `OpenClaw/template/template-cron.zh.yaml` 中 `session:<id>` 注释与占位符混淆的问题。
- 修复 `OpenClaw/template/template-cron.zh.yaml` 中部分 `{{XXX}}` 占位符未加引号导致的 YAML 解析错误。
- 修复 `OpenClaw/scripts/build-cron.py` 单次替换无法处理嵌套变量（如 `DEDUP_STATE_FILE: "{{WORKSPACE}}/..."`）的问题，改为最多 5 轮多轮替换。
- 修复 `OpenClaw/scripts/build-cron.py` 中 `build_persona_prompt` 占位符过滤逻辑不完整的问题，使用正则检测任意 `{{...}}` 子串，避免 `{{PERSONA_ROLE}}-admin` 等部分占位符泄漏到 prompt。
- 修复 `OpenClaw/template/checks/docker.yaml` 使用未定义 `{{TIME_NOW_SAFE}}` 变量的问题，改为由 AGENT 执行时从当前时间派生文件名。
- 修复 `OpenClaw/template/checks/docker.yaml` 清理旧报告命令未确保 `.trash/` 目录存在的问题。
- 同步更新 `TODO.md` 中已删除/重命名的 `OpenClaw/template/check/docker.yaml` 路径引用。
- 修复 `OpenClaw/scripts/build-cron.py` 未注入时间变量的问题，构建时统一注入 `DATE_TODAY`、`TIME_NOW`、`WEEKDAY`。
- 修复 `OpenClaw/template/checks/cron-check.yaml` 重试方案，改用 `openclaw cron run --wait <任务ID>` 立即重试新故障，避免删除重建导致 job ID 改变。
- 修复 `OpenClaw/scripts/build-cron.py` 中 `build_command` 函数存在未使用 `scene` 和 `template` 参数的问题，简化函数签名。
- 修复 `OpenClaw/scripts/build-cron.py` 的 `render_template` 允许场景 YAML 覆盖父模板 `template` 的问题，现在禁止场景级 `template` 覆盖，统一由父模板控制 Harness 机制。

## [0.0.0] - 2026-06-21

### Added

- 项目初始化，提交基础目录结构与文档。
- 新增 `README.md`、`CLAUDE.md`、`AGENT.md`、`TODO.md`、`.gitignore`。
- 新增 `OpenClaw/template/template-cron.zh.yaml` 通用模板。
- 新增 `OpenClaw/template/reminders/` 下早安、午安、晚安、自定义提醒场景模板。
- 新增 `docs/OpenClaw/` 下架构、最佳实践、任务模板总览三篇文档。
- 新增 `.claude/skills/web-research/SKILL.md`。
