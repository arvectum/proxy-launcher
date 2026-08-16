# APL-REC-006 — Idempotency suite

## Purpose

This suite proves that recovery operations remain deterministic under duplicate calls, retries, and replay after partial failure.

## Covered invariants

- duplicate state-machine transitions fail closed and do not mutate state, verification target, or history;
- repeated OFF-verification failures return to the same RESTORE loop until OFF is positively verified;
- complete activate/restore cycles can be repeated from OFF without residual state;
- the same immutable recovery evidence may be admitted and authorized repeatedly;
- successor recovery claims may be replayed for RESTORE but never acquire APPLY authority;
- APPLY failure recovery retries remain deterministic and converge only after successful OFF verification.

## Regression gate

`tests/test_recovery_idempotency.py` is part of the normal test discovery used by CI. APL-REC-006 is considered satisfied only when this suite and the repository-wide regression suite pass.
