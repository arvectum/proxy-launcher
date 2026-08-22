import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]

MAINTAINED_CANONICAL_SOURCES = (
    "proxy_core.py",
    "application_filesystem.py",
    "portable_lifecycle.py",
    "configuration_storage.py",
    "routing_policy.py",
    "local_proxy_transport.py",
    "process_supervision.py",
    "application_runtime.py",
    "windows_system_proxy.py",
    "recovery_autostart.py",
    "windows_pac_recovery.py",
    "logging_bridge.py",
    "system_proxy_runtime.py",
)

OBSOLETE_MIGRATION_LANGUAGE = (
    "APL-IP-003",
    "proxy_core_legacy",
    "outside this slice",
    "later bounded",
    "extracted independently later",
)


class MaintainedSourceHygieneTests(unittest.TestCase):
    def test_canonical_sources_describe_current_architecture_not_refactor_history(self):
        violations = {}
        for relative in MAINTAINED_CANONICAL_SOURCES:
            source = (ROOT / relative).read_text(encoding="utf-8")
            lowered = source.lower()
            found = [
                token
                for token in OBSOLETE_MIGRATION_LANGUAGE
                if token.lower() in lowered
            ]
            if found:
                violations[relative] = found
        self.assertEqual(violations, {})

    def test_canonical_sources_have_current_ownership_docstrings(self):
        invalid = {}
        for relative in MAINTAINED_CANONICAL_SOURCES:
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            doc = ast.get_docstring(tree, clean=True) or ""
            if not doc.startswith("Canonical "):
                invalid[relative] = doc.splitlines()[0] if doc else "<missing>"
        self.assertEqual(invalid, {})

    def test_configured_owners_use_one_composition_binding_term(self):
        invalid = {}
        for relative in MAINTAINED_CANONICAL_SOURCES:
            if relative == "proxy_core.py":
                continue
            tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
            configure = next(
                (
                    node
                    for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == "configure"
                ),
                None,
            )
            if configure is None:
                invalid[relative] = "<missing configure>"
                continue
            doc = ast.get_docstring(configure, clean=True) or ""
            if not doc.startswith("Bind the canonical composition module"):
                invalid[relative] = doc
        self.assertEqual(invalid, {})


if __name__ == "__main__":
    unittest.main()
