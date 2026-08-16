# APL-DIAG-002 — Secret redaction

**Status:** IMPLEMENTED / READY FOR MERGE
**Depends on:** APL-DIAG-001 Structured logging
**Redaction marker:** `[REDACTED]`

## Goal

Prevent credential material from being persisted in Proxy Launcher diagnostics while keeping operationally useful values (hosts, ports, IP addresses, paths and `no_proxy` entries) visible.

## Architecture

`secret_redaction.py` is the single dependency-free redaction layer. `structured_logging.py` applies it before a record is serialized to JSONL, so redaction does not depend on individual logging call sites.

The redaction boundary covers:

- free-text `message` values;
- explicit structured `event` values;
- recursively nested `fields` values;
- string representations of non-primitive field values.

Redaction is bounded (maximum depth/items/string length) and logging remains fail-open for application availability: a diagnostics failure must never block proxy start, stop or rollback.

## Covered secret forms

- URI user-info (`scheme://user:password@host`, token-style user-info);
- `Authorization` / `Proxy-Authorization` and sensitive auth headers;
- `Cookie` / `Set-Cookie`;
- Basic, Bearer, Digest and Negotiate credential material;
- password, secret, token, API-key, client-secret, credential and PIN assignments;
- DPAPI credential/password blobs when carried by sensitive keys;
- query-string tokens/API keys;
- CLI forms such as `--password value` and `--api-key=value`;
- JWTs and high-confidence provider-prefixed tokens;
- PEM private-key payloads;
- case/punctuation/camelCase variants and compound suffix keys such as `clientSecret` or `upstream_access_token`.

## Deliberately preserved diagnostics

The layer does not redact ordinary infrastructure data solely because it is identifying or network-related. In particular, host names, IP addresses, ports, file paths, `no_proxy`, PAC paths and standalone usernames remain available unless they occur inside URI user-info or another credential container.

## Acceptance criteria

- [x] One reusable redaction module is the source of truth.
- [x] Structured log messages are redacted before persistence.
- [x] Structured fields are redacted recursively.
- [x] Explicit event strings are redacted before persistence.
- [x] Proxy URI credentials are removed while host/port/path remain visible.
- [x] Authorization headers, cookies, JWTs, API keys, tokens and private keys are covered.
- [x] DPAPI blobs are redacted when carried in credential fields.
- [x] CamelCase, punctuation and compound sensitive field names are covered.
- [x] False-positive regression coverage preserves hosts, paths, `no_proxy`, usernames and non-sensitive suffix words.
- [x] Traversal and string sizes remain bounded.
- [x] Platform-neutral tests run on Ubuntu and Windows through the existing structured-logging workflow.
