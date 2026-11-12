# TODO

## Hermes 定时任务模板迁移（2026-11-12 代码完成，待真机验收）

分支 `feat/hermes-cron`，基线 `bc332f4`。

### 已完成
- 父模板 `Hermes/{zh_CN,en_US}/cron-template/template-cron.yaml`：变量默认值、Harness 统一约束、Loop 段落（含嵌套条件块）。
- 每语言 14 个场景：提醒 4、巡检 4、项目推进 3、学习 1、纯脚本 1、变更监控 1；附 `script-only.py`、`change-monitor.py`、`monitor-source.txt`。
- 编译器 `build-cron.py`：按原生 `hermes cron` 字段校验（布尔/列表/枚举/monitor 互斥/脚本越界/重复键），八种只读输出模式。
- 参考文档四篇 × 两语言（模板与 Loop／原生参数／命令与验收／升级与迁移），SKILL 死链清零。
- `tests/hermes/` 14 项全绿；`scripts/check.py` 把 Hermes 场景一并纳入渲染校验。
- 根 `README.md`、`README.en.md`、`CHANGELOG.md` 已同步。

### 待完成
- [ ] 隔离 `HERMES_HOME` 真机验收：创建暂停任务 → 读回 ID 与字段 → 手动 run → 观察一个真实周期 → 暂停/删除；不触碰现有 `siyuan-md-sync` 任务。
- [ ] Hermes 升级后复查 `tools/cronjob_tools.py::CRONJOB_SCHEMA`，确认 `--tool-json`／`--plan` 的字段映射仍成立。

### 约束备忘
- OpenClaw 与 Hermes 各自独立，互不迁移运行态。
- Hermes 侧默认不消耗模型额度：优先 `--no-agent` 纯脚本模式。
- 不改动运行中的 Hermes：本次未创建任何任务，`cron` 仅原有 `siyuan-md-sync`（`a6560ca811e8`）。
- 生成的命令必须可审阅后再执行；编译器本身不执行、不安装。

## AI-ProjConf 任务状态治理（2026-11-12 模板已落地，实例迁移待执行）

- 已完成：四套模板（中英 × single/multi）新增 `.project/INDEX.md.example` 唯一状态源（含执行者列、多人协作约定）、front matter 生命周期与入口协议；新增 `.project/rules/workflow.md.example` 操作手册（新任务／干一半／插队／隔天恢复四场景 + 开场白 + 反模式）；新增共享校验脚本 `AI-ProjConf/scripts/check-project.py`；四套 `TODO.md.example` 已移除，本轮范围改由会话指令给出；`.docs/README.md.example` 标 `status: reference`；`AI-ProjConf/README.md`、`README.en.md`、`CHANGELOG.md` 已同步。
- 待办：`~/Desktop/project/youchu` 实例迁移尚未执行。需补 `.project/INDEX.md`，给 87 份正文加 front matter，把 60 份无状态文档标 `reference`／`superseded`，清理 45 份含未决词文档里的过期表述，并把 `06-后续任务与云端交接.md` 的 29 个编号、`09-阶段计划.md` 的 9 个步骤映射进注册表。迁移不移动任何目录，保住 502 条内部链接。
- 待确认：校验脚本 `--max-age` 默认 14 天是否适配 youchu 推进节奏；`KEY_FACTS` 需按项目填写（如配额、内核版本等稳定事实的定义文件）；执行者列是否按真实分工填写。
- 副本现状：模拟改造副本 `~/Desktop/project/youchu-refactor-preview` 已按要求删除（进废纸篓）；原仓 `~/Desktop/project/youchu` 全程未被改动，当前在 `bd3e9e1`。如需重做，按最新原仓重新扫描（149 份正文、502 条链接）后再登记。
