import unittest

from proxy_backend import ProxyBackend, ProxyBackendConfig
from windows_backend import WindowsBackend, _normalize_no_proxy


class _FakeWindowsCore:
    DEFAULT_NO_PROXY = ["localhost", "127.0.0.1", "*.LOCAL"]

    def __init__(self):
        self.settings = {
            "local_http_port": 8080,
            "local_pac_port": 8082,
            "pac_path": "/proxy.pac",
        }
        self.custom_no_proxy = ["Example.Internal", "localhost"]
        self.enabled = False
        self.pending = False
        self.enable_calls = 0
        self.disable_calls = 0
        self.sync_calls = 0
        self.logs = []

    def load_settings(self):
        return dict(self.settings)

    def load_no_proxy(self):
        return list(self.custom_no_proxy)

    def pac_url(self, settings):
        return "http://127.0.0.1:%d%s" % (
            settings["local_pac_port"], settings["pac_path"])

    def enable_system_proxy(self):
        self.enable_calls += 1
        self.enabled = True
        return True

    def disable_system_proxy(self):
        self.disable_calls += 1
        self.enabled = False
        return True

    def system_proxy_enabled(self):
        return self.enabled

    def network_restore_pending(self):
        return self.pending

    def sync_client_no_proxy(self):
        self.sync_calls += 1
        return True

    def _log(self, message):
        self.logs.append(message)


def _matching_config():
    return ProxyBackendConfig(
        pac_url="http://127.0.0.1:8082/proxy.pac",
        http_proxy_url="http://127.0.0.1:8080",
        no_proxy=("localhost", "127.0.0.1", "*.local", "example.internal"),
    )


class WindowsBackendTests(unittest.TestCase):
    def setUp(self):
        self.core = _FakeWindowsCore()
        self.backend = WindowsBackend(self.core)

    def test_is_concrete_proxy_backend_with_stable_id(self):
        self.assertIsInstance(self.backend, ProxyBackend)
        self.assertEqual(self.backend.backend_id, "windows")

    def test_enable_delegates_to_proven_windows_path_for_matching_config(self):
        config = _matching_config()
        self.assertTrue(self.backend.enable(config))
        self.assertEqual(self.core.enable_calls, 1)
        self.assertTrue(self.backend.is_enabled(config))

    def test_disable_and_restore_pending_delegate_without_weakening_rollback(self):
        self.core.enabled = True
        self.core.pending = True
        self.assertTrue(self.backend.restore_pending())
        self.assertTrue(self.backend.disable())
        self.assertEqual(self.core.disable_calls, 1)
        self.assertFalse(self.core.enabled)

    def test_sync_no_proxy_delegates_only_for_resolved_current_config(self):
        self.assertTrue(self.backend.sync_no_proxy(_matching_config()))
        self.assertEqual(self.core.sync_calls, 1)

    def test_config_mismatch_is_fail_closed_and_never_mutates_windows(self):
        variants = [
            ProxyBackendConfig(
                pac_url="http://foreign.example/proxy.pac",
                http_proxy_url="http://127.0.0.1:8080",
                no_proxy=_matching_config().no_proxy,
            ),
            ProxyBackendConfig(
                pac_url="http://127.0.0.1:8082/proxy.pac",
                http_proxy_url="http://127.0.0.1:9080",
                no_proxy=_matching_config().no_proxy,
            ),
            ProxyBackendConfig(
                pac_url="http://127.0.0.1:8082/proxy.pac",
                http_proxy_url="http://127.0.0.1:8080",
                no_proxy=("localhost",),
            ),
        ]
        for config in variants:
            with self.subTest(config=config):
                self.assertFalse(self.backend.enable(config))
                self.assertFalse(self.backend.is_enabled(config))
                self.assertFalse(self.backend.sync_no_proxy(config))
        self.assertEqual(self.core.enable_calls, 0)
        self.assertEqual(self.core.sync_calls, 0)

    def test_no_proxy_comparison_is_normalized_and_deduplicated(self):
        config = ProxyBackendConfig(
            pac_url="http://127.0.0.1:8082/proxy.pac",
            http_proxy_url="http://127.0.0.1:8080",
            no_proxy=(" LOCALHOST ", "127.0.0.1", "*.local", "EXAMPLE.INTERNAL", "localhost"),
        )
        self.assertTrue(self.backend.enable(config))
        self.assertEqual(
            _normalize_no_proxy(("A", " a ", "", None, "B")),
            ("a", "b"),
        )


if __name__ == "__main__":
    unittest.main()
