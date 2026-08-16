#!/usr/bin/env python3
"""Generate deterministic PyInstaller VERSIONINFO from the canonical VERSION file."""
from __future__ import annotations

import argparse
from pathlib import Path
import re

PRODUCT_NAME = "Arvectum Proxy Launcher"
COMPANY_NAME = "ООО «Арвектум»"
ORIGINAL_FILENAME = "Arvectum Proxy Launcher.exe"
COPYRIGHT = "© 2026 ООО «Арвектум». All rights reserved."
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def parse_version(version: str) -> tuple[int, int, int, int]:
    match = SEMVER.fullmatch(version.strip())
    if not match:
        raise ValueError(f"VERSION is not valid SemVer: {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3)), 0


def render(version: str) -> str:
    major, minor, patch, build = parse_version(version)
    numeric = f"{major}.{minor}.{patch}.{build}"
    tuple_text = f"({major}, {minor}, {patch}, {build})"
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={tuple_text}, prodvers={tuple_text},
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0,
    date=(0, 0)),
  kids=[
    StringFileInfo([
      StringTable('041904B0', [
        StringStruct('CompanyName', '{COMPANY_NAME}'),
        StringStruct('FileDescription', '{PRODUCT_NAME}'),
        StringStruct('FileVersion', '{numeric}'),
        StringStruct('InternalName', 'ArvectumProxyLauncher'),
        StringStruct('LegalCopyright', '{COPYRIGHT}'),
        StringStruct('OriginalFilename', '{ORIGINAL_FILENAME}'),
        StringStruct('ProductName', '{PRODUCT_NAME}'),
        StringStruct('ProductVersion', '{version.strip()}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1049, 1200])])
  ]
)
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version-file", default="VERSION")
    parser.add_argument("--output", default="version_info.txt")
    args = parser.parse_args()

    version = Path(args.version_file).read_text(encoding="utf-8").strip()
    output = Path(args.output)
    payload = render(version)
    output.write_text(payload, encoding="utf-8", newline="\n")
    print(f"Generated {output} for {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
