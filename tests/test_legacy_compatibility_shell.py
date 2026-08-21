import ast
import inspect
import pathlib
import unittest

import application_filesystem
import configuration_storage
import local_proxy_transport
import portable_lifecycle
import process_supervision
import proxy_core as core
import proxy_core_legacy as legacy


ROOT = pathlib.Path(__file__).resolve().parents[1]
LEGACY_PATH = ROOT / "proxy_core_legacy.py"

CANONICAL_RUNTIME_OWNERS = {
    "application_filesystem",
    "application_runtime",
    "configuration_storage",
    "local_proxy_transport",
    "logging_bridge",
    "portable_lifecycle",
    "process_supervision",
    "recovery_autostart",
    "routing_policy",
    "system_proxy_runtime",
    "windows_pac_recovery",
    "windows_system_proxy",
}

DECOUPLED_CORE_STDLIB = ("re", "select", "struct")

DECOUPLED_OWNER_ATTRIBUTES = {
    "routing_policy.py": {"os", "io", "re"},
    "local_proxy_transport.py": {
        "base64",
        "re",
        "select",
        "socket",
        "struct",
        "threading",
    },
    "process_supervision.py": {
        "io",
        "json",
        "os",
        "socket",
        "subprocess",
        "sys",
    },
    "application_filesystem.py": {"io", "json", "os", "sys"},
    "configuration_storage.py": {
        "base64",
        "hashlib",
        "io",
        "json",
        "os",
        "threading",
        "time",
    },
    "portable_lifecycle.py": {"hashlib", "io", "os", "subprocess", "sys"},
}


def _exact_core_attributes(source: str) -> set[str]:
    tree = ast.parse(source)
    return {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "core"
    }


class LegacyCompatibilityShellTests(unittest.TestCase):
    def test_proxy_core_and_legacy_name_share_one_mutable_module_object(self):
        self.assertIs(core, legacy)
        self.assertTrue(str(core.__file__).endswith("proxy_core.py"))

    def test_legacy_source_contains_no_runtime_function_or_class_implementation(self):
        source = LEGACY_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        implementation_nodes = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda))
        ]
        self.assertEqual(implementation_nodes, [])
        self.assertLess(len(source.splitlines()), 100)

    def test_legacy_shell_retains_only_precomposition_identity_and_state_contract(self):
        self.assertEqual(core.APP_VERSION, "0.2.3")
        self.assertEqual(core.ENGINEERING_MILESTONE, "P0.2")
        self.assertEqual(core._INSTALL_OWNER_MARKER, ".arvectum-install-owner")
        self.assertEqual(core._INSTALL_OWNER_VALUE, "ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER")
        self.assertIn("ARVECTUM_PROXY_LAUNCHER_WINDOWS_RC2_1", core._LEGACY_INSTALL_OWNER_VALUES)
        self.assertEqual(core._LAUNCHER_EXE_NAME, "Arvectum Proxy Launcher.exe")
        self.assertEqual(core._USER_AUTOSTART_RUN_VALUE, "ArvectumProxyLauncher")
        self.assertIsInstance(core._STATE_READY, bool)
        self.assertIn("proxy_core.log", core._STATE_FILES)

    def test_decoupled_stdlib_modules_are_absent_from_core_namespace(self):
        for name in DECOUPLED_CORE_STDLIB:
            self.assertFalse(hasattr(core, name), name)

    def test_socket_is_retained_only_as_shared_monkeypatch_compatibility_alias(self):
        self.assertIs(core.socket, local_proxy_transport.socket)
        self.assertIs(core.socket, process_supervision.socket)
        for relative_path in ("local_proxy_transport.py", "process_supervision.py"):
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertNotIn("socket", _exact_core_attributes(source), relative_path)

    def test_state_bootstrap_stdlib_aliases_share_module_objects_but_are_not_looked_up_via_core(self):
        # Existing tests and external callers may patch these compatibility
        # aliases. Local imports intentionally resolve to the same Python module
        # objects, so those monkeypatches keep working without service-location.
        self.assertIs(core.os, application_filesystem.os)
        self.assertIs(core.io, application_filesystem.io)
        self.assertIs(core.sys, application_filesystem.sys)

        self.assertIs(core.base64, configuration_storage.base64)
        self.assertIs(core.hashlib, configuration_storage.hashlib)
        self.assertIs(core.io, configuration_storage.io)
        self.assertIs(core.json, configuration_storage.json)
        self.assertIs(core.os, configuration_storage.os)
        self.assertIs(core.threading, configuration_storage.threading)
        self.assertIs(core.time, configuration_storage.time)

        self.assertIs(core.hashlib, portable_lifecycle.hashlib)
        self.assertIs(core.io, portable_lifecycle.io)
        self.assertIs(core.os, portable_lifecycle.os)
        self.assertIs(core.subprocess, portable_lifecycle.subprocess)
        self.assertIs(core.sys, portable_lifecycle.sys)

    def test_removed_core_stdlib_names_are_unused_by_all_canonical_owners(self):
        for owner in CANONICAL_RUNTIME_OWNERS:
            source = (ROOT / (owner + ".py")).read_text(encoding="utf-8")
            exact_core_attributes = _exact_core_attributes(source)
            for name in DECOUPLED_CORE_STDLIB:
                self.assertNotIn(name, exact_core_attributes, "%s: core.%s" % (owner, name))

    def test_decoupled_owners_do_not_use_core_as_stdlib_service_locator(self):
        for relative_path, forbidden in DECOUPLED_OWNER_ATTRIBUTES.items():
            source = (ROOT / relative_path).read_text(encoding="utf-8")
            exact_core_attributes = _exact_core_attributes(source)
            for name in forbidden:
                self.assertNotIn(
                    name,
                    exact_core_attributes,
                    "%s: core.%s" % (relative_path, name),
                )

    def test_no_live_runtime_callable_is_owned_by_proxy_core_legacy(self):
        legacy_owned = sorted(
            name
            for name, value in vars(core).items()
            if callable(value) and getattr(value, "__module__", None) == "proxy_core_legacy"
        )
        self.assertEqual(legacy_owned, [])

    def test_every_live_project_runtime_callable_has_an_explicit_canonical_owner(self):
        unexpected = {}
        inventory = {}
        for name, value in vars(core).items():
            if not (inspect.isfunction(value) or inspect.isclass(value)):
                continue
            owner = getattr(value, "__module__", None)
            inventory[name] = owner
            if owner not in CANONICAL_RUNTIME_OWNERS:
                unexpected[name] = owner

        self.assertTrue(inventory)
        self.assertEqual(unexpected, {})

        # Representative public/mutation-sensitive seams from every bounded
        # extraction area prove that the inventory is observing composed core,
        # not merely an empty shell import.
        expected = {
            "install_dir": "application_filesystem",
            "ensure_stable_app_copy": "portable_lifecycle",
            "structured_log": "logging_bridge",
            "load_settings": "configuration_storage",
            "build_pac": "routing_policy",
            "ProxyCore": "local_proxy_transport",
            "is_running": "process_supervision",
            "classify_recovery_autostart": "recovery_autostart",
            "_read_internet_settings": "windows_system_proxy",
            "enable_system_proxy": "system_proxy_runtime",
            "clear_orphaned_arvectum_pac": "windows_pac_recovery",
            "main": "application_runtime",
        }
        for name, owner in expected.items():
            self.assertEqual(inventory.get(name), owner, name)


if __name__ == "__main__":
    unittest.main()
