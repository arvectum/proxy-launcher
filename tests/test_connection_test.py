import unittest
from unittest import mock
import urllib.error

import connection_test as ct


class _FakeResponse:
    def __init__(self, code=200, url="https://example.com", body=b"ok"):
        self.status = code
        self._url = url
        self._body = body
        self.closed = False

    def getcode(self):
        return self.status

    def geturl(self):
        return self._url

    def read(self, _size=-1):
        return self._body

    def close(self):
        self.closed = True


class _FakeSocket:
    def __init__(self, replies=None):
        self.replies = list(replies or [])
        self.sent = []
        self.closed = False
        self.timeout = None

    def settimeout(self, timeout):
        self.timeout = timeout

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, _size):
        if not self.replies:
            return b""
        return self.replies.pop(0)

    def close(self):
        self.closed = True


class ConnectionTestContractTests(unittest.TestCase):
    def test_normalize_url_adds_https_and_rejects_missing_host(self):
        self.assertEqual(ct._normalize_url("example.com"), "https://example.com")
        with self.assertRaises(ValueError):
            ct._normalize_url("https://")

    def test_http_error_still_counts_as_network_connectivity(self):
        error = urllib.error.HTTPError(
            "https://example.com", 403, "Forbidden", hdrs=None, fp=None)
        opener = mock.Mock()
        opener.open.side_effect = error
        with mock.patch.object(ct.urllib.request, "build_opener", return_value=opener):
            code, final_url = ct._open_url("https://example.com", timeout=1)
        self.assertEqual(code, 403)
        self.assertEqual(final_url, "https://example.com")

    def test_upstream_probe_never_exposes_credentials(self):
        settings = {
            "upstream": [{
                "host": "proxy.example",
                "port": 8000,
                "username": "alice",
                "password": "super-secret",
            }]
        }
        fake_socket = _FakeSocket()
        with mock.patch.object(ct.socket, "create_connection", return_value=fake_socket):
            result = ct._check_upstream(settings, timeout=1)
        self.assertEqual(result["status"], ct.PASS)
        rendered = str(result)
        self.assertNotIn("alice", rendered)
        self.assertNotIn("super-secret", rendered)

    def test_socks_target_uses_scheme_default_port(self):
        host, port = ct._socks_target("https://пример.рф/path")
        self.assertEqual(host.decode("ascii"), "xn--e1afmkfd.xn--p1ai")
        self.assertEqual(port, 443)

    def test_socks_check_performs_real_socks5_connect_handshake(self):
        fake_socket = _FakeSocket([
            b"\x05\x00",
            b"\x05\x00\x00\x01",
            b"\x00\x00\x00\x00",
            b"\x00\x00",
        ])
        with mock.patch.object(ct.socket, "create_connection", return_value=fake_socket):
            result = ct._check_local_socks(
                {"local_socks_port": 1080},
                "https://example.com",
                timeout=1,
                running=True,
            )
        self.assertEqual(result["status"], ct.PASS)
        self.assertEqual(fake_socket.sent[0], b"\x05\x01\x00")
        self.assertTrue(fake_socket.sent[1].startswith(b"\x05\x01\x00\x03"))
        self.assertTrue(fake_socket.closed)

    def test_pac_check_validates_arvectum_pac_shape(self):
        body = (
            b"function FindProxyForURL(url, host) { "
            b"return 'PROXY 127.0.0.1:8080; DIRECT'; }"
        )
        response = _FakeResponse(
            code=200,
            url="http://127.0.0.1:8082/proxy.pac",
            body=body,
        )
        opener = mock.Mock()
        opener.open.return_value = response
        with mock.patch.object(ct.urllib.request, "build_opener", return_value=opener):
            result = ct._check_pac(
                {"local_pac_port": 8082, "pac_path": "/proxy.pac"},
                timeout=1,
                running=True,
            )
        self.assertEqual(result["status"], ct.PASS)
        self.assertTrue(response.closed)

    def test_system_configuration_active_is_pass(self):
        result = ct._check_system_configuration(
            running=True, enabled=True, pending=False, orphaned=False, stale=False)
        self.assertEqual(result["status"], ct.PASS)

    def test_system_configuration_recovery_is_fail_closed(self):
        result = ct._check_system_configuration(
            running=False, enabled=False, pending=True, orphaned=False, stale=False)
        self.assertEqual(result["status"], ct.FAIL)
        self.assertIn("Восстановить настройки сети", result["action"])

    def test_engine_off_skips_local_endpoints_but_not_whole_report(self):
        http = ct._check_local_http(
            {"local_http_port": 8080}, "https://example.com", 1, running=False)
        socks = ct._check_local_socks(
            {"local_socks_port": 1080}, "https://example.com", 1, running=False)
        pac = ct._check_pac(
            {"local_pac_port": 8082, "pac_path": "/proxy.pac"}, 1, running=False)
        self.assertEqual({http["status"], socks["status"], pac["status"]}, {ct.SKIP})
        self.assertEqual(ct._overall([http, socks, pac]), ct.WARN)

    def test_run_connection_test_returns_six_governed_checks(self):
        fake_core = mock.Mock()
        fake_core.load_settings.return_value = {
            "local_http_port": 8080,
            "local_socks_port": 1080,
            "local_pac_port": 8082,
            "pac_path": "/proxy.pac",
            "upstream": [{"host": "proxy.example", "port": 8000}],
        }
        fake_core.is_running.return_value = True
        fake_core.system_proxy_enabled.return_value = True
        fake_core.network_restore_pending.return_value = False
        fake_core.orphaned_arvectum_pac.return_value = False
        fake_core.stale_system_proxy.return_value = False

        results = {
            "internet.direct": ct._result("internet.direct", "Интернет напрямую", ct.PASS, "ok"),
            "upstream.tcp": ct._result("upstream.tcp", "Внешний прокси", ct.PASS, "ok"),
            "local.http": ct._result("local.http", "HTTP через Launcher", ct.PASS, "ok"),
            "local.socks": ct._result("local.socks", "SOCKS5 через Launcher", ct.PASS, "ok"),
            "pac.endpoint": ct._result("pac.endpoint", "PAC", ct.PASS, "ok"),
        }
        with mock.patch.object(ct, "_check_direct_internet",
                               return_value=results["internet.direct"]), \
             mock.patch.object(ct, "_check_upstream",
                               return_value=results["upstream.tcp"]), \
             mock.patch.object(ct, "_check_local_http",
                               return_value=results["local.http"]), \
             mock.patch.object(ct, "_check_local_socks",
                               return_value=results["local.socks"]), \
             mock.patch.object(ct, "_check_pac",
                               return_value=results["pac.endpoint"]):
            report = ct.run_connection_test(
                "example.com", timeout=1, core_module=fake_core)

        self.assertEqual(report["overall"], ct.PASS)
        self.assertTrue(report["read_only"])
        self.assertEqual(
            [item["id"] for item in report["checks"]],
            [
                "internet.direct",
                "upstream.tcp",
                "local.http",
                "local.socks",
                "pac.endpoint",
                "windows.system_proxy",
            ],
        )

    def test_format_report_is_actionable(self):
        report = {
            "overall": ct.FAIL,
            "target_url": "https://example.com",
            "checks": [
                ct._result(
                    "upstream.tcp", "Внешний прокси", ct.FAIL, "недоступен",
                    action="Проверьте внешний прокси."
                )
            ],
            "recommended_actions": ["Проверьте внешний прокси."],
        }
        text = ct.format_report(report)
        self.assertIn("требуется действие", text)
        self.assertIn("[FAIL] Внешний прокси", text)
        self.assertIn("Что сделать:", text)


if __name__ == "__main__":
    unittest.main()
