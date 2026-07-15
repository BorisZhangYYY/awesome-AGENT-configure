/**
 * AAC 场景专属 Trigger：文件/目录变化检测（工作区整理）
 *
 * 执行步骤：
 *   1. 调用通用时间窗口检查 checkTimeWindowOnly()，若当前时间不在窗口内则直接跳过。
 *   2. 读取 AAC_WATCH_FILE 路径的文件或目录信息：
 *      - 文件 → 使用大小 + 修改时间作为哈希。
 *      - 目录 → 递归汇总总大小与最新修改时间作为哈希。
 *   3. 将当前哈希与上一次保存的哈希对比：
 *      - 首次运行 → 只记录基线，不触发。
 *      - 哈希发生变化 → 触发唤醒。
 *      - 哈希未变化 → 跳过本次唤醒。
 *   4. 无论是否触发，都持久化当前哈希到 AAC_FILE_STATE_FILE。
 *
 * 环境变量：
 *   AAC_WATCH_FILE       - 监控的文件/目录路径（默认当前目录）
 *   AAC_FILE_STATE_FILE  - 状态缓存文件路径（默认 /tmp/.aac-file-state.json）
 */

// 步骤 1：通用时间窗口检查
const baseResult = checkTimeWindowOnly();
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
