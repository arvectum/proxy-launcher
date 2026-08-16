# -*- coding: utf-8 -*-
"""Windows GUI single-instance boundary for Arvectum Proxy Launcher.

The production GUI uses a session-local named mutex as a crash-safe process
sentinel and an auto-reset named event for duplicate-launch activation. The
module is deliberately independent of Tk so it can be tested without a desktop.
"""

import ctypes
import os


MUTEX_NAME = r"Local\Arvectum.ProxyLauncher.GUI.7D1327C3-7A2D-4D58-95B7-0B315E4AF008"
ACTIVATE_EVENT_NAME = r"Local\Arvectum.ProxyLauncher.GUI.Activate.7D1327C3-7A2D-4D58-95B7-0B315E4AF008"

ERROR_ALREADY_EXISTS = 183
WAIT_OBJECT_0 = 0x00000000
WAIT_TIMEOUT = 0x00000102
WAIT_FAILED = 0xFFFFFFFF
SW_RESTORE = 9


class _Win32KernelObjects:
    """Small ctypes adapter around the Win32 primitives used by the boundary."""

    def __init__(self):
        from ctypes import wintypes

        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)

        self.kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel32.CreateMutexW.restype = wintypes.HANDLE
        self.kernel32.CreateEventW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel32.CreateEventW.restype = wintypes.HANDLE
        self.kernel32.SetEvent.argtypes = [wintypes.HANDLE]
        self.kernel32.SetEvent.restype = wintypes.BOOL
        self.kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        self.kernel32.WaitForSingleObject.restype = wintypes.DWORD
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL

        self.user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        self.user32.FindWindowW.restype = wintypes.HWND
        self.user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self.user32.ShowWindow.restype = wintypes.BOOL
        self.user32.BringWindowToTop.argtypes = [wintypes.HWND]
        self.user32.BringWindowToTop.restype = wintypes.BOOL
        self.user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        self.user32.SetForegroundWindow.restype = wintypes.BOOL

    @staticmethod
    def _win_error():
        code = ctypes.get_last_error()
        return ctypes.WinError(code or 1)

    def create_mutex(self, name):
        ctypes.set_last_error(0)
        handle = self.kernel32.CreateMutexW(None, False, name)
        error = ctypes.get_last_error()
        if not handle:
            raise ctypes.WinError(error or 1)
        return handle, error == ERROR_ALREADY_EXISTS

    def create_event(self, name):
        handle = self.kernel32.CreateEventW(None, False, False, name)
        if not handle:
            raise self._win_error()
        return handle

    def set_event(self, handle):
        if not self.kernel32.SetEvent(handle):
            raise self._win_error()

    def event_signaled(self, handle):
        result = int(self.kernel32.WaitForSingleObject(handle, 0))
        if result == WAIT_OBJECT_0:
            return True
        if result == WAIT_TIMEOUT:
            return False
        if result == WAIT_FAILED:
            raise self._win_error()
        raise OSError("Unexpected WaitForSingleObject result: %s" % result)

    def close_handle(self, handle):
        if handle:
            self.kernel32.CloseHandle(handle)

    def activate_window(self, title):
        """Best-effort activation from the newly launched foreground process."""
        hwnd = self.user32.FindWindowW(None, title)
        if not hwnd:
            return False
        self.user32.ShowWindow(hwnd, SW_RESTORE)
        self.user32.BringWindowToTop(hwnd)
        self.user32.SetForegroundWindow(hwnd)
        return True


class WindowsSingleInstance:
    """Own the GUI mutex or notify the already-running GUI and exit."""

    def __init__(self, mutex_name=MUTEX_NAME, event_name=ACTIVATE_EVENT_NAME,
                 backend=None, platform=None):
        self.mutex_name = mutex_name
        self.event_name = event_name
        self._platform = os.name if platform is None else platform
        self._backend = backend
        self._mutex_handle = None
        self._event_handle = None
        self._acquired = False
        self._primary = False

    @property
    def primary(self):
        return self._primary

    def _get_backend(self):
        if self._backend is None:
            self._backend = _Win32KernelObjects()
        return self._backend

    def acquire(self):
        if self._acquired:
            return self._primary
        if self._platform != "nt":
            self._acquired = True
            self._primary = True
            return True

        backend = self._get_backend()
        mutex_handle = None
        event_handle = None
        try:
            mutex_handle, already_exists = backend.create_mutex(self.mutex_name)
            # Every instance opens the same auto-reset event. If a duplicate
            # arrives before the primary starts polling, the signal stays set
            # until the primary consumes it.
            event_handle = backend.create_event(self.event_name)
        except Exception:
            if event_handle is not None:
                backend.close_handle(event_handle)
            if mutex_handle is not None:
                backend.close_handle(mutex_handle)
            raise

        self._mutex_handle = mutex_handle
        self._event_handle = event_handle
        self._acquired = True
        self._primary = not already_exists
        return self._primary

    def notify_existing(self, window_title):
        if self._platform != "nt" or self._primary or not self._acquired:
            return False
        backend = self._get_backend()
        signaled = False
        activated = False
        if self._event_handle is not None:
            backend.set_event(self._event_handle)
            signaled = True
        try:
            activated = bool(backend.activate_window(window_title))
        except Exception:
            # The event is the canonical activation path. Native foregrounding
            # is intentionally best-effort because Windows may deny focus steal.
            activated = False
        return signaled or activated

    def poll_activation(self):
        if self._platform != "nt" or not self._primary or self._event_handle is None:
            return False
        return bool(self._get_backend().event_signaled(self._event_handle))

    def close(self):
        backend = self._backend
        if backend is not None:
            if self._event_handle is not None:
                backend.close_handle(self._event_handle)
            if self._mutex_handle is not None:
                backend.close_handle(self._mutex_handle)
        self._event_handle = None
        self._mutex_handle = None
        self._acquired = False
        self._primary = False
