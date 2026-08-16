import pathlib
import unittest

DOC = (pathlib.Path(__file__).resolve().parents[1] / 'docs' / 'APL_ROUTE_002_PER_APPLICATION_FEASIBILITY.md').read_text(encoding='utf-8')

class RouteFeasibilityContractTests(unittest.TestCase):
    def test_platform_decisions_are_explicit(self):
        for token in ('Windows Filtering Platform', 'FWPM_CONDITION_ALE_APP_ID', 'socket cgroupv2', 'NetworkExtension', 'MDM-managed'):
            self.assertIn(token, DOC)
    def test_live_enforcement_is_not_falsely_claimed(self):
        self.assertIn('Actual WFP redirect enforcement requires privileged/native installation', DOC)
        self.assertIn('Do not promise arbitrary consumer per-app routing', DOC)
    def test_windows_is_first_prototype(self):
        self.assertIn('P1 prototype target — APL-ROUTE-003', DOC)

if __name__ == '__main__': unittest.main()
