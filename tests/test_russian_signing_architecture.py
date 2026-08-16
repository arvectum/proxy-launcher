import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RussianSigningArchitectureTests(unittest.TestCase):
    def read(self, name: str) -> str:
        return (ROOT / name).read_text(encoding="utf-8-sig")

    def test_architecture_is_russia_first_and_not_prematurely_active(self):
        architecture = self.read("release/APL_REL_009_RUSSIAN_PRODUCTION_SIGNING_ARCHITECTURE.md")
        self.assertIn("Russia-first production signing architecture", architecture)
        self.assertIn("PRODUCTION SIGNING NOT YET ACTIVE", architecture)
        self.assertIn("ОТУЦ", architecture)
        self.assertIn("APL-REL-010", architecture)

    def test_existing_qualified_signature_is_not_misrepresented_as_code_signing(self):
        architecture = self.read("release/APL_REL_009_RUSSIAN_PRODUCTION_SIGNING_ARCHITECTURE.md")
        self.assertIn("must not be assumed to be a Windows code-signing certificate", architecture)
        self.assertIn("1.3.6.1.5.5.7.3.3", architecture)
        self.assertIn("detached release evidence", architecture)

    def test_release_evidence_contract_is_defined(self):
        architecture = self.read("release/APL_REL_009_RUSSIAN_PRODUCTION_SIGNING_ARCHITECTURE.md")
        for required in (
            "SHA256SUMS.txt",
            "SHA256SUMS.txt.sig",
            "signer-certificate.cer",
            "signing-evidence.json",
            "signature_verified",
            "embedded_code_signing_verified",
        ):
            self.assertIn(required, architecture)

    def test_private_key_boundary_is_hardware_backed_and_cloud_free(self):
        architecture = self.read("release/APL_REL_009_RUSSIAN_PRODUCTION_SIGNING_ARCHITECTURE.md")
        lowered = architecture.lower()
        self.assertIn("non-exportable", lowered)
        self.assertIn("rutoken", lowered)
        self.assertIn("pin", lowered)
        self.assertIn("never stored in github", lowered)
        self.assertIn("owner-operated", lowered)

    def test_foreign_provider_is_deferred_not_primary(self):
        architecture = self.read("release/APL_REL_009_RUSSIAN_PRODUCTION_SIGNING_ARCHITECTURE.md")
        self.assertIn("Foreign code-signing providers", architecture)
        self.assertIn("future international-market compatibility track", architecture)
        self.assertIn("not a dependency for the Russian production release", architecture)

    def test_release_policy_points_to_russian_architecture(self):
        policy = self.read("RELEASE_POLICY.md")
        self.assertIn("APL_REL_009_RUSSIAN_PRODUCTION_SIGNING_ARCHITECTURE.md", policy)
        self.assertIn("Russia first", policy)
        self.assertIn("SHA256SUMS.txt.sig", policy)
        self.assertIn("Production Russian signing is **not yet activated**", policy)

    def test_rel_008_remains_foundation_only(self):
        foundation = self.read("release/APL_REL_008_WINDOWS_CODE_SIGNING.md")
        self.assertIn("APL-REL-009", foundation)
        self.assertIn("provider-neutral Authenticode engineering foundation only", foundation)
        self.assertIn("qualified Rutoken certificate must not be assumed", foundation)


if __name__ == "__main__":
    unittest.main()
