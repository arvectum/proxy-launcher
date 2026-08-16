# -*- coding: utf-8 -*-
"""APL-REC-007 — deterministic failure-injection tests for governed recovery.

The suite injects one synthetic operation failure at each recovery boundary
required by the roadmap: save, apply, active verification, listener start and
restore.  The important invariant is not that every failure can immediately
return to OFF; it is that the state machine never reports a false safe state.
Failures after mutation begins must remain recovery-required until a successful
restore is followed by OFF verification.
"""

import unittest

from recovery_state import RecoveryState, RecoveryStateMachine, VerificationTarget


class InjectedFailure(RuntimeError):
    """Synthetic operation failure used only by the APL-REC-007 suite."""


class FailureInjector:
    def __init__(self, fail_at):
        self.fail_at = fail_at
        self.calls = []

    def operation(self, name):
        self.calls.append(name)
        if name == self.fail_at:
            raise InjectedFailure(name)


class FailureInjectionTests(unittest.TestCase):
    def assert_safe_off(self, machine):
        self.assertIs(machine.state, RecoveryState.OFF)
        self.assertIsNone(machine.verification_target)
        self.assertTrue(machine.is_safe_off)
        self.assertFalse(machine.recovery_required)

    def recover_to_off(self, machine, injector=None):
        if injector is not None:
            injector.operation("restore")
        machine.restore_completed()
        self.assertIs(machine.state, RecoveryState.VERIFY)
        self.assertIs(machine.verification_target, VerificationTarget.OFF)
        machine.off_verified()
        self.assert_safe_off(machine)

    def activate_through_apply(self, machine, injector):
        machine.begin_activation()
        injector.operation("save")
        machine.original_saved()
        injector.operation("apply")
        machine.apply_completed()

    def test_injected_save_failure_aborts_before_any_mutation(self):
        machine = RecoveryStateMachine()
        injector = FailureInjector("save")

        machine.begin_activation()
        with self.assertRaisesRegex(InjectedFailure, "save"):
            injector.operation("save")

        self.assertIs(machine.state, RecoveryState.SAVE_ORIGINAL)
        self.assertFalse(machine.recovery_required)
        machine.abort_before_apply()
        self.assert_safe_off(machine)
        self.assertEqual(injector.calls, ["save"])

    def test_injected_apply_failure_forces_restore_before_off(self):
        machine = RecoveryStateMachine()
        injector = FailureInjector("apply")

        machine.begin_activation()
        injector.operation("save")
        machine.original_saved()
        with self.assertRaisesRegex(InjectedFailure, "apply"):
            injector.operation("apply")
        machine.apply_failed()

        self.assertIs(machine.state, RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)
        self.assertFalse(machine.is_safe_off)
        self.recover_to_off(machine)

    def test_injected_active_verification_failure_forces_restore(self):
        machine = RecoveryStateMachine()
        injector = FailureInjector("verify")

        self.activate_through_apply(machine, injector)
        self.assertIs(machine.verification_target, VerificationTarget.ACTIVE)
        with self.assertRaisesRegex(InjectedFailure, "verify"):
            injector.operation("verify")
        machine.active_verification_failed()

        self.assertIs(machine.state, RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)
        self.recover_to_off(machine)

    def test_injected_listener_start_failure_never_commits_active(self):
        machine = RecoveryStateMachine()
        injector = FailureInjector("start_listener")

        self.activate_through_apply(machine, injector)
        # Listener availability is part of proving the ACTIVE state.  A start
        # failure therefore consumes the ACTIVE verification failure path; the
        # machine must never pass through ACTIVE.
        with self.assertRaisesRegex(InjectedFailure, "start_listener"):
            injector.operation("start_listener")
        machine.active_verification_failed()

        self.assertNotIn(
            RecoveryState.ACTIVE,
            [transition.current for transition in machine.history],
        )
        self.assertIs(machine.state, RecoveryState.RESTORE)
        self.assertTrue(machine.recovery_required)
        self.recover_to_off(machine)

    def test_injected_restore_failure_stays_in_recovery_until_retry_succeeds(self):
        machine = RecoveryStateMachine()
        injector = FailureInjector("restore")

        self.activate_through_apply(machine, injector)
        injector.operation("verify")
        injector.operation("start_listener")
        machine.active_verified()
        machine.begin_restore()

        before_history = machine.history
        with self.assertRaisesRegex(InjectedFailure, "restore"):
            injector.operation("restore")

        # A failed external restore operation must not advance the formal state
        # to VERIFY/OFF.  Recovery remains mandatory and the failed side effect
        # contributes no transition history.
        self.assertIs(machine.state, RecoveryState.RESTORE)
        self.assertEqual(machine.history, before_history)
        self.assertTrue(machine.recovery_required)
        self.assertFalse(machine.is_safe_off)

        retry = FailureInjector(None)
        self.recover_to_off(machine, retry)
        self.assertEqual(retry.calls, ["restore"])

    def test_failure_matrix_has_no_false_off_or_active_terminal_state(self):
        expected_terminal = {
            "save": RecoveryState.OFF,
            "apply": RecoveryState.OFF,
            "verify": RecoveryState.OFF,
            "start_listener": RecoveryState.OFF,
            "restore": RecoveryState.OFF,
        }

        observed = {}
        for failure_point in expected_terminal:
            machine = RecoveryStateMachine()
            injector = FailureInjector(failure_point)

            machine.begin_activation()
            try:
                injector.operation("save")
            except InjectedFailure:
                machine.abort_before_apply()
                observed[failure_point] = machine.state
                continue

            machine.original_saved()
            try:
                injector.operation("apply")
            except InjectedFailure:
                machine.apply_failed()
                self.recover_to_off(machine)
                observed[failure_point] = machine.state
                continue

            machine.apply_completed()
            try:
                injector.operation("verify")
                injector.operation("start_listener")
            except InjectedFailure:
                machine.active_verification_failed()
                self.recover_to_off(machine)
                observed[failure_point] = machine.state
                continue

            machine.active_verified()
            machine.begin_restore()
            try:
                injector.operation("restore")
            except InjectedFailure:
                self.assertIs(machine.state, RecoveryState.RESTORE)
                self.assertTrue(machine.recovery_required)
                retry = FailureInjector(None)
                self.recover_to_off(machine, retry)
            else:
                machine.restore_completed()
                machine.off_verified()
            observed[failure_point] = machine.state

        self.assertEqual(observed, expected_terminal)


if __name__ == "__main__":
    unittest.main()
