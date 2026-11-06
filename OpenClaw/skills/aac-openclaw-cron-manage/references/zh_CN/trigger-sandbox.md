# OpenClaw Trigger 沙箱限制

> 本文档是 AAC cron 任务 trigger 脚本开发的**强制约束**。
> 任何修改 `scripts/trigger.js` 或新增场景 `.js` 前，必须先阅读本文。

## 沙箱环境

OpenClaw Gateway（2026.7.1+）的 `--trigger-script` 在 **code mode 沙箱**中评估：

- 引擎：**QuickJS-WASI**（隔离环境，无 ICU 数据）
- 语言：ES2022 纯 JavaScript（TypeScript 会被转译）
- 入口：脚本顶层 `return` 一个对象，`{ fire: true }` 放行任务，`{ fire: false }` 跳过

## 禁用 API 清单

| API | 状态 | 后果 | 替代方案 |
|-----|------|------|----------|
| `Intl.*`（DateTimeFormat 等） | ❌ 无 ICU | `ReferenceError: Intl is not defined` | 构建期注入 `AAC_TZ_OFFSET_MINUTES`，纯 Date 偏移运算 |
| `require()` / `import` | ❌ 静态拒绝 | `ToolInputError: code mode module access is disabled` | 无替代，禁止依赖任何模块 |
| `fs` / `path` / `child_process` / `os` | ❌ 模块被禁 | 同上 | 文件/进程操作移入 Agent Prompt（exec/read/write 工具） |
| `process` 全局对象 | ❌ 未定义 | `ReferenceError: process is not defined` | 配置由 build-cron.py 注入为 `const` 常量 |
| `fetch` / 网络 API | ❌ 未定义 | `ReferenceError` | 网络检测移入 Agent Prompt |
| `setTimeout` / `setInterval` | ❌ 未定义 | `ReferenceError` | trigger 必须同步返回 |

## 可用 API

- ES2022 语言特性：`Date` / `Math` / `JSON` / `String` / `Array` / `Object` / 模板字符串 / 解构等
- 脚本顶层 `return`（code mode 特性）

## 时区换算的正确姿势

IANA 时区换算需要 tz 数据库，沙箱内**无法实现**。AAC 的做法：

1. `build-cron.py` 在构建期用 Python `zoneinfo` 计算时区当前 UTC 偏移；
2. 注入常量 `const AAC_TZ_OFFSET_MINUTES = 480;`（以 Asia/Shanghai 为例）；
3. trigger.js 纯 Date 运算：`new Date(Date.now() + offset * 60000)` 后用 `getUTC*()` 读数。

> ⚠️ **夏令时警告**：偏移在构建期固化。有夏令时的时区（如 America/New_York）在切换后需重新构建任务刷新偏移；无夏令时的时区（如 Asia/Shanghai）永久有效。
> 未注入 `AAC_TZ_OFFSET_MINUTES` 时，trigger.js 回退为 Gateway 主机本地时间。

## 故障表现与排查

沙箱内使用禁用 API 时，**trigger 评估直接失败**，表现为：

```text
status: error (Nx)
last error: cron trigger evaluation failed (internal_error): ReferenceError: ...
```

此时 Agent 会话**永远不会启动**——无报告、无通知、无去重标记，只有 cron 错误计数增长。

排查命令：

```bash
openclaw cron list                          # 看 status 列
openclaw cron show <job-id>                 # 看 last error
```

## 历史事故

- **2026-07-15**：trigger.js 使用 `require('fs')` 做去重 → 全部任务评估失败。修复：去重移至 Agent Prompt。
- **2026-07-19**：trigger.js 使用 `Intl.DateTimeFormat` 做时区换算 → 三个巡检任务全部评估失败（error 4x~7x）。修复：改为构建期注入 UTC 偏移。

## 开发红线

1. **只允许 ES2022 纯 JS**——写完先自问：这段代码在浏览器 `vm` 无 ICU 环境能跑吗？
2. **新增任何 API 前必须实测**：`openclaw cron run --wait <job-id>` 验证 trigger 评估通过。
3. **配置一律构建期注入**：用 `const XXX = ...;`  preamble，禁止运行期探测环境。
4. **文件/网络/进程需求 → 移入 Agent Prompt**，trigger 只做轻量放行判定。
