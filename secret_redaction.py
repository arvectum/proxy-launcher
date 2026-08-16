# -*- coding: utf-8 -*-
"""Secret redaction primitives for Arvectum Proxy Launcher diagnostics.

APL-DIAG-002 centralizes the rules used before diagnostic data is persisted.
The module is dependency-free and deliberately conservative: infrastructure
values such as hosts, IP addresses, ports, file paths and no_proxy entries stay
visible while credential material is replaced with a stable marker.
"""

import re


REDACTED = "[REDACTED]"
MAX_DEPTH_MARKER = "[MAX_DEPTH]"
TRUNCATED_MARKER = "[TRUNCATED]"

_SENSITIVE_KEYS = {
    "password", "passwd", "pwd", "passphrase",
    "secret", "secret_key", "client_secret",
    "token", "access_token", "refresh_token", "id_token", "session_token",
    "authorization", "proxy_authorization", "proxy_auth", "auth_token",
    "cookie", "set_cookie", "session", "session_id",
    "credential", "credentials", "credential_blob", "credentials_blob",
    "credentials_dpapi", "password_dpapi", "dpapi_blob",
    "pin", "private_key", "private_key_data",
    "api_key", "apikey", "x_api_key", "x_auth_token",
}

_SENSITIVE_SUFFIXES = (
    "password", "passwd", "passphrase", "secret", "secret_key", "token",
    "authorization", "cookie", "credential", "credentials", "pin",
    "private_key", "api_key", "apikey",
)

_SENSITIVE_NAME_PATTERN = (
    r"password|passwd|pwd|passphrase|secret|secret[_-]?key|client[_-]?secret|"
    r"token|access[_-]?token|refresh[_-]?token|id[_-]?token|session[_-]?token|"
    r"authorization|proxy[_-]?authorization|proxy[_-]?auth|auth[_-]?token|"
    r"cookie|set[_-]?cookie|session[_-]?id|credential|credentials|"
    r"credential[_-]?blob|credentials[_-]?blob|credentials[_-]?dpapi|"
    r"password[_-]?dpapi|dpapi[_-]?blob|pin|private[_-]?key|api[_-]?key|apikey|"
    r"x[_-]?api[_-]?key|x[_-]?auth[_-]?token"
)

# Private-key blocks are always secret, independent of their surrounding label.
_PRIVATE_KEY_BLOCK = re.compile(
    r"-----BEGIN (?P<kind>[A-Z0-9 ]*PRIVATE KEY)-----.*?"
    r"-----END (?P=kind)-----",
    re.DOTALL,
)

# Any URI user-info can contain credentials (user:password, token, API key).
_URI_USERINFO = re.compile(
    r"(?i)\b(?P<scheme>[a-z][a-z0-9+.-]*://)(?P<userinfo>[^\s/@]+)@"
)

# Header values which are credentials or credential containers.
_SECRET_HEADER = re.compile(
    r"(?im)\b(?P<name>authorization|proxy-authorization|cookie|set-cookie|"
    r"x-api-key|api-key|x-auth-token)\s*:\s*[^\r\n]+"
)

# Authorization schemes are sometimes logged without their header name.
_AUTH_SCHEME = re.compile(
    r"(?i)\b(?P<scheme>bearer|basic|digest|negotiate)\s+"
    r"(?P<value>[A-Za-z0-9._~+/=:-]{8,})"
)

# Key/value pairs in plain text, query strings and JSON-ish messages. The
# callback decides whether the complete key is sensitive; this avoids false
# positives such as ``notsecret=value`` while still catching suffix forms like
# ``upstream_access_token=value`` and camelCase ``clientSecret=value``.
_ASSIGNMENT = re.compile(
    r"(?P<prefix>(?P<key>[\"']?[A-Za-z][A-Za-z0-9_.-]*[\"']?)\s*(?:=|:)\s*)"
    r"(?P<value>\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*'|[^\s,;&]+)",
    re.IGNORECASE,
)

# Query parameters require a first pass because a surrounding ``url=...``
# assignment would otherwise consume the whole URL before nested token keys are
# inspected.
_QUERY_PAIR = re.compile(
    r"(?P<prefix>[?&](?P<key>[A-Za-z][A-Za-z0-9_.-]*)=)(?P<value>[^&#\s]+)",
    re.IGNORECASE,
)

# Common CLI form: --password value / --token=value.
_SECRET_CLI = re.compile(
    r"(?i)(?P<prefix>--(?:" + _SENSITIVE_NAME_PATTERN + r"))(?:\s+|=)"
    r"(?P<value>[^\s]+)"
)

# JWTs can surface in exception text without an explicit "token" label.
_JWT = re.compile(
    r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\."
    r"[A-Za-z0-9_-]{10,}(?![A-Za-z0-9_-])"
)

# High-confidence provider-style token prefixes. These remain useful even when
# a caller logs a raw token with no key or auth scheme.
_PREFIXED_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"sk-[A-Za-z0-9_-]{20,})(?![A-Za-z0-9_])"
)


def _safe_text(value):
    try:
        return str(value)
    except Exception:
        return "<unprintable>"


def _normalize_key(key):
    text = _safe_text(key)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def is_sensitive_key(key):
    """Return True when a structured field name conventionally carries a secret."""
    normalized = _normalize_key(key)
    if normalized in _SENSITIVE_KEYS:
        return True
    return any(normalized.endswith("_" + suffix) for suffix in _SENSITIVE_SUFFIXES)


def _redact_private_key(match):
    kind = match.group("kind")
    return "-----BEGIN %s-----\n%s\n-----END %s-----" % (kind, REDACTED, kind)


def _redact_query_pair(match):
    if not is_sensitive_key(match.group("key")):
        return match.group(0)
    return match.group("prefix") + REDACTED


def _redact_assignment(match):
    key = match.group("key").strip("\"'")
    prefix = match.group("prefix")
    if is_sensitive_key(key):
        return prefix + REDACTED
    value = match.group("value")
    if "=" in value or ":" in value:
        nested = redact_text(value)
        if nested != value:
            return prefix + nested
    return match.group(0)


def redact_text(value, limit=None):
    """Return text with credential material replaced by ``[REDACTED]``."""
    text = _safe_text(value)
    text = _PRIVATE_KEY_BLOCK.sub(_redact_private_key, text)
    text = _URI_USERINFO.sub(lambda m: m.group("scheme") + REDACTED + "@", text)
    text = _SECRET_HEADER.sub(lambda m: m.group("name") + ": " + REDACTED, text)
    text = _AUTH_SCHEME.sub(lambda m: m.group("scheme") + " " + REDACTED, text)
    text = _SECRET_CLI.sub(lambda m: m.group("prefix") + "=" + REDACTED, text)
    text = _QUERY_PAIR.sub(_redact_query_pair, text)
    text = _ASSIGNMENT.sub(_redact_assignment, text)
    text = _JWT.sub(REDACTED, text)
    text = _PREFIXED_TOKEN.sub(REDACTED, text)
    if limit is not None:
        limit = max(32, int(limit))
        if len(text) > limit:
            text = text[: limit - 16] + "...[truncated]"
    return text


def redact_value(value, depth=0, max_depth=4, max_items=50, string_limit=2048):
    """Recursively redact structured diagnostic values with bounded traversal."""
    if depth >= max_depth:
        return MAX_DEPTH_MARKER
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return redact_text(value, limit=string_limit)
    if isinstance(value, dict):
        out = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= max_items:
                out["__truncated__"] = True
                break
            key_text = _safe_text(key)[:128]
            out[key_text] = REDACTED if is_sensitive_key(key_text) else redact_value(
                item,
                depth=depth + 1,
                max_depth=max_depth,
                max_items=max_items,
                string_limit=string_limit,
            )
        return out
    if isinstance(value, (list, tuple, set)):
        try:
            items = list(value)
        except Exception:
            return redact_text(repr(value), limit=string_limit)
        out = [
            redact_value(
                item,
                depth=depth + 1,
                max_depth=max_depth,
                max_items=max_items,
                string_limit=string_limit,
            )
            for item in items[:max_items]
        ]
        if len(items) > max_items:
            out.append(TRUNCATED_MARKER)
        return out
    try:
        representation = repr(value)
    except Exception:
        representation = "<unprintable>"
    return redact_text(representation, limit=string_limit)
