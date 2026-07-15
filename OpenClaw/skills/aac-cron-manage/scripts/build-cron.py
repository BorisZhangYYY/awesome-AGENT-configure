#!/usr/bin/env python3
"""OpenClaw Cron 模板渲染器

读取场景 YAML 和通用模板，渲染后输出 openclaw cron create 命令。
本脚本完全自包含，无外部文件依赖，可直接拷贝到任意项目使用。

用法：
    python3 build-cron.py scene.yaml
    python3 build-cron.py scene.yaml --json
    python3 build-cron.py scene.yaml --preview

依赖：
    pip install pyyaml
"""

import argparse
import json
import os
import re
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    print("错误：本脚本依赖 PyYAML，请先安装：pip install pyyaml", file=sys.stderr)
    raise SystemExit(1) from exc


# ===== 默认变量值 =====
# 场景 YAML 中未提供的变量使用以下默认值。

DEFAULTS = {
    "SCHEDULE_TYPE": "cron",
    "TIMEZONE": "Asia/Shanghai",
    "DELIVERY_MODE": "announce",
    "BEST_EFFORT": "true",
    "LIGHT_CONTEXT": "false",
    "DISABLED": "false",
    "DELETE_AFTER_RUN": "false",
    "KEEP_AFTER_RUN": "false",
    "EXACT": "false",
    "TIMEOUT_SECONDS": "300",
    "THINKING": "off",
    "DEDUP_STATE_FILE": "{{WORKSPACE}}/.state/dedup.txt",
    "DEDUP_GRANULARITY": "daily",
    "LOOP_MODE_ENABLED": "false",
    "LOOP_TASK_TYPE": "软件开发",
    "LOOP_EXEC_INSTRUCTIONS": "",
    "LOOP_STATE_SCHEMA": "",
    "DEV_PROJECT_NAME": "",
    "DEV_PROJECT_DIR": "/path/to/your/project",
    "DEV_PHASE": "",
    "DEV_BRANCH": "",
    "DEV_STATE_FILE": "{{DEV_PROJECT_DIR}}/.state/dev-session.json",
    "DEV_TEST_PATTERN": "test_*.py",
    "DEV_COMMIT_PREFIX": "feat",
    "DEV_GOAL": "",
    "DEV_MILESTONES": "[]",
    "DEV_CURRENT_MILESTONE": "",
    "DEV_AUTO_DISABLE_ON_GOAL_REACHED": "false",
    "DEV_TASK_INSTRUCTIONS": "",
    "DEV_DOCS_DIR": "{{DEV_PROJECT_DIR}}/docs",
    "SCENE_SPECIFIC_INSTRUCTIONS": "",
    "PERSONA_MODE": "inline",
    "WORKSPACE": "~/.openclaw/workspace",
    # Trigger 默认值（OpenClaw 2026.7.1+）
    "TRIGGER_ENABLED": "false",
    "TRIGGER_SCRIPT": "",
    "TRIGGER_ONCE": "false",
}

# ===== CLI 参数映射表 =====
# 模板字段到 openclaw cron create 命令行参数的映射。

FLAGS = {
    "official": {
        "name": "--name",
        "message": "--message",
        "systemEvent": "--system-event",
        "schedule.timezone": "--tz",
        "delivery.channel": "--channel",
        "delivery.to": "--to",
        "delivery.threadId": "--thread-id",
        "delivery.webhookUrl": "--webhook",
        "session.target": "--session",
        "session.timeoutSeconds": "--timeout-seconds",
        "agent.agentId": "--agent",
        "agent.model": "--model",
        "agent.thinking": "--thinking",
        "agent.tools": "--tools",
        "command.script": "--command",
        "command.cwd": "--command-cwd",
        "command.argv": "--command-argv",
        "command.input": "--command-input",
        "command.env": "--command-env",
        "command.noOutputTimeoutSeconds": "--no-output-timeout-seconds",
        "command.outputMaxBytes": "--output-max-bytes",
        "advanced.wake": "--wake",
        "advanced.stagger": "--stagger",
    },
    "special": {
        "schedule.expr": {
            "type": "positional",
            "note": "cron 表达式，作为 openclaw cron create 的第一个位置参数",
        },
        "delivery.mode": {
            "type": "enum_flag",
            "values": {
                "announce": "--announce",
                "webhook": "--webhook",
                "none": "--no-deliver",
            },
        },
        "delivery.bestEffort": {
            "type": "boolean_flag",
            "true_flag": "--best-effort-deliver",
            "false_flag": "--no-best-effort-deliver",
        },
        "context.lightContext": {
            "type": "boolean_flag",
            "true_flag": "--light-context",
            "false_flag": None,
        },
        "advanced.disabled": {
            "type": "boolean_flag",
            "true_flag": "--disabled",
            "false_flag": None,
        },
        "advanced.deleteAfterRun": {
            "type": "boolean_flag",
            "true_flag": "--delete-after-run",
            "false_flag": None,
        },
        "advanced.keepAfterRun": {
            "type": "boolean_flag",
            "true_flag": "--keep-after-run",
            "false_flag": None,
        },
        "advanced.exact": {
            "type": "boolean_flag",
            "true_flag": "--exact",
            "false_flag": None,
        },
        # OpenClaw 2026.7.1+ trigger 支持
        "trigger.once": {
            "type": "boolean_flag",
            "true_flag": "--trigger-once",
            "false_flag": None,
        },
    },
}


def main():
    args = parse_args()
    scene_path = Path(args.scene_file)

    if not scene_path.exists():
        raise FileNotFoundError(f"场景文件不存在：{scene_path}")

    scene = load_yaml(scene_path)
    template, template_path = load_template(scene, scene_path)

    variables = build_variables(DEFAULTS, template, scene)

    # 对 Loop 模式相关变量做前置校验，避免未定义变量泄漏到 cron message
    validate_loop_variables(variables)

    # 根据 persona 配置注入 {{PERSONA_PROMPT}}
    variables["PERSONA_PROMPT"] = build_persona_prompt(template, variables)

    # 渲染 message（结构处理 → 变量替换 → 起源标记）
    message = render_message(template, scene, variables, template_path)

    # 递归展开变量值中的嵌套占位符，供 build_command 使用
    variables = resolve_variables(variables)
    variables["MESSAGE"] = message

    # 检查是否残留未解析的模板标记
    check_unresolved(message)

    cmd = build_command(variables, FLAGS, str(scene_path), args.test)

    if args.preview:
        print("=== 渲染后的 MESSAGE（前500字符）===")
        print(message[:500] + ("..." if len(message) > 500 else ""))
        print()
        print("=== 完整命令 ===")
        print(format_shell_command(cmd))
        return

    if args.json:
        print(json.dumps(cmd, ensure_ascii=False, indent=2))
    else:
        print(format_shell_command(cmd))


def parse_args():
    parser = argparse.ArgumentParser(
        description="根据场景 YAML 生成 openclaw cron create 命令"
    )
    parser.add_argument("scene_file", help="场景 YAML 文件路径")
    parser.add_argument(
        "--json", action="store_true", help="以 JSON 数组格式输出命令"
    )
    parser.add_argument(
        "--preview", action="store_true", help="预览渲染后的 message 和命令，不执行创建"
    )
    parser.add_argument(
        "--test", action="store_true", help="测试模式：跳过时间窗口和去重，任务名称加【TEST】前缀，创建后自动删除"
    )
    return parser.parse_args()


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_template(scene, scene_path):
    """根据 scene 中的 templateRef 加载通用模板。"""
    template_ref = scene.get("templateRef", "../template-cron.zh.yaml")
    template_path = Path(template_ref)
    if not template_path.is_absolute():
        template_path = (scene_path.parent / template_path).resolve()
    else:
        template_path = template_path.resolve()

    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在：{template_path}")

    return load_yaml(template_path), template_path


def build_variables(defaults, template, scene):
    """合并变量，优先级：defaults < 模板内置 variables < 场景 variables。"""
    variables = {}
    variables.update(defaults or {})
    variables.update(template.get("variables", {}) or {})
    variables.update(scene.get("variables", {}) or {})
    # 注入 WORKSPACE：将 ~ 展开并转为绝对路径，若场景已显式定义则优先使用
    workspace = os.path.abspath(os.path.expanduser(variables.get("WORKSPACE", "~/.openclaw/workspace")))
    variables["WORKSPACE"] = workspace
    return variables


def resolve_variables(variables, max_depth=5):
    """递归展开变量值中的嵌套占位符，返回完全展开后的新字典。

    对变量值中的嵌套占位符（如 DEDUP_STATE_FILE: "{{WORKSPACE}}/..."）进行预展开，
    避免在 template 替换阶段对同一文本多次扫描，同时降低误替换值中字面量 `{{}}` 的风险。
    列表和字典类型保持原样，由调用方按需序列化。
    """
    resolved = {}
    for k, v in variables.items():
        if v is None:
            resolved[k] = ""
        elif isinstance(v, (list, dict)):
            resolved[k] = v
        else:
            resolved[k] = str(v)

    for _ in range(max_depth):
        changed = False
        new_resolved = {}
        for key, value in resolved.items():
            if not isinstance(value, str):
                new_resolved[key] = value
                continue
            new_value = value
            for other_key, other_value in resolved.items():
                if not isinstance(other_value, str):
                    continue
                placeholder = "{{" + other_key + "}}"
                if placeholder in new_value:
                    new_value = new_value.replace(placeholder, other_value)
                    changed = True
            new_resolved[key] = new_value
        resolved = new_resolved
        if not changed:
            break
    return resolved


def render_message(template, scene, variables, template_path):
    """完整的消息渲染管线。

    阶段 1：处理结构标记（{{#LOOP_ONLY}}、{{#IF}} 等），此时变量值尚未替换，
            用户内容中的 {{#IF}} 等字面量不会被误解析为模板指令。
    阶段 2：替换 {{VAR}} 占位符为实际变量值。
    阶段 3：注入 AAC 起源标记。
    """
    if scene.get("template"):
        raise ValueError(
            "场景 YAML 不允许直接定义顶层 template 字段，"
            "请使用 SCENE_SPECIFIC_INSTRUCTIONS 变量注入场景特定内容"
        )

    template_str = template.get("template", "")
    if not template_str:
        return variables.get("MESSAGE", "")

    # 阶段 1：结构处理（先于变量替换，防止用户内容注入模板指令）
    message = apply_loop_mode(template_str, variables)
    message = apply_conditional_blocks(message, variables)

    # 阶段 2：变量替换
    resolved = resolve_variables(variables)
    message = substitute_variables(message, resolved)

    # 阶段 3：起源标记
    message = inject_origin_tag(message, template_path, variables)

    return message


def substitute_variables(text, variables):
    """替换文本中的 {{VAR}} 占位符为实际变量值。

    列表/字典值使用 json.dumps 序列化（双引号 JSON），
    而非 Python 的 str()（单引号 repr），确保在 JSON 代码块中的合法性。
    """
    result = text
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        if isinstance(value, (list, dict)):
            result = result.replace(placeholder, json.dumps(value, ensure_ascii=False))
        else:
            result = result.replace(placeholder, str(value))
    return result


def check_unresolved(message):
    """检查 message 中是否有未解析的模板标记，通过 stderr 发出警告。

    覆盖两类标记：
    - 变量占位符：{{XXX}}（大写变量风格）
    - 控制标记：{{#IF}}、{{/IF}}、{{#ELSE}}、{{#LOOP_ONLY}} 等
    """
    var_pattern = r"\{\{[A-Z][A-Z0-9_]*\}\}"
    control_pattern = r"\{\{[#/](?:IF|LOOP_ONLY|NON_LOOP_ONLY|ELSE)\s*\w*\}\}"

    unresolved_vars = set(re.findall(var_pattern, message))
    unresolved_ctrl = set(re.findall(control_pattern, message))

    all_unresolved = sorted(unresolved_vars | unresolved_ctrl)
    if all_unresolved:
        print(
            f"警告：message 中可能存在未解析的模板标记：{all_unresolved}",
            file=sys.stderr,
        )


def apply_loop_mode(message, variables):
    """根据 LOOP_MODE_ENABLED 保留或剥离 Loop 模式专属片段。

    template-cron.zh.yaml 中同时包含普通任务和 Loop 任务两套 Prompt，
    分别用 {{#LOOP_ONLY}}...{{/LOOP_ONLY}} 和 {{#NON_LOOP_ONLY}}...{{/NON_LOOP_ONLY}}
    标记。本函数根据 LOOP_MODE_ENABLED 的值只保留对应分支，并移除标记本身。
    """
    loop_enabled = parse_bool(variables.get("LOOP_MODE_ENABLED", "false"))
    if loop_enabled:
        # 删除普通任务专属片段
        message = re.sub(
            r"\{\{#NON_LOOP_ONLY\}\}.*?\{\{/NON_LOOP_ONLY\}\}",
            "",
            message,
            flags=re.DOTALL,
        )
        # 移除 Loop 标记，保留内容
        message = message.replace("{{#LOOP_ONLY}}", "").replace("{{/LOOP_ONLY}}", "")
    else:
        # 删除 Loop 任务专属片段
        message = re.sub(
            r"\{\{#LOOP_ONLY\}\}.*?\{\{/LOOP_ONLY\}\}",
            "",
            message,
            flags=re.DOTALL,
        )
        # 移除普通标记，保留内容
        message = message.replace("{{#NON_LOOP_ONLY}}", "").replace("{{/NON_LOOP_ONLY}}", "")
    return message


def apply_conditional_blocks(message, variables):
    """处理 {{#IF VAR}}...{{#ELSE}}...{{/IF}} 条件块。

    若 VAR 语义为「真」（非空且非 falsy 字面量），保留 IF 分支；否则保留 ELSE 分支。
    处理时机：在变量替换之前执行，防止用户内容中的 {{#IF}} 字面量被误解析。
    """
    pattern = r"\{\{#IF\s+(\w+)\}\}(.*?)\{\{#ELSE\}\}(.*?)\{\{/IF\}\}"

    def replacer(match):
        var_name = match.group(1)
        if_block = match.group(2)
        else_block = match.group(3)
        value = variables.get(var_name, "")
        if _is_truthy(value):
            return if_block
        return else_block

    return re.sub(pattern, replacer, message, flags=re.DOTALL)


def _is_truthy(value):
    """判断变量值在模板条件中是否为「真」。

    除 Python 原生 falsy 值（None、空字符串、0、False、空列表/字典）外，
    还将以下字符串字面量视为 falsy：
    "false"、"0"、"no"、"off"、"[]"、"{}"、"null"、"none"
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, dict)):
        return len(value) > 0
    if isinstance(value, (int, float)):
        return bool(value)
    s = str(value).strip().lower()
    if s in ("", "false", "0", "no", "off", "[]", "{}", "null", "none"):
        return False
    return True


def inject_origin_tag(message, template_path, variables, now=None):
    """在 message 开头注入 AAC 起源标记，用于后续 SKILL 识别和管理。

    格式：<!-- AAC_ORIGIN: template=xxx | generated=xxx | category=xxx | job=xxx -->

    即使 cron 被大幅定制化（改名、改结构），只要 message 中保留此标记，
    AAC SKILL（如 update-cron）就能识别其上游模板来源。

    now 参数用于测试：传入固定 datetime 以产生可复现输出。
    """
    if now is None:
        now = datetime.now(timezone.utc)
    origin_timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    template_name = template_path.name
    category = _sanitize_origin(str(variables.get("CATEGORY", "")))
    job_name = _sanitize_origin(str(variables.get("JOB_NAME", "")))

    origin_tag = (
        f"<!-- AAC_ORIGIN: template={template_name}"
        f" | generated={origin_timestamp}"
        f" | category={category}"
        f" | job={job_name} -->"
    )
    return origin_tag + "\n\n" + message


def _sanitize_origin(text):
    """替换 HTML 注释终止符 --> 为 -- >，防止 origin 标签提前闭合。"""
    return text.replace("-->", "-- >")


def build_persona_prompt(template, variables):
    """根据 persona 配置生成 {{PERSONA_PROMPT}} 的内容。"""
    persona = template.get("persona", {})
    mode = str(variables.get("PERSONA_MODE", "")).strip().lower()
    # 显式未设置（空字符串、null）时回退到模板默认值
    if not mode:
        mode = str(persona.get("mode", "inline")).strip().lower()
    persona_file = variables.get("PERSONA_FILE", persona.get("file", ""))
    persona_role = variables.get("PERSONA_ROLE", "")
    # 场景未定义 PERSONA_ROLE 时，尝试从模板 persona.role 读取
    # 但需过滤包含未解析占位符（如 "{{PERSONA_ROLE}}"）的字符串，避免泄漏到输出
    if not persona_role or str(persona_role).strip() == "":
        raw_role = persona.get("role", "")
        if raw_role and not re.search(r"\{\{.*?\}\}", raw_role):
            persona_role = raw_role

    if mode == "file" and persona_file:
        return f"请基于 {persona_file} 中定义的人设。"
    if persona_role:
        return f"你是一个{persona_role}。"
    return ""


def build_command(variables, flags, scene_path, test_mode=False):
    """根据变量和 flags 映射表构建 openclaw cron create 命令数组。"""
    cmd = ["openclaw", "cron", "create"]

    # 位置参数：schedule.expr
    schedule_expr = variables.get("SCHEDULE_EXPR")
    if not schedule_expr:
        raise ValueError("缺少必要变量：SCHEDULE_EXPR")
    cmd.append(str(schedule_expr))

    # 测试模式：任务名称加前缀，自动删除
    job_name = variables.get("JOB_NAME", "")
    if test_mode:
        job_name = f"【TEST】{job_name}"
        variables["JOB_NAME"] = job_name

    # message 与 command 二选一
    command_script = variables.get("COMMAND_SCRIPT", "")
    if command_script:
        # 命令模式：渲染 command 相关参数
        add_flag(cmd, "command.script", command_script, flags)
        add_flag(cmd, "command.cwd", variables.get("COMMAND_CWD", ""), flags)
        add_flag(cmd, "command.argv", variables.get("COMMAND_ARGV", ""), flags)
        add_flag(cmd, "command.input", variables.get("COMMAND_INPUT", ""), flags)
        add_flag(cmd, "command.env", variables.get("COMMAND_ENV", ""), flags)
        add_flag(
            cmd,
            "command.noOutputTimeoutSeconds",
            variables.get("COMMAND_NO_OUTPUT_TIMEOUT", ""),
            flags,
        )
        add_flag(
            cmd,
            "command.outputMaxBytes",
            variables.get("COMMAND_OUTPUT_MAX_BYTES", ""),
            flags,
        )
    else:
        # Agent 模式：渲染 --message / --system-event
        message = variables.get("MESSAGE", "")
        if message:
            add_flag(cmd, "message", message, flags)
        system_event = variables.get("SYSTEM_EVENT", "")
        if system_event:
            add_flag(cmd, "systemEvent", system_event, flags)

    # 基础信息
    add_flag(cmd, "name", variables.get("JOB_NAME", ""), flags)

    # 调度
    add_flag(cmd, "schedule.timezone", variables.get("TIMEZONE", ""), flags)

    # 投递
    add_special_delivery(cmd, variables, flags)
    add_flag(cmd, "delivery.channel", variables.get("CHANNEL", ""), flags)
    add_flag(cmd, "delivery.to", variables.get("TO", ""), flags)
    add_flag(cmd, "delivery.threadId", variables.get("THREAD_ID", ""), flags)
    add_flag(cmd, "delivery.webhookUrl", variables.get("WEBHOOK_URL", ""), flags)

    # 会话
    session_target = str(variables.get("SESSION_TARGET", "")).strip()
    persistent_id = str(variables.get("PERSISTENT_ID", "")).strip()
    # 优先级：SESSION_TARGET 显式值（含 session:xxx）> PERSISTENT_ID 自动拼接 > 默认 isolated
    if not session_target.startswith("session:") and not session_target:
        if persistent_id:
            session_target = f"session:{persistent_id}"
        else:
            session_target = "isolated"
    if session_target:
        add_flag(cmd, "session.target", session_target, flags)
    add_flag(cmd, "session.timeoutSeconds", variables.get("TIMEOUT_SECONDS", ""), flags)

    # 上下文
    add_special_boolean(cmd, "context.lightContext", variables.get("LIGHT_CONTEXT", ""), flags)

    # Agent 配置
    add_flag(cmd, "agent.agentId", variables.get("AGENT_ID", ""), flags)
    add_flag(cmd, "agent.model", variables.get("MODEL", ""), flags)
    add_flag(cmd, "agent.thinking", variables.get("THINKING", ""), flags)
    add_flag(cmd, "agent.tools", variables.get("TOOLS", ""), flags)

    # 高级选项
    add_special_boolean(cmd, "advanced.disabled", variables.get("DISABLED", ""), flags)
    add_special_boolean(cmd, "advanced.deleteAfterRun", variables.get("DELETE_AFTER_RUN", ""), flags)
    add_special_boolean(cmd, "advanced.keepAfterRun", variables.get("KEEP_AFTER_RUN", ""), flags)
    add_flag(cmd, "advanced.wake", variables.get("WAKE", ""), flags)
    add_special_boolean(cmd, "advanced.exact", variables.get("EXACT", ""), flags)
    add_flag(cmd, "advanced.stagger", variables.get("STAGGER", ""), flags)

    # OpenClaw 2026.7.1+ trigger 支持
    add_trigger(cmd, variables, scene_path, test_mode)

    # 测试模式：自动追加 --delete-after-run
    if test_mode:
        cmd.append("--delete-after-run")

    return cmd


def add_trigger(cmd, variables, scene_path, test_mode=False):
    """处理 trigger 配置：构建组合脚本并添加 --trigger-script 参数。

    构建流程：
    1. 注入环境变量（AAC_TIMEZONE / AAC_WINDOW_START 等）
    2. 读取通用 trigger.js（时间窗口 + 去重）
    3. 检测场景目录是否有同名 .js 文件：
       - 有 → 拼接场景 JS（场景内自行调用 checkTimeWindowAndDedup()）
       - 无 → 自动追加 `return checkTimeWindowAndDedup();`
    4. 若 test_mode → 在脚本头部注入 AAC_TEST_MODE = "true"
    """
    trigger_enabled = parse_bool(variables.get("TRIGGER_ENABLED", "false"))
    if not trigger_enabled:
        return

    trigger_script = build_trigger_script(scene_path, variables, test_mode)
    if not trigger_script:
        return

    job_name = str(variables.get("JOB_NAME", "untitled")).strip()
    scene_dir = os.path.dirname(os.path.abspath(scene_path))
    trigger_dir = scene_dir
    os.makedirs(trigger_dir, exist_ok=True)
    trigger_path = os.path.join(trigger_dir, "trigger.js")

    with open(trigger_path, "w", encoding="utf-8") as f:
        f.write(trigger_script)

    cmd.append("--trigger-script")
    cmd.append(trigger_path)

    trigger_once = parse_bool(variables.get("TRIGGER_ONCE", "false"))
    if trigger_once:
        cmd.append("--trigger-once")


def build_trigger_script(scene_path, variables, test_mode=False):
    """构建完整的 trigger 脚本：环境变量 + 通用 trigger.js + 场景 JS（可选）。"""
    # 优先通过 AAC_REPO 环境变量定位 trigger.js
    aac_repo = os.environ.get("AAC_REPO", "")
    if aac_repo:
        trigger_js_path = Path(aac_repo) / "OpenClaw" / "triggers" / "trigger.js"
    else:
        # fallback: 向上搜索 triggers/trigger.js
        script_dir = Path(__file__).parent
        search_dir = script_dir
        trigger_js_path = None
        for _ in range(6):
            candidate = search_dir / "triggers" / "trigger.js"
            if candidate.exists():
                trigger_js_path = candidate
                break
            parent = search_dir.parent
            if parent == search_dir:
                break
            search_dir = parent

    if not trigger_js_path or not trigger_js_path.exists():
        raise FileNotFoundError(f"通用 trigger 脚本不存在：{trigger_js_path or 'triggers/trigger.js'}")

    # 1. 环境变量注入
    env_lines = []
    timezone = variables.get("TIMEZONE", "")
    if timezone:
        env_lines.append(f'process.env.AAC_TIMEZONE = {json.dumps(timezone)};')

    window_start = variables.get("WINDOW_START", "")
    window_end = variables.get("WINDOW_END", "")
    if window_start:
        env_lines.append(f'process.env.AAC_WINDOW_START = {json.dumps(window_start)};')
    if window_end:
        env_lines.append(f'process.env.AAC_WINDOW_END = {json.dumps(window_end)};')

    dedup_file = variables.get("DEDUP_STATE_FILE", "")
    if dedup_file:
        env_lines.append(f'process.env.AAC_DEDUP_FILE = {json.dumps(dedup_file)};')

    dedup_granularity = variables.get("DEDUP_GRANULARITY", "daily")
    env_lines.append(f'process.env.AAC_DEDUP_GRANULARITY = {json.dumps(dedup_granularity)};')

    # ⚠️ 注意：trigger.js 已移除 fs 模块依赖，DEDUP 环境变量保留但不再由 trigger 消费。
    # 去重逻辑已移至 Agent Prompt 中，由 Agent 自行通过 exec/read/write 工具维护状态文件。

    # 场景专属变量
    docker_state = variables.get("DOCKER_STATE_FILE", "")
    if docker_state:
        env_lines.append(f'process.env.AAC_DOCKER_STATE_FILE = {json.dumps(docker_state)};')

    git_dir = variables.get("GIT_DIR", "")
    if git_dir:
        env_lines.append(f'process.env.AAC_GIT_DIR = {json.dumps(git_dir)};')
    git_state = variables.get("GIT_STATE_FILE", "")
    if git_state:
        env_lines.append(f'process.env.AAC_GIT_STATE_FILE = {json.dumps(git_state)};')

    watch_file = variables.get("WATCH_FILE", "")
    if watch_file:
        env_lines.append(f'process.env.AAC_WATCH_FILE = {json.dumps(watch_file)};')
    file_state = variables.get("FILE_STATE_FILE", "")
    if file_state:
        env_lines.append(f'process.env.AAC_FILE_STATE_FILE = {json.dumps(file_state)};')

    watch_url = variables.get("WATCH_URL", "")
    if watch_url:
        env_lines.append(f'process.env.AAC_WATCH_URL = {json.dumps(watch_url)};')
    http_state = variables.get("HTTP_STATE_FILE", "")
    if http_state:
        env_lines.append(f'process.env.AAC_HTTP_STATE_FILE = {json.dumps(http_state)};')

    # 测试模式
    if test_mode:
        env_lines.append('process.env.AAC_TEST_MODE = "true";')

    preamble = "// ===== AAC Trigger 环境变量注入 =====\n" + "\n".join(env_lines) + "\n\n"

    # 2. 通用 trigger.js
    base_script = trigger_js_path.read_text(encoding="utf-8")

    # 3. 检测场景专属 JS
    scene_dir = Path(scene_path).parent
    scene_name = Path(scene_path).stem
    scene_js = scene_dir / f"{scene_name}.js"

    if scene_js.exists():
        scene_script = scene_js.read_text(encoding="utf-8")
        full_script = preamble + base_script + "\n\n" + scene_script
    else:
        # 无场景 JS → 直接返回时间窗口检查结果
        full_script = preamble + base_script + "\n\n// ===== 场景无专属逻辑，直接返回通用检查结果 =====\nreturn checkTimeWindowOnly();\n"

    return full_script


def add_flag(cmd, field_path, value, flags):
    """添加普通官方参数到命令数组。"""
    if is_empty(value):
        return
    flag = flags.get("official", {}).get(field_path)
    if not flag:
        return
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False)
    cmd.extend([flag, str(value)])


def add_special_delivery(cmd, variables, flags):
    """处理 delivery.mode 和 delivery.bestEffort 两个特殊投递参数。"""
    mode = variables.get("DELIVERY_MODE", "")
    rule = flags.get("special", {}).get("delivery.mode", {})
    flag = rule.get("values", {}).get(mode)
    if flag:
        cmd.append(flag)

    best_effort = variables.get("BEST_EFFORT", "")
    add_special_boolean(cmd, "delivery.bestEffort", best_effort, flags)


def add_special_boolean(cmd, field_path, value, flags):
    """处理 boolean 类型的官方参数。"""
    rule = flags.get("special", {}).get(field_path)
    if not rule:
        return

    bool_value = parse_bool(value)
    if bool_value:
        flag = rule.get("true_flag")
        if flag:
            cmd.append(flag)
    else:
        flag = rule.get("false_flag")
        if flag:
            cmd.append(flag)


def parse_bool(value):
    """把字符串或布尔值解析为 bool。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


def validate_loop_variables(variables):
    """对 Loop 模式相关变量做前置校验，防止无效配置生成 cron 命令。"""
    loop_raw = str(variables.get("LOOP_MODE_ENABLED", "false")).strip().lower()
    if loop_raw not in ("true", "1", "yes", "on", "false", "0", "no", "off", ""):
        raise ValueError(
            f"LOOP_MODE_ENABLED 必须是布尔值字符串，收到：{variables.get('LOOP_MODE_ENABLED')!r}"
        )

    # 校验 TIMEOUT_SECONDS 为正整数
    timeout_raw = variables.get("TIMEOUT_SECONDS", "")
    if timeout_raw:
        try:
            timeout = int(str(timeout_raw).strip())
            if timeout <= 0:
                raise ValueError
        except ValueError as exc:
            raise ValueError(
                f"TIMEOUT_SECONDS 必须是正整数，收到：{timeout_raw!r}"
            ) from exc

    loop_enabled = parse_bool(variables.get("LOOP_MODE_ENABLED", "false"))
    if not loop_enabled:
        return

    # 校验项目路径不是默认占位符
    dev_project_dir = str(variables.get("DEV_PROJECT_DIR", "")).strip()
    if dev_project_dir == "/path/to/your/project":
        raise ValueError(
            "DEV_PROJECT_DIR 仍是默认占位符 /path/to/your/project，"
            "请在场景 YAML 中替换为实际项目绝对路径"
        )

    # 校验里程碑列表为合法 JSON 数组
    milestones_raw = variables.get("DEV_MILESTONES", "[]")
    try:
        milestones = json.loads(str(milestones_raw))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"DEV_MILESTONES 必须是合法 JSON 数组字符串，收到：{milestones_raw!r}"
        ) from exc
    if not isinstance(milestones, list):
        raise ValueError(
            f"DEV_MILESTONES 必须是 JSON 数组，收到：{type(milestones).__name__}"
        )


def is_empty(value):
    """判断值是否为空（0 不算空；空列表/空字典视为空）。"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, (list, dict)) and not value:
        return True
    return False


def format_shell_command(cmd):
    """把命令数组格式化为可执行的 shell 命令字符串。"""
    return " \\\n  ".join(shlex.quote(str(x)) for x in cmd)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc
