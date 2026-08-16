import unittest

from recovery_ownership import (
    OwnershipPurpose,
    RecoveryEvidence,
    RecoveryOwnershipError,
    RecoveryOwnershipGuard,
)
from recovery_state import (
    RecoveryState,
    RecoveryStateMachine,
    VerificationTarget,
)


DIGEST = "c" * 64
SCOPE = "windows:user-proxy"
OWNER = "launcher-session-owner"
SUCCESSOR = "launcher-session-successor"


def evidence():
    return RecoveryEvidence(
        owner_id=OWNER,
        operation_id="operation-crash-001",
        snapshot_id="snapshot-crash-001",
        resource_scope=SCOPE,
        original_state_sha256=DIGEST,
    )


def successor_guard():
    guard = RecoveryOwnershipGuard(actor_id=SUCCESSOR, expected_scope=SCOPE)
    guard.claim_orphaned(
        evidence(),
        reason="original launcher process terminated unexpectedly",
    )
    return guard


def activate_to_apply(machine):
    machine.begin_activation()
    machine.original_saved()
    return machine


def activate_to_verify(machine):
    activate_to_apply(machine)
    machine.apply_completed()
    return machine


def activate_to_active(machine):
    activate_to_verify(machine)
    machine.active_verified()
    return machine


def close_recovery(machine, guard):
    guard.authorize(evidence(), OwnershipPurpose.RESTORE)
    machine.restore_completed()
    self_target = machine.verification_target
    if self_target is not VerificationTarget.OFF:
        raise AssertionError("restore must enter VERIFY(target=OFF)")
    machine.off_verified()
    return machine


class CrashRecoveryTests(unittest.TestCase):
    """APL-REC-003 crash injection tests over the governed recovery lifecycle.

    A crash is represented by loss of the original ownership actor followed by a
    newly constructed successor guard. The RecoveryStateMachine instance stands
    for the durable lifecycle checkpoint owned by the platform adapter; these
    tests intentionally avoid registry/filesystem I/O.
    """

    def test_crash_during_apply_routes_to_successor_restore_and_off(self):
        machine = activate_to_apply(RecoveryStateMachine())
        self.assertEqual(machine.state, RecoveryState.APPLY)
        self.assertTrue(machine.recovery_required)

        guard = successor_guard()
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(evidence(), OwnershipPurpose.APPLY)

        machine.apply_failed()
        self.assertEqual(machine.state, RecoveryState.RESTORE)
        close_recovery(machine, guard)

        self.assertEqual(machine.state, RecoveryState.OFF)
        self.assertTrue(machine.is_safe_off)
        self.assertFalse(machine.recovery_required)

    def test_crash_during_active_verification_cannot_be_declared_active(self):
        machine = activate_to_verify(RecoveryStateMachine())
        self.assertEqual(machine.state, RecoveryState.VERIFY)
        self.assertEqual(machine.verification_target, VerificationTarget.ACTIVE)

        guard = successor_guard()
        machine.active_verification_failed()
        self.assertEqual(machine.state, RecoveryState.RESTORE)
        close_recovery(machine, guard)

        self.assertEqual(machine.state, RecoveryState.OFF)
        self.assertFalse(machine.is_active)

    def test_crash_while_active_is_recovered_by_successor_only(self):
        machine = activate_to_active(RecoveryStateMachine())
        self.assertTrue(machine.is_active)

        guard = successor_guard()
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(evidence(), OwnershipPurpose.APPLY)

        machine.begin_restore()
        close_recovery(machine, guard)

        self.assertTrue(machine.is_safe_off)

    def test_crash_during_restore_allows_restore_retry_then_verified_off(self):
        machine = activate_to_active(RecoveryStateMachine())
        machine.begin_restore()
        self.assertEqual(machine.state, RecoveryState.RESTORE)

        guard = successor_guard()
        close_recovery(machine, guard)

        self.assertEqual(machine.state, RecoveryState.OFF)

    def test_crash_during_off_verification_requires_retry_before_off(self):
        machine = activate_to_active(RecoveryStateMachine())
        machine.begin_restore()
        guard = successor_guard()
        guard.authorize(evidence(), OwnershipPurpose.RESTORE)
        machine.restore_completed()

        self.assertEqual(machine.state, RecoveryState.VERIFY)
        self.assertEqual(machine.verification_target, VerificationTarget.OFF)

        machine.off_verification_failed()
        self.assertEqual(machine.state, RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)
        self.assertFalse(machine.is_safe_off)

        close_recovery(machine, guard)
        self.assertTrue(machine.is_safe_off)

    def test_successor_without_claim_cannot_restore_orphaned_operation(self):
        machine = activate_to_active(RecoveryStateMachine())
        machine.begin_restore()
        guard = RecoveryOwnershipGuard(actor_id=SUCCESSOR, expected_scope=SCOPE)

        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(evidence(), OwnershipPurpose.RESTORE)

        self.assertEqual(machine.state, RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)
        self.assertFalse(machine.is_safe_off)

    def test_crash_recovery_never_reuses_stale_evidence_for_apply(self):
        machine = activate_to_apply(RecoveryStateMachine())
        guard = successor_guard()

        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(evidence(), OwnershipPurpose.APPLY)

        self.assertEqual(machine.state, RecoveryState.APPLY)
        self.assertTrue(machine.recovery_required)

    def test_failed_off_verification_never_produces_false_closure(self):
        machine = activate_to_active(RecoveryStateMachine())
        machine.begin_restore()
        guard = successor_guard()
        guard.authorize(evidence(), OwnershipPurpose.RESTORE)
        machine.restore_completed()
        machine.off_verification_failed()

        self.assertNotEqual(machine.state, RecoveryState.OFF)
        self.assertEqual(machine.state, RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)


if __name__ == "__main__":
    unittest.main()
