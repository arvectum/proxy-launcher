import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MANIFEST_REL = "release/baselines/APL-CLIENT-002_WINDOWS_0.2.3_CUSTOMER_CONFIRMED.md"

REQUIRED_TOKENS = (
    "4d2ab937ce3c775ca627fa2deeefe3fb464ef48d",
    "683362A03785FD31625F5C570DC661B3562CE23C822FBDB07A8E27365BDA7909",
    "CD802FA0E7C48653098ADBEAF9B654CD6138196D8B2BB8DA2979198962803868",
    "Arvectum-Proxy-Launcher-Windows-0.2.3-P0-portable.zip",
    "31745739554",
    "9198914448",
    "CONFIRMED CUSTOMER BASELINE FROZEN",
)


class CustomerBaselineFreezeTests(unittest.TestCase):
    def test_baseline_manifest_exists(self):
        manifest = ROOT / MANIFEST_REL
        self.assertTrue(
            manifest.is_file(),
            "Customer baseline freeze manifest must exist at release/baselines/",
        )

    def test_baseline_manifest_records_authoritative_identity(self):
        text = (ROOT / MANIFEST_REL).read_text(encoding="utf-8-sig")
        for token in REQUIRED_TOKENS:
            self.assertIn(token, text, f"Baseline manifest must contain: {token}")

    def test_baseline_manifest_must_not_instruct_p0_tag_creation(self):
        text = (ROOT / MANIFEST_REL).read_text(encoding="utf-8-sig")
        for forbidden in (
            "v0.2.3-P0",
            "v0.2.3-P0.2",
            "v0.2.3-P0.4",
            "git tag v0.2.3-P0",
        ):
            self.assertNotIn(forbidden, text, f"Baseline manifest must not instruct tag: {forbidden}")


if __name__ == "__main__":
    unittest.main()