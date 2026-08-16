import unittest
from types import SimpleNamespace

import backend_runtime
from macos_networksetup_preflight import MacOSPreflightStatus


class MacOSOperationalWiringTests(unittest.TestCase):
    def fake(self, status, reasons=()):
        return SimpleNamespace(status=status, reasons=tuple(reasons))

    def test_ready_macos_preflight_enables_new_mutation(self):
        status = backend_runtime.operational_status_for_platform(
            "darwin",
            macos_preflight=self.fake(MacOSPreflightStatus.READY),
        )
        self.assertEqual(status.backend_id, "macos")
        self.assertEqual(status.state, backend_runtime.OperationalState.READY)
        self.assertTrue(status.can_enable)
        view = backend_runtime.operational_status_view(status)
        self.assertEqual(view["badge"], "Доступно")
        self.assertTrue(view["enabled"])

    def test_auth_required_is_visible_and_actionable(self):
        status = backend_runtime.operational_status_for_platform(
            "darwin",
            macos_preflight=self.fake(
                MacOSPreflightStatus.AUTH_REQUIRED,
                ("authorization required",),
            ),
        )
        self.assertEqual(status.state, backend_runtime.OperationalState.AUTH_REQUIRED)
        self.assertTrue(status.can_enable)
        self.assertIn("разрешение", status.message.lower())
        self.assertEqual(status.reasons, ("authorization required",))

    def test_unavailable_macos_preflight_fails_closed(self):
        preflight = self.fake(
            MacOSPreflightStatus.UNAVAILABLE,
            ("networksetup is unavailable",),
        )
        status = backend_runtime.operational_status_for_platform(
            "darwin", macos_preflight=preflight
        )
        self.assertEqual(status.state, backend_runtime.OperationalState.UNAVAILABLE)
        self.assertFalse(status.can_enable)
        with self.assertRaises(backend_runtime.BackendOperationalError) as caught:
            backend_runtime.require_enable_operational(
                "darwin", macos_preflight=preflight
            )
        self.assertIs(caught.exception.status, status)

    def test_ready_macos_require_gate_returns_status(self):
        preflight = self.fake(MacOSPreflightStatus.READY)
        status = backend_runtime.require_enable_operational(
            "darwin", macos_preflight=preflight
        )
        self.assertEqual(status.state, backend_runtime.OperationalState.READY)


if __name__ == "__main__":
    unittest.main()
