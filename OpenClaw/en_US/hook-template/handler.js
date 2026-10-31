/**
 * {{PLUGIN_NAME}} — Context injection hook handler
 *
 * Listens for the agent:bootstrap event and injects the contents of context.md
 * into the bootstrap context every time an Agent session starts.
 * Does not modify the user's existing workspace files.
 *
 * Customization:
 *   Usually you only need to edit context.md; this file rarely needs changes.
 *   To adjust the injection position or method, edit injectContext().
 *
 * Events:
 *   agent:bootstrap — fired when an Agent session initializes
 *
 * Environment variables (optional):
 *   {{PLUGIN_ENV_PREFIX}}_CONTEXT_PATH — custom context file path
 */

const fs = require("fs");
const path = require("path");

/**
 * Read the context file contents.
 * @returns {string} context text
 */
function loadContext() {
  const customPath = process.env["{{PLUGIN_ENV_PREFIX}}_CONTEXT_PATH"];
  const contextPath = customPath || path.join(__dirname, "context.md");

  if (!fs.existsSync(contextPath)) {
    console.warn(`[{{PLUGIN_NAME}}] Context file not found: ${contextPath}`);
    return "";
  }

  return fs.readFileSync(contextPath, "utf-8").trim();
}

/**
 * Inject context text into the bootstrap message list.
 *
 * @param {string} contextText - context text
 * @param {Array<{role: string, content: string}>} messages - current bootstrap messages
 * @returns {Array<{role: string, content: string}>} messages after injection
 */
function injectContext(contextText, messages) {
  if (!contextText) return messages;

  const contextMessage = {
    role: "user",
    content: `[{{PLUGIN_NAME}}]\n\n${contextText}`,
  };

  // Default injection position: after the system message, before user messages.
  // Adjust this logic to append at the end or insert at a specific index.
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
 * agent:bootstrap event entry point.
 */
function onAgentBootstrap(event, context) {
  const contextText = loadContext();

  if (!contextText) {
    console.log(`[{{PLUGIN_NAME}}] Context is empty; skipping injection`);
    return event;
  }

  console.log(
    `[{{PLUGIN_NAME}}] Injecting context (${contextText.length} characters)`
  );

  event.messages = injectContext(contextText, event.messages || []);
  return event;
}

module.exports = {
  "agent:bootstrap": onAgentBootstrap,
};
