import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROVENANCE = (ROOT / 'IP_PROVENANCE.md').read_text(encoding='utf-8')
SCRIPT = (ROOT / 'tools' / 'ip_provenance_check.py').read_text(encoding='utf-8')
NOTICES = (ROOT / 'THIRD_PARTY_NOTICES.txt').read_text(encoding='utf-8')

class IpProvenanceContractTests(unittest.TestCase):
    def test_automated_evidence_never_claims_legal_signoff(self):
        self.assertIn('HUMAN-LEGAL SIGN-OFF PENDING', PROVENANCE)
        self.assertIn('human_review_required', SCRIPT)
        self.assertIn('legal_signoff_required', SCRIPT)
        self.assertIn('Git history must not be rewritten', PROVENANCE)
    def test_manifest_hashes_governed_source(self):
        self.assertIn('git", "ls-files', SCRIPT)
        self.assertIn('sha256', SCRIPT)
        self.assertIn('review_findings', SCRIPT)
    def test_third_party_boundaries_cover_all_platform_artifacts(self):
        for token in ('Python', 'Tcl/Tk', 'PyInstaller', 'AppImage type-2 runtime', 'Inno Setup', 'NetworkManager/PolicyKit'):
            self.assertIn(token, NOTICES)
    def test_clean_tag_remains_blocked_until_human_review(self):
        self.assertIn('Clean IP baseline/tag', PROVENANCE)
        self.assertIn('BLOCKED', PROVENANCE)

if __name__ == '__main__': unittest.main()
