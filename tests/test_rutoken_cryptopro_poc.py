import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RutokenCryptoProPocContractTests(unittest.TestCase):
    def read(self, name: str) -> str:
        return (ROOT / name).read_text(encoding="utf-8-sig")

    def test_windows_is_the_primary_owner_operated_host(self):
        doc = self.read("release/APL_REL_010_RUTOKEN_CRYPTOPRO_SIGNING_POC.md")
        self.assertIn("Primary POC host:** Windows", doc)
        self.assertIn("MacBook, compatibility-only follow-up", doc)
        self.assertIn("OWNER-OPERATED HARDWARE RUN REQUIRED", doc)

    def test_poc_script_never_accepts_pin_or_exportable_key_material(self):
        script = self.read("tools/rutoken_cryptopro_poc.ps1")
        lowered = script.lower()
        self.assertNotIn("[string]$pin", lowered)
        self.assertNotIn("[string]$password", lowered)
        self.assertNotIn("export-pfxcertificate", lowered)
        self.assertIn("private_key_export_attempted", lowered)
        self.assertIn("pin_stored", lowered)
        self.assertIn("$false", lowered)

    def test_detached_crypto_pro_round_trip_is_implemented(self):
        script = self.read("tools/rutoken_cryptopro_poc.ps1")
        for required in (
            "'-sfsign', '-sign', '-detached', '-add'",
            "'-sfsign', '-verify', '-detached'",
            "SHA256SUMS.txt",
            "SHA256SUMS.txt.sig",
            "signer-certificate.cer",
            "signing-evidence.json",
        ):
            self.assertIn(required, script)

    def test_code_signing_eku_is_inspected_but_not_activated(self):
        script = self.read("tools/rutoken_cryptopro_poc.ps1")
        doc = self.read("release/APL_REL_010_RUTOKEN_CRYPTOPRO_SIGNING_POC.md")
        self.assertIn("1.3.6.1.5.5.7.3.3", script)
        self.assertIn("code_signing_eku_present", script)
        self.assertIn("authenticode_probe_attempted", script)
        self.assertIn("production_signing_activated", script)
        self.assertIn("activate production signing automatically", doc)

    def test_poc_uses_csptest_without_making_cryptcp_mandatory(self):
        script = self.read("tools/rutoken_cryptopro_poc.ps1")
        doc = self.read("release/APL_REL_010_RUTOKEN_CRYPTOPRO_SIGNING_POC.md")
        self.assertIn("csptest.exe", script)
        self.assertIn("csptest -sfsign", doc)
        self.assertIn("separate licensing", doc)

    def test_current_certificate_is_not_misrepresented_as_code_signing(self):
        doc = self.read("release/APL_REL_010_RUTOKEN_CRYPTOPRO_SIGNING_POC.md")
        self.assertIn("EKU absent", doc)
        self.assertIn("not treated as a code-signing certificate", doc)
        self.assertIn("candidate profile", doc)
        self.assertIn("ОТУЦ", doc)


if __name__ == "__main__":
    unittest.main()
