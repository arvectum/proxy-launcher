import ast
import io
import pathlib
import re
import tokenize
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TASK_ID_RE = re.compile(r"\bAPL-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+\b")
SLICE_HISTORY_RE = re.compile(r"\bSlice\s+\d+\b", re.IGNORECASE)
GUI_ENTRY_POINTS = (
    ROOT / "proxy_gui.py",
    ROOT / "linux_gui.py",
)
CONCRETE_BACKEND_MODULES = {
    "windows_backend",
    "linux_backend",
    "macos_backend",
    "windows_system_proxy",
    "windows_pac_recovery",
    "system_proxy_runtime",
}
STALE_BOUNDARY_IDENTIFIERS = {
    "legacy" + "_core",
    "_resolved_" + "legacy_config",
    "_config_matches_" + "legacy_runtime",
}


def _production_python_files():
    paths = set(ROOT.glob("*.py"))
    for directory in ("core", "diagnostics"):
        base = ROOT / directory
        if base.exists():
            paths.update(base.rglob("*.py"))
    return sorted(paths)


def _narrative_history_markers(path):
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    hits = set()

    def collect(text):
        hits.update(TASK_ID_RE.findall(text))
        hits.update(SLICE_HISTORY_RE.findall(text))

    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node, clean=False)
            if docstring:
                collect(docstring)

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            collect(token.string)

    return sorted(hits)


def _imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".", 1)[0])
    return modules


def _stale_identifier_consumers():
    consumers = {}
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts or path == pathlib.Path(__file__).resolve():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        except (UnicodeDecodeError, SyntaxError):
            continue
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in STALE_BOUNDARY_IDENTIFIERS:
                    found.add(node.name)
            elif isinstance(node, ast.arg) and node.arg in STALE_BOUNDARY_IDENTIFIERS:
                found.add(node.arg)
            elif isinstance(node, ast.Name) and node.id in STALE_BOUNDARY_IDENTIFIERS:
                found.add(node.id)
            elif isinstance(node, ast.Attribute) and node.attr in STALE_BOUNDARY_IDENTIFIERS:
                found.add(node.attr)
            elif isinstance(node, ast.keyword) and node.arg in STALE_BOUNDARY_IDENTIFIERS:
                found.add(node.arg)
        if found:
            consumers[path.relative_to(ROOT).as_posix()] = sorted(found)
    return consumers


class ApplicationBoundaryHygieneTests(unittest.TestCase):
    def test_production_narrative_does_not_encode_engineering_task_history(self):
        violations = {}
        for path in _production_python_files():
            hits = _narrative_history_markers(path)
            if hits:
                violations[path.relative_to(ROOT).as_posix()] = hits
        if violations:
            self.fail(repr(violations))

    def test_gui_entry_points_do_not_import_concrete_backend_implementations(self):
        violations = {}
        for path in GUI_ENTRY_POINTS:
            imported = _imported_modules(path)
            forbidden = sorted(imported & CONCRETE_BACKEND_MODULES)
            if forbidden:
                violations[path.relative_to(ROOT).as_posix()] = forbidden
        self.assertEqual(violations, {})

    def test_backend_runtime_owns_concrete_backend_selection(self):
        source = (ROOT / "backend_runtime.py").read_text(encoding="utf-8")
        for class_name in ("WindowsBackend", "LinuxBackend", "MacOSBackend"):
            self.assertIn(class_name, source)
        self.assertIn("create_backend", source)
        self.assertIn("require_enable_operational", source)

    def test_stale_boundary_identifiers_have_no_live_python_consumers(self):
        consumers = _stale_identifier_consumers()
        if consumers:
            self.fail(repr(consumers))


if __name__ == "__main__":
    unittest.main()
