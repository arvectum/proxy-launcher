import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CanonicalBranchPolicyTests(unittest.TestCase):
    def read(self, name: str) -> str:
        return (ROOT / name).read_text(encoding="utf-8-sig")

    def test_release_policy_declares_main_as_canonical_branch(self):
        policy = self.read("RELEASE_POLICY.md")
        self.assertIn("* **Canonical integration branch:** `main`.", policy)
        self.assertNotIn("* **Canonical integration branch:** `master`.", policy)
        self.assertIn("Release tags must point directly to a commit on `main` that has green CI status.", policy)
        self.assertIn("-> main\n  -> green CI", policy)

    def test_github_workflow_canonical_triggers_target_main(self):
        workflow = self.read(".github/workflows/windows-p0.yml")
        self.assertIn("- main", workflow)
        # Check that branch triggers include main and not master
        push_section = workflow.split("push:")[1].split("pull_request:")[0]
        pr_section = workflow.split("pull_request:")[1].split("workflow_dispatch:")[0]
        self.assertIn("- main", push_section)
        self.assertNotIn("- master", push_section)
        self.assertIn("- main", pr_section)
        self.assertNotIn("- master", pr_section)

    def test_gitverse_workflow_targets_main(self):
        gitverse = self.read(".gitverse/workflows/gitverse-ci.yaml")
        self.assertIn("для ветки main", gitverse)
        self.assertIn("- main", gitverse)
        self.assertNotIn("- master", gitverse)

    def test_security_policy_targets_main(self):
        security = self.read("SECURITY")
        self.assertIn("`main`", security)
        self.assertNotIn("`master`", security)


if __name__ == "__main__":
    unittest.main()
