# Gate R3 — Diagnostics & Supportability

**Status:** PASS
**Date:** 2026-08-16

## Repository baseline

- Canonical repository: `arvectum/proxy-launcher`
- Canonical branch: `main`
- Audited baseline SHA: `4b49d2d50210b6497180d9ce6405de01dc0c6039`
- Baseline change: merge of APL-DIAG-006 support bundle privacy tests

## Gate objective

Gate R3 proves that the Windows product can produce actionable, privacy-bounded diagnostic evidence for customer support without requiring external connectivity and without silently changing proxy, recovery, autostart, PAC, WinINET, environment, or credential state.

The gate is an engineering/supportability closure, not a telemetry or remote-support authorization. Diagnostic collection remains local and user-controlled.

## Implemented diagnostics chain

### APL-DIAG-001 — Structured logging

PASS.

- Stable JSONL schema `arvectum.proxy.log.v1`.
- UTC timestamps, severity/event IDs and run/process/thread correlation.
- Bounded rotation and legacy plaintext-log preservation.
- Backward-compatible `_log(message)` contract.
- Logging failures do not break proxy/network recovery.

### APL-DIAG-002 — Secret redaction

PASS.

- Central redaction layer used by logging and diagnostic export.
- Covers credential-bearing URIs, authorization material, sensitive structured keys, tokens, passwords, cookies, JWT-shaped values, API-key/provider credential forms and private-key material.
- Nested structures and free-text diagnostic errors are sanitized before persistence/export.

### APL-DIAG-003 — Windows diagnostics collector

PASS.

- Read-only support snapshot and atomic ZIP export.
- Captures application/platform state, relevant paths, sanitized configuration, WinINET and environment proxy state, local listener state, interfaces, recovery/migration/autostart evidence and sanitized log rotations.
- Performs no external network request; listener probes are localhost-only.
- Raw settings and recovery backup files are excluded from the archive.
- Partial source failures are isolated so remaining evidence can still be produced.

### APL-DIAG-004 — Doctor / automated self-diagnostics

PASS.

- Stable report schema `arvectum.proxy.doctor.v1`.
- Deterministic PASS/WARN/FAIL result model with exit codes 0/1/2.
- Detects collector integrity problems, invalid ports/upstream shape, migration/recovery conflicts, engine/PAC inconsistency, stale/orphaned PAC ownership, listener problems and recovery-autostart anomalies.
- Human-readable and JSON CLI modes.
- Packaged EXE routing via `--doctor` / `--doctor-json`.
- GUI `Диагностика` action runs without blocking Tk.
- Doctor reports remediation but performs no automatic network repair.

### APL-DIAG-006 — Support bundle privacy tests

PASS.

- Treats the generated support ZIP as an untrusted export boundary.
- Canary tests cover settings, WinINET, process/user proxy environment, recovery/autostart commands, structured/plain logs and collector exception text.
- Archive allowlist prevents raw settings/backups/unrelated files from escaping.
- ZIP member names are fixed relative paths and do not expose source filesystem paths.
- Secret-shaped fixtures are generated at runtime so repository-wide secret scanning remains meaningful.

## Identifier note

There is no `APL-DIAG-005` artifact in canonical `main` at this baseline. Gate R3 does not invent a retrospective task or claim an implementation that is not present. The gate is based on the diagnostics/supportability capabilities actually implemented and merged as APL-DIAG-001, 002, 003, 004 and 006. The numbering gap is therefore recorded explicitly for roadmap hygiene and is not used to conceal a missing acceptance criterion.

## CI evidence on audited baseline

For SHA `4b49d2d50210b6497180d9ce6405de01dc0c6039`, the following GitHub Actions runs completed successfully:

- `APL-DIAG-003/006 Windows diagnostics + privacy` — success.
- `APL-DIAG-004 Doctor` — success.
- `Windows P0 portable` — success.
- `Windows installer` — success.
- `Dependency vulnerability scan` — success.
- `Release Evidence Package` — success.
- `Mirror to GitVerse` — success.

The diagnostics workflow runs collector tests, support-bundle privacy tests, the full unit suite, and native Windows no-proxy bundle smoke. The Doctor workflow validates the Doctor contract and packaged Windows execution path.

## Supportability acceptance

- [x] Support-relevant runtime events are persisted in a stable structured format.
- [x] Diagnostics and logs apply centralized secret redaction.
- [x] A local Windows support bundle can be created without external connectivity.
- [x] Collection is best-effort and does not fail wholesale when one source is unavailable.
- [x] Raw credential-bearing settings/backups are excluded from the support archive.
- [x] Final support ZIP privacy is tested with canaries at the artifact boundary.
- [x] Automated Doctor produces stable machine-readable and human-readable health results.
- [x] Doctor distinguishes warnings from hard failures and supplies remediation guidance.
- [x] Doctor and collector do not silently repair or mutate network/recovery state.
- [x] Windows GUI exposes diagnostics without blocking the UI thread.
- [x] Packaged Windows executable supports Doctor operation.
- [x] Native Windows CI exercises diagnostics paths.
- [x] Existing Windows portable/installer tracks remain green on the audited baseline.

## Scope boundary

Gate R3 confirms local diagnostics, automated self-diagnosis, safe support evidence collection and privacy-bounded export for the current Windows product track.

Gate R3 does **not** assert anonymous telemetry, remote log upload, remote-control capability, automatic incident submission, cross-platform diagnostics parity for macOS/Linux, or production code-signing trust. Those are separate product/distribution tracks and are not grounds for failure of this Windows diagnostics gate.

## Decision

**GATE R3 — PASS.**

The current Windows Proxy Launcher baseline is supportable: a customer/support engineer can obtain structured logs, run deterministic self-diagnostics, and produce a sanitized support bundle while preserving the product's fail-safe network/recovery boundary.

---

*Gate R3 audit complete. Diagnostics & Supportability gate closed on audited baseline `4b49d2d50210b6497180d9ce6405de01dc0c6039`.*
