/**
 * {{PLUGIN_NAME}} — 上下文注入 Hook Handler
 *
 * 监听 agent:bootstrap 事件，在每次 Agent 会话启动时将 context.md 的内容
 * 注入到 bootstrap 上下文中。不修改用户已有的工作区文件。
 *
 * 定制方式：
 *   只需修改 context.md 的内容即可，本文件通常无需改动。
 *   如需调整注入位置或注入方式，修改 injectContext() 函数。
 *
 * 事件：
 *   agent:bootstrap — Agent 会话初始化时触发
 *
 * 环境变量（可选）：
 *   {{PLUGIN_ENV_PREFIX}}_CONTEXT_PATH — 自定义上下文文件路径
 */

const fs = require("fs");
const path = require("path");

/**
 * 读取上下文文件内容
 * @returns {string} 上下文文本
 */
function loadContext() {
  const customPath = process.env["{{PLUGIN_ENV_PREFIX}}_CONTEXT_PATH"];
  const contextPath = customPath || path.join(__dirname, "context.md");

  if (!fs.existsSync(contextPath)) {
    console.warn(`[{{PLUGIN_NAME}}] 上下文文件不存在：${contextPath}`);
    return "";
  }

  return fs.readFileSync(contextPath, "utf-8").trim();
}

/**
 * 将上下文内容注入到 bootstrap 消息列表中
 *
 * @param {string} contextText - 上下文文本
 * @param {Array<{role: string, content: string}>} messages - 当前 bootstrap 消息列表
 * @returns {Array<{role: string, content: string}>} 注入后的消息列表
 */
function injectContext(contextText, messages) {
  if (!contextText) return messages;

  const contextMessage = {
    role: "user",
    content: `[{{PLUGIN_NAME}}]\n\n${contextText}`,
  };

  // 默认注入位置：在系统消息之后、用户消息之前
  // 如需调整位置（如追加到末尾、插入到指定位置），修改此逻辑
  const result = [...messages];
  const systemIndex = result.findIndex((m) => m.role === "system");

  if (systemIndex >= 0) {
    result.splice(systemIndex + 1, 0, contextMessage);
  } else {
    result.unshift(contextMessage);
  }

  return result;
}

/**
 * agent:bootstrap 事件处理入口
 */
function onAgentBootstrap(event, context) {
  const contextText = loadContext();

  if (!contextText) {
    console.log(`[{{PLUGIN_NAME}}] 上下文为空，跳过注入`);
    return event;
  }

  console.log(
    `[{{PLUGIN_NAME}}] 注入上下文（${contextText.length} 字符）`
  );

  event.messages = injectContext(contextText, event.messages || []);
  return event;
}

module.exports = {
  "agent:bootstrap": onAgentBootstrap,
};
