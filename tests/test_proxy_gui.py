import unittest
from unittest import mock

import proxy_gui as gui


class _BoolVar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class AutostartOwnershipTests(unittest.TestCase):
    def test_foreign_task_conflict_resets_checkbox(self):
        launcher = gui.Launcher.__new__(gui.Launcher)
        launcher.auto_var = _BoolVar(True)
        launcher._autostart_task_xml = mock.Mock(return_value="foreign task xml")
        launcher._autostart_task_is_ours = mock.Mock(return_value=False)

        with mock.patch.object(gui.messagebox, "showerror"):
            launcher._toggle_autostart()

        self.assertFalse(launcher.auto_var.get())


if __name__ == "__main__":
    unittest.main()
