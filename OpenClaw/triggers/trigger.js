/**
 * AAC 通用 Trigger：时间窗口 + 去重检查
 *
 * 本脚本为所有 AAC Cron 任务的通用基础防护层。
 * 场景若有额外逻辑（如 docker 状态检测），由 build-cron.py 将场景 JS 拼接在本文件之后。
 *
 * 环境变量：
 *   AAC_TIMEZONE        - 时区（默认 Asia/Shanghai）
 *   AAC_WINDOW_START    - 窗口开始时间 HH:MM
 *   AAC_WINDOW_END      - 窗口结束时间 HH:MM
 *   AAC_DEDUP_FILE      - 去重状态文件路径
 *   AAC_DEDUP_GRANULARITY - 去重粒度：daily | half-day | hourly | per-run
 *   AAC_TEST_MODE       - "true" 时跳过时间窗口和去重检查（测试模式）
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

function getDedupKey(now) {
  const granularity = process.env.AAC_DEDUP_GRANULARITY || "daily";
  const date = `${now.year}-${now.month}-${now.day}`;

  switch (granularity) {
    case "daily":
      return date;
    case "half-day": {
      const hour = parseInt(now.hour);
      return `${date}-${hour < 12 ? "AM" : "PM"}`;
    }
    case "hourly":
      return `${date}-${now.hour}`;
    case "per-run":
      return null;
    default:
      return date;
  }
}

function checkDedup(key) {
  if (!key) return true;

  const fs = require("fs");
  const file = process.env.AAC_DEDUP_FILE;
  if (!file) return true;

  let state = {};
  try {
    const content = fs.readFileSync(file, "utf-8").trim();
    if (content) state = JSON.parse(content);
  } catch (e) {
    // 文件不存在或解析失败，视为新状态
  }

  if (state[key]) {
    return false;
  }

  state[key] = true;
  const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
  for (const k in state) {
    if (typeof state[k] === "number" && state[k] < cutoff) {
      delete state[k];
    }
  }
  state[key] = Date.now();

  const dir = require("path").dirname(file);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(file, JSON.stringify(state, null, 2));
  return true;
}

/**
 * 通用时间窗口 + 去重检查入口
 * 场景 JS 可直接调用此函数，或先调用此函数再执行场景专属逻辑。
 */
function checkTimeWindowAndDedup() {
  // 测试模式：直接放行
  if (process.env.AAC_TEST_MODE === "true") {
    return { fire: true, reason: "Test mode: bypass all checks" };
  }

  const now = getNow();

  if (!checkTimeWindow(now)) {
    return { fire: false, reason: `Outside time window (${now.hour}:${now.minute})` };
  }

  const key = getDedupKey(now);
  if (!checkDedup(key)) {
    return { fire: false, reason: `Already fired for key: ${key}` };
  }

  return { fire: true, reason: "Time window OK and not deduped" };
}

// 注意：本文件不返回任何值，由 build-cron.py 拼接场景 JS 后统一返回
