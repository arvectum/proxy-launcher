#!/usr/bin/env python3
"""Build and verify the third-party license bundle for promoted desktop artifacts.

APL-IP-004 treats license delivery as an artifact property, not merely repository
metadata. The collector copies complete license/copyright texts from the exact
Python/Tcl/Tk/PyInstaller environment used to freeze the application, records
SHA-256 hashes, and fails closed when an expected license family cannot be found.

The generated directory is safe to embed into platform packages. It contains no
secrets and performs no downloads. Runtime/system package license material is
preferred; governed repository-pinned upstream text is used only where a supported
platform distributes the runtime without its license text beside the runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
from typing import Iterable

SCHEMA = "arvectum.third-party-license-bundle.v1"
REQUIRED_COMPONENTS = ("python", "tcl", "tk", "pyinstaller")
REPO_ROOT = Path(__file__).resolve().parents[1]
LICENSE_BASENAMES = {
    "license",
    "license.txt",
    "license.rst",
    "copying",
    "copying.txt",
    "copyright",
    "license.terms",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _existing(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        try:
            resolved = path.resolve(strict=True)
        except (FileNotFoundError, OSError):
            continue
        if not resolved.is_file() or resolved in seen:
            continue
        if resolved.stat().st_size <= 0:
            continue
        seen.add(resolved)
        result.append(resolved)
    return result


def python_license_candidates() -> list[Path]:
    major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    roots = {
        Path(sys.base_prefix),
        Path(sys.exec_prefix),
        Path(sys.executable).resolve().parent,
    }
    candidates: list[Path] = []
    for root in roots:
        candidates.extend(
            [
                root / "LICENSE.txt",
                root / "LICENSE",
                root / "Doc" / "license.rst",
                root / "Resources" / "License.rtf",
                root / "Resources" / "LICENSE.txt",
                root / "Resources" / "LICENSE",
            ]
        )

    # python.org macOS framework installations keep the distributable license in
    # the companion /Applications/Python X.Y directory rather than next to the
    # framework binary. This is still part of the exact selected Python install.
    mac_install = Path("/Applications") / f"Python {major_minor}"
    candidates.extend(
        [
            mac_install / "License.rtf",
            mac_install / "LICENSE.txt",
            mac_install / "LICENSE",
        ]
    )

    # Debian-family Python packages place complete license/copyright material in
    # /usr/share/doc instead of the interpreter prefix. Prefer version-specific
    # package records and retain python3 as a bounded distro fallback.
    candidates.extend(
        [
            Path(f"/usr/share/doc/python{major_minor}/copyright"),
            Path(f"/usr/share/doc/python{major_minor}-minimal/copyright"),
            Path(f"/usr/share/doc/libpython{major_minor}-stdlib/copyright"),
            Path(f"/usr/share/doc/libpython{major_minor}-minimal/copyright"),
            Path("/usr/share/doc/python3/copyright"),
        ]
    )
    return _existing(candidates)


def tcl_tk_license_candidates() -> tuple[list[Path], list[Path]]:
    try:
        import tkinter  # pylint: disable=import-outside-toplevel

        interp = tkinter.Tcl()
        tcl_library = Path(interp.eval("info library"))
    except Exception as exc:  # pragma: no cover - platform environment error
        raise RuntimeError(f"Tkinter/Tcl runtime is unavailable: {exc}") from exc

    parent = tcl_library.parent
    tcl_candidates = [
        tcl_library / "license.terms",
        parent / "tcl8.6" / "license.terms",
        Path("/usr/share/doc/tcl8.6/copyright"),
        Path("/usr/share/doc/tcl/copyright"),
    ]

    tk_candidates: list[Path] = [
        Path("/usr/share/doc/tk8.6/copyright"),
        Path("/usr/share/doc/tk/copyright"),
    ]
    for pattern in ("tk*/license.terms", "Tk*/license.terms"):
        try:
            tk_candidates.extend(parent.glob(pattern))
        except OSError:
            pass
    # Windows python.org layouts commonly keep Tcl/Tk below <base>/tcl.
    base_tcl = Path(sys.base_prefix) / "tcl"
    if base_tcl.exists():
        for pattern in ("tcl*/license.terms", "Tcl*/license.terms"):
            tcl_candidates.extend(base_tcl.glob(pattern))
        for pattern in ("tk*/license.terms", "Tk*/license.terms"):
            tk_candidates.extend(base_tcl.glob(pattern))

    # macOS framework builds may place Tcl/Tk frameworks beside Python.
    framework_roots = [
        Path("/Library/Frameworks/Tcl.framework/Versions/Current/Resources"),
        Path("/Library/Frameworks/Tk.framework/Versions/Current/Resources"),
    ]
    tcl_candidates.extend([framework_roots[0] / "license.terms", framework_roots[0] / "License.txt"])
    tk_candidates.extend([framework_roots[1] / "license.terms", framework_roots[1] / "License.txt"])

    # GitHub-hosted python.org macOS runners expose Tcl/Tk 8.6 to _tkinter but
    # do not expose license.terms beside that runtime. Keep an audited, pinned
    # upstream copy in-repo so packaging stays offline and deterministic.
    tcl_candidates.append(REPO_ROOT / "third_party_licenses" / "tcl" / "8.6" / "license.terms")
    tk_candidates.append(REPO_ROOT / "third_party_licenses" / "tk" / "8.6" / "license.terms")

    return _existing(tcl_candidates), _existing(tk_candidates)


def pyinstaller_license_candidates() -> list[Path]:
    try:
        dist = importlib.metadata.distribution("pyinstaller")
    except importlib.metadata.PackageNotFoundError as exc:
        raise RuntimeError("PyInstaller is not installed in the selected build environment") from exc

    candidates: list[Path] = []
    for item in dist.files or ():
        path = Path(str(item))
        if path.name.lower() not in LICENSE_BASENAMES:
            continue
        try:
            located = Path(dist.locate_file(item))
        except (TypeError, ValueError):
            continue
        candidates.append(located)
    return _existing(candidates)


def _copy_group(component: str, sources: list[Path], output: Path) -> list[dict[str, str]]:
    if not sources:
        raise RuntimeError(f"No complete license text found for required component: {component}")
    records: list[dict[str, str]] = []
    component_dir = output / component
    component_dir.mkdir(parents=True, exist_ok=True)
    for index, source in enumerate(sources, start=1):
        suffix = source.suffix if source.suffix else ".txt"
        target = component_dir / f"LICENSE-{index}{suffix}"
        shutil.copyfile(source, target)
        records.append(
            {
                "component": component,
                "source_basename": source.name,
                "bundle_path": target.relative_to(output).as_posix(),
                "sha256": sha256(target),
            }
        )
    return records


def build_bundle(output: Path) -> dict[str, object]:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    tcl, tk = tcl_tk_license_candidates()
    groups = {
        "python": python_license_candidates(),
        "tcl": tcl,
        "tk": tk,
        "pyinstaller": pyinstaller_license_candidates(),
    }

    records: list[dict[str, str]] = []
    for component in REQUIRED_COMPONENTS:
        records.extend(_copy_group(component, groups[component], output))

    manifest: dict[str, object] = {
        "schema": SCHEMA,
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "components": list(REQUIRED_COMPONENTS),
        "files": records,
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verify_bundle(output)
    return manifest


def verify_bundle(bundle: Path) -> dict[str, object]:
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Missing license-bundle manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise RuntimeError(f"Unexpected license-bundle schema: {manifest.get('schema')!r}")

    components = set(manifest.get("components", []))
    missing_components = set(REQUIRED_COMPONENTS) - components
    if missing_components:
        raise RuntimeError(f"License bundle missing required components: {sorted(missing_components)}")

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise RuntimeError("License bundle manifest contains no files")
    covered: set[str] = set()
    for record in files:
        if not isinstance(record, dict):
            raise RuntimeError("Malformed license-bundle file record")
        component = str(record.get("component", ""))
        rel = str(record.get("bundle_path", ""))
        expected = str(record.get("sha256", ""))
        if component not in REQUIRED_COMPONENTS or not rel or len(expected) != 64:
            raise RuntimeError(f"Malformed license-bundle record: {record!r}")
        path = bundle / rel
        if not path.is_file() or path.stat().st_size <= 0:
            raise RuntimeError(f"Missing/empty license text: {rel}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"License text hash mismatch for {rel}: {actual} != {expected}")
        covered.add(component)
    missing_files = set(REQUIRED_COMPONENTS) - covered
    if missing_files:
        raise RuntimeError(f"No license text record for required components: {sorted(missing_files)}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true", help="collect exact environment license texts")
    mode.add_argument("--verify", action="store_true", help="verify an existing generated bundle")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        if args.build:
            manifest = build_bundle(output)
            print(f"APL-IP-004 license bundle built: {output} ({len(manifest['files'])} texts)")
        else:
            manifest = verify_bundle(output)
            print(f"APL-IP-004 license bundle verified: {output} ({len(manifest['files'])} texts)")
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"APL-IP-004 FAIL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
