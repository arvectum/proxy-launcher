import json
import unittest

import backend_contract
from backend_runtime import backend_id_for_platform
from capability_model import Feature, declared_backend_ids


class UnifiedBackendContractTests(unittest.TestCase):
    def test_all_governed_backend_classes_satisfy_one_contract(self):
        self.assertTrue(backend_contract.validate_all_backends())

    def test_contract_has_exactly_five_canonical_operations(self):
        self.assertEqual(
            tuple(operation.name for operation in backend_contract.BACKEND_OPERATIONS),
            ("enable", "disable", "is_enabled", "restore_pending", "sync_no_proxy"),
        )

    def test_backend_registry_matches_capability_registry(self):
        self.assertEqual(
            set(backend_contract.governed_backend_classes()),
            set(declared_backend_ids()),
        )

    def test_runtime_platform_mapping_covers_every_governed_backend(self):
        observed = {
            backend_id_for_platform("win32"),
            backend_id_for_platform("darwin"),
            backend_id_for_platform("linux"),
        }
        self.assertEqual(observed, set(declared_backend_ids()))

    def test_every_backend_has_required_regression_coverage(self):
        required = {
            "CONTRACT-001",
            "LIFECYCLE-001",
            "ROLLBACK-001",
            "FOREIGN-001",
            "BYPASS-001",
            "RUNTIME-001",
            "CAPABILITY-001",
        }
        for backend_id in declared_backend_ids():
            with self.subTest(backend_id=backend_id):
                covered = {
                    row.requirement_id
                    for row in backend_contract.regression_requirements_for(backend_id)
                }
                self.assertTrue(required.issubset(covered))

    def test_windows_baseline_guard_is_windows_only(self):
        row = next(
            item
            for item in backend_contract.REGRESSION_MATRIX
            if item.requirement_id == "WINDOWS-BASELINE-001"
        )
        self.assertEqual(row.backends, ("windows",))

    def test_system_proxy_safety_capabilities_are_supported_on_all_backends(self):
        required_features = (
            Feature.SYSTEM_PROXY,
            Feature.BYPASS_RULES,
            Feature.SAFE_ROLLBACK,
        )
        from capability_model import capabilities_for_backend

        for backend_id in declared_backend_ids():
            platform = capabilities_for_backend(backend_id)
            for feature in required_features:
                with self.subTest(backend_id=backend_id, feature=feature.value):
                    self.assertTrue(platform.supports(feature))

    def test_manifest_is_deterministic_json_serializable_and_versioned(self):
        manifest = backend_contract.contract_manifest()
        encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True)
        self.assertIn('"contract_version": "1"', encoded)
        self.assertEqual(manifest["backends"], ["linux", "macos", "windows"])
        self.assertEqual(len(manifest["operations"]), 5)

    def test_signature_drift_is_rejected(self):
        from proxy_backend import ProxyBackend

        class DriftedBackend(ProxyBackend):
            @property
            def backend_id(self):
                return "windows"

            def enable(self, config, force=False):
                return True

            def disable(self):
                return True

            def is_enabled(self, config):
                return False

            def restore_pending(self):
                return False

            def sync_no_proxy(self, config):
                return True

        with self.assertRaises(backend_contract.BackendContractError):
            backend_contract.validate_backend_class(DriftedBackend, "windows")


if __name__ == "__main__":
    unittest.main()
