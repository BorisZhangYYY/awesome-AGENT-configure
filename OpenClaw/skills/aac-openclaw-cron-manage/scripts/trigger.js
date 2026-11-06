/**
 * AAC 通用 Trigger：时间窗口检查（纯 JS，零外部依赖）
 *
 * 执行步骤：
 *   1. 若注入了 AAC_TEST_MODE（--test 测试模式），直接放行。
 *   2. 根据 AAC_TZ_OFFSET_MINUTES（构建期注入）换算目标时区当前时间。
 *   3. 若配置了 AAC_WINDOW_START / AAC_WINDOW_END：
 *      - 将当前时间转换为当天分钟数。
 *      - 普通窗口（如 07:00-09:30）：当前分钟在窗口内则放行。
 *      - 跨午夜窗口（如 22:00-06:00）：当前分钟在窗口前段或后段则放行。
 *      - 不在窗口内 → 返回 fire: false。
 *   4. 未配置窗口或检查通过 → 返回 fire: true。
 *
 * ┌─────────────────────────────────────────────────────────────────┐
 * │ ⚠️ OpenClaw Trigger 沙箱限制（QuickJS-WASI 隔离环境）            │
 * │                                                                   │
 * │ Trigger 脚本在 OpenClaw Gateway 的 code mode 沙箱中评估，         │
 * │ 引擎为 QuickJS-WASI（无 ICU），以下 API **全部不可用**：           │
 * │                                                                   │
 * │   ❌ Intl（DateTimeFormat/NumberFormat 等，无 ICU 数据）           │
 * │      → 时区换算禁止用 Intl，必须用 AAC_TZ_OFFSET_MINUTES 偏移法    │
 * │   ❌ require() / import（模块访问被静态拒绝，直接报错）            │
 * │      → 禁止 fs / path / child_process / os 等一切 Node 模块       │
 * │   ❌ process 全局对象                                              │
 * │      → 禁止 process.env / process.cwd() 等                        │
 * │   ❌ fetch / XMLHttpRequest / 网络 API                             │
 * │   ❌ setTimeout / setInterval / 异步定时器                         │
 * │                                                                   │
 * │ ✅ 可用：ES2022 纯 JavaScript（Date / Math / JSON / 字符串等）     │
 * │                                                                   │
 * │ 任何新 API 接入前，先用 `openclaw cron run --wait <id>` 实测，     │
 * │ 沙箱内不可用的 API 会以 ReferenceError 使 trigger 评估失败，       │
 * │ 表现为 cron 状态 error 且 Agent 会话永远不启动。                   │
 * └─────────────────────────────────────────────────────────────────┘
 *
 * 去重逻辑已移至 Agent Prompt 中执行，trigger 仅负责时间窗口判定。
 *
 * 常量（由 build-cron.py 注入）：
 *   AAC_TIMEZONE           - IANA 时区名（如 "Asia/Shanghai"），仅作记录
 *   AAC_TZ_OFFSET_MINUTES  - 目标时区 UTC 偏移分钟数（如 480 = UTC+8），
 *                            由 build-cron.py 通过 Python zoneinfo 在构建期计算。
 *                            ⚠️ 夏令时时区在切换后需重新构建任务以刷新偏移；
 *                            无夏令时的时区（如 Asia/Shanghai）永久有效。
 *                            未注入时回退为 Gateway 主机本地时间。
 *   AAC_WINDOW_START       - 窗口开始时间 HH:MM
 *   AAC_WINDOW_END         - 窗口结束时间 HH:MM
 *   AAC_TEST_MODE          - 测试模式标记（--test 注入），置真时跳过窗口检查
 */

function getNow() {
  // 优先：构建期注入的固定 UTC 偏移（纯 Date 运算，沙箱安全）
  if (typeof AAC_TZ_OFFSET_MINUTES === "number") {
    const shifted = new Date(Date.now() + AAC_TZ_OFFSET_MINUTES * 60000);
    return {
      year: shifted.getUTCFullYear(),
      month: shifted.getUTCMonth() + 1,
      day: shifted.getUTCDate(),
      hour: shifted.getUTCHours(),
      minute: shifted.getUTCMinutes(),
    };
  }
  // 回退：Gateway 主机本地时间
  const now = new Date();
  return {
    year: now.getFullYear(),
    month: now.getMonth() + 1,
    day: now.getDate(),
    hour: now.getHours(),
    minute: now.getMinutes(),
  };
}

function checkTimeWindow(now) {
  const start = AAC_WINDOW_START;
  const end = AAC_WINDOW_END;
  if (!start || !end) return true;

  const currentMin = parseInt(now.hour) * 60 + parseInt(now.minute);
  const [sh, sm] = start.split(":").map(Number);
  const [eh, em] = end.split(":").map(Number);
  const startMin = sh * 60 + sm;
  const endMin = eh * 60 + em;

  if (startMin <= endMin) {
    return currentMin >= startMin && currentMin <= endMin;
  }
  // 跨午夜窗口（如 22:00-06:00）
  return currentMin >= startMin || currentMin <= endMin;
}

/**
 * 时间窗口检查入口
 * 场景 JS 可直接调用此函数，或先调用此函数再执行场景专属逻辑。
 */
function main() {
  // 测试模式：跳过窗口检查，直接放行（由 build-cron.py --test 注入）
  if (typeof AAC_TEST_MODE !== "undefined" && AAC_TEST_MODE) {
    return { fire: true, reason: "AAC test mode: window check skipped" };
  }

  const now = getNow();

  if (!checkTimeWindow(now)) {
    return { fire: false, reason: `Outside time window (${now.hour}:${now.minute})` };
  }

  return { fire: true, reason: "Time window OK" };
}

// 注意：本文件不返回任何值，由 build-cron.py 拼接场景 JS 后统一返回
