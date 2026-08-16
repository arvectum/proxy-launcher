# APL-REC-003 — Crash recovery tests

## Status

Implemented.

## Purpose

APL-REC-003 verifies that a launcher crash or restart cannot strand the governed network lifecycle in an unsafe state, silently transfer mutation authority, or falsely report `OFF` before recovery has been verified.

The tests compose the contracts introduced by:

- APL-REC-001 — deterministic recovery state machine;
- APL-REC-002 — immutable recovery evidence and ownership/successor rules.

The suite is platform-independent. It does not mutate the Windows registry, environment variables, filesystem proxy configuration, or live network settings. Those side effects remain adapter responsibilities.

## Crash model

A crash is represented by loss of the original ownership actor and construction of a new successor `RecoveryOwnershipGuard` for the same immutable evidence record. The `RecoveryStateMachine` represents the durable lifecycle checkpoint maintained by the platform adapter.

The successor must explicitly claim the orphaned record before RESTORE. The claim is recovery-only and never grants APPLY authority.

## Injected crash points

`tests/test_crash_recovery.py` covers:

1. crash during `APPLY`;
2. crash during `VERIFY(target=ACTIVE)`;
3. crash while `ACTIVE`;
4. crash during `RESTORE`;
5. crash during `VERIFY(target=OFF)`;
6. successor restart without an explicit orphan claim;
7. attempted successor reuse of stale evidence for APPLY;
8. failed OFF verification and mandatory recovery retry.

## Required invariants

Every crash test enforces the following safety properties:

- a successor cannot authorize APPLY using the original owner's recovery evidence;
- a successor cannot RESTORE without an explicit orphaned-recovery claim;
- any post-APPLY failure remains recovery-required until RESTORE completes;
- failed `VERIFY(target=OFF)` returns to `RESTORE` rather than declaring `OFF`;
- `OFF` is reached only after successful OFF verification;
- crash recovery is risk-reducing only: restart can restore the original state but cannot extend the previous process's mutation authority.

## CI coverage

The tests use Python `unittest` and are automatically included by the canonical Windows clean build command:

`python -m unittest discover -s tests -v`

Therefore APL-REC-003 is exercised by the existing Windows P0 pull-request workflow together with the complete unit-test suite and packaged clean build.

## Boundary

APL-REC-003 proves the platform-independent crash/restart contract. It does not yet simulate a real operating-system process kill against live WinINET settings. Native destructive/integration fault-injection belongs to a later Windows recovery validation task where rollback can be isolated and safely supervised.
