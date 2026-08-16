# APL-SEC-005 — Corrupted configuration recovery

Status: **IMPLEMENTED**

Normal application loads distinguish structural corruption from ordinary I/O failures.

For malformed JSON, invalid schema/types/ranges, unknown keys, or unsupported future configuration versions:

- the corrupted primary is moved into the stable `quarantine/` directory;
- a SHA-256 fingerprint and non-secret metadata sidecar are written when possible;
- a validated last-known-good configuration is restored atomically when available;
- otherwise the application runs with programmatic safe defaults without silently accepting malformed state;
- `config_recovery.json` records the recovery source without embedding configuration content.

A locked/unreadable file is **not** classified as corrupted and is never renamed or overwritten merely because an I/O operation failed.

Diagnostic/read-only loads (`migrate_legacy=False`) do not quarantine or rewrite corrupted configuration.
