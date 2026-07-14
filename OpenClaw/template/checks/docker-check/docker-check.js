/**
 * AAC 场景专属 Trigger：Docker 容器状态检测
 *
 * 组合逻辑：先执行通用时间窗口+去重检查，再执行 Docker 状态检测。
 * 任一条件不满足即跳过本次唤醒。
 *
 * 环境变量：
 *   AAC_DOCKER_STATE_FILE - Docker 状态缓存文件路径（默认 /tmp/.aac-docker-state.json）
 */

// 先执行通用检查
const baseResult = checkTimeWindowAndDedup();
if (!baseResult.fire) {
  return baseResult;
}

// ===== Docker 专属检测 =====

function exec(cmd) {
  try {
    const { execSync } = require("child_process");
    return execSync(cmd, { encoding: "utf-8", timeout: 30000 }).trim();
  } catch (e) {
    return "";
  }
}

function getContainerState() {
  const output = exec("docker ps -a --format '{{.Names}}:{{.Status}}'");
  if (!output) return {};

  const lines = output.split("\n").filter((l) => l.trim());
  const state = {};
  for (const line of lines) {
    const [name, ...statusParts] = line.split(":");
    if (name) state[name.trim()] = statusParts.join(":").trim();
  }
  return state;
}

function hasUnhealthy(state) {
  for (const name in state) {
    if (state[name].includes("unhealthy")) return true;
  }
  return false;
}

function hashState(state) {
  const entries = Object.entries(state).sort((a, b) => a[0].localeCompare(b[0]));
  return entries.map(([k, v]) => `${k}=${v}`).join("|");
}

const fs = require("fs");
const stateFile = process.env.AAC_DOCKER_STATE_FILE || "/tmp/.aac-docker-state.json";
const currentState = getContainerState();
const currentHash = hashState(currentState);

let lastState = {};
try {
  if (fs.existsSync(stateFile)) {
    lastState = JSON.parse(fs.readFileSync(stateFile, "utf-8"));
  }
} catch (e) {
  lastState = {};
}

const lastHash = lastState.hash || "";

// 保存当前状态
const dir = require("path").dirname(stateFile);
if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(stateFile, JSON.stringify({ hash: currentHash, timestamp: Date.now() }, null, 2));

// 首次运行 → 只记录基线
if (!lastHash) {
  return { fire: false, reason: "First run, recording baseline state" };
}

// 状态变化 → 触发
if (currentHash !== lastHash) {
  return { fire: true, reason: `Container state changed (base: ${baseResult.reason})` };
}

// 存在 unhealthy → 触发
if (hasUnhealthy(currentState)) {
  return { fire: true, reason: `Unhealthy containers detected (base: ${baseResult.reason})` };
}

return { fire: false, reason: `No state change, all healthy (base: ${baseResult.reason})` };
