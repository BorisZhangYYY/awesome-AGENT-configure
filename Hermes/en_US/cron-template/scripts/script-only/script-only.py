#!/usr/bin/env python3
"""Read-only syntax check used by the `scripts/script-only` scene.

Contract (enforced by tests/hermes/test_scenes.py):

* success: exit 0, exactly one line of JSON on stdout, identical across runs
* bad target: exit 1, stdout empty, reason on stderr
* missing argument target: exit 2, stdout empty, reason on stderr
* this script writes nothing, touches no network and calls no model

Deploy by hand: copy this file to ``$HERMES_HOME/scripts/aac/script-only.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def digest(source: bytes) -> str:
    return hashlib.sha256(source).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile-check a Python file; never execute it.")
    parser.add_argument("--target", help="file to check (default: this script)")
    args = parser.parse_args()

    target = Path(args.target).resolve() if args.target else Path(__file__).resolve()
    if not target.is_file():
        print(f"script-only: target not found: {target}", file=sys.stderr)
        return 2

    source = target.read_bytes()
    try:
        compile(source, str(target), "exec")
    except SyntaxError as exc:
        print(f"script-only: syntax error in {target.name}: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({
        "status": "ok",
        "target": target.name,
        "lines": source.count(b"\n") + (0 if source.endswith(b"\n") or not source else 1),
        "sha256": digest(source),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
