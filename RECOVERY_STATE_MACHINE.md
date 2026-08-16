# APL-REC-001 — Formal recovery state machine

## Status

Implemented.

## Canonical lifecycle

The only normal network-mutation lifecycle is:

`OFF -> SAVE_ORIGINAL -> APPLY -> VERIFY -> ACTIVE -> RESTORE -> VERIFY -> OFF`

The public state name `VERIFY` is reused deliberately, while the state machine carries an internal verification target (`ACTIVE` or `OFF`) so the two checks cannot be confused.

## State meaning

| State | Contract |
| --- | --- |
| `OFF` | Launcher-owned proxy mutation is not active and recovery is not pending. |
| `SAVE_ORIGINAL` | Original network state is being captured before any mutation. |
| `APPLY` | Launcher-owned proxy settings are being applied. |
| `VERIFY` / target `ACTIVE` | Applied state must be proven before reporting `ACTIVE`. |
| `ACTIVE` | Launcher-owned proxy state has been verified active. |
| `RESTORE` | Original state is being restored or a failed apply/verification is being rolled back. |
| `VERIFY` / target `OFF` | Restored state must be proven before reporting `OFF`. |

## Safety invariants

1. `APPLY` is unreachable until the original state has been saved successfully.
2. A save failure may return directly to `OFF` only because mutation has not begun.
3. Once `APPLY` begins, a failure cannot return directly to `OFF`; it must enter `RESTORE`.
4. Failed verification of the active state enters `RESTORE`.
5. `ACTIVE` can be reported only after `VERIFY(target=ACTIVE)` succeeds.
6. `OFF` can be reported after mutation only after `RESTORE -> VERIFY(target=OFF)` succeeds.
7. Failed off-verification returns to `RESTORE`; recovery remains pending.
8. Verification results are target-specific: an `ACTIVE` proof cannot satisfy an `OFF` proof, and vice versa.
9. Illegal state skipping raises `RecoveryTransitionError` rather than being silently accepted.
10. Transition history is exposed as an immutable snapshot for diagnostics/tests.

## Failure paths

Safe pre-mutation abort:

`OFF -> SAVE_ORIGINAL -> OFF`

Apply failure:

`OFF -> SAVE_ORIGINAL -> APPLY -> RESTORE -> VERIFY -> OFF`

Active verification failure:

`OFF -> SAVE_ORIGINAL -> APPLY -> VERIFY(target=ACTIVE) -> RESTORE -> VERIFY(target=OFF) -> OFF`

Restore verification failure loops conservatively:

`RESTORE -> VERIFY(target=OFF) -> RESTORE -> ...`

The state machine never declares `OFF` merely because a restore attempt was made.

## Implementation

The platform-independent implementation lives in `recovery_state.py`. It performs no registry, environment, process, or filesystem mutation; platform adapters advance the machine only after the corresponding operation succeeds. This separation makes the recovery contract testable without Windows side effects.

`tests/test_recovery_state_machine.py` covers the canonical path, illegal transition prevention, apply/verification failures, target-specific verification, retry behavior, and immutable transition history.

## Boundary with APL-REC-002

APL-REC-001 defines *which transitions are legal*. APL-REC-002 defines *which evidence proves ownership and therefore authorizes those transitions*.
