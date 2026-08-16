# APL-SEC-003 — Secrets boundary

Status: **IMPLEMENTED**

On Windows, upstream username/password material is serialized only inside a current-user DPAPI `credentials_dpapi` blob. The governed schema rejects mixing that blob with plaintext/legacy credential fields.

Legacy plaintext settings are migrated on normal application load. During that migration the last-known-good snapshot is deliberately skipped, preventing creation of a second plaintext credential copy.

Additional boundaries:

- DPAPI protection failure aborts the save; there is no plaintext fallback on Windows;
- diagnostics use read-only settings loading and the existing central secret-redaction layer;
- corruption/recovery metadata stores filenames, hashes/reasons and recovery source only, never configuration contents or credentials;
- diagnostics expose only path/state metadata for Config & Security recovery files.
