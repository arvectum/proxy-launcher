# APL-WIN-002 — Built-in connection test

Status: **implemented**

## Goal

Provide one built-in, read-only connection test that distinguishes failures in the internet connection, configured upstream proxy, local Launcher endpoints, PAC delivery, and Windows system proxy state.

## Checks

| Check | Contract |
| --- | --- |
| `internet.direct` | Access the selected URL with proxies explicitly disabled. HTTP error responses still count as network connectivity. |
| `upstream.tcp` | Probe every configured upstream `host:port` concurrently. Credentials are never included in the report. |
| `local.http` | Perform an end-to-end request to the selected URL through the Launcher's local HTTP proxy. |
| `local.socks` | Perform a SOCKS5 greeting and CONNECT through the Launcher's local SOCKS5 endpoint to the selected target host/port. |
| `pac.endpoint` | Fetch the configured local PAC endpoint directly and verify the Arvectum PAC shape (`FindProxyForURL`, localhost proxy address). |
| `windows.system_proxy` | Evaluate Windows proxy/recovery state with the same fail-closed ownership rules used by the launcher status UX. |

## Result model

Each check returns `PASS`, `WARN`, `FAIL`, or `SKIP`, a human-readable detail, elapsed time, and an optional recommended action. The overall state is:

- `FAIL` when at least one check fails;
- `WARN` when there is no failure but at least one warning or skipped local endpoint;
- `PASS` only when all six checks pass.

When the proxy engine is stopped, local HTTP/SOCKS/PAC checks are explicitly `SKIP` rather than producing misleading connection errors. Direct internet and Windows state are still checked.

## Safety

- The test is read-only: it does not start/stop the engine, edit PAC/WinINET settings, modify recovery evidence, or clear stale settings.
- Existing recovery ownership rules remain authoritative.
- Upstream usernames/passwords are never rendered in the structured report or GUI result.
- Network probes use bounded timeouts and concurrent execution so one dead endpoint does not serially block the whole test.

## UX

The existing **«Проверить соединение»** action now runs the governed test in a background thread. The configured URL remains user-editable. The result dialog shows every subsystem and a deduplicated **«Что сделать»** section for failures/warnings.

## Verification

`tests/test_connection_test.py` covers URL normalization, HTTP connectivity semantics, credential redaction, upstream reachability, real SOCKS5 handshake shape, PAC validation, Windows fail-closed state handling, stopped-engine SKIP semantics, the six-check report contract, and actionable formatting. The full repository regression suite is required before merge.
