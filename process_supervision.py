"""Canonical process supervision for Arvectum Proxy Launcher.

APL-IP-003 Slice 6 centralizes runtime-status and process-ownership supervision:
PAC health probing, listener diagnostics, Windows process identity checks, PID
record persistence, ownership-aware running-state evaluation, and safe process
termination.

The implementation is installed into the established mutable ``proxy_core``
module object. Collaborators are resolved dynamically through that compatibility
seam so the sealed Windows 0.2.3 behaviour and historical monkeypatch-based
regression tests remain stable. CLI orchestration and network recovery stay
outside this module for later bounded slices.
"""

from __future__ import annotations

from types import ModuleType

_CORE: ModuleType | None = None


def configure(core: ModuleType) -> None:
    """Bind the established core module used as the compatibility seam."""
    global _CORE
    _CORE = core


def _core() -> ModuleType:
    if _CORE is None:
        raise RuntimeError("process supervision is not configured")
    return _CORE


def _pac_healthy(settings=None):
    core = _core()
    settings = settings or core.load_settings()
    port = int(settings.get("local_pac_port", 8082))
    path = str(settings.get("pac_path", "/proxy.pac") or "/proxy.pac")
    if not path.startswith("/"):
        path = "/" + path
    try:
        sock = core.socket.create_connection(("127.0.0.1", port), timeout=1.0)
        request = (
            "GET %s HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n" % path
        ).encode("ascii")
        sock.sendall(request)
        data = b""
        while len(data) < 65536:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        sock.close()
        return (
            b"200 OK" in data
            and b"FindProxyForURL" in data
            and b"127.0.0.1:" in data
        )
    except Exception:
        return False


def proxy_listener_active():
    """Return whether a compatible PAC endpoint is active on localhost.

    Listener health deliberately does not establish instance ownership. Another
    Arvectum installation can expose the same endpoint; callers that require
    ownership must use :func:`is_running`.
    """
    core = _core()
    return core._pac_healthy(core.load_settings())


def _windows_process_creation_time(pid):
    core = _core()
    if not core.is_windows():
        return None
    try:
        import ctypes
        from ctypes import wintypes

        process_query_limited_information = 0x1000
        kernel32 = ctypes.windll.kernel32
        kernel32.OpenProcess.argtypes = [
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        ]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetProcessTimes.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME),
        ]
        kernel32.GetProcessTimes.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(
            process_query_limited_information, False, int(pid)
        )
        if not handle:
            return None
        try:
            creation = wintypes.FILETIME()
            exit_time = wintypes.FILETIME()
            kernel = wintypes.FILETIME()
            user = wintypes.FILETIME()
            if not kernel32.GetProcessTimes(
                handle,
                ctypes.byref(creation),
                ctypes.byref(exit_time),
                ctypes.byref(kernel),
                ctypes.byref(user),
            ):
                return None
            return (
                int(creation.dwHighDateTime) << 32
            ) | int(creation.dwLowDateTime)
        finally:
            kernel32.CloseHandle(handle)
    except Exception as exc:
        core._log("process creation time error: %r" % exc)
        return None


def _windows_process_executable_path(pid):
    core = _core()
    if not core.is_windows():
        return None
    try:
        import ctypes
        from ctypes import wintypes

        process_query_limited_information = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information, False, int(pid)
        )
        if not handle:
            return None
        try:
            size = wintypes.DWORD(32768)
            buffer = ctypes.create_unicode_buffer(size.value)
            if not ctypes.windll.kernel32.QueryFullProcessImageNameW(
                handle, 0, buffer, ctypes.byref(size)
            ):
                return None
            return core.os.path.realpath(buffer.value)
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        return None


def _read_pid():
    core = _core()
    try:
        with core.io.open(core.pid_path(), "r", encoding="utf-8") as stream:
            raw = stream.read().strip()
        try:
            data = core.json.loads(raw)
        except Exception:
            data = None
        if isinstance(data, dict) and data.get("pid"):
            return {
                "pid": int(data["pid"]),
                "created": data.get("created"),
                "exe_path": data.get("exe_path"),
                "identity": data.get("identity"),
            }
        # Historical PID-only records are intentionally treated as unverified:
        # they cannot safely authorize taskkill after reboot/PID reuse.
        return {"pid": int(raw), "created": None}
    except Exception:
        return None


def is_running():
    """Return True only for the proxy process owned by this app instance."""
    core = _core()
    if not core.proxy_listener_active():
        return False
    if not core.is_windows():
        return True
    record = core._read_pid()
    if (
        not isinstance(record, dict)
        or not record.get("pid")
        or record.get("created") is None
    ):
        return False
    actual = core._windows_process_creation_time(int(record["pid"]))
    if actual is None or int(actual) != int(record["created"]):
        return False
    recorded_path = record.get("exe_path")
    actual_path = core._windows_process_executable_path(int(record["pid"]))
    return bool(
        recorded_path
        and actual_path
        and core.os.path.normcase(core.os.path.realpath(recorded_path))
        == core.os.path.normcase(core.os.path.realpath(actual_path))
    )


def _write_pid():
    core = _core()
    try:
        pid = core.os.getpid()
        record = {
            "pid": pid,
            "created": core._windows_process_creation_time(pid),
            "exe_path": core.os.path.realpath(core.sys.executable),
            "identity": core.os.path.normcase(
                core.os.path.realpath(core.install_dir())
            ),
        }
        with core.io.open(core.pid_path(), "w", encoding="utf-8") as stream:
            core.json.dump(record, stream)
    except Exception as exc:
        core._log("pid write error: %r" % exc)


def _remove_pid():
    core = _core()
    try:
        core.os.remove(core.pid_path())
    except Exception:
        pass


def _kill_pid(record):
    core = _core()
    if not record:
        return False
    pid = int(record.get("pid")) if isinstance(record, dict) else int(record)
    expected_created = record.get("created") if isinstance(record, dict) else None
    try:
        if core.is_windows():
            actual_created = core._windows_process_creation_time(pid)
            if (
                expected_created is None
                or actual_created is None
                or int(expected_created) != int(actual_created)
            ):
                core._log(
                    "refusing unsafe taskkill for pid=%s: "
                    "process identity mismatch/unverified" % pid
                )
                return False
            result = core.subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                text=True,
                creationflags=getattr(core.subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode != 0:
                core._log(
                    "taskkill failed for pid=%s: %s"
                    % (pid, (result.stderr or result.stdout).strip())
                )
                return False
            return True
        core.os.kill(pid, 9)
        return True
    except Exception as exc:
        core._log("kill pid error (%s): %r" % (pid, exc))
        return False


def install_into_core(core: ModuleType) -> None:
    """Install canonical process-supervision seams into the core module."""
    configure(core)
    for name in (
        "_pac_healthy",
        "proxy_listener_active",
        "_windows_process_creation_time",
        "_windows_process_executable_path",
        "_read_pid",
        "is_running",
        "_write_pid",
        "_remove_pid",
        "_kill_pid",
    ):
        setattr(core, name, globals()[name])
