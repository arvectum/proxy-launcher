# -*- coding: utf-8 -*-
"""APL-REC-006 — idempotency regression suite for governed recovery."""

import unittest

from recovery_ownership import (
    OwnershipPurpose,
    RecoveryEvidence,
    RecoveryOwnershipGuard,
)
from recovery_state import (
    RecoveryState,
    RecoveryStateMachine,
    RecoveryTransitionError,
    VerificationTarget,
)


SCOPE = "wininet:user-proxy"


def evidence() -> RecoveryEvidence:
    return RecoveryEvidence(
        owner_id="owner-1",
        operation_id="op-1",
        snapshot_id="snapshot-1",
        resource_scope=SCOPE,
        original_state_sha256="a" * 64,
    )


class RecoveryIdempotencyTests(unittest.TestCase):
    def assert_rejected_without_mutation(self, machine, operation):
        before_state = machine.state
        before_target = machine.verification_target
        before_history = machine.history
        with self.assertRaises(RecoveryTransitionError):
            operation()
        self.assertIs(machine.state, before_state)
        self.assertIs(machine.verification_target, before_target)
        self.assertEqual(machine.history, before_history)

    def test_duplicate_transition_calls_are_fail_closed_and_side_effect_free(self):
        machine = RecoveryStateMachine()

        machine.begin_activation()
        self.assert_rejected_without_mutation(machine, machine.begin_activation)

        machine.original_saved()
        self.assert_rejected_without_mutation(machine, machine.original_saved)

        machine.apply_completed()
        self.assertIs(machine.verification_target, VerificationTarget.ACTIVE)
        self.assert_rejected_without_mutation(machine, machine.apply_completed)

        machine.active_verified()
        self.assert_rejected_without_mutation(machine, machine.active_verified)

        machine.begin_restore()
        self.assert_rejected_without_mutation(machine, machine.begin_restore)

        machine.restore_completed()
        self.assertIs(machine.verification_target, VerificationTarget.OFF)
        self.assert_rejected_without_mutation(machine, machine.restore_completed)

        machine.off_verified()
        self.assertIs(machine.state, RecoveryState.OFF)
        self.assert_rejected_without_mutation(machine, machine.off_verified)

    def test_repeated_off_verification_failures_reenter_same_restore_loop(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        machine.apply_completed()
        machine.active_verified()
        machine.begin_restore()

        for _ in range(3):
            machine.restore_completed()
            self.assertIs(machine.state, RecoveryState.VERIFY)
            self.assertIs(machine.verification_target, VerificationTarget.OFF)
            machine.off_verification_failed()
            self.assertIs(machine.state, RecoveryState.RESTORE)
            self.assertIsNone(machine.verification_target)

        machine.restore_completed()
        machine.off_verified()
        self.assertTrue(machine.is_safe_off)
        self.assertFalse(machine.recovery_required)

    def test_two_complete_cycles_end_in_identical_safe_off_state(self):
        machine = RecoveryStateMachine()

        for _ in range(2):
            machine.begin_activation()
            machine.original_saved()
            machine.apply_completed()
            machine.active_verified()
            machine.begin_restore()
            machine.restore_completed()
            machine.off_verified()
            self.assertTrue(machine.is_safe_off)
            self.assertIsNone(machine.verification_target)

        transitions = [(t.previous, t.current) for t in machine.history]
        expected_cycle = [
            (RecoveryState.OFF, RecoveryState.SAVE_ORIGINAL),
            (RecoveryState.SAVE_ORIGINAL, RecoveryState.APPLY),
            (RecoveryState.APPLY, RecoveryState.VERIFY),
            (RecoveryState.VERIFY, RecoveryState.ACTIVE),
            (RecoveryState.ACTIVE, RecoveryState.RESTORE),
            (RecoveryState.RESTORE, RecoveryState.VERIFY),
            (RecoveryState.VERIFY, RecoveryState.OFF),
        ]
        self.assertEqual(transitions, expected_cycle * 2)

    def test_same_evidence_can_be_admitted_and_authorized_repeatedly(self):
        record = evidence()
        guard = RecoveryOwnershipGuard(actor_id="owner-1", expected_scope=SCOPE)

        self.assertIs(guard.admit(record), record)
        self.assertIs(guard.admit(record), record)
        self.assertTrue(guard.authorize(record, OwnershipPurpose.APPLY))
        self.assertTrue(guard.authorize(record, OwnershipPurpose.APPLY))
        self.assertTrue(guard.authorize(record, OwnershipPurpose.RESTORE))
        self.assertTrue(guard.authorize(record, OwnershipPurpose.RESTORE))
        self.assertIsNone(guard.claim)

    def test_successor_restore_authorization_is_repeatable_but_never_grants_apply(self):
        record = evidence()
        guard = RecoveryOwnershipGuard(actor_id="recovery-worker", expected_scope=SCOPE)

        first_claim = guard.claim_orphaned(record, reason="owner process crashed")
        second_claim = guard.claim_orphaned(record, reason="owner process crashed")
        self.assertEqual(first_claim, second_claim)
        self.assertEqual(guard.claim, second_claim)

        self.assertTrue(guard.authorize(record, OwnershipPurpose.RESTORE))
        self.assertTrue(guard.authorize(record, OwnershipPurpose.RESTORE))

        with self.assertRaisesRegex(Exception, "APPLY requires"):
            guard.authorize(record, OwnershipPurpose.APPLY)

    def test_recovery_retry_after_apply_failure_is_deterministic(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        machine.apply_failed()
        self.assertIs(machine.state, RecoveryState.RESTORE)

        for _ in range(2):
            machine.restore_completed()
            machine.off_verification_failed()
            self.assertIs(machine.state, RecoveryState.RESTORE)

        machine.restore_completed()
        machine.off_verified()
        self.assertTrue(machine.is_safe_off)


if __name__ == "__main__":
    unittest.main()
