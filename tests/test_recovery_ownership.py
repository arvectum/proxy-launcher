import unittest

from recovery_ownership import (
    OwnershipPurpose,
    RecoveryEvidence,
    RecoveryOwnershipError,
    RecoveryOwnershipGuard,
)


DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def evidence(**overrides):
    values = {
        "owner_id": "launcher-session-a",
        "operation_id": "operation-001",
        "snapshot_id": "snapshot-001",
        "resource_scope": "windows:user-proxy",
        "original_state_sha256": DIGEST_A,
    }
    values.update(overrides)
    return RecoveryEvidence(**values)


class RecoveryOwnershipTests(unittest.TestCase):
    def test_owner_may_authorize_apply(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-a", expected_scope="windows:user-proxy"
        )
        self.assertTrue(guard.authorize(evidence(), OwnershipPurpose.APPLY))

    def test_owner_may_authorize_restore(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-a", expected_scope="windows:user-proxy"
        )
        self.assertTrue(guard.authorize(evidence(), OwnershipPurpose.RESTORE))

    def test_foreign_actor_cannot_apply(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-b", expected_scope="windows:user-proxy"
        )
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(evidence(), OwnershipPurpose.APPLY)

    def test_successor_cannot_restore_without_explicit_claim(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-b", expected_scope="windows:user-proxy"
        )
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(evidence(), OwnershipPurpose.RESTORE)

    def test_successor_claim_authorizes_restore_only(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-b", expected_scope="windows:user-proxy"
        )
        guard.claim_orphaned(evidence(), reason="owner process terminated unexpectedly")
        self.assertTrue(guard.authorize(evidence(), OwnershipPurpose.RESTORE))
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(evidence(), OwnershipPurpose.APPLY)

    def test_original_owner_cannot_create_successor_claim(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-a", expected_scope="windows:user-proxy"
        )
        with self.assertRaises(RecoveryOwnershipError):
            guard.claim_orphaned(evidence(), reason="not needed")

    def test_claim_requires_reason(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-b", expected_scope="windows:user-proxy"
        )
        with self.assertRaises(RecoveryOwnershipError):
            guard.claim_orphaned(evidence(), reason="")

    def test_scope_mismatch_is_rejected(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-a", expected_scope="windows:user-proxy"
        )
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(
                evidence(resource_scope="linux:desktop-proxy"), OwnershipPurpose.APPLY
            )

    def test_invalid_digest_is_rejected(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-a", expected_scope="windows:user-proxy"
        )
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(
                evidence(original_state_sha256="not-a-digest"), OwnershipPurpose.APPLY
            )

    def test_evidence_substitution_after_admission_is_rejected(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-a", expected_scope="windows:user-proxy"
        )
        guard.admit(evidence())
        with self.assertRaises(RecoveryOwnershipError):
            guard.admit(evidence(snapshot_id="snapshot-002", original_state_sha256=DIGEST_B))

    def test_missing_identity_field_is_rejected(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-a", expected_scope="windows:user-proxy"
        )
        with self.assertRaises(RecoveryOwnershipError):
            guard.admit(evidence(operation_id=""))

    def test_claim_is_bound_to_exact_evidence_identity(self):
        guard = RecoveryOwnershipGuard(
            actor_id="launcher-session-b", expected_scope="windows:user-proxy"
        )
        guard.claim_orphaned(evidence(), reason="crash recovery")
        with self.assertRaises(RecoveryOwnershipError):
            guard.authorize(
                evidence(operation_id="operation-002"), OwnershipPurpose.RESTORE
            )


if __name__ == "__main__":
    unittest.main()
