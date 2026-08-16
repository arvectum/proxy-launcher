import unittest
from unittest import mock

import backend_runtime
import proxy_core as core
from proxy_backend import ProxyBackendConfig


class _FakeBackend:
    backend_id = "fake"

    def __init__(self):
        self.enabled = None
        self.disabled = 0
        self.checked = None
        self.pending = False
        self.synced = None

    def enable(self, config):
        self.enabled = config
        return True

    def disable(self):
        self.disabled += 1
        return True

    def is_enabled(self, config):
        self.checked = config
        return True

    def restore_pending(self):
        return self.pending

    def sync_no_proxy(self, config):
        self.synced = config
        return True


class BackendRuntimeWiringTests(unittest.TestCase):
    def setUp(self):
        core._reset_proxy_backend_for_tests()
        self.settings = {
            "local_http_port": 8080,
            "local_pac_port": 8082,
            "pac_path": "/proxy.pac",
        }

    def tearDown(self):
        core._reset_proxy_backend_for_tests()

    def test_resolved_config_is_shared_and_normalized(self):
        with mock.patch.object(core, "load_settings", return_value=dict(self.settings)), \
             mock.patch.object(core, "load_no_proxy", return_value=["Example.Internal", "LOCALHOST"]), \
             mock.patch.object(core, "DEFAULT_NO_PROXY", ["localhost", "127.0.0.1"]):
            config = core.resolved_backend_config()

        self.assertEqual(
            config,
            ProxyBackendConfig(
                pac_url="http://127.0.0.1:8082/proxy.pac",
                http_proxy_url="http://127.0.0.1:8080",
                no_proxy=("localhost", "127.0.0.1", "example.internal"),
            ),
        )

    def test_public_runtime_seams_delegate_to_one_selected_backend(self):
        backend = _FakeBackend()
        with mock.patch.object(core, "load_settings", return_value=dict(self.settings)), \
             mock.patch.object(core, "load_no_proxy", return_value=[]), \
             mock.patch.object(backend_runtime, "create_backend", return_value=backend) as create:
            self.assertTrue(core.enable_system_proxy())
            self.assertTrue(core.system_proxy_enabled())
            self.assertFalse(core.network_restore_pending())
            self.assertTrue(core.sync_client_no_proxy())
            self.assertTrue(core.disable_system_proxy())

        self.assertEqual(create.call_count, 1)
        self.assertIsInstance(backend.enabled, ProxyBackendConfig)
        self.assertEqual(backend.checked, backend.enabled)
        self.assertEqual(backend.synced, backend.enabled)
        self.assertEqual(backend.disabled, 1)

    def test_backend_selection_failure_is_fail_closed(self):
        error = backend_runtime.UnsupportedPlatformError("unsupported")
        with mock.patch.object(backend_runtime, "create_backend", side_effect=error):
            self.assertFalse(core.enable_system_proxy())
            core._reset_proxy_backend_for_tests()
            self.assertFalse(core.disable_system_proxy())
            core._reset_proxy_backend_for_tests()
            self.assertFalse(core.system_proxy_enabled())
            core._reset_proxy_backend_for_tests()
            self.assertTrue(core.network_restore_pending())
            core._reset_proxy_backend_for_tests()
            self.assertFalse(core.sync_client_no_proxy())


if __name__ == "__main__":
    unittest.main()
