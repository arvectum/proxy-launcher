import unittest

from routing_rules import ApplicationIdentity, DestinationKind, DestinationSelector, RoutingAction, RoutingRule, ordered_rules

class RoutingRuleModelTests(unittest.TestCase):
    def test_windows_app_identity_is_case_stable(self):
        app = ApplicationIdentity(platform='windows', executable_path=r'C:\Program Files\Browser\browser.exe')
        self.assertEqual(app.stable_id, 'windows:exe:c:/program files/browser/browser.exe')
    def test_unicode_domain_is_canonical_idna(self):
        selector = DestinationSelector(DestinationKind.DOMAIN, 'пример.рф.')
        self.assertEqual(selector.value, 'xn--e1afmkfd.xn--p1ai')
    def test_cidr_is_canonical(self):
        selector = DestinationSelector(DestinationKind.CIDR, '10.0.0.8/24')
        self.assertEqual(selector.value, '10.0.0.0/24')
    def test_all_cannot_be_mixed(self):
        with self.assertRaises(ValueError):
            RoutingRule('bad', RoutingAction.DIRECT, (DestinationSelector(DestinationKind.ALL), DestinationSelector(DestinationKind.DOMAIN, 'example.com')))
    def test_round_trip_is_canonical(self):
        rule = RoutingRule('browser-direct', RoutingAction.DIRECT, (DestinationSelector(DestinationKind.DOMAIN, 'Example.COM'),), ApplicationIdentity('windows', executable_path=r'C:\x.exe'), priority=10)
        restored = RoutingRule.from_dict(rule.to_dict())
        self.assertEqual(restored.canonical_json(), rule.canonical_json())
    def test_ordering_is_priority_then_id(self):
        rules = [RoutingRule('b', RoutingAction.DIRECT, priority=20), RoutingRule('a', RoutingAction.PROXY, priority=20), RoutingRule('c', RoutingAction.DIRECT, priority=10), RoutingRule('off', RoutingAction.DIRECT, priority=0, enabled=False)]
        self.assertEqual([r.rule_id for r in ordered_rules(rules)], ['c','a','b'])

if __name__ == '__main__': unittest.main()
