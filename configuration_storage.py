"""Canonical configuration storage for Arvectum Proxy Launcher.

APL-IP-003 Slice 3 centralizes the governed settings model, configuration
loading, Windows credential protection, atomic persistence, last-known-good
snapshots, quarantine, and deterministic corruption recovery.

The module is installed into the established ``proxy_core`` module object.
Behavior-sensitive collaborators deliberately resolve through that compatibility
seam so the 0.2.3 behavioural contract and monkeypatch regressions remain
stable, while ordinary standard-library dependencies are owned locally.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import threading
import time
from types import ModuleType
from typing import Any


CONFIG_VERSION = 1
CONFIG_SCHEMA = "arvectum.proxy.settings.v1"
CONFIG_RECOVERY_SCHEMA = "arvectum.proxy.settings_recovery.v1"
_MAX_UPSTREAMS = 16
_CONFIG_ALLOWED_TOP_LEVEL = {
    "config_version",
    "local_http_port",
    "local_socks_port",
    "local_pac_port",
    "pac_path",
    "upstream",
}
_RUNTIME_UPSTREAM_KEYS = {"host", "port", "username", "password"}
_DISK_UPSTREAM_KEYS = {
    "host",
    "port",
    "username",
    "password",
    "credentials_dpapi",
    "password_dpapi",
}
DEFAULT_SETTINGS = {
    "config_version": CONFIG_VERSION,
    "local_http_port": 8080,
    "local_socks_port": 1080,
    "local_pac_port": 8082,
    "pac_path": "/proxy.pac",
    "upstream": [
        {"host": "", "port": 8000, "username": "", "password": ""}
    ],
}

_CORE: ModuleType | None = None


def configure(core: ModuleType) -> None:
    """Bind the established core module used as the compatibility seam."""
    global _CORE
    _CORE = core


def _core() -> ModuleType:
    if _CORE is None:
        raise RuntimeError("configuration storage is not configured")
    return _CORE


def _json_clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def _validate_port(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not (1 <= value <= 65535):
        raise ValueError("%s must be an integer from 1 to 65535" % field)
    return value


def _validate_host(value: Any, field: str = "upstream.host") -> str:
    if not isinstance(value, str):
        raise ValueError("%s must be a string" % field)
    value = value.strip()
    if len(value) > 512:
        raise ValueError("%s is too long" % field)
    if any(ord(ch) < 32 or ch.isspace() for ch in value):
        raise ValueError("%s contains whitespace/control characters" % field)
    if any(part in value for part in ("://", "/", "\\", "@")):
        raise ValueError("%s must be a host/address, not a URL" % field)
    return value


def _validate_pac_path(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("pac_path must be a string")
    if not value.startswith("/") or len(value) > 256:
        raise ValueError("pac_path must be an absolute local path up to 256 characters")
    if any(ord(ch) < 32 or ch.isspace() for ch in value) or "?" in value or "#" in value:
        raise ValueError("pac_path contains unsafe characters")
    return value


def _validate_config_version(value: Any) -> int:
    core = _core()
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("config_version must be a non-negative integer")
    if value > core.CONFIG_VERSION:
        raise ValueError("unsupported future config_version %s" % value)
    return value


def _validate_upstream_list(value: Any, storage: bool = False) -> list[dict[str, Any]]:
    core = _core()
    if not isinstance(value, list):
        raise ValueError("upstream must be a list")
    if len(value) > core._MAX_UPSTREAMS:
        raise ValueError("upstream contains more than %d entries" % core._MAX_UPSTREAMS)
    allowed = core._DISK_UPSTREAM_KEYS if storage else core._RUNTIME_UPSTREAM_KEYS
    result = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise ValueError("upstream[%d] must be an object" % index)
        unknown = set(raw) - allowed
        if unknown:
            raise ValueError("upstream[%d] contains unknown keys: %s" % (
                index, ", ".join(sorted(unknown))))
        upstream = {
            "host": core._validate_host(raw.get("host", ""), "upstream[%d].host" % index),
            "port": core._validate_port(raw.get("port", 8000), "upstream[%d].port" % index),
        }
        if storage:
            for key in ("username", "password", "credentials_dpapi", "password_dpapi"):
                if key in raw:
                    if not isinstance(raw[key], str):
                        raise ValueError("upstream[%d].%s must be a string" % (index, key))
                    upstream[key] = raw[key]
            if upstream.get("credentials_dpapi") and any(
                    key in upstream for key in ("username", "password", "password_dpapi")):
                raise ValueError("credentials_dpapi cannot be mixed with legacy/plaintext credentials")
            if "password" in upstream and "password_dpapi" in upstream:
                raise ValueError("password and password_dpapi cannot coexist")
        else:
            username = raw.get("username", "")
            password = raw.get("password", "")
            if not isinstance(username, str) or not isinstance(password, str):
                raise ValueError("runtime upstream credentials must be strings")
            upstream["username"] = username
            upstream["password"] = password
        result.append(upstream)
    return result


def _validate_settings_model(settings: Any, storage: bool = False) -> dict[str, Any]:
    core = _core()
    if not isinstance(settings, dict):
        raise ValueError("settings must be an object")
    unknown = set(settings) - core._CONFIG_ALLOWED_TOP_LEVEL
    if unknown:
        raise ValueError("settings contain unknown keys: %s" % ", ".join(sorted(unknown)))
    core._validate_config_version(settings.get("config_version"))
    result = {
        "config_version": core.CONFIG_VERSION,
        "local_http_port": core._validate_port(
            settings.get("local_http_port", core.DEFAULT_SETTINGS["local_http_port"]),
            "local_http_port"),
        "local_socks_port": core._validate_port(
            settings.get("local_socks_port", core.DEFAULT_SETTINGS["local_socks_port"]),
            "local_socks_port"),
        "local_pac_port": core._validate_port(
            settings.get("local_pac_port", core.DEFAULT_SETTINGS["local_pac_port"]),
            "local_pac_port"),
        "pac_path": core._validate_pac_path(
            settings.get("pac_path", core.DEFAULT_SETTINGS["pac_path"])),
    }
    ports = {
        result["local_http_port"], result["local_socks_port"], result["local_pac_port"]
    }
    if len(ports) != 3:
        raise ValueError("local HTTP, SOCKS5 and PAC ports must be distinct")
    upstream_default = ([{"host": "", "port": 8000}] if storage
                        else core.DEFAULT_SETTINGS["upstream"])
    result["upstream"] = core._validate_upstream_list(
        settings.get("upstream", upstream_default), storage=storage)
    return result


def _validate_runtime_settings(settings: Any) -> dict[str, Any]:
    return _core()._validate_settings_model(settings, storage=False)


def _validate_serialized_settings(settings: Any) -> dict[str, Any]:
    return _core()._validate_settings_model(settings, storage=True)


def _disk_contains_plaintext_credentials(settings: Any) -> bool:
    if not isinstance(settings, dict):
        return False
    for upstream in settings.get("upstream") or []:
        if isinstance(upstream, dict) and ("username" in upstream or "password" in upstream):
            if bool(upstream.get("username")) or bool(upstream.get("password")):
                return True
    return False


def _fsync_parent_dir(path: str) -> None:
    core = _core()
    if core.is_windows():
        return
    try:
        descriptor = os.open(path or ".", os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _atomic_write_bytes(path: str, payload: bytes) -> None:
    """Durably replace *path* without exposing a partially written target."""
    core = _core()
    parent = os.path.dirname(path) or "."
    os.makedirs(parent, exist_ok=True)
    temporary = "%s.tmp.%d.%d" % (path, os.getpid(), threading.get_ident())
    try:
        with open(temporary, "wb") as stream:
            try:
                if not core.is_windows():
                    os.chmod(temporary, 0o600)
            except OSError:
                pass
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        core._fsync_parent_dir(parent)
    finally:
        if os.path.exists(temporary):
            try:
                os.remove(temporary)
            except OSError:
                pass


def _atomic_write_json(path: str, value: Any) -> None:
    core = _core()
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    core._atomic_write_bytes(path, payload)


def _atomic_write_text(path: str, value: str) -> None:
    _core()._atomic_write_bytes(path, value.encode("utf-8"))


def _safe_recovery_reason(value: Any) -> str:
    return str(value).replace("\r", " ").replace("\n", " ")[:500]


def _load_serialized_settings(path: str) -> dict[str, Any]:
    core = _core()
    with io.open(path, "r", encoding="utf-8") as stream:
        return core._validate_serialized_settings(json.load(stream))


def _runtime_settings_from_disk(settings: Any) -> dict[str, Any]:
    core = _core()
    return core._validate_runtime_settings(core._decode_upstream_secrets(settings))


def _quarantine_corrupt_file(path: str, reason: Any) -> str | None:
    core = _core()
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as stream:
            raw = stream.read()
        digest = hashlib.sha256(raw).hexdigest()
        os.makedirs(core.config_quarantine_dir(), exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        target = os.path.join(
            core.config_quarantine_dir(),
            "%s.corrupt-%s-%s" % (os.path.basename(path), stamp, digest[:12]))
        if os.path.exists(target):
            target += "-%d-%d" % (os.getpid(), threading.get_ident())
        os.replace(path, target)
        core._fsync_parent_dir(os.path.dirname(path) or ".")
        core._fsync_parent_dir(core.config_quarantine_dir())
        try:
            core._atomic_write_json(target + ".meta.json", {
                "schema": core.CONFIG_RECOVERY_SCHEMA,
                "reason": core._safe_recovery_reason(reason),
                "sha256": digest,
                "source_name": os.path.basename(path),
                "quarantined_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })
        except Exception as meta_error:
            core._log("config quarantine metadata write error: %r" % meta_error)
        core._log("corrupted configuration quarantined: %s" % target)
        return target
    except Exception as error:
        core._log("config quarantine error: %r" % error)
        return None


def _record_configuration_recovery(reason: Any, quarantined: str | None,
                                   recovered_from: str) -> None:
    core = _core()
    try:
        core._atomic_write_json(core.config_recovery_path(), {
            "schema": core.CONFIG_RECOVERY_SCHEMA,
            "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "reason": core._safe_recovery_reason(reason),
            "quarantined": os.path.basename(quarantined) if quarantined else None,
            "recovered_from": recovered_from,
        })
    except Exception as error:
        core._log("config recovery evidence write error: %r" % error)


def _recover_corrupt_settings(error: Exception) -> dict[str, Any]:
    core = _core()
    primary = core.settings_path()
    quarantined = core._quarantine_corrupt_file(primary, error)
    if quarantined is None and os.path.exists(primary):
        core._record_configuration_recovery(error, None, "defaults_preserved_primary")
        return core._json_clone(core.DEFAULT_SETTINGS)

    backup = core.settings_backup_path()
    if os.path.exists(backup):
        try:
            disk = core._load_serialized_settings(backup)
            runtime = core._runtime_settings_from_disk(disk)
            restore_disk = disk
            if core.is_windows() and core._disk_contains_plaintext_credentials(disk):
                restore_disk = core._validate_serialized_settings(
                    core._encode_settings_for_disk(runtime))
            core._atomic_write_json(primary, restore_disk)
            core._record_configuration_recovery(error, quarantined, "lastgood")
            core._log("settings recovered from last-known-good configuration")
            return runtime
        except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as backup_error:
            core._quarantine_corrupt_file(backup, backup_error)
        except OSError as backup_error:
            core._log("last-known-good settings recovery I/O error: %r" % backup_error)

    core._record_configuration_recovery(error, quarantined, "programmatic_defaults")
    core._log("settings recovery fell back to programmatic defaults")
    return core._json_clone(core.DEFAULT_SETTINGS)


def _dpapi_protect_text(value: Any) -> str | None:
    """Encrypt a UTF-8 secret with Windows DPAPI for the current user."""
    core = _core()
    if value in (None, ""):
        return ""
    if not core.is_windows():
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD),
                        ("pbData", ctypes.POINTER(ctypes.c_byte))]

        crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        crypt32.CryptProtectData.argtypes = [
            ctypes.POINTER(DATA_BLOB), wintypes.LPCWSTR, ctypes.POINTER(DATA_BLOB),
            ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
        crypt32.CryptProtectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p

        raw = str(value).encode("utf-8")
        buffer = (ctypes.c_byte * len(raw)).from_buffer_copy(raw)
        source = DATA_BLOB(len(raw), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))
        destination = DATA_BLOB()
        CRYPTPROTECT_UI_FORBIDDEN = 0x1
        if not crypt32.CryptProtectData(
                ctypes.byref(source), "Arvectum Proxy Launcher upstream password",
                None, None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(destination)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            encrypted = ctypes.string_at(destination.pbData, destination.cbData)
            return base64.b64encode(encrypted).decode("ascii")
        finally:
            if destination.pbData:
                kernel32.LocalFree(ctypes.cast(destination.pbData, ctypes.c_void_p))
    except Exception as error:
        core._log("DPAPI protect error: %r" % error)
        return None


def _dpapi_unprotect_text(value: Any) -> str | None:
    core = _core()
    if value in (None, ""):
        return ""
    if not core.is_windows():
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD),
                        ("pbData", ctypes.POINTER(ctypes.c_byte))]

        crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        crypt32.CryptUnprotectData.argtypes = [
            ctypes.POINTER(DATA_BLOB), ctypes.POINTER(wintypes.LPWSTR),
            ctypes.POINTER(DATA_BLOB), ctypes.c_void_p, ctypes.c_void_p,
            wintypes.DWORD, ctypes.POINTER(DATA_BLOB)]
        crypt32.CryptUnprotectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p

        raw = base64.b64decode(str(value).encode("ascii"), validate=True)
        buffer = (ctypes.c_byte * len(raw)).from_buffer_copy(raw)
        source = DATA_BLOB(len(raw), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))
        destination = DATA_BLOB()
        description = wintypes.LPWSTR()
        CRYPTPROTECT_UI_FORBIDDEN = 0x1
        if not crypt32.CryptUnprotectData(
                ctypes.byref(source), ctypes.byref(description), None, None, None,
                CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(destination)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return ctypes.string_at(destination.pbData, destination.cbData).decode("utf-8")
        finally:
            if description:
                kernel32.LocalFree(ctypes.cast(description, ctypes.c_void_p))
            if destination.pbData:
                kernel32.LocalFree(ctypes.cast(destination.pbData, ctypes.c_void_p))
    except Exception as error:
        core._log("DPAPI unprotect error: %r" % error)
        return None


def _decode_upstream_secrets(settings: Any) -> dict[str, Any]:
    core = _core()
    data = core._json_clone(settings)
    decoded = []
    for raw in data.get("upstream") or []:
        upstream = dict(raw)
        credentials_blob = upstream.pop("credentials_dpapi", None)
        legacy_password_blob = upstream.pop("password_dpapi", None)
        if credentials_blob not in (None, ""):
            plain = core._dpapi_unprotect_text(credentials_blob)
            if plain is None:
                core._log("settings contain unreadable DPAPI credentials; leaving auth empty")
                upstream["username"] = ""
                upstream["password"] = ""
            else:
                try:
                    auth = json.loads(plain)
                    upstream["username"] = str(auth.get("username") or "")
                    upstream["password"] = str(auth.get("password") or "")
                except Exception as error:
                    core._log("DPAPI credentials payload is invalid: %r" % error)
                    upstream["username"] = ""
                    upstream["password"] = ""
        elif legacy_password_blob not in (None, ""):
            plain = core._dpapi_unprotect_text(legacy_password_blob)
            upstream["username"] = str(upstream.get("username") or "")
            upstream["password"] = "" if plain is None else plain
        else:
            upstream["username"] = str(upstream.get("username") or "")
            upstream["password"] = str(upstream.get("password") or "")
        decoded.append(upstream)
    data["upstream"] = decoded
    return data


def _encode_settings_for_disk(settings: Any) -> dict[str, Any]:
    core = _core()
    data = core._validate_runtime_settings(settings)
    encoded = []
    for raw in data.get("upstream") or []:
        upstream = dict(raw)
        username = str(upstream.pop("username", "") or "")
        password = str(upstream.pop("password", "") or "")
        upstream.pop("credentials_dpapi", None)
        upstream.pop("password_dpapi", None)
        if core.is_windows():
            if username or password:
                payload = json.dumps(
                    {"username": username, "password": password},
                    ensure_ascii=False, separators=(",", ":"))
                protected = core._dpapi_protect_text(payload)
                if protected is None:
                    raise RuntimeError("Windows DPAPI could not protect upstream credentials")
                upstream["credentials_dpapi"] = protected
        else:
            # Production Windows builds never use this plaintext representation;
            # source-level non-Windows tests retain the historical compatibility.
            upstream["username"] = username
            upstream["password"] = password
        encoded.append(upstream)
    data["upstream"] = encoded
    return data


def load_settings(migrate_legacy: bool = True,
                  recover_corrupt: bool | None = None) -> dict[str, Any]:
    """Load governed settings while keeping diagnostic reads non-mutating."""
    core = _core()
    if recover_corrupt is None:
        recover_corrupt = bool(migrate_legacy)
    data = core._json_clone(core.DEFAULT_SETTINGS)
    path = core.settings_path()
    if not os.path.exists(path):
        return data
    try:
        loaded = core._load_serialized_settings(path)
        runtime = core._runtime_settings_from_disk(loaded)
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        core._log("settings validation/read error: %r" % error)
        return core._recover_corrupt_settings(error) if recover_corrupt else data
    except OSError as error:
        # Locked/unavailable files are not corruption and must never be renamed.
        core._log("settings I/O error: %r" % error)
        return data
    except Exception as error:
        core._log("settings read error: %r" % error)
        return data

    legacy_plaintext = core._disk_contains_plaintext_credentials(loaded)
    if legacy_plaintext and core.is_windows() and migrate_legacy:
        if core.save_settings(runtime):
            core._log("legacy plaintext upstream credentials migrated to DPAPI")
        else:
            core._log("legacy plaintext upstream credentials migration to DPAPI failed")
    return runtime


def save_settings(settings: Any) -> bool:
    """Validate, snapshot, and atomically persist settings."""
    core = _core()
    path = core.settings_path()
    legacy_tmp = path + ".tmp"
    try:
        if os.path.exists(legacy_tmp):
            try:
                os.remove(legacy_tmp)
            except OSError:
                pass

        runtime = core._validate_runtime_settings(settings)
        disk_settings = core._validate_serialized_settings(
            core._encode_settings_for_disk(runtime))
        os.makedirs(core.data_dir(), exist_ok=True)

        if os.path.exists(path):
            try:
                previous = core._load_serialized_settings(path)
            except (ValueError, TypeError, UnicodeError, json.JSONDecodeError) as error:
                quarantined = core._quarantine_corrupt_file(path, error)
                if quarantined is None and os.path.exists(path):
                    raise RuntimeError("existing corrupted settings could not be quarantined")
            except OSError:
                raise
            else:
                # Never preserve a second plaintext copy during the legacy
                # Windows -> DPAPI migration.
                if not (core.is_windows()
                        and core._disk_contains_plaintext_credentials(previous)):
                    core._atomic_write_json(core.settings_backup_path(), previous)
                else:
                    core._log("last-known-good snapshot skipped for plaintext legacy credentials")

        core._atomic_write_json(path, disk_settings)
        core._log("settings saved atomically")
        return True
    except Exception as error:
        core._log("settings save error: %r" % error)
        try:
            if os.path.exists(legacy_tmp):
                os.remove(legacy_tmp)
        except OSError:
            pass
        return False


def install_into_core(core: ModuleType) -> ModuleType:
    """Expose canonical configuration ownership through the compatibility seam."""
    core.CONFIG_VERSION = CONFIG_VERSION
    core.CONFIG_SCHEMA = CONFIG_SCHEMA
    core.CONFIG_RECOVERY_SCHEMA = CONFIG_RECOVERY_SCHEMA
    core._MAX_UPSTREAMS = _MAX_UPSTREAMS
    core._CONFIG_ALLOWED_TOP_LEVEL = set(_CONFIG_ALLOWED_TOP_LEVEL)
    core._RUNTIME_UPSTREAM_KEYS = set(_RUNTIME_UPSTREAM_KEYS)
    core._DISK_UPSTREAM_KEYS = set(_DISK_UPSTREAM_KEYS)
    core.DEFAULT_SETTINGS = _json_clone(DEFAULT_SETTINGS)

    core._json_clone = _json_clone
    core._validate_port = _validate_port
    core._validate_host = _validate_host
    core._validate_pac_path = _validate_pac_path
    core._validate_config_version = _validate_config_version
    core._validate_upstream_list = _validate_upstream_list
    core._validate_settings_model = _validate_settings_model
    core._validate_runtime_settings = _validate_runtime_settings
    core._validate_serialized_settings = _validate_serialized_settings
    core._disk_contains_plaintext_credentials = _disk_contains_plaintext_credentials

    core._fsync_parent_dir = _fsync_parent_dir
    core._atomic_write_bytes = _atomic_write_bytes
    core._atomic_write_json = _atomic_write_json
    core._atomic_write_text = _atomic_write_text

    core._safe_recovery_reason = _safe_recovery_reason
    core._load_serialized_settings = _load_serialized_settings
    core._runtime_settings_from_disk = _runtime_settings_from_disk
    core._quarantine_corrupt_file = _quarantine_corrupt_file
    core._record_configuration_recovery = _record_configuration_recovery
    core._recover_corrupt_settings = _recover_corrupt_settings

    core._dpapi_protect_text = _dpapi_protect_text
    core._dpapi_unprotect_text = _dpapi_unprotect_text
    core._decode_upstream_secrets = _decode_upstream_secrets
    core._encode_settings_for_disk = _encode_settings_for_disk

    core.load_settings = load_settings
    core.save_settings = save_settings
    return core
