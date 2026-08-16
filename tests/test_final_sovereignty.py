import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FINAL = (ROOT / 'docs' / 'APL_IP_002_FINAL_CROSS_PLATFORM_SOVEREIGNTY.md').read_text(encoding='utf-8')

class FinalSovereigntyContractTests(unittest.TestCase):
    def test_all_platforms_are_consolidated(self):
        for token in ('Windows', 'Linux/Astra', 'macOS', 'APL-IP-002-WIN', 'APL-IP-002-LNX', 'APL-IP-002-MAC'):
            self.assertIn(token, FINAL)
    def test_final_verdict_remains_conditional(self):
        self.assertIn('CONDITIONAL PASS', FINAL)
        self.assertIn('P0 Windows build inputs', FINAL)
        self.assertIn('APL-IP-001', FINAL)
    def test_runtime_cloud_dependency_is_not_introduced(self):
        self.assertIn('No supported desktop SKU requires an Arvectum cloud control plane', FINAL)

if __name__ == '__main__': unittest.main()
