# Gate R5 — Config & Security

Status: **PASS**
Date: 2026-08-16
PR: **#38 — Phase 5 — Config & Security**
Squash merge commit: `29813507c1fdb5cb9f3313ca1a24e5414b8bf3ce`
Canonical PR Config & Security run: `31945476558`
Post-merge main Config & Security run: `31945594502`

## Admission criteria

| Criterion | Evidence | Result |
| --- | --- | --- |
| Stable storage | Versioned validated settings model; mutable Windows state rooted in `%LOCALAPPDATA%\Arvectum\ProxyLauncher`; governed last-known-good, recovery and quarantine paths | PASS |
| Secrets boundary | Current-user Windows DPAPI credential blob; DPAPI failure has no plaintext fallback; legacy migration does not duplicate plaintext credentials into last-known-good state | PASS |
| Atomic writes | Same-directory temporary file, complete write, flush/fsync, atomic `os.replace`, parent-directory fsync where supported, cleanup on failure; previous primary preserved on injected replacement failure | PASS |
| Corruption recovery | Structural corruption quarantine with SHA-256 evidence; validated last-known-good restore; deterministic safe-default fallback; ordinary I/O failures are not misclassified as corruption; diagnostic reads remain non-mutating | PASS |

## Phase scope

- **APL-SEC-001 — Configuration model:** PASS
- **APL-SEC-002 — Stable data directories:** PASS
- **APL-SEC-003 — Secrets boundary:** PASS
- **APL-SEC-004 — Atomic configuration writes:** PASS
- **APL-SEC-005 — Corrupted configuration recovery:** PASS

## Verification evidence

### Pull request gate

Canonical PR run `31945476558` executed the governed Config & Security matrix on Python `3.12.10`:

- Ubuntu: compile PASS; Phase 5 contract **14/14 PASS**; full unit regression suite **258/258 PASS**.
- Windows: compile PASS; Phase 5 contract **14/14 PASS**; full unit regression suite **258/258 PASS**.

Related Windows product smoke checks were also green before merge:

- Windows P0 portable: PASS.
- Windows installer: PASS, including build, compile, fresh install, status, upgrade and uninstall smoke.

### Exact merged SHA gate

After squash merge, run `31945594502` re-executed the permanent Config & Security matrix against exact `main` SHA `29813507c1fdb5cb9f3313ca1a24e5414b8bf3ce`:

- Ubuntu: setup, compile, Phase 5 contract and full unit suite PASS.
- Windows: setup, compile, Phase 5 contract and full unit suite PASS.

## Decision

**Gate R5 = PASS.**

Phase 5 — Config & Security is admitted and closed. Phase 6 — Windows Productization is unblocked.
