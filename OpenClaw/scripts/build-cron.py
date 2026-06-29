#!/usr/bin/env python3
"""OpenClaw Cron 模板渲染器

读取场景 YAML 和通用模板，渲染后输出 openclaw cron create 命令。

用法：
    python3 OpenClaw/scripts/build-cron.py OpenClaw/template/reminders/morning.yaml
    python3 OpenClaw/scripts/build-cron.py OpenClaw/template/reminders/morning.yaml --json
"""

import argparse
import json
import os
import re
import shlex
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    print("错误：本脚本依赖 PyYAML，请先安装：pip install pyyaml", file=sys.stderr)
    raise SystemExit(1) from exc


def main():
    args = parse_args()
    scene_path = Path(args.scene_file)

    if not scene_path.exists():
        raise FileNotFoundError(f"场景文件不存在：{scene_path}")

    # 定位配置目录（与脚本位于同一 OpenClaw 目录下）
    script_dir = Path(__file__).resolve().parent
    conf_dir = script_dir.parent / "conf"

    flags = load_yaml(conf_dir / "flags.yaml")
    defaults = load_yaml(conf_dir / "defaults.yaml")

    scene = load_yaml(scene_path)
    template = load_template(scene, scene_path)

    variables = build_variables(defaults, template, scene)

    # 注入运行时相关变量；若场景 YAML 已显式定义，优先使用场景值
    now = datetime.now()
    weekday_cn = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][now.weekday()]
    variables.setdefault("DATE_TODAY", now.strftime("%Y-%m-%d"))
    variables.setdefault("TIME_NOW", now.strftime("%H:%M"))
    variables.setdefault("WEEKDAY", weekday_cn)

    # 根据 persona 配置注入 {{PERSONA_PROMPT}}
    variables["PERSONA_PROMPT"] = build_persona_prompt(template, variables)

    # 渲染 message
    message = render_template(template, scene, variables)
    variables["MESSAGE"] = message

    cmd = build_command(variables, flags)

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

    return load_yaml(template_path)


def build_variables(defaults, template, scene):
    """合并变量，优先级：defaults < 模板内置 variables < 场景 variables。"""
    variables = {}
    variables.update(defaults or {})
    variables.update(template.get("variables", {}) or {})
    variables.update(scene.get("variables", {}) or {})
    # 注入 WORKSPACE：将 ~ 展开为绝对路径，若场景已显式定义则优先使用
    workspace = os.path.expanduser(variables.get("WORKSPACE", "~/.openclaw/workspace"))
    variables["WORKSPACE"] = workspace
    return variables


def resolve_variables(variables, max_depth=5):
    """递归展开变量值中的嵌套占位符，返回完全展开后的新字典。

    对变量值中的嵌套占位符（如 DEDUP_STATE_FILE: "{{WORKSPACE}}/..."）进行预展开，
    避免在 template 替换阶段对同一文本多次扫描，同时降低误替换值中字面量 `{{}}` 的风险。
    """
    resolved = {k: str(v) if v is not None else "" for k, v in variables.items()}
    for _ in range(max_depth):
        changed = False
        new_resolved = {}
        for key, value in resolved.items():
            new_value = value
            for other_key, other_value in resolved.items():
                placeholder = "{{" + other_key + "}}"
                if placeholder in new_value:
                    new_value = new_value.replace(placeholder, other_value)
                    changed = True
            new_resolved[key] = new_value
        resolved = new_resolved
        if not changed:
            break
    return resolved


def render_template(template, scene, variables):
    """渲染 template 字段。

    仅使用父模板中的 template。场景 YAML 不允许直接定义顶层 template 字段，
    以确保时间窗口、去重等非官方 Harness 机制对所有场景一致生效。
    场景特定内容应通过 {{SCENE_SPECIFIC_INSTRUCTIONS}} 占位符注入。
    """
    if scene.get("template"):
        raise ValueError(
            "场景 YAML 不允许直接定义顶层 template 字段，"
            "请使用 SCENE_SPECIFIC_INSTRUCTIONS 变量注入场景特定内容"
        )

    template_str = template.get("template", "")
    if not template_str:
        # 未配置 template，直接使用 message 字段内容
        return variables.get("MESSAGE", "")

    # 先完全展开所有变量值中的嵌套占位符
    resolved = resolve_variables(variables)

    # 统一单轮替换 template 中的占位符
    result = template_str
    for key, value in resolved.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))

    return result


def build_persona_prompt(template, variables):
    """根据 persona 配置生成 {{PERSONA_PROMPT}} 的内容。"""
    persona = template.get("persona", {})
    mode = str(variables.get("PERSONA_MODE", persona.get("mode", "inline"))).lower()
    persona_file = variables.get("PERSONA_FILE", persona.get("file", ""))
    persona_role = variables.get("PERSONA_ROLE", "")
    # 场景未定义 PERSONA_ROLE 时，尝试从模板 persona.role 读取
    # 但需过滤包含未解析占位符（如 "{{PERSONA_ROLE}}"）的字符串，避免泄漏到输出
    if not persona_role:
        raw_role = persona.get("role", "")
        if raw_role and not re.search(r"\{\{.*?\}\}", raw_role):
            persona_role = raw_role

    if mode == "file" and persona_file:
        return f"请基于 {persona_file} 中定义的人设。"
    if persona_role:
        return f"你是一个{persona_role}。"
    return ""


def build_command(variables, flags):
    """根据变量和 flags 映射表构建 openclaw cron create 命令数组。"""
    cmd = ["openclaw", "cron", "create"]

    # 位置参数：schedule.expr
    schedule_expr = variables.get("SCHEDULE_EXPR")
    if not schedule_expr:
        raise ValueError("缺少必要变量：SCHEDULE_EXPR")
    cmd.append(str(schedule_expr))

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

    return cmd


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
