import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class CanonicalSourceRefactorTests(unittest.TestCase):
    def test_mailmap_normalizes_only_human_historical_identities(self):
        text = (ROOT / ".mailmap").read_text(encoding="utf-8")
        self.assertIn("arvectum", text)
        self.assertIn("arutyunoveth", text)
        self.assertIn("Arvectum <arvectum@gmail.com>", text)
        for forbidden in ("OpenAI", "GitHub Actions", "noreply@openai.com"):
            self.assertNotIn(forbidden, text)

    def test_proxy_core_is_thin_composition_boundary(self):
        facade = (ROOT / "proxy_core.py").read_text(encoding="utf-8")
        runtime = (ROOT / "system_proxy_runtime.py").read_text(encoding="utf-8")
        self.assertIn("SystemProxyRuntime", facade)
        self.assertIn("proxy_core_legacy", facade)
        self.assertIn("sys.modules", facade.replace("_runtime_sys.modules", "sys.modules"))
        self.assertLess(len(facade), 5000)
        self.assertIn("class SystemProxyRuntime", runtime)
        self.assertIn("class WindowsCoreAdapter", runtime)
        self.assertIn("fail-closed", runtime.lower())

    def test_runtime_preserves_recovery_without_enable_preflight(self):
        runtime = (ROOT / "system_proxy_runtime.py").read_text(encoding="utf-8")
        disable_body = runtime.split("def disable_system_proxy", 1)[1].split("def system_proxy_enabled", 1)[0]
        restore_body = runtime.split("def network_restore_pending", 1)[1].split("def sync_client_no_proxy", 1)[0]
        self.assertNotIn("require_new_mutation_operational", disable_body)
        self.assertNotIn("require_new_mutation_operational", restore_body)
        self.assertIn("return True", restore_body)

    def test_historical_customer_baseline_is_not_relabelled(self):
        baseline = (ROOT / "release" / "baselines" / "APL-CLIENT-002_WINDOWS_0.2.3_CUSTOMER_CONFIRMED.md").read_text(encoding="utf-8-sig")
        self.assertIn("CONFIRMED CUSTOMER BASELINE FROZEN", baseline)
        self.assertIn("0.2.3", baseline)


if __name__ == "__main__":
    unittest.main()
