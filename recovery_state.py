# -*- coding: utf-8 -*-
"""Formal network recovery state machine for Arvectum Proxy Launcher.

APL-REC-001 defines one canonical lifecycle for network mutation:

    OFF -> SAVE_ORIGINAL -> APPLY -> VERIFY -> ACTIVE
        -> RESTORE -> VERIFY -> OFF

``VERIFY`` is intentionally one public state name.  Internally the machine
records whether verification is proving ACTIVE or OFF, so a caller cannot
accidentally accept the wrong verification result.

This module is deliberately platform-independent and side-effect free.  It is
the contract used by Windows recovery code and by later platform adapters.
Ownership/evidence admission rules are layered on top in APL-REC-002.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class RecoveryState(str, Enum):
    OFF = "OFF"
    SAVE_ORIGINAL = "SAVE_ORIGINAL"
    APPLY = "APPLY"
    VERIFY = "VERIFY"
    ACTIVE = "ACTIVE"
    RESTORE = "RESTORE"


class VerificationTarget(str, Enum):
    ACTIVE = "ACTIVE"
    OFF = "OFF"


class RecoveryTransitionError(RuntimeError):
    """Raised when code attempts to skip or reverse a governed transition."""


@dataclass(frozen=True)
class RecoveryTransition:
    previous: RecoveryState
    current: RecoveryState
    verification_target: Optional[VerificationTarget]


class RecoveryStateMachine:
    """Deterministic state machine for governed proxy activation/recovery.

    The machine does not perform registry, environment, process or file I/O.
    Those operations belong to the caller.  The caller advances the machine
    only after the corresponding operation has completed successfully.

    Failure rules are conservative:
    * before APPLY, activation may abort back to OFF;
    * after APPLY starts, failure must enter RESTORE;
    * failed ACTIVE verification must enter RESTORE;
    * failed OFF verification stays in the recovery loop by returning to
      RESTORE; it can never report OFF without successful verification.
    """

    def __init__(self, initial: RecoveryState = RecoveryState.OFF):
        self._state = RecoveryState(initial)
        self._verification_target: Optional[VerificationTarget] = None
        self._history: list[RecoveryTransition] = []

    @property
    def state(self) -> RecoveryState:
        return self._state

    @property
    def verification_target(self) -> Optional[VerificationTarget]:
        return self._verification_target

    @property
    def history(self) -> Tuple[RecoveryTransition, ...]:
        return tuple(self._history)

    @property
    def is_active(self) -> bool:
        return self._state is RecoveryState.ACTIVE

    @property
    def is_safe_off(self) -> bool:
        return self._state is RecoveryState.OFF

    @property
    def recovery_required(self) -> bool:
        return self._state in {
            RecoveryState.APPLY,
            RecoveryState.VERIFY,
            RecoveryState.ACTIVE,
            RecoveryState.RESTORE,
        }

    def _move(
        self,
        target: RecoveryState,
        *,
        verification_target: Optional[VerificationTarget] = None,
    ) -> RecoveryState:
        previous = self._state
        self._state = target
        self._verification_target = verification_target
        self._history.append(
            RecoveryTransition(previous, target, verification_target)
        )
        return self._state

    def begin_activation(self) -> RecoveryState:
        self._require(RecoveryState.OFF, "activation can begin only from OFF")
        return self._move(RecoveryState.SAVE_ORIGINAL)

    def original_saved(self) -> RecoveryState:
        self._require(
            RecoveryState.SAVE_ORIGINAL,
            "original settings must be saved before APPLY",
        )
        return self._move(RecoveryState.APPLY)

    def abort_before_apply(self) -> RecoveryState:
        self._require(
            RecoveryState.SAVE_ORIGINAL,
            "pre-apply abort is valid only while saving original state",
        )
        return self._move(RecoveryState.OFF)

    def apply_completed(self) -> RecoveryState:
        self._require(RecoveryState.APPLY, "APPLY must precede active verification")
        return self._move(
            RecoveryState.VERIFY,
            verification_target=VerificationTarget.ACTIVE,
        )

    def apply_failed(self) -> RecoveryState:
        self._require(RecoveryState.APPLY, "apply failure is valid only in APPLY")
        return self._move(RecoveryState.RESTORE)

    def active_verified(self) -> RecoveryState:
        self._require_verification_target(VerificationTarget.ACTIVE)
        return self._move(RecoveryState.ACTIVE)

    def active_verification_failed(self) -> RecoveryState:
        self._require_verification_target(VerificationTarget.ACTIVE)
        return self._move(RecoveryState.RESTORE)

    def begin_restore(self) -> RecoveryState:
        self._require(RecoveryState.ACTIVE, "normal restore can begin only from ACTIVE")
        return self._move(RecoveryState.RESTORE)

    def restore_completed(self) -> RecoveryState:
        self._require(RecoveryState.RESTORE, "RESTORE must precede off verification")
        return self._move(
            RecoveryState.VERIFY,
            verification_target=VerificationTarget.OFF,
        )

    def off_verified(self) -> RecoveryState:
        self._require_verification_target(VerificationTarget.OFF)
        return self._move(RecoveryState.OFF)

    def off_verification_failed(self) -> RecoveryState:
        self._require_verification_target(VerificationTarget.OFF)
        return self._move(RecoveryState.RESTORE)

    def _require(self, expected: RecoveryState, message: str) -> None:
        if self._state is not expected:
            raise RecoveryTransitionError(
                "%s (current=%s, expected=%s)" % (
                    message,
                    self._state.value,
                    expected.value,
                )
            )

    def _require_verification_target(self, target: VerificationTarget) -> None:
        if self._state is not RecoveryState.VERIFY:
            raise RecoveryTransitionError(
                "verification result requires VERIFY (current=%s)" % self._state.value
            )
        if self._verification_target is not target:
            actual = self._verification_target.value if self._verification_target else "NONE"
            raise RecoveryTransitionError(
                "verification target mismatch (current=%s, expected=%s)" % (
                    actual,
                    target.value,
                )
            )


def canonical_recovery_sequence() -> Tuple[RecoveryState, ...]:
    """Return the normative APL-REC-001 happy-path sequence."""
    return (
        RecoveryState.OFF,
        RecoveryState.SAVE_ORIGINAL,
        RecoveryState.APPLY,
        RecoveryState.VERIFY,
        RecoveryState.ACTIVE,
        RecoveryState.RESTORE,
        RecoveryState.VERIFY,
        RecoveryState.OFF,
    )
