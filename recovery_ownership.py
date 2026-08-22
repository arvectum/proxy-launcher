# -*- coding: utf-8 -*-
"""Governed recovery ownership rules for Arvectum Proxy Launcher.

recovery-state ownership defines which recovery state transitions are legal. recovery mutation ownership
adds the evidence/ownership contract that decides who may authorize mutation
and recovery transitions.

The module is deliberately side-effect free. Durable storage and platform
mutation remain responsibilities of platform adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Optional


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RecoveryOwnershipError(RuntimeError):
    """Raised when recovery evidence or ownership authority is invalid."""


class OwnershipPurpose(str, Enum):
    APPLY = "APPLY"
    RESTORE = "RESTORE"


@dataclass(frozen=True)
class RecoveryEvidence:
    """Immutable provenance for the original state captured before mutation."""

    owner_id: str
    operation_id: str
    snapshot_id: str
    resource_scope: str
    original_state_sha256: str

    def validate(self) -> None:
        fields = {
            "owner_id": self.owner_id,
            "operation_id": self.operation_id,
            "snapshot_id": self.snapshot_id,
            "resource_scope": self.resource_scope,
            "original_state_sha256": self.original_state_sha256,
        }
        for name, value in fields.items():
            if not isinstance(value, str) or not value.strip():
                raise RecoveryOwnershipError("%s must be non-empty" % name)
        if not _SHA256_RE.fullmatch(self.original_state_sha256):
            raise RecoveryOwnershipError(
                "original_state_sha256 must be a lowercase SHA-256 digest"
            )

    @property
    def identity(self) -> tuple[str, str, str, str, str]:
        return (
            self.owner_id,
            self.operation_id,
            self.snapshot_id,
            self.resource_scope,
            self.original_state_sha256,
        )


@dataclass(frozen=True)
class RecoveryClaim:
    """Explicit successor claim over one exact orphaned recovery record."""

    successor_owner_id: str
    evidence_identity: tuple[str, str, str, str, str]
    reason: str


class RecoveryOwnershipGuard:
    """Authorize APPLY/RESTORE using exact, target-scoped ownership evidence.

    Rules:
    * APPLY is permitted only to the owner that captured the original state.
    * RESTORE is permitted to that same owner, or to an explicitly claimed
      crash-recovery successor for the exact same evidence record.
    * a successor claim never grants APPLY authority;
    * evidence is bound to one expected resource scope;
    * evidence from another operation/snapshot cannot be substituted after it
      has been admitted;
    * ownership is proven by evidence, never inferred from process identity,
      current settings, file presence, or a successful mutation attempt.
    """

    def __init__(self, *, actor_id: str, expected_scope: str):
        if not actor_id or not actor_id.strip():
            raise RecoveryOwnershipError("actor_id must be non-empty")
        if not expected_scope or not expected_scope.strip():
            raise RecoveryOwnershipError("expected_scope must be non-empty")
        self._actor_id = actor_id
        self._expected_scope = expected_scope
        self._admitted_identity: Optional[tuple[str, str, str, str, str]] = None
        self._claim: Optional[RecoveryClaim] = None

    @property
    def actor_id(self) -> str:
        return self._actor_id

    @property
    def expected_scope(self) -> str:
        return self._expected_scope

    @property
    def claim(self) -> Optional[RecoveryClaim]:
        return self._claim

    def admit(self, evidence: RecoveryEvidence) -> RecoveryEvidence:
        """Validate and pin one exact evidence record to this guard."""
        evidence.validate()
        if evidence.resource_scope != self._expected_scope:
            raise RecoveryOwnershipError(
                "recovery evidence scope mismatch (actual=%s, expected=%s)"
                % (evidence.resource_scope, self._expected_scope)
            )
        if self._admitted_identity is None:
            self._admitted_identity = evidence.identity
        elif self._admitted_identity != evidence.identity:
            raise RecoveryOwnershipError(
                "recovery evidence substitution is forbidden after admission"
            )
        return evidence

    def claim_orphaned(self, evidence: RecoveryEvidence, *, reason: str) -> RecoveryClaim:
        """Claim exact durable evidence after the original owner is unavailable.

        The claim is recovery-only. It authorizes RESTORE but can never be used
        to start or continue APPLY under a successor identity.
        """
        self.admit(evidence)
        if self._actor_id == evidence.owner_id:
            raise RecoveryOwnershipError(
                "original owner does not need a successor recovery claim"
            )
        if not reason or not reason.strip():
            raise RecoveryOwnershipError("recovery claim reason must be non-empty")
        claim = RecoveryClaim(
            successor_owner_id=self._actor_id,
            evidence_identity=evidence.identity,
            reason=reason.strip(),
        )
        self._claim = claim
        return claim

    def authorize(self, evidence: RecoveryEvidence, purpose: OwnershipPurpose) -> bool:
        """Authorize one mutation purpose or raise RecoveryOwnershipError."""
        self.admit(evidence)
        purpose = OwnershipPurpose(purpose)

        if purpose is OwnershipPurpose.APPLY:
            if self._actor_id != evidence.owner_id:
                raise RecoveryOwnershipError(
                    "APPLY requires the owner that captured the original state"
                )
            return True

        if self._actor_id == evidence.owner_id:
            return True
        if self._claim is None:
            raise RecoveryOwnershipError(
                "RESTORE by a successor requires an explicit orphaned recovery claim"
            )
        if self._claim.successor_owner_id != self._actor_id:
            raise RecoveryOwnershipError("recovery claim belongs to another successor")
        if self._claim.evidence_identity != evidence.identity:
            raise RecoveryOwnershipError("recovery claim does not match admitted evidence")
        return True
