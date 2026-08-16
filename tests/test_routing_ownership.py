import os
import tempfile
import unittest

from routing_ownership import OwnedRoutingResource, RoutingOwnershipError, RoutingOwnershipStore, plan_digest

class RoutingOwnershipTests(unittest.TestCase):
    def test_prepare_persists_before_apply_and_blocks_second_owner(self):
        with tempfile.TemporaryDirectory() as temp:
            store = RoutingOwnershipStore(os.path.join(temp, 'routing.json'))
            state = store.prepare(platform='windows', canonical_plan_json='{"a":1}', resources=[OwnedRoutingResource('wfp-filter','Arvectum.ProxyLauncher.filter.1')], session_id='session-1', now='2026-08-17T00:00:00+00:00')
            self.assertEqual(state.phase, 'prepared')
            self.assertEqual(store.load().plan_digest, plan_digest('{"a":1}'))
            with self.assertRaises(RoutingOwnershipError):
                store.prepare(platform='windows', canonical_plan_json='{}', resources=[OwnedRoutingResource('wfp-filter','Arvectum.ProxyLauncher.filter.2')])

    def test_clear_requires_restoring_and_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            path = os.path.join(temp, 'routing.json')
            store = RoutingOwnershipStore(path)
            store.prepare(platform='windows', canonical_plan_json='{}', resources=[OwnedRoutingResource('wfp-filter','Arvectum.ProxyLauncher.filter.1')])
            store.transition('applied')
            with self.assertRaises(RoutingOwnershipError): store.clear_after_verified_restore(verified=True)
            store.transition('restoring')
            with self.assertRaises(RoutingOwnershipError): store.clear_after_verified_restore(verified=False)
            store.clear_after_verified_restore(verified=True)
            self.assertFalse(os.path.exists(path))

    def test_foreign_resource_namespace_is_rejected(self):
        with self.assertRaises(ValueError):
            OwnedRoutingResource('wfp-filter', 'OtherVendor.filter')

    def test_unsafe_phase_transition_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            store = RoutingOwnershipStore(os.path.join(temp, 'routing.json'))
            store.prepare(platform='linux', canonical_plan_json='{}', resources=[OwnedRoutingResource('nft-chain','Arvectum.ProxyLauncher.chain.1')])
            with self.assertRaises(RoutingOwnershipError): store.transition('restoring') if False else store.transition('prepared')

if __name__ == '__main__': unittest.main()
