import unittest

from routing_rules import ApplicationIdentity, DestinationKind, DestinationSelector, RoutingAction, RoutingRule
from windows_app_routing import WindowsAppRoutingError, compile_windows_filter_plan, get_wfp_app_id

class WindowsAppRoutingPrototypeTests(unittest.TestCase):
    def test_compile_cidr_rule_is_enforcement_ready_plan_only(self):
        rule = RoutingRule('browser-proxy', RoutingAction.PROXY, (DestinationSelector(DestinationKind.CIDR, '203.0.113.0/24'),), ApplicationIdentity('windows', executable_path=r'C:\Browser\browser.exe'))
        plans = compile_windows_filter_plan([rule], app_id_resolver=lambda path: b'\x01\x02')
        self.assertEqual(len(plans), 1)
        plan = plans[0]
        self.assertEqual(plan.operation, 'redirect_to_local_proxy')
        self.assertEqual(plan.application_wfp_id_hex, '0102')
        self.assertTrue(plan.enforcement_ready)
        self.assertIn('FWPM_CONDITION_IP_REMOTE_ADDRESS', [c.condition for c in plan.conditions])

    def test_domain_rule_is_explicitly_not_ready_for_enforcement(self):
        rule = RoutingRule('browser-domain', RoutingAction.DIRECT, (DestinationSelector(DestinationKind.DOMAIN, 'example.com'),), ApplicationIdentity('windows', executable_path=r'C:\Browser\browser.exe'))
        plan = compile_windows_filter_plan([rule], app_id_resolver=lambda path: b'app')[0]
        self.assertFalse(plan.enforcement_ready)
        self.assertIn('DNS-aware', plan.note)

    def test_non_windows_application_is_rejected(self):
        rule = RoutingRule('bad', RoutingAction.PROXY, application=ApplicationIdentity('linux', executable_path='/bin/x'))
        with self.assertRaises(WindowsAppRoutingError):
            compile_windows_filter_plan([rule], app_id_resolver=lambda path: b'app')

    def test_app_id_probe_refuses_non_windows_host(self):
        with self.assertRaises(WindowsAppRoutingError):
            get_wfp_app_id('/tmp/x', platform='linux')

if __name__ == '__main__': unittest.main()
