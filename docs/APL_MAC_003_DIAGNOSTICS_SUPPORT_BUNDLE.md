# APL-MAC-003 — macOS diagnostics & support bundle

Status: implemented/tested; real-host content review remains part of APL-MAC-008.

The support bundle contains a bounded JSON report plus a short README. Runtime metadata, read-only preflight counts/reasons and narrowly selected Apple command results are allowed. Proxy credentials, arbitrary environment dumps, browser history, home-directory listings and rollback payload contents are explicitly excluded.

- [x] structured schema/version/platform metadata;
- [x] macOS runtime and preflight summary;
- [x] bounded read-only command capture;
- [x] no credential or rollback-payload collection;
- [x] atomic ZIP creation;
- [x] deterministic privacy/bundle tests;
- [ ] inspect one real support bundle on macOS — APL-MAC-008.
