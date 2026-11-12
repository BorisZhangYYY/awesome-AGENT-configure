#!/usr/bin/env python3
"""Compile AAC Hermes cron YAML into reviewable native commands; never execute or install.

The compiler is deliberately dull: it validates the scene against the native
`hermes cron` surface, renders the shared template, and prints a command or a
request. It never runs `hermes`, never copies scripts and never edits jobs.json.

Modes (all read-only):
  (default)      shell-quoted `hermes cron` command
  --json         the same command as an argv array
  --validate     field and scene checks only
  --preview      rendered job fields plus argv
  --tool-json    `cronjob_manage` request for the tool lane
  --plan         ordered cross-lane plan with the job ID left as a placeholder
  --catalog      list the scenes shipped in this repository
  --check-cli    print the read-only CLI checks an operator should run first
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import sys
from typing import Any

import yaml

TOKEN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
CONDITIONAL = re.compile(r"\{\{#if ([A-Z][A-Z0-9_]*)\}\}(.*?)\{\{/if\}\}", re.S)
CONDITIONAL_TOKEN = re.compile(r"\{\{#if ([A-Z][A-Z0-9_]*)\}\}|\{\{/if\}\}")
VARIABLE_NAME = re.compile(r"[A-Z][A-Z0-9_]*")

REASONING_EFFORT = ("none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra")

# Native job fields, by validation kind. Anything outside this map is a typo and
# must fail instead of being dropped silently.
BOOL_FIELDS = ("catch_up", "no_agent", "continuity", "paused", "pinned", "attach_to_session")
LIST_FIELDS = ("skills", "context_from", "enabled_toolsets")
PATH_FIELDS = ("script", "monitor_script")
INT_FIELDS = ("grace_minutes",)
STRING_FIELDS = (
    "schedule", "name", "deliver", "failure_deliver", "repeat", "monitor_url",
    "workdir", "model", "provider", "interpreter", "timezone", "paused_reason",
    "templateRef",
)
JOB_FIELDS = set(BOOL_FIELDS) | set(LIST_FIELDS) | set(PATH_FIELDS) | set(INT_FIELDS) | set(
    STRING_FIELDS
) | {"reasoning_effort"} - {"templateRef"}

# The CLI can set these; the cronjob_manage tool cannot (and vice versa).
CLI_ONLY_FIELDS = ("model", "provider", "reasoning_effort", "interpreter", "grace_minutes")
TOOL_ONLY_FIELDS = ("context_from", "enabled_toolsets", "attach_to_session")

SCALAR_FLAGS = {
    "name": "--name", "deliver": "--deliver", "failure_deliver": "--failure-deliver",
    "repeat": "--repeat", "script": "--script", "monitor_script": "--monitor-script",
    "monitor_url": "--monitor-url", "workdir": "--workdir", "model": "--model",
    "provider": "--provider", "reasoning_effort": "--reasoning-effort",
    "interpreter": "--interpreter", "timezone": "--timezone",
    "grace_minutes": "--grace-minutes", "paused_reason": "--paused-reason",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that refuses duplicate mapping keys instead of keeping the last."""


def _construct_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                None, None, f"Duplicate key: {key!r}", key_node.start_mark
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.load(handle, Loader=UniqueKeyLoader)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return data


def is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no", "off")
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return value is not None


def apply_conditionals(text: str, variables: dict[str, Any]) -> str:
    """Resolve nested {{#if FLAG}} ... {{/if}} blocks, keeping the inner text verbatim."""
    pieces: list[str] = []
    stack: list[bool] = []
    position = 0
    for match in CONDITIONAL_TOKEN.finditer(text):
        if all(stack):
            pieces.append(text[position:match.start()])
        position = match.end()
        name = match.group(1)
        if name:
            stack.append(is_truthy(variables.get(name)) and all(stack))
        else:
            if not stack:
                raise ValueError("Unbalanced {{/if}} in template")
            stack.pop()
    if stack:
        raise ValueError("Unbalanced {{#if}} block in template")
    pieces.append(text[position:])
    return "".join(pieces)


def render(value: Any, variables: dict[str, Any], resolving: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        return {key: render(item, variables, resolving) for key, item in value.items()}
    if isinstance(value, list):
        return [render(item, variables, resolving) for item in value]
    if not isinstance(value, str):
        return value

    def resolve(name: str) -> Any:
        if name in resolving:
            raise ValueError(f"Cyclic variable: {' -> '.join((*resolving, name))}")
        if name not in variables:
            raise ValueError(f"Undefined variable: {name}")
        return render(variables[name], variables, (*resolving, name))

    value = apply_conditionals(value, variables)
    match = TOKEN.fullmatch(value)
    if match:
        return resolve(match.group(1))

    def replace(match: re.Match[str]) -> str:
        item = resolve(match.group(1))
        if isinstance(item, (dict, list)):
            return json.dumps(item, ensure_ascii=False)
        if isinstance(item, bool):
            return "true" if item else "false"
        return str(item)

    return TOKEN.sub(replace, value)


def check_script_path(field: str, value: str, home: Path) -> None:
    if not value:
        return
    raw = Path(value)
    if raw.is_absolute():
        raise ValueError(f"{field} must be relative to {home}/scripts, got {value!r}")
    base = (home / "scripts").resolve()
    target = (base / raw).resolve()
    if target != base and base not in target.parents:
        raise ValueError(
            f"{field} must stay inside {home}/scripts (symlinks included), got {value!r}"
        )


def validate_job(job: dict[str, Any], home: Path) -> None:
    unknown = sorted(set(job) - JOB_FIELDS - {"prompt"})
    if unknown:
        raise ValueError(f"Unknown job field(s): {', '.join(unknown)}")

    for key in BOOL_FIELDS:
        if key in job and not isinstance(job[key], bool):
            raise ValueError(f"job.{key} must be a boolean, got {job[key]!r}")

    for key in LIST_FIELDS:
        if key not in job:
            continue
        value = job[key]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise ValueError(f"job.{key} must be a list of strings, got {value!r}")

    for key in INT_FIELDS:
        if key not in job:
            continue
        value = job[key]
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"job.{key} must be an integer, got {value!r}")
        if not 0 <= value <= 1440:
            raise ValueError(f"job.{key} must be between 0 and 1440 minutes, got {value}")

    if "reasoning_effort" in job and job["reasoning_effort"] not in REASONING_EFFORT:
        raise ValueError(
            f"reasoning_effort must be one of {', '.join(REASONING_EFFORT)}, "
            f"got {job['reasoning_effort']!r}"
        )

    if "monitor_url" in job:
        url = str(job["monitor_url"])
        if not url.startswith(("http://", "https://")):
            raise ValueError(f"monitor_url must be an http(s) URL, got {url!r}")

    if job.get("monitor_script") and job.get("monitor_url"):
        raise ValueError("monitor_script and monitor_url are mutually exclusive")

    if job.get("no_agent") is True:
        if not job.get("script"):
            raise ValueError("no_agent requires script (the script IS the job)")
        if job.get("monitor_script") or job.get("monitor_url"):
            raise ValueError("no_agent cannot be combined with monitor mode")

    if job.get("paused_reason") and job.get("paused") is not True:
        raise ValueError("paused_reason requires paused: true")

    if job.get("provider") and not job.get("model"):
        raise ValueError("provider requires model")

    if job.get("model") and job.get("pinned") is True:
        raise ValueError("pinned conflicts with model; pin the current model or set one, not both")

    for key in PATH_FIELDS:
        if key in job:
            check_script_path(f"job.{key}", str(job[key]), home)

    if not job.get("schedule"):
        raise ValueError("job.schedule is required")


def compile_scene(
    scene_path: Path, home: Path, overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    scene_path = scene_path.resolve()
    scene = load_yaml(scene_path)
    ref = scene.get("templateRef")
    if not isinstance(ref, str) or not ref:
        raise ValueError("Scene requires templateRef")
    template_path = (scene_path.parent / ref).resolve()
    if not template_path.is_file():
        raise ValueError(f"templateRef not found: {ref} (from {scene_path.name})")
    template = load_yaml(template_path)

    variables: dict[str, Any] = {
        **template.get("variables", {}),
        **scene.get("variables", {}),
        **(overrides or {}),
        "HERMES_HOME": str(home),
    }
    job = {**template.get("job", {}), **scene.get("job", {})}
    job = {key: item for key, item in render(job, variables).items() if item is not None}
    job["prompt"] = "" if job.get("no_agent") else re.sub(
        r"\n{3,}", "\n\n", str(render(template.get("template", ""), variables))
    ).strip()
    validate_job(job, home)
    return job


def apply_test_mode(job: dict[str, Any]) -> dict[str, Any]:
    test = dict(job)
    test["schedule"] = "in 1m"
    test["repeat"] = 1
    test["deliver"] = "local"
    test["catch_up"] = False
    test["paused"] = True
    test["paused_reason"] = "AAC test job: paused until an operator runs it explicitly"
    test["name"] = f"[TEST] {test.get('name', 'AAC')}"
    return test


def build_command(
    job: dict[str, Any], home: Path, job_id: str | None = None, profile: str | None = None
) -> list[str]:
    cmd = ["env", f"HERMES_HOME={home}", "hermes"]
    if profile:
        cmd += ["-p", profile]
    cmd.append("cron")
    if job_id is None:
        cmd += ["create", str(job["schedule"])]
        if job.get("prompt"):
            cmd.append(job["prompt"])
    else:
        cmd += ["edit", job_id, "--schedule", str(job["schedule"]), "--prompt", job.get("prompt", "")]

    for key, flag in SCALAR_FLAGS.items():
        if key in job:
            cmd += [flag, str(job[key])]

    if "catch_up" in job:
        cmd += ["--catch-up", "on" if job["catch_up"] else "off"]

    if job_id is not None and job.get("skills") == []:
        cmd.append("--clear-skills")
    for skill in job.get("skills", []):
        cmd += ["--skill", skill]

    for key, flag in (("no_agent", "--no-agent"), ("continuity", "--continuity"),
                      ("paused", "--paused"), ("pinned", "--pin")):
        if job.get(key) is True:
            cmd.append(flag)

    if job_id is not None:
        for key, flag in (("no_agent", "--agent"), ("continuity", "--no-continuity"),
                          ("pinned", "--unpin")):
            if job.get(key) is False:
                cmd.append(flag)

    return cmd


def tool_arguments(job: dict[str, Any], action: str, job_id: str | None = None) -> dict[str, Any]:
    blocked = [key for key in CLI_ONLY_FIELDS if key in job]
    if blocked:
        raise ValueError(
            f"cronjob_manage cannot set {', '.join(blocked)}; use the CLI lane for those fields"
        )
    args: dict[str, Any] = {"action": action}
    if job_id:
        args["job_id"] = job_id
    for key in ("schedule", "name", "deliver", "failure_deliver", "repeat", "catch_up",
                "skills", "no_agent", "script", "workdir", "timezone", "continuity",
                "pinned", "paused", "paused_reason", "context_from", "enabled_toolsets",
                "attach_to_session"):
        if key in job:
            args[key] = job[key]
    monitor = job.get("monitor_url") or job.get("monitor_script")
    if monitor:
        args["monitor"] = monitor
    if job.get("prompt"):
        args["prompt"] = job["prompt"]
    return args


def build_plan(job: dict[str, Any], home: Path, profile: str | None) -> list[dict[str, Any]]:
    staged = dict(job)
    staged["paused"] = True
    staged.setdefault("paused_reason", "AAC: created paused, resume only after verification")
    steps: list[dict[str, Any]] = [
        {"step": 1, "intent": "create the job paused (no schedule is armed yet)",
         "argv": build_command(staged, home, None, profile)},
        {"step": 2, "intent": "read back the real job ID from the scheduler",
         "command": "hermes cron list --all", "expect": "the ID of the job just created"},
    ]
    if any(key in job for key in TOOL_ONLY_FIELDS):
        steps.append({
            "step": len(steps) + 1,
            "intent": "apply tool-only fields with the real ID bound",
            "tool": {"name": "cronjob_manage",
                     "arguments": tool_arguments(job, "update", "<JOB_ID>")},
        })
    steps += [
        {"step": len(steps) + 1, "intent": "verify fields and pause state",
         "command": "hermes cron runs <JOB_ID> --limit 5"},
        {"step": len(steps) + 1, "intent": "resume only after explicit approval",
         "command": "hermes cron resume <JOB_ID>"},
    ]
    return steps


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def catalog(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for locale in ("zh_CN", "en_US"):
        base = root / "Hermes" / locale / "cron-template"
        for path in sorted(base.glob("*/*/*.yaml")):
            data = load_yaml(path)
            variables = data.get("variables", {})
            job = data.get("job", {})
            rows.append({
                "locale": locale,
                "scene": str(path.relative_to(base)),
                "name": str(variables.get("JOB_NAME", "")),
                "schedule": str(variables.get("SCHEDULE", "")),
                "paused": "yes" if job.get("paused") is True else "no",
                "mode": "script" if job.get("no_agent") is True else (
                    "monitor" if job.get("monitor_script") or job.get("monitor_url") else "agent"
                ),
            })
    return rows


CLI_CHECKS = (
    "hermes cron create --help",
    "hermes cron edit --help",
    "hermes cron list --all",
    "hermes cron status",
)


def parse_sets(pairs: list[str]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    for item in pairs:
        if "=" not in item:
            raise ValueError(f"--set expects KEY=YAML_VALUE, got {item!r}")
        key, raw = item.split("=", 1)
        key = key.strip()
        if not VARIABLE_NAME.fullmatch(key):
            raise ValueError(f"--set key must be UPPER_SNAKE_CASE, got {key!r}")
        overrides[key] = yaml.safe_load(raw)
    return overrides


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile AAC Hermes cron YAML into reviewable native commands; never execute."
    )
    parser.add_argument("scene", nargs="?", help="scene YAML inside Hermes/<locale>/cron-template/")
    parser.add_argument("--home", type=Path, help="target HERMES_HOME (default: $HERMES_HOME)")
    parser.add_argument("--profile", help="target Hermes profile; use instead of --home")
    parser.add_argument("--set", dest="sets", action="append", default=[], metavar="KEY=VALUE",
                        help="override a scene variable; repeatable, YAML-parsed")
    parser.add_argument("--json", action="store_true", help="emit the argv array as JSON")
    parser.add_argument("--preview", action="store_true", help="show rendered job and argv")
    parser.add_argument("--validate", action="store_true", help="validate only")
    parser.add_argument("--test", action="store_true",
                        help="emit a paused one-shot 'in 1m' job for a canary run")
    parser.add_argument("--edit", metavar="JOB_ID", help="generate an edit command for this ID")
    parser.add_argument("--tool-json", action="store_true",
                        help="emit a cronjob_manage request instead of a command")
    parser.add_argument("--plan", action="store_true",
                        help="emit the ordered cross-lane plan with JOB_ID placeholders")
    parser.add_argument("--catalog", action="store_true", help="list the scenes in this repository")
    parser.add_argument("--check-cli", action="store_true",
                        help="print the read-only CLI checks to run before deploying")
    args = parser.parse_args()

    if args.home and args.profile:
        print("Error: --home and --profile are mutually exclusive", file=sys.stderr)
        return 2

    try:
        if args.catalog:
            print(json.dumps(catalog(repo_root()), ensure_ascii=False, indent=2))
            return 0
        if args.check_cli:
            print("\n".join(CLI_CHECKS))
            return 0
        if not args.scene:
            print("Error: a scene path is required", file=sys.stderr)
            return 2

        home = (args.home or Path(os.environ.get("HERMES_HOME", "~/.hermes"))).expanduser().resolve()
        job = compile_scene(Path(args.scene), home, parse_sets(args.sets))
        if args.test:
            job = apply_test_mode(job)

        if args.validate:
            print(f"Valid Hermes cron scene: {jdo_short(job)}")
            return 0
        if args.preview:
            print(json.dumps({
                "job": job,
                "argv": build_command(job, home, args.edit, args.profile),
            }, ensure_ascii=False, indent=2))
            return 0
        if args.tool_json or args.plan:
            if args.test:
                raise ValueError("--test only applies to the CLI lane")
            if args.plan:
                print(json.dumps(build_plan(job, home, args.profile), ensure_ascii=False, indent=2))
            else:
                action = "update" if args.edit else "create"
                print(json.dumps({"name": "cronjob_manage",
                                  "arguments": tool_arguments(job, action, args.edit)},
                                 ensure_ascii=False, indent=2))
            return 0

        cmd = build_command(job, home, args.edit, args.profile)
        if args.json:
            print(json.dumps(cmd, ensure_ascii=False, indent=2))
        else:
            print(shlex.join(cmd))
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


def jdo_short(job: dict[str, Any]) -> str:
    fields = [key for key in ("name", "schedule", "deliver") if key in job]
    parts = [f"{key}={job[key]!r}" for key in fields]
    if job.get("no_agent"):
        parts.append("mode=script")
    return ", ".join(parts)


if __name__ == "__main__":
    raise SystemExit(main())
