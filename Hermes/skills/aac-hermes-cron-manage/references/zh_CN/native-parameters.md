# 原生参数对照

简体中文 | [English](../en_US/native-parameters.md)

以目标安装的 `hermes cron create --help` 与 `hermes cron edit --help` 为准；本表用于说明模板字段怎么落到命令或工具参数上。

## 1. 字段总表

| 场景 `job` 字段 | CLI 参数 | 公共工具参数 | 类型 | 默认 | 说明 |
|---|---|---|---|---|---|
| `schedule` | 位置参数 | `schedule` | 字符串 | 必填 | `30m` 周期、`in 30m` 一次、`0 9 * * *` cron、`every monday 9am` |
| `name` | `--name` | `name` | 字符串 | 无 | 建议带 `【AAC-类别】` 前缀，名称不唯一，不能当 ID |
| `deliver` | `--deliver` | `deliver` | 字符串 | 创建来源 | 模板统一写 `local`；外部投递需单独授权 |
| `failure_deliver` | `--failure-deliver` | `failure_deliver` | 字符串 | 跟随 `deliver` | 仅覆盖失败通知；`local` 表示抑制 |
| `repeat` | `--repeat` | `repeat` | 整数 | 周期任务永久、一次任务一次 | 一次性任务限次数 |
| `catch_up` | `--catch-up on\|off` | `catch_up` | 布尔 | 见配置 | 模板统一 `false`，不补跑过期任务 |
| `skills` | `--skill`（可重复） | `skills` | 字符串列表 | 空 | 编辑时 `[]` 表示清空，CLI 用 `--clear-skills` |
| `script` | `--script` | `script` | 路径 | 无 | 相对 `$HERMES_HOME/scripts/`，越界或符号链接逃逸会被拒绝 |
| `no_agent` | `--no-agent` | `no_agent` | 布尔 | `false` | 必须配 `script`；不能与 monitor 同用 |
| `monitor_script` | `--monitor-script` | `monitor` | 路径 | 无 | 与 `monitor_url` 互斥 |
| `monitor_url` | `--monitor-url` | `monitor` | http(s) URL | 无 | 与 `monitor_script` 互斥 |
| `workdir` | `--workdir` | `workdir` | 绝对路径 | 无 | 注入该目录的上下文文件并作为 cwd |
| `timezone` | `--timezone` | `timezone` | IANA 名称 | 跟随 profile | cron 表达式按该时区解释 |
| `continuity` | `--continuity` / `--no-continuity` | `continuity` | 布尔 | `false` | 注入本任务上次输出，不等于持久状态 |
| `paused` | `--paused` | `paused` | 布尔 | `false` | 创建即停用；恢复用 `hermes cron resume` |
| `paused_reason` | `--paused-reason` | `paused_reason` | 字符串 | 无 | 必须同时 `paused: true` |
| `pinned` | `--pin` / `--unpin` | `pinned` | 布尔 | `false` | 锁当前主模型；与 `model` 互斥 |
| `grace_minutes` | `--grace-minutes` | 不支持 | 整数 0–1440 | 半周期并夹在 2–120 | 补跑窗口；`0` 表示从不补跑 |
| `model` | `--model` | 不支持 | 字符串 | 跟随 cron/主模型 | 显式固定模型，按需使用 |
| `provider` | `--provider` | 不支持 | 字符串 | 跟随模型 | 必须与 `model` 同时出现 |
| `reasoning_effort` | `--reasoning-effort` | 不支持 | 枚举 | 跟随配置 | `none`/`minimal`/`low`/`medium`/`high`/`xhigh`/`max`/`ultra` |
| `interpreter` | `--interpreter` | 不支持 | 路径 | Hermes 自带 Python | 仅用于 `.py` 脚本，指向自建 venv |
| `context_from` | 不支持 | `context_from` | 字符串列表 | 空 | 串联其他任务的输出，需工具通道 |
| `enabled_toolsets` | 不支持 | `enabled_toolsets` | 字符串列表 | 全部默认工具 | `[]` 表示显式零工具，不会被放大回默认 |
| `attach_to_session` | 不支持 | `attach_to_session` | 布尔 | 不设置 | 让投递可继续对话；`deliver: local` 时无效果 |

## 2. 两条通道的边界

- **CLI 通道**（`hermes cron create/edit`）能设 `model`、`provider`、`reasoning_effort`、`interpreter`、`grace_minutes`，不能设 `context_from`、`enabled_toolsets`、`attach_to_session`。
- **公共工具通道**（`cronjob_manage`）相反：能设后三者，不能设前五项。`monitor_script` 与 `monitor_url` 在工具侧合并为单个 `monitor` 字段。
- 两边都要用的配置走 `--plan`：CLI 先建暂停任务、读回真实 ID，再把 ID 绑定到工具请求，最后读回字段并（在授权后）恢复。
- 任何一侧装不下的字段都必须报错，不允许静默丢弃。`build-cron.py --tool-json` 遇到 CLI 专属字段会直接失败。

## 3. 布尔与清空的语义

- `null` 或省略 = 不修改。
- 字符串字段用 `''` 清空；`skills`、`context_from` 用 `[]` 清空。
- 模式切换必须显式相反值：关 `no_agent` 用 `--agent`，关 `continuity` 用 `--no-continuity`，解除模型锁用 `--unpin`。
- `enabled_toolsets: []` 是「一个工具都不给」，与「未设置」不是一回事。

## 4. 校验要点

`build-cron.py` 在生成命令前会拦下：未知字段、布尔写成字符串、列表写成标量、`no_agent` 缺 `script`、monitor 双开、`monitor_url` 非 http(s)、`script` 越出 `$HERMES_HOME/scripts`、`paused_reason` 缺 `paused`、`model` 与 `pinned` 并存、`provider` 缺 `model`、`reasoning_effort` 越界、`grace_minutes` 超出 0–1440、YAML 重复键。错误只写 stderr，stdout 保持为空，便于脚本判断。
