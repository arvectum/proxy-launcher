import unittest
from unittest import mock

import proxy_gui as gui
import windows_single_instance as single


class _Backend:
    def __init__(self, mutex_exists=False):
        self.mutex_exists = mutex_exists
        self.created_mutex_names = []
        self.created_event_names = []
        self.set_events = []
        self.closed = []
        self.activation_titles = []
        self.poll_values = []

    def create_mutex(self, name):
        self.created_mutex_names.append(name)
        return "mutex-handle", self.mutex_exists

    def create_event(self, name):
        self.created_event_names.append(name)
        return "event-handle"

    def set_event(self, handle):
        self.set_events.append(handle)

    def event_signaled(self, handle):
        if self.poll_values:
            return self.poll_values.pop(0)
        return False

    def close_handle(self, handle):
        self.closed.append(handle)

    def activate_window(self, title):
        self.activation_titles.append(title)
        return True


class WindowsSingleInstanceTests(unittest.TestCase):
    def test_non_windows_is_noop_primary(self):
        instance = single.WindowsSingleInstance(platform="posix")
        self.assertTrue(instance.acquire())
        self.assertTrue(instance.primary)
        self.assertFalse(instance.poll_activation())
        self.assertFalse(instance.notify_existing(gui.APP_NAME))

    def test_first_windows_instance_owns_named_boundary(self):
        backend = _Backend(mutex_exists=False)
        instance = single.WindowsSingleInstance(backend=backend, platform="nt")

        self.assertTrue(instance.acquire())
        self.assertTrue(instance.primary)
        self.assertEqual(backend.created_mutex_names, [single.MUTEX_NAME])
        self.assertEqual(backend.created_event_names, [single.ACTIVATE_EVENT_NAME])
        self.assertEqual(backend.set_events, [])

    def test_duplicate_signals_primary_and_attempts_foreground(self):
        backend = _Backend(mutex_exists=True)
        instance = single.WindowsSingleInstance(backend=backend, platform="nt")

        self.assertFalse(instance.acquire())
        self.assertFalse(instance.primary)
        self.assertTrue(instance.notify_existing(gui.APP_NAME))
        self.assertEqual(backend.set_events, ["event-handle"])
        self.assertEqual(backend.activation_titles, [gui.APP_NAME])

    def test_primary_consumes_activation_requests_without_blocking(self):
        backend = _Backend(mutex_exists=False)
        backend.poll_values = [True, False]
        instance = single.WindowsSingleInstance(backend=backend, platform="nt")
        self.assertTrue(instance.acquire())
        self.assertTrue(instance.poll_activation())
        self.assertFalse(instance.poll_activation())

    def test_close_is_idempotent_and_releases_event_then_mutex(self):
        backend = _Backend(mutex_exists=False)
        instance = single.WindowsSingleInstance(backend=backend, platform="nt")
        instance.acquire()
        instance.close()
        instance.close()
        self.assertEqual(backend.closed, ["event-handle", "mutex-handle"])
        self.assertFalse(instance.primary)

    def test_event_creation_failure_releases_mutex(self):
        backend = _Backend(mutex_exists=False)
        backend.create_event = mock.Mock(side_effect=OSError("event denied"))
        instance = single.WindowsSingleInstance(backend=backend, platform="nt")
        with self.assertRaises(OSError):
            instance.acquire()
        self.assertEqual(backend.closed, ["mutex-handle"])


class DuplicateLaunchIntegrationTests(unittest.TestCase):
    def test_duplicate_gui_exits_before_local_or_network_side_effects(self):
        instance = mock.Mock()
        instance.acquire.return_value = False
        with mock.patch.object(gui.sys, "argv", ["proxy_gui.py"]), \
             mock.patch.object(gui.core, "handoff_to_stable_copy", return_value=False), \
             mock.patch.object(gui.core, "self_heal_error", return_value=None), \
             mock.patch.object(gui, "_portable_fallback_active", return_value=False), \
             mock.patch.object(gui.single_instance_module, "WindowsSingleInstance", return_value=instance), \
             mock.patch.object(gui.core, "_ensure_local_files") as ensure_files, \
             mock.patch.object(gui.core, "repair_portable_run_entries") as repair_runs, \
             mock.patch.object(gui.tk, "Tk") as tk_root:
            self.assertEqual(gui.main(), 0)

        instance.notify_existing.assert_called_once_with(gui.APP_NAME)
        instance.close.assert_called_once()
        ensure_files.assert_not_called()
        repair_runs.assert_not_called()
        tk_root.assert_not_called()

    def test_headless_service_command_bypasses_gui_mutex(self):
        with mock.patch.object(gui.sys, "argv", ["proxy_gui.py", "--status"]), \
             mock.patch.object(gui.core, "handoff_to_stable_copy", return_value=False), \
             mock.patch.object(gui.core, "self_heal_error", return_value=None), \
             mock.patch.object(gui, "_portable_fallback_active", return_value=False), \
             mock.patch.object(gui.core, "main", return_value=0) as core_main, \
             mock.patch.object(gui.single_instance_module, "WindowsSingleInstance") as boundary:
            self.assertEqual(gui.main(), 0)
        core_main.assert_called_once_with()
        boundary.assert_not_called()

    def test_activation_poll_restores_existing_tk_window(self):
        root = mock.Mock()
        instance = mock.Mock()
        instance.poll_activation.return_value = True
        with mock.patch.object(gui, "_activate_main_window") as activate:
            gui._poll_single_instance_activation(root, instance)
        activate.assert_called_once_with(root)
        root.after.assert_called_once()


if __name__ == "__main__":
    unittest.main()
