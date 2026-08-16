import unittest
from types import SimpleNamespace
from macos_networksetup_preflight import MacOSPreflightStatus
from macos_capability_ux import macos_capability_view, macos_failure_message

class MacOSCapabilityUxTests(unittest.TestCase):
    def test_ready(self):
        view = macos_capability_view(SimpleNamespace(status=MacOSPreflightStatus.READY, reasons=()))
        self.assertTrue(view["can_on"]); self.assertFalse(view["authorization_required"])
    def test_auth_required_is_actionable_but_explicit(self):
        view = macos_capability_view(SimpleNamespace(status=MacOSPreflightStatus.AUTH_REQUIRED, reasons=("auth",)))
        self.assertTrue(view["can_on"]); self.assertTrue(view["authorization_required"])
    def test_unavailable_fails_closed(self):
        view = macos_capability_view(SimpleNamespace(status=MacOSPreflightStatus.UNAVAILABLE, reasons=("missing",)))
        self.assertFalse(view["can_on"])
    def test_failure_messages_do_not_claim_mutation_success(self):
        self.assertIn("не применён", macos_failure_message("not authorized"))
        self.assertIn("оставлена без изменений", macos_failure_message("networksetup failed"))

if __name__ == "__main__": unittest.main()
