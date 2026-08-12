import socket
import tempfile
from pathlib import Path
import threading
import unittest
from unittest import mock

import proxy_core as core


def _listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    s.listen(5)
    return s, s.getsockname()[1]


def _recv_all(sock, timeout=3):
    sock.settimeout(timeout)
    out = b""
    while True:
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            break
        if not chunk:
            break
        out += chunk
    return out


class ProxyCoreTests(unittest.TestCase):
    def test_no_proxy_matching_is_boundary_safe(self):
        with mock.patch.object(core, "load_no_proxy", return_value=["zakupki.gov.ru", "10.*"]):
            self.assertTrue(core.host_bypasses_proxy("zakupki.gov.ru"))
            self.assertTrue(core.host_bypasses_proxy("sub.zakupki.gov.ru"))
            self.assertFalse(core.host_bypasses_proxy("evilzakupki.gov.ru"))
            self.assertTrue(core.host_bypasses_proxy("10.2.3.4"))
            self.assertFalse(core.host_bypasses_proxy("11.2.3.4"))
            self.assertTrue(core.host_bypasses_proxy("[::1]"))

    def test_pac_url_honors_custom_path(self):
        self.assertEqual(
            core.pac_url({"local_pac_port": 9123, "pac_path": "custom.pac"}),
            "http://127.0.0.1:9123/custom.pac",
        )

    def test_start_without_upstream_never_touches_system_proxy(self):
        settings = dict(core.DEFAULT_SETTINGS)
        settings["upstream"] = [{"host": "", "port": 8000, "username": "", "password": ""}]
        with mock.patch.object(core, "load_settings", return_value=settings), \
             mock.patch.object(core, "enable_system_proxy") as enable, \
             mock.patch("builtins.print"):
            self.assertEqual(core._cmd_start(), 2)
            enable.assert_not_called()

    def test_excluded_http_host_goes_direct_even_when_client_uses_local_http_proxy(self):
        destination, dest_port = _listener()
        upstream, upstream_port = _listener()
        upstream_hit = threading.Event()
        destination_request = []

        def destination_worker():
            conn, _ = destination.accept()
            destination_request.append(conn.recv(8192))
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nDIRECT")
            conn.close()
            destination.close()

        def upstream_worker():
            upstream.settimeout(1.5)
            try:
                conn, _ = upstream.accept()
            except socket.timeout:
                upstream.close()
                return
            upstream_hit.set()
            conn.close()
            upstream.close()

        threading.Thread(target=destination_worker, daemon=True).start()
        threading.Thread(target=upstream_worker, daemon=True).start()

        settings = dict(core.DEFAULT_SETTINGS)
        settings["upstream"] = [{"host": "127.0.0.1", "port": upstream_port, "username": "u", "password": "p"}]
        engine = core.ProxyCore(settings)
        client_side, proxy_side = socket.socketpair()

        original_create_connection = socket.create_connection

        def route_fake_host(address, *args, **kwargs):
            host, port = address
            if host == "excluded.test":
                return original_create_connection(("127.0.0.1", dest_port), *args, **kwargs)
            return original_create_connection(address, *args, **kwargs)

        with mock.patch.object(core, "load_no_proxy", return_value=["excluded.test"]), \
             mock.patch.object(core.socket, "create_connection", side_effect=route_fake_host):
            t = threading.Thread(target=engine._handle_http, args=(proxy_side,), daemon=True)
            t.start()
            client_side.sendall(
                ("GET http://excluded.test:%d/hello HTTP/1.1\r\nHost: excluded.test:%d\r\nConnection: close\r\n\r\n" % (dest_port, dest_port)).encode()
            )
            response = _recv_all(client_side)
            client_side.close()
            t.join(2)

        self.assertIn(b"DIRECT", response)
        self.assertFalse(upstream_hit.is_set(), "excluded host unexpectedly reached upstream proxy")
        self.assertTrue(destination_request)
        self.assertTrue(destination_request[0].startswith(b"GET /hello HTTP/1.1"))


    def test_excluded_connect_host_goes_direct_even_when_client_uses_local_http_proxy(self):
        destination, dest_port = _listener()
        upstream, upstream_port = _listener()
        upstream_hit = threading.Event()

        def destination_worker():
            conn, _ = destination.accept()
            data = conn.recv(16)
            conn.sendall(b"PONG:" + data)
            conn.close()
            destination.close()

        def upstream_worker():
            upstream.settimeout(1.5)
            try:
                conn, _ = upstream.accept()
            except socket.timeout:
                upstream.close()
                return
            upstream_hit.set()
            conn.close()
            upstream.close()

        threading.Thread(target=destination_worker, daemon=True).start()
        threading.Thread(target=upstream_worker, daemon=True).start()

        settings = dict(core.DEFAULT_SETTINGS)
        settings["upstream"] = [{"host": "127.0.0.1", "port": upstream_port, "username": "u", "password": "p"}]
        engine = core.ProxyCore(settings)
        client_side, proxy_side = socket.socketpair()
        original_create_connection = socket.create_connection

        def route_fake_host(address, *args, **kwargs):
            host, port = address
            if host == "excluded.test":
                return original_create_connection(("127.0.0.1", dest_port), *args, **kwargs)
            return original_create_connection(address, *args, **kwargs)

        with mock.patch.object(core, "load_no_proxy", return_value=["excluded.test"]), \
             mock.patch.object(core.socket, "create_connection", side_effect=route_fake_host):
            t = threading.Thread(target=engine._handle_http, args=(proxy_side,), daemon=True)
            t.start()
            client_side.sendall(("CONNECT excluded.test:%d HTTP/1.1\r\nHost: excluded.test:%d\r\n\r\n" % (dest_port, dest_port)).encode())
            client_side.settimeout(2)
            response = client_side.recv(4096)
            self.assertIn(b"200 Connection Established", response)
            client_side.sendall(b"PING")
            tunnel = client_side.recv(4096)
            client_side.close()
            t.join(2)

        self.assertIn(b"PONG:PING", tunnel)
        self.assertFalse(upstream_hit.is_set(), "excluded CONNECT unexpectedly reached upstream proxy")

    def test_excluded_socks_host_goes_direct_without_upstream(self):
        destination, dest_port = _listener()
        upstream, upstream_port = _listener()
        upstream_hit = threading.Event()

        def destination_worker():
            conn, _ = destination.accept()
            data = conn.recv(16)
            conn.sendall(b"SOCKS:" + data)
            conn.close()
            destination.close()

        def upstream_worker():
            upstream.settimeout(1.5)
            try:
                conn, _ = upstream.accept()
            except socket.timeout:
                upstream.close()
                return
            upstream_hit.set()
            conn.close()
            upstream.close()

        threading.Thread(target=destination_worker, daemon=True).start()
        threading.Thread(target=upstream_worker, daemon=True).start()

        settings = dict(core.DEFAULT_SETTINGS)
        settings["upstream"] = [{"host": "127.0.0.1", "port": upstream_port, "username": "u", "password": "p"}]
        engine = core.ProxyCore(settings)
        client_side, proxy_side = socket.socketpair()
        original_create_connection = socket.create_connection

        def route_fake_host(address, *args, **kwargs):
            host, port = address
            if host == "excluded.test":
                return original_create_connection(("127.0.0.1", dest_port), *args, **kwargs)
            return original_create_connection(address, *args, **kwargs)

        with mock.patch.object(core, "load_no_proxy", return_value=["excluded.test"]), \
             mock.patch.object(core.socket, "create_connection", side_effect=route_fake_host):
            t = threading.Thread(target=engine._handle_socks, args=(proxy_side,), daemon=True)
            t.start()
            client_side.settimeout(2)
            client_side.sendall(b"\x05\x01\x00")
            self.assertEqual(client_side.recv(2), b"\x05\x00")
            host = b"excluded.test"
            client_side.sendall(b"\x05\x01\x00\x03" + bytes([len(host)]) + host + dest_port.to_bytes(2, "big"))
            reply = client_side.recv(10)
            self.assertGreaterEqual(len(reply), 2)
            self.assertEqual(reply[:2], b"\x05\x00")
            client_side.sendall(b"PING")
            tunnel = client_side.recv(4096)
            client_side.close()
            t.join(2)

        self.assertIn(b"SOCKS:PING", tunnel)
        self.assertFalse(upstream_hit.is_set(), "excluded SOCKS host unexpectedly reached upstream proxy")

    def test_cmd_stop_fails_when_network_restore_is_incomplete(self):
        with mock.patch.object(core, "_read_pid", return_value=None), \
             mock.patch.object(core, "_kill_pid", return_value=False), \
             mock.patch.object(core, "is_running", return_value=False), \
             mock.patch.object(core, "disable_system_proxy", return_value=False), \
             mock.patch.object(core, "network_restore_pending", return_value=True), \
             mock.patch("builtins.print"):
            self.assertEqual(core._cmd_stop(), 1)

    def test_cmd_rollback_fails_when_network_restore_is_incomplete(self):
        with mock.patch.object(core, "_read_pid", return_value=None), \
             mock.patch.object(core, "_kill_pid", return_value=False), \
             mock.patch.object(core, "is_running", return_value=False), \
             mock.patch.object(core, "disable_system_proxy", return_value=False), \
             mock.patch.object(core, "network_restore_pending", return_value=True), \
             mock.patch("builtins.print"):
            self.assertEqual(core._cmd_rollback(), 1)

    def test_sync_client_no_proxy_removes_old_arvectum_entry_but_preserves_user_value(self):
        with tempfile.TemporaryDirectory() as td:
            backup_path = str(Path(td) / "proxy_env_backup.json")
            backup = {
                "HTTP_PROXY": {"exists": False, "value": None},
                "HTTPS_PROXY": {"exists": False, "value": None},
                "ALL_PROXY": {"exists": False, "value": None},
                "NO_PROXY": {"exists": True, "value": "user.example"},
            }
            Path(backup_path).write_text(__import__("json").dumps(backup), encoding="utf-8")
            writes = {}

            def write_env(name, value):
                writes[name] = value
                return True

            with mock.patch.object(core, "is_windows", return_value=True), \
                 mock.patch.object(core, "_env_backup_path", return_value=backup_path), \
                 mock.patch.object(core, "load_no_proxy", return_value=["current.example"]), \
                 mock.patch.object(core, "_write_user_env", side_effect=write_env), \
                 mock.patch.object(core, "_broadcast_environment_change"):
                self.assertTrue(core.sync_client_no_proxy())

            value = writes["NO_PROXY"]
            self.assertIn("user.example", value)
            self.assertIn("current.example", value)
            self.assertNotIn("removed.example", value)

    def test_network_restore_pending_detects_backup_files(self):
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "system_proxy_enabled", return_value=False), \
             mock.patch.object(core.os.path, "exists", side_effect=[True, False]):
            self.assertTrue(core.network_restore_pending())

    def test_nonexcluded_http_host_uses_upstream_and_adds_auth(self):
        upstream, upstream_port = _listener()
        received = []

        def upstream_worker():
            conn, _ = upstream.accept()
            received.append(conn.recv(8192))
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 8\r\nConnection: close\r\n\r\nUPSTREAM")
            conn.close()
            upstream.close()

        threading.Thread(target=upstream_worker, daemon=True).start()
        settings = dict(core.DEFAULT_SETTINGS)
        settings["upstream"] = [{"host": "127.0.0.1", "port": upstream_port, "username": "user", "password": "pass"}]
        engine = core.ProxyCore(settings)
        client_side, proxy_side = socket.socketpair()

        with mock.patch.object(core, "load_no_proxy", return_value=[]):
            t = threading.Thread(target=engine._handle_http, args=(proxy_side,), daemon=True)
            t.start()
            client_side.sendall(b"GET http://example.test/path HTTP/1.1\r\nHost: example.test\r\nConnection: close\r\n\r\n")
            response = _recv_all(client_side)
            client_side.close()
            t.join(2)

        self.assertIn(b"UPSTREAM", response)
        self.assertTrue(received)
        self.assertIn(b"Proxy-Authorization: Basic dXNlcjpwYXNz", received[0])

    def test_pac_server_health_check_identifies_our_process(self):
        listeners = []
        ports = []
        for _ in range(3):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("127.0.0.1", 0))
            ports.append(sock.getsockname()[1])
            sock.close()
        settings = {
            "local_http_port": ports[0],
            "local_socks_port": ports[1],
            "local_pac_port": ports[2],
            "pac_path": "/proxy.pac",
            "upstream": [],
        }
        engine = core.ProxyCore(settings)
        ok, msg = engine.start()
        self.assertTrue(ok, msg)
        try:
            self.assertTrue(core._pac_healthy(settings))
        finally:
            engine.stop()
        self.assertFalse(core._pac_healthy(settings))

    def test_unverified_stale_windows_pid_is_never_taskkilled(self):
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_windows_process_creation_time", return_value=123), \
             mock.patch.object(core.subprocess, "run") as run:
            self.assertFalse(core._kill_pid({"pid": 9999, "created": None}))
            run.assert_not_called()

    def test_mismatched_windows_process_creation_time_is_never_taskkilled(self):
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_windows_process_creation_time", return_value=456), \
             mock.patch.object(core.subprocess, "run") as run:
            self.assertFalse(core._kill_pid({"pid": 9999, "created": 123}))
            run.assert_not_called()

    def test_owns_running_proxy_requires_matching_pid_identity(self):
        with mock.patch.object(core, "_read_pid", return_value={"pid": 9999, "created": 123}), \
             mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_windows_process_creation_time", return_value=123), \
             mock.patch.object(core, "_pac_healthy", return_value=True):
            self.assertTrue(core.owns_running_proxy())

        with mock.patch.object(core, "_read_pid", return_value={"pid": 9999, "created": 123}), \
             mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "_windows_process_creation_time", return_value=456), \
             mock.patch.object(core, "_pac_healthy", return_value=True):
            self.assertFalse(core.owns_running_proxy())

    def test_rollback_without_backup_does_not_disable_foreign_manual_proxy(self):
        foreign = {
            "AutoConfigURL": {"exists": False, "value": None},
            "ProxyEnable": {"exists": True, "value": 1},
            "ProxyServer": {"exists": True, "value": "corp.proxy:3128"},
            "ProxyOverride": {"exists": True, "value": "<local>;intranet"},
            "AutoDetect": {"exists": True, "value": 1},
        }
        with mock.patch.object(core, "_internet_backup_path", return_value="/definitely/missing/arvectum-backup.json"), \
             mock.patch.object(core, "_read_internet_settings", return_value=foreign), \
             mock.patch.object(core, "_reg_set") as reg_set, \
             mock.patch.object(core, "_reg_del") as reg_del:
            self.assertTrue(core._restore_internet_backup())
            reg_set.assert_not_called()
            reg_del.assert_not_called()

    def test_rollback_without_backup_removes_only_owned_pac(self):
        settings = dict(core.DEFAULT_SETTINGS)
        owned = core.pac_url(settings)
        current = {
            "AutoConfigURL": {"exists": True, "value": owned},
            "ProxyEnable": {"exists": True, "value": 0},
            "ProxyServer": {"exists": True, "value": "corp.proxy:3128"},
            "ProxyOverride": {"exists": True, "value": "<local>;intranet"},
            "AutoDetect": {"exists": True, "value": 1},
        }
        with mock.patch.object(core, "_internet_backup_path", return_value="/definitely/missing/arvectum-backup.json"), \
             mock.patch.object(core, "load_settings", return_value=settings), \
             mock.patch.object(core, "_read_internet_settings", return_value=current), \
             mock.patch.object(core, "_reg_set") as reg_set, \
             mock.patch.object(core, "_reg_del", return_value=True) as reg_del:
            self.assertFalse(core._restore_internet_backup())
            reg_del.assert_called_once_with("AutoConfigURL")
            reg_set.assert_not_called()

    def test_foreign_running_proxy_without_backup_cannot_be_rolled_back(self):
        with mock.patch.object(core, "is_windows", return_value=True), \
             mock.patch.object(core, "is_running", return_value=True), \
             mock.patch.object(core, "owns_running_proxy", return_value=False), \
             mock.patch.object(core, "has_network_backup", return_value=False), \
             mock.patch.object(core, "_restore_internet_backup") as restore:
            self.assertFalse(core.disable_system_proxy())
            restore.assert_not_called()

    def test_restore_internet_backup_restores_proxy_override_exactly(self):
        backup = {
            "AutoConfigURL": {"exists": False, "value": None},
            "ProxyEnable": {"exists": True, "value": 1},
            "ProxyServer": {"exists": True, "value": "corp.proxy:3128"},
            "ProxyOverride": {"exists": True, "value": "<local>;*.internal"},
            "AutoDetect": {"exists": False, "value": None},
        }
        with tempfile.TemporaryDirectory() as td:
            backup_path = str(Path(td) / "proxy_internet_backup.json")
            Path(backup_path).write_text(__import__("json").dumps(backup), encoding="utf-8")
            with mock.patch.object(core, "_internet_backup_path", return_value=backup_path), \
                 mock.patch.object(core, "_reg_set", return_value=True) as reg_set, \
                 mock.patch.object(core, "_reg_del", return_value=True) as reg_del:
                self.assertTrue(core._restore_internet_backup())

        reg_set.assert_has_calls([
            mock.call("ProxyEnable", "1", "REG_DWORD"),
            mock.call("ProxyServer", "corp.proxy:3128", "REG_SZ"),
            mock.call("ProxyOverride", "<local>;*.internal", "REG_SZ"),
        ], any_order=True)
        reg_del.assert_has_calls([
            mock.call("AutoConfigURL"),
            mock.call("AutoDetect"),
        ], any_order=True)


if __name__ == "__main__":
    unittest.main()
