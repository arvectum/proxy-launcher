#!/usr/bin/env python3
"""Compare two APL-MAC-008 macOS network snapshots.

Automatic-proxy enabled state and PAC URL must match exactly. Bypass domains are
compared case-insensitively as a set, matching the backend ownership semantics and
avoiding false failures caused only by presentation order.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional

SCHEMA_VERSION = 1


def _domains(values: Iterable[Any]) -> List[str]:
    return sorted({str(value or "").strip().lower() for value in values if str(value or "").strip()})


def _load(path: Path) -> Dict[str, Any]:
    with path.expanduser().open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or invalid snapshot schema: %s" % path)
    if not isinstance(payload.get("services"), dict) or not payload["services"]:
        raise ValueError("snapshot has no enabled services: %s" % path)
    return payload


def compare_states(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    differences: List[str] = []
    before_services = before["services"]
    after_services = after["services"]

    before_names = set(before_services)
    after_names = set(after_services)
    for name in sorted(before_names - after_names):
        differences.append("service missing after rollback: %s" % name)
    for name in sorted(after_names - before_names):
        differences.append("unexpected enabled service after rollback: %s" % name)

    for name in sorted(before_names & after_names):
        left = before_services[name]
        right = after_services[name]
        left_auto = left.get("auto_proxy", {})
        right_auto = right.get("auto_proxy", {})
        if bool(left_auto.get("enabled")) != bool(right_auto.get("enabled")):
            differences.append("%s: automatic proxy enabled state differs" % name)
        if str(left_auto.get("url", "")) != str(right_auto.get("url", "")):
            differences.append("%s: PAC URL differs" % name)
        if _domains(left.get("bypass_domains", ())) != _domains(right.get("bypass_domains", ())):
            differences.append("%s: bypass domains differ" % name)

    return differences


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", help="baseline JSON snapshot")
    parser.add_argument("after", help="post-rollback JSON snapshot")
    args = parser.parse_args(argv)

    try:
        before = _load(Path(args.before))
        after = _load(Path(args.after))
        differences = compare_states(before, after)
    except Exception as exc:
        print("APL-MAC-008 comparison error: %s" % exc, file=sys.stderr)
        return 2

    if differences:
        print("APL-MAC-008 NETWORK ROLLBACK: FAIL")
        for difference in differences:
            print("- %s" % difference)
        return 1

    print("APL-MAC-008 NETWORK ROLLBACK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
