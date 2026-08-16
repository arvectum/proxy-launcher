# APL-DIAG-006 — Support bundle privacy tests

Status: implemented

## Goal

Make the Windows support bundle safe to hand to support by enforcing privacy as a tested artifact contract rather than relying only on individual redaction helpers.

APL-DIAG-006 does not change the support bundle into an anonymous telemetry package. Operational metadata needed for troubleshooting (for example hostnames, proxy endpoint hosts, local ports and filesystem paths already collected by APL-DIAG-003) remains diagnostic data. The privacy boundary enforced here is that credential material and raw private state files must not escape into the ZIP.

## Threat model

The generated support ZIP is treated as an untrusted export boundary. Tests seed unique canary secrets into every supported source class and inspect the final ZIP bytes/members.

Covered sources:

- application settings returned by `load_settings()`;
- WinINET proxy state;
- process proxy environment variables;
- user proxy environment variables;
- recovery/autostart command values;
- structured JSON logs;
- legacy/plain-text logs;
- collector exception text;
- raw settings and recovery backup files placed next to application state.

Covered secret forms:

- password-bearing URIs;
- sensitive structured keys;
- Authorization/Bearer values;
- CLI token arguments;
- query-string access tokens;
- API-key headers;
- GitHub-style prefixed tokens;
- JWT-shaped tokens;
- PEM private-key blocks.

## Archive contract

The privacy suite enforces the following invariants:

1. The bundle contains only generated diagnostics data and sanitized log rotations.
2. Raw settings, WinINET backup, environment backup and unrelated files are never copied into the archive.
3. Unique secret canaries injected into supported sources are absent from every archive member.
4. Collector exception text is redacted before it reaches `diagnostics.json`.
5. ZIP entry names are relative fixed archive paths and do not expose source filesystem paths.
6. Redaction preserves non-secret troubleshooting metadata where possible, such as proxy hostnames.
7. Temporary ZIP files are removed after atomic creation.

## Test implementation

Primary suite:

`tests/test_support_bundle_privacy.py`

The tests exercise the real `windows_diagnostics.create_support_bundle()` path with a deterministic fake core and inspect the completed ZIP using `zipfile`.

The suite is intentionally separate from the APL-DIAG-003 functional collector tests so failures can be classified specifically as a support-export privacy regression.

## CI gate

`.github/workflows/windows-diagnostics.yml` runs the APL-DIAG-006 privacy suite on both Ubuntu and Windows in addition to the existing APL-DIAG-003 collector tests and the full unit suite.

Any leaked canary, unexpected raw state file, unsafe archive member path or malformed diagnostics payload fails the pull request gate.

## Acceptance criteria

APL-DIAG-006 is complete when:

- the dedicated privacy test module passes on Ubuntu and Windows;
- the complete unit suite remains green;
- the native Windows support-bundle smoke test remains green;
- no raw credential canary appears in the generated bundle;
- the task is merged into canonical `main`.
