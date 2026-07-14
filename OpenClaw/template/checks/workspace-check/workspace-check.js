/**
 * AAC 场景专属 Trigger：文件/目录变化检测（工作区整理）
 *
 * 组合逻辑：先执行通用时间窗口+去重检查，再执行文件/目录变化检测。
 * 任一条件不满足即跳过本次唤醒。
 *
 * 环境变量：
 *   AAC_WATCH_FILE       - 监控的文件/目录路径（默认当前目录）
 *   AAC_FILE_STATE_FILE  - 状态缓存文件路径（默认 /tmp/.aac-file-state.json）
 */

// 先执行通用检查
const baseResult = checkTimeWindowAndDedup();
if (!baseResult.fire) {
  return baseResult;
}

// ===== 文件/目录变化检测 =====

const fs = require("fs");
const path = require("path");

function getMtime(filePath) {
  try {
    const stat = fs.statSync(filePath);
    return stat.mtime.getTime();
  } catch (e) {
    return null;
  }
}

function hashDirectory(dirPath) {
  let totalSize = 0;
  let latestMtime = 0;

  function walk(dir) {
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          walk(fullPath);
        } else {
          try {
            const stat = fs.statSync(fullPath);
            totalSize += stat.size;
            if (stat.mtime.getTime() > latestMtime) {
              latestMtime = stat.mtime.getTime();
            }
          } catch (e) {
            // skip
          }
        }
      }
    } catch (e) {
      // skip
    }
  }

  walk(dirPath);
  return `${totalSize}:${latestMtime}`;
}

const watchFile = process.env.AAC_WATCH_FILE || ".";
const stateFile = process.env.AAC_FILE_STATE_FILE || "/tmp/.aac-file-state.json";

let currentHash;
try {
  const stat = fs.statSync(watchFile);
  if (stat.isDirectory()) {
    currentHash = hashDirectory(watchFile);
  } else {
    currentHash = `${stat.size}:${stat.mtime.getTime()}`;
  }
} catch (e) {
  return { fire: false, reason: `Cannot stat ${watchFile}: ${e.message}` };
}

let lastState = {};
try {
  if (fs.existsSync(stateFile)) {
    lastState = JSON.parse(fs.readFileSync(stateFile, "utf-8"));
  }
} catch (e) {
  lastState = {};
}

const dir = path.dirname(stateFile);
if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(stateFile, JSON.stringify({ hash: currentHash, timestamp: Date.now() }, null, 2));

if (!lastState.hash) {
  return { fire: false, reason: `First run, recording baseline (base: ${baseResult.reason})` };
}

if (currentHash !== lastState.hash) {
  return { fire: true, reason: `File changed: ${watchFile} (base: ${baseResult.reason})` };
}

return { fire: false, reason: `No change (base: ${baseResult.reason})` };
