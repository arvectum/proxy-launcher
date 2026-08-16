import unittest

from recovery_state import (
    RecoveryState,
    RecoveryStateMachine,
    RecoveryTransitionError,
    VerificationTarget,
    canonical_recovery_sequence,
)


class RecoveryStateMachineTests(unittest.TestCase):
    def test_canonical_sequence_is_exact(self):
        self.assertEqual(
            canonical_recovery_sequence(),
            (
                RecoveryState.OFF,
                RecoveryState.SAVE_ORIGINAL,
                RecoveryState.APPLY,
                RecoveryState.VERIFY,
                RecoveryState.ACTIVE,
                RecoveryState.RESTORE,
                RecoveryState.VERIFY,
                RecoveryState.OFF,
            ),
        )

    def test_happy_path_activation_and_restore(self):
        machine = RecoveryStateMachine()
        self.assertEqual(machine.begin_activation(), RecoveryState.SAVE_ORIGINAL)
        self.assertEqual(machine.original_saved(), RecoveryState.APPLY)
        self.assertEqual(machine.apply_completed(), RecoveryState.VERIFY)
        self.assertEqual(machine.verification_target, VerificationTarget.ACTIVE)
        self.assertEqual(machine.active_verified(), RecoveryState.ACTIVE)
        self.assertTrue(machine.is_active)
        self.assertEqual(machine.begin_restore(), RecoveryState.RESTORE)
        self.assertEqual(machine.restore_completed(), RecoveryState.VERIFY)
        self.assertEqual(machine.verification_target, VerificationTarget.OFF)
        self.assertEqual(machine.off_verified(), RecoveryState.OFF)
        self.assertTrue(machine.is_safe_off)
        self.assertFalse(machine.recovery_required)

    def test_cannot_apply_without_saved_original(self):
        machine = RecoveryStateMachine()
        with self.assertRaises(RecoveryTransitionError):
            machine.original_saved()

    def test_save_failure_may_abort_without_mutation(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        self.assertEqual(machine.abort_before_apply(), RecoveryState.OFF)
        self.assertTrue(machine.is_safe_off)

    def test_apply_failure_forces_restore(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        self.assertEqual(machine.apply_failed(), RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)

    def test_failed_active_verification_forces_restore(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        machine.apply_completed()
        self.assertEqual(machine.active_verification_failed(), RecoveryState.RESTORE)

    def test_verify_target_prevents_false_active_result(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        machine.apply_completed()
        with self.assertRaises(RecoveryTransitionError):
            machine.off_verified()

    def test_verify_target_prevents_false_off_result(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        machine.apply_completed()
        machine.active_verified()
        machine.begin_restore()
        machine.restore_completed()
        with self.assertRaises(RecoveryTransitionError):
            machine.active_verified()

    def test_failed_off_verification_reenters_restore(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        machine.apply_completed()
        machine.active_verified()
        machine.begin_restore()
        machine.restore_completed()
        self.assertEqual(machine.off_verification_failed(), RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)
        self.assertFalse(machine.is_safe_off)

    def test_cannot_skip_restore_from_active_to_off(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        machine.original_saved()
        machine.apply_completed()
        machine.active_verified()
        with self.assertRaises(RecoveryTransitionError):
            machine.off_verified()

    def test_history_is_immutable_snapshot(self):
        machine = RecoveryStateMachine()
        machine.begin_activation()
        history = machine.history
        self.assertIsInstance(history, tuple)
        self.assertEqual(history[0].previous, RecoveryState.OFF)
        self.assertEqual(history[0].current, RecoveryState.SAVE_ORIGINAL)


if __name__ == "__main__":
    unittest.main()
