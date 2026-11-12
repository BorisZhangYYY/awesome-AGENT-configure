#!/usr/bin/env python3
"""Deterministic monitor source for the `monitors/change-monitor` scene.

Prints the SHA-256 of ``monitor-source.txt`` next to this script. The output is
byte-identical while the file is unchanged, which is what lets Hermes suppress
the agent run; it carries no timestamps or counters.

Contract (enforced by tests/hermes/test_scenes.py):

* success: exit 0, one line of JSON with ``sha256`` and ``bytes``
* missing source: exit 2, stdout empty, reason on stderr
* this script writes nothing and touches no network

Deploy by hand: copy this file and ``monitor-source.txt`` into
``$HERMES_HOME/scripts/aac/``.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

SOURCE_NAME = "monitor-source.txt"


def main() -> int:
    source = Path(__file__).resolve().parent / SOURCE_NAME
    if not source.is_file():
        print(f"change-monitor: missing source file: {source}", file=sys.stderr)
        return 2

    payload = source.read_bytes()
    print(json.dumps({
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
