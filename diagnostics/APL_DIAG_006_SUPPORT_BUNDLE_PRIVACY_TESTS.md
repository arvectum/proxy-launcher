# APL-DIAG-006 — Support bundle privacy tests

Status: implemented

## Goal

Make the Windows support bundle safe to hand to support by enforcing privacy as a tested artifact contract rather than relying only on individual redaction helpers.

APL-DIAG-006 does not change the support bundle into an anonymous telemetry package. Operational metadata needed for troubleshooting (for example hostnames, proxy endpoint hosts, local ports and filesystem paths already collected by APL-DIAG-003) remains diagnostic data. The privacy boundary enforced here is that credential material and raw private state files must not escape into the ZIP.

## Threat model

The generated support ZIP is treated as an untrusted export boundary. Tests seed unique canary values into every supported source class and inspect the final ZIP bytes/members.

Covered sources include application settings, WinINET proxy state, process/user proxy environment variables, recovery/autostart commands, structured and legacy logs, collector exception text, and raw state/backup files adjacent to application data.

Covered secret forms include password-bearing URIs, sensitive structured keys, Authorization/Bearer values, CLI/query credentials, API-key headers, provider-prefixed credentials, JWT-shaped values, and PEM private-key blocks.

## Archive contract

1. The bundle contains only generated diagnostics data and sanitized log rotations.
2. Raw settings, WinINET backup, environment backup and unrelated files are never copied into the archive.
3. Unique canaries injected into supported sources are absent from every archive member.
4. Collector exception text is redacted before it reaches `diagnostics.json`.
5. ZIP entry names are relative fixed archive paths and do not expose source filesystem paths.
6. Redaction preserves non-secret troubleshooting metadata where possible, such as proxy hostnames.
7. Temporary ZIP files are removed after atomic creation.

## Test implementation

Primary suite: `tests/test_support_bundle_privacy.py`.

Secret-shaped fixtures are assembled at runtime rather than committed as token/private-key lookalikes, so repository-wide secret scanning remains effective.

## CI gate

`.github/workflows/windows-diagnostics.yml` runs the APL-DIAG-006 privacy suite on both Ubuntu and Windows in addition to the existing APL-DIAG-003 collector tests and the full unit suite.

Any leaked canary, unexpected raw state file, unsafe archive member path or malformed diagnostics payload fails the pull request gate.

## Acceptance criteria

APL-DIAG-006 is complete when the dedicated privacy suite passes on Ubuntu and Windows, the complete unit suite remains green, native Windows bundle smoke passes, no raw credential canary appears in the generated bundle, and the task is merged into canonical `main`.
