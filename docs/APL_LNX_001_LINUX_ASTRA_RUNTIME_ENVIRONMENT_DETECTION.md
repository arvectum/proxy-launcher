# APL-LNX-001 — Linux/Astra runtime environment detection

Status: implemented

## Goal

Provide one deterministic, read-only runtime fingerprint for the Linux product line before distro-specific integration or packaging logic is allowed to make decisions.

## Runtime facts

`linux_runtime.detect_linux_runtime()` returns an immutable `LinuxRuntimeEnvironment` with:

- distribution id, `ID_LIKE`, display name, version/codename and variant from `os-release`;
- Astra-specific version from `/etc/astra_version` when present;
- kernel release and machine architecture;
- desktop/session facts from XDG/session environment variables;
- resolved `nmcli` path and explicit NetworkManager client availability;
- governed `is_astra`, `is_debian_family` and stable `runtime_id` classifications.

## Astra classification

Primary modern marker:

- `/etc/os-release`: `ID=astra`.

Compatibility markers:

- `NAME`/`PRETTY_NAME` containing `Astra Linux`;
- readable non-empty `/etc/astra_version` for older/special installations.

Astra is also classified as Debian-family because current Astra Linux `os-release` declares `ID_LIKE=debian` and historical supported releases derive from the Debian family.

## Safety properties

- detection is read-only and starts no services;
- no shell commands are executed;
- `os-release` is parsed as data, never sourced as shell code;
- missing or unreadable release files degrade to `runtime_id=linux` rather than guessing a distro;
- missing `nmcli` is reported as a capability fact, not auto-installed;
- non-Linux platforms raise `LinuxRuntimeDetectionError`.

## NetworkManager boundary

APL-LNX-001 only detects whether the `nmcli` client exists. It does not claim that NetworkManager is active, owns the current connection, or that the current user has mutation permission. Those operational checks belong to the following Linux integration/preflight tasks.

## Official Astra basis

Astra Linux documentation identifies `/etc/os-release` with `ID=astra`, `ID_LIKE=debian`, version fields, and `/etc/astra_version` as supported OS-version evidence. Astra networking documentation describes `nmcli` as the NetworkManager command-line interface.

References:

- https://wiki.astralinux.ru/pages/viewpage.action?pageId=137563146
- https://wiki.astralinux.ru/pages/viewpage.action?pageId=35029228
- https://wiki.astralinux.ru/pages/viewpage.action?pageId=3277370

## Verification

`tests/test_linux_runtime.py` covers:

1. safe `os-release` parsing;
2. current Astra detection via `ID=astra`;
3. Astra compatibility detection via `/etc/astra_version`;
4. negative Debian/Astra classification;
5. Debian-family classification via `ID_LIKE`;
6. `/usr/lib/os-release` fallback;
7. generic-Linux degradation when release metadata is absent;
8. fail-closed rejection on non-Linux platforms.

The test module is compiled and executed by `.github/workflows/core-backends.yml` on both Ubuntu and macOS runners; detection itself is fully injected so Astra fixtures are deterministic and do not depend on the CI host distribution.
