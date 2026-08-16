# APL-REC-002 — Recovery ownership rules

## Status

Implemented.

## Purpose

APL-REC-001 defines which recovery transitions are legal. APL-REC-002 defines which evidence proves that Arvectum Proxy Launcher owns a mutation/recovery operation and therefore who is allowed to authorize APPLY and RESTORE.

Ownership is never inferred from current proxy settings, process identity alone, the existence of a recovery file, or the fact that a mutation attempt succeeded.

## Required ownership evidence

Every governed mutation must be bound to one immutable `RecoveryEvidence` record captured before mutation:

- `owner_id` — identity of the launcher session/process that captured the original state;
- `operation_id` — unique mutation/recovery operation identifier;
- `snapshot_id` — unique identifier of the saved original-state snapshot;
- `resource_scope` — exact target being mutated, for example `windows:user-proxy`;
- `original_state_sha256` — lowercase SHA-256 digest of the captured original state.

All fields are mandatory. Evidence is rejected if the scope differs from the adapter's expected scope or if the digest is malformed.

## Authority rules

1. **APPLY requires original ownership.** Only the actor identified by `owner_id` may authorize APPLY.
2. **Normal RESTORE follows the same owner.** The actor that captured the original state may authorize RESTORE directly.
3. **Crash recovery uses explicit successor ownership.** A different actor may restore only after making an explicit orphaned-recovery claim over the exact admitted evidence record.
4. **Successor ownership is recovery-only.** A successor claim can authorize RESTORE but never APPLY. A restart cannot use stale evidence to continue or begin a mutation.
5. **Evidence is pinned after admission.** Once a guard admits an evidence identity, a different operation, snapshot, scope, owner, or digest cannot be substituted.
6. **Claims are exact-record scoped.** A successor claim for one evidence record cannot authorize another operation or snapshot.
7. **Claims require a reason.** Crash/restart takeover must record why the original owner is unavailable; silent takeover is not allowed.
8. **Original owners do not self-claim.** The original owner already has restore authority and cannot manufacture a successor path.
9. **No authority from observation.** Matching current settings, file presence, PID reuse, username, hostname, or successful verification do not establish ownership.
10. **No false closure.** Ownership authority does not replace APL-REC-001 verification. RESTORE still must reach `VERIFY(target=OFF)` and succeed before `OFF` is declared.

## Crash/restart model

Normal owner path:

`capture evidence -> owner APPLY -> owner RESTORE -> VERIFY(OFF)`

Crash/restart path:

`durable evidence from owner A -> owner A unavailable -> successor B explicit claim -> successor B RESTORE -> VERIFY(OFF)`

Forbidden restart path:

`durable evidence from owner A -> successor B APPLY`

The successor may only reduce risk by restoring the saved original state. It may not extend the previous owner's mutation authority.

## Implementation

The platform-independent implementation lives in `recovery_ownership.py`:

- `RecoveryEvidence` validates immutable ownership provenance;
- `RecoveryOwnershipGuard` pins one evidence record and authorizes APPLY/RESTORE;
- `RecoveryClaim` represents an explicit recovery-only successor claim;
- `RecoveryOwnershipError` rejects invalid evidence, foreign APPLY, unclaimed successor RESTORE, scope mismatch, or evidence substitution.

The module performs no registry, environment, process, or filesystem I/O. Platform adapters must persist/load evidence and advance the APL-REC-001 state machine only after the corresponding ownership authorization succeeds.

`tests/test_recovery_ownership.py` covers owner APPLY/RESTORE, foreign-owner rejection, explicit successor recovery, recovery-only successor authority, scope/digest validation, claim reason requirements, exact-record binding, and evidence-substitution prevention.

## Boundary with APL-REC-003

APL-REC-002 establishes the ownership/evidence contract. APL-REC-003 adds crash-recovery tests that exercise restart/orphan scenarios against the recovery lifecycle using these rules.
