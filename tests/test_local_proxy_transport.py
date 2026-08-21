import base64
import unittest
from unittest import mock

import proxy_core as core


class LocalProxyTransportExtractionTests(unittest.TestCase):
    def test_canonical_module_owns_transport_class(self):
        self.assertEqual(core.ProxyCore.__module__, "local_proxy_transport")
        self.assertEqual(core._SOCKS5_REPLY_BIND_ADDR, b"\x00\x00\x00\x00")

    def test_upstream_preparation_preserves_credentials_and_port_fallback(self):
        settings = {
            "upstream": [
                {"host": " proxy.test ", "port": "invalid", "username": "user", "password": "pass"},
                {"host": "", "port": 9000, "username": "ignored", "password": "ignored"},
            ]
        }
        engine = core.ProxyCore(settings)
        expected_token = base64.b64encode(b"user:pass").decode("ascii")
        self.assertEqual(engine._upstreams, [("proxy.test", 8000, expected_token)])

    def test_http_handler_resolves_canonical_routing_seam_dynamically(self):
        settings = {
            "local_http_port": 8080,
            "local_socks_port": 1080,
            "local_pac_port": 8082,
            "pac_path": "/proxy.pac",
            "upstream": [],
        }
        engine = core.ProxyCore(settings)
        client = mock.Mock()
        client.recv.return_value = (
            b"GET http://Example.TEST/path HTTP/1.1\r\n"
            b"Host: Example.TEST\r\nConnection: close\r\n\r\n"
        )
        direct = mock.Mock()

        with mock.patch.object(core, "_normalize_host", return_value="example.test") as normalize, \
             mock.patch.object(core, "host_bypasses_proxy", return_value=True) as bypass, \
             mock.patch.object(core.socket, "create_connection", return_value=direct) as connect, \
             mock.patch.object(engine, "_relay") as relay:
            engine._handle_http(client)

        normalize.assert_called_once_with("Example.TEST")
        bypass.assert_called_once_with("example.test")
        connect.assert_called_once_with(("example.test", 80), timeout=15)
        direct.settimeout.assert_called_once_with(300)
        self.assertTrue(direct.sendall.call_args.args[0].startswith(b"GET /path HTTP/1.1"))
        relay.assert_called_once_with(direct, client, engine._stop)

    def test_pac_handler_resolves_build_pac_through_compatibility_seam(self):
        settings = {
            "local_http_port": 8080,
            "local_socks_port": 1080,
            "local_pac_port": 8082,
            "pac_path": "/custom.pac",
            "upstream": [],
        }
        engine = core.ProxyCore(settings)
        client = mock.Mock()
        client.recv.return_value = b"GET /custom.pac HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"

        with mock.patch.object(core, "build_pac", return_value="PAC-SLICE-5") as build_pac:
            engine._handle_pac(client)

        build_pac.assert_called_once_with()
        response = client.sendall.call_args.args[0]
        self.assertIn(b"HTTP/1.1 200 OK", response)
        self.assertIn(b"PAC-SLICE-5", response)
        self.assertIn(b"Content-Type: application/x-ns-proxy-autoconfig", response)

    def test_pac_handler_preserves_404_for_wrong_path(self):
        engine = core.ProxyCore({"pac_path": "/proxy.pac", "upstream": []})
        client = mock.Mock()
        client.recv.return_value = b"GET /wrong.pac HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        with mock.patch.object(core, "build_pac") as build_pac:
            engine._handle_pac(client)
        build_pac.assert_not_called()
        self.assertIn(b"404 Not Found", client.sendall.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
