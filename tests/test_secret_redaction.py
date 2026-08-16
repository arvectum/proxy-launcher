import json
import os
from pathlib import Path
import tempfile
import unittest

from secret_redaction import REDACTED, is_sensitive_key, redact_text, redact_value
from structured_logging import StructuredLogger


class SecretRedactionTests(unittest.TestCase):
    def test_uri_userinfo_is_redacted_but_host_and_path_survive(self):
        raw = "upstream=http://alice:p%40ss@example.test:8000/api?q=1"
        clean = redact_text(raw)
        self.assertNotIn("alice", clean)
        self.assertNotIn("p%40ss", clean)
        self.assertIn("http://[REDACTED]@example.test:8000/api?q=1", clean)

    def test_auth_headers_cookie_and_bearer_are_redacted(self):
        raw = (
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz\n"
            "Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==\n"
            "Cookie: session=super-secret\n"
            "fallback Bearer zyxwvutsrqponmlkjihgfedcba"
        )
        clean = redact_text(raw)
        for secret in (
            "abcdefghijklmnopqrstuvwxyz",
            "QWxhZGRpbjpvcGVuIHNlc2FtZQ==",
            "super-secret",
            "zyxwvutsrqponmlkjihgfedcba",
        ):
            self.assertNotIn(secret, clean)
        self.assertEqual(clean.count(REDACTED), 4)

    def test_assignments_json_query_and_cli_are_redacted(self):
        raw = (
            'password=hunter2 client_secret: "correct horse" '
            'url=https://example.test/?access_token=query-secret&mode=1 '
            '--api-key cli-secret'
        )
        clean = redact_text(raw)
        for secret in ("hunter2", "correct horse", "query-secret", "cli-secret"):
            self.assertNotIn(secret, clean)
        self.assertIn("mode=1", clean)
        self.assertIn("https://example.test/", clean)

    def test_jwt_and_prefixed_tokens_are_redacted_without_labels(self):
        jwt = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghijklmnopqrstuv"
        github = "github_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        openai_like = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
        clean = redact_text("%s %s %s" % (jwt, github, openai_like))
        self.assertNotIn(jwt, clean)
        self.assertNotIn(github, clean)
        self.assertNotIn(openai_like, clean)
        self.assertEqual(clean.count(REDACTED), 3)

    def test_private_key_payload_is_redacted(self):
        private_key = (
            "-----BEGIN PRIVATE KEY-----\n"
            "MIIEvQIBADANBgkqhkiG9w0BAQEFAASC...\n"
            "-----END PRIVATE KEY-----"
        )
        clean = redact_text(private_key)
        self.assertIn("-----BEGIN PRIVATE KEY-----", clean)
        self.assertIn("-----END PRIVATE KEY-----", clean)
        self.assertNotIn("MIIEvQIB", clean)
        self.assertIn(REDACTED, clean)

    def test_structured_fields_redact_sensitive_keys_recursively(self):
        value = {
            "host": "proxy.example.test",
            "password_dpapi": "encrypted-but-sensitive-blob",
            "nested": {
                "Authorization": "Bearer top-secret",
                "proxy": "http://user:password@proxy.example.test:8000",
            },
            "items": [{"clientSecret": "camel-secret", "port": 8000}],
        }
        clean = redact_value(value)
        self.assertEqual(clean["host"], "proxy.example.test")
        self.assertEqual(clean["password_dpapi"], REDACTED)
        self.assertEqual(clean["nested"]["Authorization"], REDACTED)
        self.assertEqual(clean["items"][0]["clientSecret"], REDACTED)
        self.assertEqual(clean["items"][0]["port"], 8000)
        self.assertNotIn("user:password", clean["nested"]["proxy"])

    def test_sensitive_key_detection_handles_case_punctuation_and_suffixes(self):
        for key in (
            "Password", "client-secret", "proxy.authorization", "credentials_dpapi",
            "upstream_access_token", "APIKey", "session-id", "clientSecret",
        ):
            self.assertTrue(is_sensitive_key(key), key)
        for key in ("host", "port", "pac_path", "no_proxy", "username", "notsecret"):
            self.assertFalse(is_sensitive_key(key), key)

    def test_non_sensitive_assignments_are_not_over_redacted(self):
        raw = (
            r"host=10.20.30.40 port=8080 path=C:\Users\Иван\AppData\Local\Arvectum "
            r"no_proxy=127.0.0.1,zakupki.gov.ru username=alice notsecret=value mytoken=value"
        )
        self.assertEqual(redact_text(raw), raw)

    def test_compound_sensitive_assignment_is_redacted(self):
        clean = redact_text("upstream_access_token=secret-value clientSecret=camel-secret")
        self.assertNotIn("secret-value", clean)
        self.assertNotIn("camel-secret", clean)
        self.assertEqual(clean.count(REDACTED), 2)

    def test_redaction_is_bounded_for_deep_and_large_structures(self):
        deep = {"a": {"b": {"c": {"d": {"password": "never-visible"}}}}}
        clean = redact_value(deep)
        self.assertEqual(clean["a"]["b"]["c"]["d"], "[MAX_DEPTH]")

        many = {"k%d" % i: i for i in range(60)}
        clean_many = redact_value(many)
        self.assertTrue(clean_many["__truncated__"])
        self.assertEqual(len(clean_many), 51)

    def test_structured_logger_redacts_message_event_and_fields_before_persistence(self):
        secrets = (
            "message-password",
            "event-secret-token",
            "nested-secret-token",
            "QWxhZGRpbjpvcGVuIHNlc2FtZQ==",
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "proxy_core.log"
            logger = StructuredLogger(lambda: str(path), "0.2.3", "P0.2")
            logger.log(
                "password=message-password Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==",
                event="diagnostics.token=event-secret-token",
                fields={"nested": {"accessToken": "nested-secret-token"}, "host": "example.test"},
            )
            raw = path.read_text(encoding="utf-8")
            for secret in secrets:
                self.assertNotIn(secret, raw)
            record = json.loads(raw)
            self.assertIn(REDACTED, record["message"])
            self.assertIn(REDACTED, record["event"])
            self.assertEqual(record["fields"]["nested"]["accessToken"], REDACTED)
            self.assertEqual(record["fields"]["host"], "example.test")

    def test_logger_contract_still_accepts_devnull(self):
        logger = StructuredLogger(lambda: os.devnull, "0.2.3", "P0.2")
        record = logger.make_record("proxy started password=secret")
        self.assertEqual(record["event"], "proxy.started")
        self.assertNotIn("secret", record["message"])


if __name__ == "__main__":
    unittest.main()
