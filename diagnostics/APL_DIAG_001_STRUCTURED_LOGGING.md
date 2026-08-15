# APL-DIAG-001 — Structured logging

**Status:** IMPLEMENTED / READY FOR MERGE
**Schema:** `arvectum.proxy.log.v1`

## Contract

Arvectum Proxy Launcher keeps its existing runtime log location. On Windows this is:

`%LOCALAPPDATA%\Arvectum\ProxyLauncher\proxy_core.log`

The file is JSON Lines (JSONL): one complete JSON object per line. Required fields are:

- `schema`, `ts`, `level`, `event`, `component`, `message`;
- `pid`, `thread`, `run_id`;
- `app_version`, `milestone`;
- optional structured `fields`.

Timestamps are UTC ISO-8601 with millisecond precision. Existing `_log(message)` calls remain supported; level and event are inferred deterministically. New code may call `structured_log(message, level=..., event=..., **fields)`.

## Privacy and secret handling

Before persistence, the logger redacts common credential material in both messages and structured fields, including passwords, tokens, authorization headers, proxy URL user-info, DPAPI credential blobs, PINs, client secrets and API keys. Logging errors are fail-open for the application: diagnostics must never prevent proxy start/stop/rollback.

## Retention and migration

- active log size: 2 MiB;
- rotated copies: 3 (`.1` ... `.3`);
- pre-APL-DIAG-001 plaintext log is preserved once as `.legacy` (or `.legacy.N` if needed), then the active file becomes pure JSONL;
- the GUI `Журнал` action remains compatible because the canonical log path does not change.

## Integration

The proxy engine stays in `proxy_core.py`. A dependency-free `StructuredLogger` is imported once and installed behind the existing `_log(message)` function. No proxy/network call sites need to change, existing mocks of `core._log` remain valid, and a new `structured_log(...)` entry point is available for diagnostics that need explicit event IDs or structured fields.

## Acceptance criteria

- [x] JSONL structured records with stable schema.
- [x] UTC timestamps, severity and event identifiers.
- [x] Process/thread/run correlation metadata.
- [x] Redaction of common secrets in message and fields.
- [x] Bounded rotation.
- [x] Legacy plaintext log preservation/migration.
- [x] `_log(message)` backward compatibility.
- [x] Explicit structured logging API for new diagnostics.
- [x] Logging failures never break proxy/network recovery.
- [x] Platform-neutral unit tests for schema, redaction, migration and rotation.
