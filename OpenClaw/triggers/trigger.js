/**
 * AAC 通用 Trigger：时间窗口检查
 *
 * 本脚本为所有 AAC Cron 任务的通用基础防护层。
 * ⚠️ 纯 JavaScript 实现，禁止依赖任何外部模块（fs/path 等），
 *    因为 OpenClaw Gateway trigger 执行环境禁用了 module access。
 * 去重逻辑已移至 Agent Prompt 中执行，trigger 仅负责时间窗口判定。
 *
 * 环境变量：
 *   AAC_TIMEZONE        - 时区（默认 Asia/Shanghai）
 *   AAC_WINDOW_START    - 窗口开始时间 HH:MM
 *   AAC_WINDOW_END      - 窗口结束时间 HH:MM
 *   AAC_TEST_MODE       - "true" 时跳过所有检查（测试模式）
 */

function getNow() {
  const tz = process.env.AAC_TIMEZONE || "Asia/Shanghai";
  const now = new Date();
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: tz,
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
    hour12: false,
  });
  const parts = formatter.formatToParts(now);
  const getPart = (type) => parts.find((p) => p.type === type).value;
  return {
    year: getPart("year"),
    month: getPart("month"),
    day: getPart("day"),
    hour: getPart("hour"),
    minute: getPart("minute"),
  };
}

function checkTimeWindow(now) {
  const start = process.env.AAC_WINDOW_START;
  const end = process.env.AAC_WINDOW_END;
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
 * 通用时间窗口检查入口
 * 场景 JS 可直接调用此函数，或先调用此函数再执行场景专属逻辑。
 */
function checkTimeWindowOnly() {
  // 测试模式：直接放行
  if (process.env.AAC_TEST_MODE === "true") {
    return { fire: true, reason: "Test mode: bypass all checks" };
  }

  const now = getNow();

  if (!checkTimeWindow(now)) {
    return { fire: false, reason: `Outside time window (${now.hour}:${now.minute})` };
  }

  return { fire: true, reason: "Time window OK" };
}

// 注意：本文件不返回任何值，由 build-cron.py 拼接场景 JS 后统一返回
