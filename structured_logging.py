# -*- coding: utf-8 -*-
"""Dependency-free structured JSONL logging for Arvectum Proxy Launcher.

APL-DIAG-001 keeps the historical ``proxy_core.log`` location, but every new
record is a single JSON object.  Logging is deliberately best-effort: a disk,
encoding, or rotation failure must never break proxy/network recovery logic.
"""

from datetime import datetime, timezone
import io
import json
import os
import re
import secrets
import threading


SCHEMA = "arvectum.proxy.log.v1"
DEFAULT_MAX_BYTES = 2 * 1024 * 1024
DEFAULT_BACKUPS = 3
_REDACTED = "[REDACTED]"

_SENSITIVE_KEYS = {
    "password", "passwd", "pwd", "passphrase", "secret", "token",
    "access_token", "refresh_token", "authorization", "proxy_authorization",
    "cookie", "set_cookie", "credential", "credentials", "credentials_dpapi",
    "password_dpapi", "pin", "private_key", "client_secret", "api_key",
}

# Message redaction is intentionally conservative and targets common credential
# forms without hiding ordinary hosts, IP addresses, ports, or diagnostic paths.
_MESSAGE_REDACTIONS = (
    # URI userinfo: scheme://user:password@host -> scheme://[REDACTED]@host
    (re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://)([^\s/@:]+):([^\s/@]+)@"), r"\1[REDACTED]@"),
    # HTTP Proxy-Authorization / Authorization Basic <blob>
    (re.compile(r"(?i)\b(proxy-authorization|authorization)\s*:\s*basic\s+[A-Za-z0-9+/=_-]+"),
     r"\1: Basic [REDACTED]"),
    # Free-standing Basic auth token where it follows a credential-ish label.
    (re.compile(r"(?i)\b(basic)\s+[A-Za-z0-9+/]{8,}={0,2}"), r"\1 [REDACTED]"),
    # key=value / key: value (quoted or unquoted), including JSON-ish messages.
    (re.compile(
        r"(?i)(\b(?:password|passwd|pwd|passphrase|secret|token|access_token|refresh_token|"
        r"authorization|proxy_authorization|credentials?_dpapi|password_dpapi|pin|api_key|"
        r"client_secret)\b\s*[=:]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
    ), r"\1[REDACTED]"),
)

_EVENT_RULES = (
    (re.compile(r"^proxy started\b", re.I), "proxy.started"),
    (re.compile(r"^proxy stopped\b", re.I), "proxy.stopped"),
    (re.compile(r"^system proxy enabled\b", re.I), "system_proxy.enabled"),
    (re.compile(r"^system proxy restored successfully\b", re.I), "system_proxy.restored"),
    (re.compile(r"^system proxy already inactive\b", re.I), "system_proxy.inactive"),
    (re.compile(r"^system proxy enable failed\b", re.I), "system_proxy.enable_failed"),
    (re.compile(r"^settings saved\b", re.I), "settings.saved"),
    (re.compile(r"^no_proxy saved\b", re.I), "no_proxy.saved"),
    (re.compile(r"^client proxy environment enabled\b", re.I), "environment.proxy_enabled"),
    (re.compile(r"^client proxy environment restored\b", re.I), "environment.proxy_restored"),
    (re.compile(r"^client no_proxy synchronized\b", re.I), "environment.no_proxy_synchronized"),
    (re.compile(r"^portable launcher copied\b", re.I), "launcher.self_heal_copied"),
    (re.compile(r"^portable launcher handed off\b", re.I), "launcher.handoff"),
    (re.compile(r"^start aborted\b", re.I), "proxy.start_aborted"),
    (re.compile(r"^start failed\b", re.I), "proxy.start_failed"),
)

_ERROR_WORDS = re.compile(r"(?i)\b(error|failed|failure|incomplete)\b")
_WARNING_WORDS = re.compile(
    r"(?i)\b(aborted|refusing|skipped|invalid|unreadable|conflict|mismatch|unverified|unsafe)\b"
)


def _utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _sanitize_message(value, limit=4096):
    text = str(value)
    for pattern, replacement in _MESSAGE_REDACTIONS:
        text = pattern.sub(replacement, text)
    if len(text) > limit:
        text = text[: limit - 16] + "...[truncated]"
    return text


def _sensitive_key(key):
    normalized = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")
    if normalized in _SENSITIVE_KEYS:
        return True
    return any(
        normalized.endswith("_" + suffix)
        for suffix in ("password", "passwd", "passphrase", "secret", "token", "authorization", "cookie", "pin")
    )


def _sanitize_value(value, depth=0):
    if depth >= 4:
        return "[MAX_DEPTH]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _sanitize_message(value, limit=2048)
    if isinstance(value, dict):
        out = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= 50:
                out["__truncated__"] = True
                break
            key_text = str(key)[:128]
            out[key_text] = _REDACTED if _sensitive_key(key_text) else _sanitize_value(item, depth + 1)
        return out
    if isinstance(value, (list, tuple, set)):
        items = list(value)
        out = [_sanitize_value(item, depth + 1) for item in items[:50]]
        if len(items) > 50:
            out.append("[TRUNCATED]")
        return out
    return _sanitize_message(repr(value), limit=2048)


def _infer_level(message):
    text = str(message)
    if _ERROR_WORDS.search(text):
        return "ERROR"
    if _WARNING_WORDS.search(text):
        return "WARNING"
    return "INFO"


def _derive_event(message, component):
    text = str(message).strip()
    for pattern, event in _EVENT_RULES:
        if pattern.search(text):
            return event
    prefix = re.split(r"[:;(]", text, maxsplit=1)[0]
    prefix = re.sub(r"\bpid\s*=\s*\d+\b", "pid", prefix, flags=re.I)
    prefix = re.sub(r"\b\d+\b", "n", prefix)
    slug = re.sub(r"[^a-z0-9]+", ".", prefix.lower()).strip(".")
    slug = re.sub(r"\.+", ".", slug)[:64].rstrip(".")
    return "%s.%s" % (component, slug or "event")


def _valid_level(level):
    normalized = str(level or "").upper()
    return normalized if normalized in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"} else None


class StructuredLogger:
    """Small JSONL logger with redaction, legacy migration, and bounded rotation."""

    def __init__(self, path_getter, app_version, milestone, component="proxy_core",
                 max_bytes=DEFAULT_MAX_BYTES, backups=DEFAULT_BACKUPS, run_id=None):
        self.path_getter = path_getter
        self.app_version = str(app_version)
        self.milestone = str(milestone)
        self.component = str(component)
        self.max_bytes = max(256, int(max_bytes))
        self.backups = max(0, int(backups))
        self.run_id = str(run_id or secrets.token_hex(8))
        self._lock = threading.RLock()
        self._prepared_paths = set()

    def log(self, message, level=None, event=None, fields=None):
        """Append one JSON record. Any logger failure is intentionally swallowed."""
        try:
            record = self.make_record(message, level=level, event=event, fields=fields)
            encoded = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            path = os.fspath(self.path_getter())
            with self._lock:
                self._prepare_path(path)
                self._rotate_if_needed(path, len(encoded))
                parent = os.path.dirname(os.path.abspath(path))
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with io.open(path, "a", encoding="utf-8", newline="\n") as stream:
                    stream.write(encoded.decode("utf-8"))
                    stream.flush()
        except Exception:
            # Diagnostics must never interfere with proxy start/stop/rollback.
            return None
        return record

    def make_record(self, message, level=None, event=None, fields=None):
        clean_message = _sanitize_message(message)
        resolved_level = _valid_level(level) or _infer_level(clean_message)
        resolved_event = str(event or _derive_event(clean_message, self.component))[:128]
        record = {
            "schema": SCHEMA,
            "ts": _utc_timestamp(),
            "level": resolved_level,
            "event": resolved_event,
            "component": self.component,
            "message": clean_message,
            "pid": os.getpid(),
            "thread": threading.current_thread().name,
            "run_id": self.run_id,
            "app_version": self.app_version,
            "milestone": self.milestone,
        }
        if fields:
            record["fields"] = _sanitize_value(dict(fields))
        return record

    def _prepare_path(self, path):
        absolute = os.path.abspath(path)
        if absolute in self._prepared_paths:
            return
        parent = os.path.dirname(absolute)
        if parent:
            os.makedirs(parent, exist_ok=True)
        if os.path.isfile(absolute) and os.path.getsize(absolute) > 0 and not self._is_structured_log(absolute):
            self._move_legacy(absolute)
        self._prepared_paths.add(absolute)

    @staticmethod
    def _is_structured_log(path):
        try:
            with io.open(path, "r", encoding="utf-8") as stream:
                for line in stream:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    return isinstance(data, dict) and data.get("schema") == SCHEMA
        except Exception:
            return False
        return True

    @staticmethod
    def _move_legacy(path):
        target = path + ".legacy"
        index = 1
        while os.path.exists(target):
            target = path + ".legacy.%d" % index
            index += 1
        os.replace(path, target)

    def _rotate_if_needed(self, path, incoming_bytes):
        if not os.path.exists(path):
            return
        try:
            current = os.path.getsize(path)
        except OSError:
            return
        if current + incoming_bytes <= self.max_bytes:
            return
        if self.backups <= 0:
            with io.open(path, "w", encoding="utf-8"):
                pass
            return
        oldest = "%s.%d" % (path, self.backups)
        if os.path.exists(oldest):
            os.remove(oldest)
        for index in range(self.backups - 1, 0, -1):
            source = "%s.%d" % (path, index)
            target = "%s.%d" % (path, index + 1)
            if os.path.exists(source):
                os.replace(source, target)
        os.replace(path, path + ".1")
