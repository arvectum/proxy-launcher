#!/usr/bin/env python3
"""Read-only exact macOS PAC/bypass snapshot for APL-MAC-008 acceptance.

The collector intentionally reuses the production NetworkSetupClient read path and
never invokes any networksetup setter. Output is local acceptance evidence and can
contain PAC URLs / bypass domains, so it is written mode 0600 and must not be
committed as a public artifact.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from macos_backend import NetworkSetupClient  # noqa: E402

SCHEMA_VERSION = 1


def collect_state(client: Optional[NetworkSetupClient] = None) -> Dict[str, Any]:
    """Collect enabled-service automatic-proxy and bypass state without mutation."""
    reader = client or NetworkSetupClient()
    services: Dict[str, Any] = {}
    for service in reader.list_services():
        if not service.enabled:
            continue
        auto = reader.get_auto_proxy(service.name)
        bypass = reader.get_bypass_domains(service.name)
        services[service.name] = {
            "auto_proxy": {
                "enabled": bool(auto.enabled),
                "url": str(auto.url),
            },
            "bypass_domains": list(bypass),
        }
    if not services:
        raise RuntimeError("no enabled macOS network services found")
    return {
        "schema_version": SCHEMA_VERSION,
        "services": services,
    }


def write_private_json(path: Path, payload: Dict[str, Any]) -> None:
    """Atomically write acceptance evidence with owner-only permissions."""
    target = path.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = target.with_name(target.name + ".tmp-%d" % os.getpid())
    descriptor = os.open(
        str(temporary),
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        0o600,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(target))
        os.chmod(str(target), 0o600)
    finally:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="private JSON evidence output path")
    args = parser.parse_args(argv)

    if sys.platform != "darwin":
        print("APL-MAC-008 collector requires macOS (darwin)", file=sys.stderr)
        return 2

    try:
        state = collect_state()
        output = Path(args.output)
        write_private_json(output, state)
    except Exception as exc:
        print("APL-MAC-008 state collection failed: %s" % exc, file=sys.stderr)
        return 1

    print(str(output.expanduser().resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
