# -*- coding: utf-8 -*-
"""
Кроссплатформенный прокси-движок для клиента (целевая ОС — Windows).

Слушает на localhost:
  * HTTP-прокси  (по умолчанию 127.0.0.1:8080)
  * SOCKS5-прокси (по умолчанию 127.0.0.1:1080)
  * отдаёт PAC-файл (по умолчанию http://127.0.0.1:8082/proxy.pac)

Всё, кроме исключений (no_proxy) и localhost, уходит на внешние прокси
из proxy_settings.json (список с failover). Исключения берутся из no_proxy.txt
и подставляются в PAC на лету — правки применяются без перезапуска.

Запуск вручную:
  pythonw.exe proxy_core.py --start     # запустить (+ включить системный прокси Windows)
  pythonw.exe proxy_core.py --stop      # остановить (+ выключить системный прокси)
  python proxy_core.py --status         # показать статус
"""

import base64
import io
import json
import os
import re
import select
import socket
import struct
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit


APP_VERSION = "0.2.2"

_STATE_FILES = (
    "proxy_settings.json", "no_proxy.txt", "proxy_core.pid", "proxy_core.log",
    "proxy_internet_backup.json", "proxy_env_backup.json",
)
_STATE_READY = False
_INSTALL_OWNER_MARKER = ".arvectum-install-owner"
_INSTALL_OWNER_VALUE = "ARVECTUM_PROXY_LAUNCHER_INSTALL_OWNER"
_LEGACY_INSTALL_OWNER_VALUES = {"ARVECTUM_PROXY_LAUNCHER_WINDOWS_RC2_1"}


def install_dir():
    """Directory containing this executable/source; never stores mutable state."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.realpath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def app_dir():
    """Compatibility alias for callers needing the executable directory."""
    return install_dir()


def is_windows():
    return os.name == "nt"


def data_dir():
    """Canonical per-user persistent state, shared by every copy of the EXE."""
    if is_windows():
        base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
        return os.path.join(base, "Arvectum", "ProxyLauncher")
    return install_dir()


def runtime_dir():
    return data_dir()


def _legacy_state_dirs():
    home = os.path.expanduser("~")
    local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
    candidates = [
        install_dir(),
        os.path.join(home, "Documents", "ArvectumProxyLauncher"),
        os.path.join(local, "ArvectumProxyLauncher"),
    ]
    seen = set()
    return [p for p in candidates if not (os.path.normcase(os.path.realpath(p)) in seen or seen.add(os.path.normcase(os.path.realpath(p))))]


def canonical_install_exe():
    """Return the owned installed EXE, if another copy is being launched."""
    if not getattr(sys, "frozen", False):
        return None
    canonical_dir = os.path.join(os.path.expanduser("~"), "Documents", "ArvectumProxyLauncher")
    # Existing accepted installations predating the marker are recognised only
    # at this exact, documented location.  A marker is then written there;
    # arbitrary Downloads/temp copies can never self-elect as canonical.
    if os.path.normcase(os.path.realpath(install_dir())) == os.path.normcase(os.path.realpath(canonical_dir)):
        try:
            marker = os.path.join(canonical_dir, _INSTALL_OWNER_MARKER)
            if not os.path.exists(marker):
                with io.open(marker, "w", encoding="ascii") as f:
                    f.write(_INSTALL_OWNER_VALUE)
        except Exception:
            pass
        return None
    candidates = [os.path.join(canonical_dir, "Arvectum Proxy Launcher.exe")]
    for candidate in candidates:
        marker = os.path.join(os.path.dirname(candidate), _INSTALL_OWNER_MARKER)
        if os.path.isfile(candidate) and os.path.isfile(marker):
            try:
                with io.open(marker, "r", encoding="ascii") as f:
                    marker_value = f.read().strip()
                    owned = marker_value == _INSTALL_OWNER_VALUE or marker_value in _LEGACY_INSTALL_OWNER_VALUES
                if owned and os.path.normcase(os.path.realpath(candidate)) != os.path.normcase(os.path.realpath(sys.executable)):
                    return os.path.realpath(candidate)
            except Exception:
                continue
    return None


def handoff_to_canonical_install():
    target = canonical_install_exe()
    if not target:
        return False
    try:
        subprocess.Popen([target], cwd=os.path.dirname(target),
                         creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
        return True
    except Exception:
        return False


def _copy_state_atomically(src, dst):
    import shutil
    tmp = dst + ".migrate.tmp"
    shutil.copyfile(src, tmp)
    with open(tmp, "rb") as f:
        f.read(1)
    os.replace(tmp, dst)


def _valid_state_file(name, path):
    if not os.path.isfile(path):
        return False
    if name in ("proxy_settings.json", "proxy_internet_backup.json", "proxy_env_backup.json", "proxy_core.pid"):
        try:
            with io.open(path, "r", encoding="utf-8") as f:
                value = json.load(f)
            return isinstance(value, dict) if name != "proxy_core.pid" else bool(value.get("pid"))
        except Exception:
            return False
    return True


def migration_error_path():
    return os.path.join(data_dir(), "state_migration_conflict.json")


def state_migration_blocked():
    return os.path.exists(migration_error_path())


def ensure_state_ready():
    """Create stable data storage and import validated legacy files once.

    Legacy copies are deliberately retained: a recovery backup is evidence and
    must never be deleted until a later exact rollback succeeds.
    """
    global _STATE_READY
    if _STATE_READY:
        return not state_migration_blocked()
    target = data_dir()
    try:
        os.makedirs(target, exist_ok=True)
        for name in _STATE_FILES:
            existing = os.path.join(target, name)
            sources = []
            for folder in _legacy_state_dirs():
                candidate = os.path.join(folder, name)
                if os.path.normcase(os.path.realpath(candidate)) == os.path.normcase(os.path.realpath(existing)):
                    continue
                if _valid_state_file(name, candidate):
                    sources.append(candidate)
            if not sources or os.path.exists(existing):
                continue
            # Two different recovery backups are ambiguous: preserve both and
            # block destructive recovery instead of guessing an "original".
            if name in ("proxy_internet_backup.json", "proxy_env_backup.json"):
                blobs = {open(p, "rb").read() for p in sources}
                if len(blobs) > 1:
                    with io.open(migration_error_path(), "w", encoding="utf-8") as f:
                        json.dump({"file": name, "sources": sources}, f, ensure_ascii=False)
                    _STATE_READY = True
                    return False
            _copy_state_atomically(sources[0], existing)
        _STATE_READY = True
        return True
    except Exception:
        return False


def settings_path():
    return os.path.join(data_dir(), "proxy_settings.json")


def no_proxy_path():
    return os.path.join(data_dir(), "no_proxy.txt")


def pid_path():
    return os.path.join(runtime_dir(), "proxy_core.pid")


def log_path():
    return os.path.join(runtime_dir(), "proxy_core.log")


def _log(msg):
    try:
        with io.open(log_path(), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))
    except Exception:
        pass


DEFAULT_SETTINGS = {
    "local_http_port": 8080,
    "local_socks_port": 1080,
    "local_pac_port": 8082,
    "pac_path": "/proxy.pac",
    "upstream": [
        {"host": "", "port": 8000, "username": "", "password": ""}
    ],
}


def _dpapi_protect_text(value):
    """Encrypt a UTF-8 secret with Windows DPAPI for the current user.

    The resulting blob may safely live in proxy_settings.json: it is bound to
    the Windows user profile and is not usable as the upstream password by
    simply copying the settings file to another account/machine.
    """
    if value in (None, ""):
        return ""
    if not is_windows():
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
            ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(DATA_BLOB),
        ]
        crypt32.CryptProtectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p

        raw = str(value).encode("utf-8")
        buf = (ctypes.c_byte * len(raw)).from_buffer_copy(raw)
        src = DATA_BLOB(len(raw), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
        dst = DATA_BLOB()
        CRYPTPROTECT_UI_FORBIDDEN = 0x1
        if not crypt32.CryptProtectData(
                ctypes.byref(src), "Arvectum Proxy Launcher upstream password", None,
                None, None, CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(dst)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            encrypted = ctypes.string_at(dst.pbData, dst.cbData)
            return base64.b64encode(encrypted).decode("ascii")
        finally:
            if dst.pbData:
                kernel32.LocalFree(ctypes.cast(dst.pbData, ctypes.c_void_p))
    except Exception as e:
        _log("DPAPI protect error: %r" % e)
        return None


def _dpapi_unprotect_text(value):
    if value in (None, ""):
        return ""
    if not is_windows():
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
            wintypes.DWORD, ctypes.POINTER(DATA_BLOB),
        ]
        crypt32.CryptUnprotectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p

        raw = base64.b64decode(str(value).encode("ascii"), validate=True)
        buf = (ctypes.c_byte * len(raw)).from_buffer_copy(raw)
        src = DATA_BLOB(len(raw), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
        dst = DATA_BLOB()
        description = wintypes.LPWSTR()
        CRYPTPROTECT_UI_FORBIDDEN = 0x1
        if not crypt32.CryptUnprotectData(
                ctypes.byref(src), ctypes.byref(description), None, None, None,
                CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(dst)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return ctypes.string_at(dst.pbData, dst.cbData).decode("utf-8")
        finally:
            if description:
                kernel32.LocalFree(ctypes.cast(description, ctypes.c_void_p))
            if dst.pbData:
                kernel32.LocalFree(ctypes.cast(dst.pbData, ctypes.c_void_p))
    except Exception as e:
        _log("DPAPI unprotect error: %r" % e)
        return None


def _decode_upstream_secrets(settings):
    data = json.loads(json.dumps(settings))
    decoded = []
    for raw in data.get("upstream") or []:
        up = dict(raw)
        credentials_blob = up.pop("credentials_dpapi", None)
        legacy_password_blob = up.pop("password_dpapi", None)
        if credentials_blob not in (None, ""):
            plain = _dpapi_unprotect_text(credentials_blob)
            if plain is None:
                _log("settings contain unreadable DPAPI credentials; leaving auth empty")
                up["username"] = ""
                up["password"] = ""
            else:
                try:
                    auth = json.loads(plain)
                    up["username"] = str(auth.get("username") or "")
                    up["password"] = str(auth.get("password") or "")
                except Exception as e:
                    _log("DPAPI credentials payload is invalid: %r" % e)
                    up["username"] = ""
                    up["password"] = ""
        elif legacy_password_blob not in (None, ""):
            # Compatibility with early RC2.1 development builds that encrypted
            # only password.  A later Save migrates to credentials_dpapi.
            plain = _dpapi_unprotect_text(legacy_password_blob)
            up["username"] = str(up.get("username") or "")
            up["password"] = "" if plain is None else plain
        else:
            # Backward compatibility with RC2 plaintext settings.  The first
            # successful load on Windows transparently migrates username and
            # password to a current-user DPAPI blob.
            up["username"] = str(up.get("username") or "")
            up["password"] = str(up.get("password") or "")
        decoded.append(up)
    data["upstream"] = decoded
    return data


def _encode_settings_for_disk(settings):
    data = json.loads(json.dumps(settings))
    encoded = []
    for raw in data.get("upstream") or []:
        up = dict(raw)
        username = str(up.pop("username", "") or "")
        password = str(up.pop("password", "") or "")
        up.pop("credentials_dpapi", None)
        up.pop("password_dpapi", None)
        if is_windows():
            if username or password:
                payload = json.dumps(
                    {"username": username, "password": password},
                    ensure_ascii=False, separators=(",", ":"))
                protected = _dpapi_protect_text(payload)
                if protected is None:
                    raise RuntimeError("Windows DPAPI could not protect upstream credentials")
                up["credentials_dpapi"] = protected
        else:
            # Source-level tests on non-Windows keep the legacy representation.
            # Client builds are Windows-only and therefore always use DPAPI.
            up["username"] = username
            up["password"] = password
        encoded.append(up)
    data["upstream"] = encoded
    return data


def load_settings():
    data = json.loads(json.dumps(DEFAULT_SETTINGS))
    p = settings_path()
    if not os.path.exists(p):
        return data
    try:
        with io.open(p, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            data.update(loaded)
        runtime = _decode_upstream_secrets(data)
        # Transparent RC2 -> RC2.1 migration: an existing plaintext password is
        # protected as soon as the new Windows build first reads the settings.
        # If DPAPI is unavailable we keep the old file untouched so the proxy
        # does not lose credentials; the failure is visible in proxy_core.log.
        legacy_plaintext = any(
            isinstance(up, dict)
            and "credentials_dpapi" not in up
            and "password_dpapi" not in up
            and (bool(up.get("username")) or bool(up.get("password")))
            for up in (loaded.get("upstream") or [])
        ) if isinstance(loaded, dict) else False
        if legacy_plaintext and is_windows():
            if save_settings(runtime):
                _log("legacy plaintext upstream credentials migrated to DPAPI")
            else:
                _log("legacy plaintext upstream credentials migration to DPAPI failed")
        return runtime
    except Exception as e:
        _log("settings read error: %r" % e)
    return data


def save_settings(settings):
    tmp = settings_path() + ".tmp"
    try:
        disk_settings = _encode_settings_for_disk(settings)
        with io.open(tmp, "w", encoding="utf-8") as f:
            json.dump(disk_settings, f, indent=2, ensure_ascii=False)
            f.flush()
        os.replace(tmp, settings_path())
        _log("settings saved")
        return True
    except Exception as e:
        _log("settings save error: %r" % e)
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False


DEFAULT_NO_PROXY = [
    "localhost",
    "127.0.0.1",
    "::1",
    "*.local",
    "10.*",
    "172.16.*", "172.17.*", "172.18.*", "172.19.*",
    "172.20.*", "172.21.*", "172.22.*", "172.23.*",
    "172.24.*", "172.25.*", "172.26.*", "172.27.*",
    "172.28.*", "172.29.*", "172.30.*", "172.31.*",
    "192.168.*",
]


def load_no_proxy():
    domains = []
    p = no_proxy_path()
    if os.path.exists(p):
        try:
            with io.open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    domains.append(line)
        except Exception as e:
            _log("no_proxy read error: %r" % e)
    return domains


def save_no_proxy(domains):
    try:
        with io.open(no_proxy_path(), "w", encoding="utf-8") as f:
            f.write("# Список исключений (no_proxy). По одному домену на строку.\n")
            f.write("# Сайты из списка открываются напрямую, минуя прокси.\n")
            f.write("# Строки, начинающиеся с #, игнорируются.\n")
            f.write("# Изменения применяются сразу, перезапуск не нужен.\n")
            f.write("\n")
            for d in domains:
                f.write(d + "\n")
        _log("no_proxy saved: %d domains" % len(domains))
    except Exception as e:
        _log("no_proxy save error: %r" % e)


def clean_domain(value):
    """Из сырого ввода (URL, host:port) вытащить чистый домен.
    Поддерживает IPv6 (::1, [::1]:порт) и маски (*.local, 10.*)."""
    d = value.strip().lower()
    d = d.split("#")[0].strip()
    if "://" in d:
        d = d.split("://", 1)[1]
    d = d.split("/")[0]
    d = d.strip()
    if not d:
        return ""
    if d.startswith("["):
        return d.lstrip("[").split("]")[0]
    colon = d.count(":")
    if colon == 1:
        host, _, port = d.rpartition(":")
        if port.isdigit():
            return host
    # 0 двоеточий — обычный хост/маска; 2+ — IPv6-адрес, оставляем как есть
    return d


def _normalize_host(host):
    host = (host or "").strip().lower().rstrip(".")
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    return host


def host_bypasses_proxy(host):
    """Единая проверка no_proxy для PAC-клиентов, HTTP_PROXY и SOCKS5.

    Важно: исключения должны работать не только в PAC. Некоторые Windows-
    приложения игнорируют PAC и используют HTTP_PROXY/HTTPS_PROXY; в таком
    случае запрос всё равно приходит в локальный proxy, и движок обязан сам
    отправить исключённый хост напрямую.
    """
    host = _normalize_host(host)
    if not host:
        return False
    patterns = list(DEFAULT_NO_PROXY)
    for item in load_no_proxy():
        if item not in patterns:
            patterns.append(item)
    for raw in patterns:
        pattern = _normalize_host(raw)
        if not pattern:
            continue
        if pattern.startswith("."):
            pattern = pattern[1:]
        if "*" in pattern or "?" in pattern:
            regex = "^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".") + "$"
            if re.match(regex, host, flags=re.IGNORECASE):
                return True
        elif host == pattern or host.endswith("." + pattern):
            return True
    return False


def build_pac():
    """PAC: локальные сервисы (localhost/внутренние сети) обходятся всегда,
    остальные исключения из no_proxy.txt добавляются сразу."""
    direct = list(DEFAULT_NO_PROXY)
    for d in load_no_proxy():
        if d not in direct:
            direct.append(d)
    lines = "\n".join(
        '        "%s",' % d.replace("\\", "\\\\").replace('"', '\\"') for d in direct
    )
    port = int(load_settings().get("local_http_port", 8080))
    return (
        "function FindProxyForURL(url, host) {\n"
        "    // Исключения no_proxy — синтезируется автоматически (localhost и внутренние сети всегда в обход)\n"
        "    var direct = [\n"
        + lines +
        "\n    ];\n"
        "    for (var i = 0; i < direct.length; i++) {\n"
        "        var d = direct[i];\n"
        "        if (d.indexOf('*') !== -1) {\n"
        "            if (shExpMatch(host, d)) return 'DIRECT';\n"
        "        } else if (host === d || shExpMatch(host, '*.' + d)\n"
        "                   || (host.indexOf(':') !== -1 && host === '[' + d + ']')) {\n"
        "            return 'DIRECT';\n"
        "        }\n"
        "    }\n"
        "    return 'PROXY 127.0.0.1:%d';\n"
        "}\n" % port
    )


# ---------------------------------------------------------------------------
# Системный прокси Windows (HKCU Internet Settings)
# ---------------------------------------------------------------------------

_INTERNET_BACKUP_PATH = "proxy_internet_backup.json"
_PROXY_ENV_NAMES = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY")


def _env_backup_path():
    return os.path.join(runtime_dir(), "proxy_env_backup.json")


def _internet_backup_path():
    return os.path.join(runtime_dir(), _INTERNET_BACKUP_PATH)


def _read_internet_settings():
    values = {}
    if not is_windows():
        return values
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings") as key:
            for name in ("AutoConfigURL", "ProxyEnable", "ProxyServer", "ProxyOverride", "AutoDetect"):
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                    values[name] = {"exists": True, "value": value}
                except FileNotFoundError:
                    values[name] = {"exists": False, "value": None}
        return values
    except Exception as e:
        _log("internet settings read error: %r" % e)
        return None


def _valid_internet_backup(values):
    required = {"AutoConfigURL", "ProxyEnable", "ProxyServer", "ProxyOverride", "AutoDetect"}
    return isinstance(values, dict) and required.issubset(values.keys())


def _known_internet_backup_paths():
    """All current and legacy locations which can prove a WinINET rollback."""
    paths = [_internet_backup_path()]
    paths.extend(os.path.join(folder, _INTERNET_BACKUP_PATH) for folder in _legacy_state_dirs())
    seen = set()
    return [path for path in paths if not (
        os.path.normcase(os.path.realpath(path)) in seen or
        seen.add(os.path.normcase(os.path.realpath(path))))]


def _valid_internet_backup_at(path):
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            return _valid_internet_backup(json.load(f))
    except Exception:
        return False


def _any_known_internet_backup_exists():
    # An invalid/unknown backup is still evidence that destructive cleanup is
    # ambiguous.  It must lead to NETWORK_DIAGNOSTIC, never orphan cleanup.
    return any(os.path.exists(path) for path in _known_internet_backup_paths())


def _exact_arvectum_pac_url(value, settings=None):
    """Compare the current PAC with our URL structurally, never by substring."""
    settings = settings or load_settings()
    try:
        actual = urlsplit(str(value or ""))
        expected = urlsplit(pac_url(settings))
        return bool(
            actual.scheme.lower() == expected.scheme.lower() == "http" and
            actual.hostname == expected.hostname == "127.0.0.1" and
            actual.port == expected.port and
            actual.path == expected.path and
            not actual.query and not actual.fragment and
            actual.username is None and actual.password is None
        )
    except (TypeError, ValueError):
        return False


def _save_internet_backup():
    """Сохраняет исходные WinINET-настройки ДО любых изменений.

    Если резервную копию создать нельзя, прокси не включается: лучше не менять
    сеть вообще, чем потом не суметь восстановить пользовательские настройки.
    """
    path = _internet_backup_path()
    if os.path.exists(path):
        try:
            with io.open(path, "r", encoding="utf-8") as f:
                if _valid_internet_backup(json.load(f)):
                    return True
        except Exception:
            pass
        _log("internet settings backup is invalid; refusing to overwrite it")
        return False
    values = _read_internet_settings()
    if not _valid_internet_backup(values):
        _log("internet settings backup aborted: registry snapshot unavailable")
        return False
    tmp = path + ".tmp"
    try:
        with io.open(tmp, "w", encoding="utf-8") as f:
            json.dump(values, f, ensure_ascii=False)
            f.flush()
        os.replace(tmp, path)
        return True
    except Exception as e:
        _log("internet settings backup error: %r" % e)
        try:
            os.remove(tmp)
        except Exception:
            pass
        return False


def _restore_internet_backup():
    path = _internet_backup_path()
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            values = json.load(f)
    except Exception:
        values = None
    if not _valid_internet_backup(values):
        # Без локального backup нельзя доказать, что текущий WinINET/PAC
        # принадлежит именно этому экземпляру Launcher. Другой установленный
        # экземпляр использует тот же localhost PAC URL, поэтому совпадение URL
        # само по себе недостаточно для безопасного удаления. Чистый rollback
        # всегда является no-op и не трогает чужую конфигурацию.
        _log("internet settings backup missing/invalid; ownership unverified, no WinINET values changed")
        return True
    ok = True
    for name, item in values.items():
        if not isinstance(item, dict) or not item.get("exists"):
            ok = _reg_del(name) and ok
            continue
        value = item.get("value")
        typ = "REG_DWORD" if name in ("ProxyEnable", "AutoDetect") else "REG_SZ"
        ok = _reg_set(name, str(int(value)) if typ == "REG_DWORD" else str(value), typ) and ok
    if ok:
        try:
            os.remove(path)
        except Exception as e:
            # A remaining backup means recovery is not complete.  Never report
            # success while the next GUI start will correctly enter recovery.
            _log("internet settings restored but backup removal failed: %r" % e)
            return False
    else:
        _log("internet settings restore incomplete; keeping backup for retry")
    return ok


def _read_user_env(name):
    """Возвращает пользовательскую переменную окружения из реестра."""
    if not is_windows():
        return False, ""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
        return True, str(value)
    except FileNotFoundError:
        return False, ""
    except Exception as e:
        _log("env read error (%s): %r" % (name, e))
        return False, ""


def _write_user_env(name, value):
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        return True
    except Exception as e:
        _log("env write error (%s): %r" % (name, e))
        return False


def _delete_user_env(name):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        _log("env delete error (%s): %r" % (name, e))
        return False


def _broadcast_environment_change():
    if not is_windows():
        return
    try:
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 2, 5000, None)
    except Exception as e:
        _log("env broadcast error: %r" % e)


def _enable_client_proxy_env(port):
    """Даёт нативным клиентам стандартный proxy env с безопасным rollback."""
    backup_path = _env_backup_path()
    backup = None
    if os.path.exists(backup_path):
        try:
            with io.open(backup_path, "r", encoding="utf-8") as f:
                candidate = json.load(f)
            if isinstance(candidate, dict) and all(name in candidate for name in _PROXY_ENV_NAMES):
                backup = candidate
        except Exception:
            pass
        if backup is None:
            _log("env backup is invalid; refusing to overwrite user environment")
            return False
    else:
        backup = {}
        for name in _PROXY_ENV_NAMES:
            exists, value = _read_user_env(name)
            backup[name] = {"exists": exists, "value": value}
        tmp = backup_path + ".tmp"
        try:
            with io.open(tmp, "w", encoding="utf-8") as f:
                json.dump(backup, f, ensure_ascii=False)
                f.flush()
            os.replace(tmp, backup_path)
        except Exception as e:
            _log("env backup error: %r" % e)
            try:
                os.remove(tmp)
            except Exception:
                pass
            return False

    local_proxy = "http://127.0.0.1:%d" % int(port)
    ok = True
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        ok = _write_user_env(name, local_proxy) and ok

    direct = _combined_no_proxy(backup)
    ok = _write_user_env("NO_PROXY", ",".join(direct)) and ok
    if not ok:
        _log("client proxy environment update incomplete")
        _disable_client_proxy_env()
        return False
    _broadcast_environment_change()
    _log("client proxy environment enabled: %s" % local_proxy)
    return True


def _combined_no_proxy(backup):
    direct = []
    existing_no_proxy = str((backup.get("NO_PROXY") or {}).get("value") or "")
    for item in existing_no_proxy.split(",") + DEFAULT_NO_PROXY + load_no_proxy():
        item = item.strip()
        if item and item not in direct:
            direct.append(item)
    return direct


def sync_client_no_proxy():
    """Обновляет активный NO_PROXY после правки исключений без restart.

    Источником пользовательского NO_PROXY остаётся исходный backup, поэтому
    удаление домена из Arvectum не удаляет исключение, которое существовало у
    пользователя ещё до запуска приложения.
    """
    if not is_windows():
        return True
    backup_path = _env_backup_path()
    if not os.path.exists(backup_path):
        return True
    try:
        with io.open(backup_path, "r", encoding="utf-8") as f:
            backup = json.load(f)
    except Exception as e:
        _log("NO_PROXY sync backup read error: %r" % e)
        return False
    if not isinstance(backup, dict) or not all(name in backup for name in _PROXY_ENV_NAMES):
        _log("NO_PROXY sync aborted: env backup is invalid")
        return False
    if not _write_user_env("NO_PROXY", ",".join(_combined_no_proxy(backup))):
        return False
    _broadcast_environment_change()
    _log("client NO_PROXY synchronized")
    return True


def _disable_client_proxy_env():
    backup_path = _env_backup_path()
    try:
        with io.open(backup_path, "r", encoding="utf-8") as f:
            backup = json.load(f)
    except Exception:
        backup = None
    if not isinstance(backup, dict) or not all(name in backup for name in _PROXY_ENV_NAMES):
        return False
    ok = True
    for name in _PROXY_ENV_NAMES:
        item = backup.get(name) or {}
        if item.get("exists"):
            ok = _write_user_env(name, str(item.get("value", ""))) and ok
        else:
            ok = _delete_user_env(name) and ok
    if ok:
        try:
            os.remove(backup_path)
        except Exception as e:
            _log("client proxy environment restored but backup removal failed: %r" % e)
            return False
        _broadcast_environment_change()
        _log("client proxy environment restored")
    else:
        _log("client proxy environment restore incomplete; keeping backup for retry")
    return ok


def pac_url(settings):
    path = str(settings.get("pac_path", "/proxy.pac") or "/proxy.pac")
    if not path.startswith("/"):
        path = "/" + path
    return "http://127.0.0.1:%d%s" % (int(settings.get("local_pac_port", 8082)), path)


def _reg_set(name, data, typ):
    if not is_windows():
        return False
    try:
        import winreg
        reg_type = winreg.REG_DWORD if typ == "REG_DWORD" else winreg.REG_SZ
        value = int(data) if reg_type == winreg.REG_DWORD else str(data)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings") as key:
            winreg.SetValueEx(key, name, 0, reg_type, value)
        return True
    except Exception as e:
        _log("registry set error (%s): %r" % (name, e))
        return False


def _reg_del(name):
    if not is_windows():
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", 0, winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, name)
            except FileNotFoundError:
                pass
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        _log("registry delete error (%s): %r" % (name, e))
        return False


def _refresh_internet():
    """Заставить WinINET (браузеры/систему) перечитать настройки прокси."""
    if not is_windows():
        return
    try:
        import ctypes
        from ctypes import wintypes

        INTERNET_OPTION_SETTINGS_CHANGED = 39
        INTERNET_OPTION_REFRESH = 37
        wininet = ctypes.windll.wininet
        wininet.InternetOpenW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD]
        wininet.InternetOpenW.restype = wintypes.HANDLE
        wininet.InternetSetOptionW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD]
        wininet.InternetSetOptionW.restype = wintypes.BOOL
        wininet.InternetCloseHandle.argtypes = [wintypes.HANDLE]
        wininet.InternetCloseHandle.restype = wintypes.BOOL
        h = wininet.InternetOpenW("ArvectumProxyLauncher", 0, None, None, 0)
        if h:
            wininet.InternetSetOptionW(h, INTERNET_OPTION_SETTINGS_CHANGED, None, 0)
            wininet.InternetSetOptionW(h, INTERNET_OPTION_REFRESH, None, 0)
            wininet.InternetCloseHandle(h)
    except Exception as e:
        _log("refresh error: %r" % e)


def _ensure_local_files():
    """Initialize canonical state and copy bundled defaults into it."""
    if not ensure_state_ready():
        return False
    if not getattr(sys, "frozen", False) or not hasattr(sys, "_MEIPASS"):
        return True
    for name in ("no_proxy.txt", "proxy_settings.json"):
        target = os.path.join(data_dir(), name)
        if not os.path.exists(target):
            src = os.path.join(sys._MEIPASS, name)
            try:
                if os.path.exists(src):
                    import shutil
                    shutil.copyfile(src, target)
            except Exception as e:
                _log("ensure files error: %r" % e)
                return False
    return True


_RECOVERY_RUN_VALUE = "ArvectumProxyLauncherRecovery"
_RECOVERY_CURRENT_OWNED = "CURRENT_OWNED"
_RECOVERY_LEGACY_ARVECTUM = "LEGACY_ARVECTUM"
_RECOVERY_FOREIGN = "FOREIGN"
_RECOVERY_MISSING = "MISSING"


def _self_start_command():
    if getattr(sys, "frozen", False):
        return '"%s" --start' % os.path.realpath(sys.executable)
    return '"%s" "%s" --start' % (sys.executable, os.path.realpath(__file__))


def _normalize_command(value):
    return " ".join(str(value or "").replace("'", '"').split()).strip().lower()


def _known_legacy_recovery_dirs():
    home = os.path.expanduser("~")
    local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
    candidates = [
        install_dir(),
        os.path.join(home, "Documents", "ArvectumProxyLauncher"),
        os.path.join(local, "ArvectumProxyLauncher"),
        os.path.join(local, "Arvectum", "ProxyLauncher"),
    ]
    return {os.path.normcase(os.path.realpath(path)) for path in candidates}


def _recovery_command_target(command):
    """Return the explicit quoted executable/batch target of a Run command."""
    match = re.match(r'^\s*"([^"]+)"(?:\s+(.*))?\s*$', str(command or ""))
    if not match:
        return None, ""
    return os.path.realpath(match.group(1)), (match.group(2) or "").strip()


def classify_recovery_autostart(command):
    """Classify the shared recovery Run value without heuristic substring checks."""
    if command is None or not str(command).strip():
        return _RECOVERY_MISSING
    if _normalize_command(command) == _normalize_command(_self_start_command()):
        return _RECOVERY_CURRENT_OWNED
    target, args = _recovery_command_target(command)
    if not target:
        return _RECOVERY_FOREIGN
    parent = os.path.normcase(os.path.realpath(os.path.dirname(target)))
    name = os.path.basename(target).lower()
    if parent not in _known_legacy_recovery_dirs():
        return _RECOVERY_FOREIGN
    if name == "arvectum proxy launcher.exe" and _normalize_command(args) == "--start":
        return _RECOVERY_LEGACY_ARVECTUM
    if name == "restore_network.bat" and not args:
        return _RECOVERY_LEGACY_ARVECTUM
    return _RECOVERY_FOREIGN


def _recovery_legacy_process_active(command):
    """Return True only if that exact legacy Run command is currently executing.

    If process inspection fails, fail closed: do not replace a potentially live
    legacy recovery owner.
    """
    target, _ = _recovery_command_target(command)
    if not target or not os.path.exists(target):
        return False
    if not is_windows():
        return True
    try:
        import ctypes
        from ctypes import wintypes
        # Use WMIC-free PowerShell only as a bounded read-only process query.
        script = (
            "$p=Get-CimInstance Win32_Process -ErrorAction Stop | Where-Object "
            "{ $_.ExecutablePath -and [IO.Path]::GetFullPath($_.ExecutablePath) -ieq "
            "[IO.Path]::GetFullPath($args[0]) -and $_.CommandLine -eq $args[1] }; "
            "if($p){exit 10}else{exit 0}"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-Command", script, target, str(command)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5,
        )
        return result.returncode != 0
    except Exception as e:
        _log("legacy recovery process inspection failed; migration blocked: %r" % e)
        return True


def _get_recovery_run_value():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run") as key:
            return winreg.QueryValueEx(key, _RECOVERY_RUN_VALUE)[0]
    except FileNotFoundError:
        return None
    except Exception as e:
        _log("recovery autostart read error: %r" % e)
        return False


def _set_recovery_run_value(value):
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run") as key:
            winreg.SetValueEx(key, _RECOVERY_RUN_VALUE, 0, winreg.REG_SZ, value)
        return True
    except Exception as e:
        _log("recovery autostart write error: %r" % e)
        return False


def _enable_recovery_autostart():
    """Страховочный запуск после reboot, пока системный proxy активен.

    Это отдельный механизм от пользовательской галочки автозапуска. Он нужен,
    чтобы после перезагрузки не остался PAC на localhost без работающего core.
    Чужое Run-value с тем же именем никогда не перезаписывается.
    """
    if not is_windows():
        return True
    expected = _self_start_command()
    current = _get_recovery_run_value()
    if current is False:
        return False
    classification = classify_recovery_autostart(current)
    if classification == _RECOVERY_FOREIGN:
        _log("recovery autostart conflicts with a foreign command; refusing overwrite")
        return False
    if classification == _RECOVERY_LEGACY_ARVECTUM:
        if _recovery_legacy_process_active(current):
            _log("legacy Arvectum recovery autostart is active; migration blocked")
            return False
        _log("legacy Arvectum recovery autostart found: %s" % _normalize_command(current))
        if not _set_recovery_run_value(expected):
            return False
        if classify_recovery_autostart(_get_recovery_run_value()) != _RECOVERY_CURRENT_OWNED:
            _set_recovery_run_value(current)
            _log("legacy Arvectum recovery autostart migration verification failed")
            return False
        if not os.path.exists(_recovery_command_target(current)[0]):
            _log("stale legacy Arvectum recovery autostart migrated")
        else:
            _log("legacy Arvectum recovery autostart migrated to current installation")
        return True
    if classification in (_RECOVERY_MISSING, _RECOVERY_CURRENT_OWNED):
        if not _set_recovery_run_value(expected):
            return False
        if classify_recovery_autostart(_get_recovery_run_value()) != _RECOVERY_CURRENT_OWNED:
            _log("recovery autostart write verification failed")
            return False
        return True
    return False


def _disable_recovery_autostart():
    if not is_windows():
        return True
    try:
        import winreg
        path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE) as key:
            try:
                current, _ = winreg.QueryValueEx(key, _RECOVERY_RUN_VALUE)
            except FileNotFoundError:
                return True
            if _normalize_command(current) != _normalize_command(_self_start_command()):
                _log("recovery autostart belongs to another command; leaving it untouched")
                return True
            winreg.DeleteValue(key, _RECOVERY_RUN_VALUE)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        _log("recovery autostart disable error: %r" % e)
        return False


def enable_system_proxy():
    settings = load_settings()
    url = pac_url(settings)
    if not is_windows():
        _log("system proxy: (non-Windows) %s" % url)
        return True
    if not _save_internet_backup():
        _log("system proxy enable aborted: cannot create safe backup")
        return False
    # PAC и старый manual ProxyServer не должны работать параллельно.
    ok = _reg_set("AutoConfigURL", url, "REG_SZ")
    ok = _reg_set("ProxyEnable", "0", "REG_DWORD") and ok
    ok = _enable_client_proxy_env(int(settings.get("local_http_port", 8080))) and ok
    ok = _enable_recovery_autostart() and ok
    if not ok:
        _restore_internet_backup()
        _disable_client_proxy_env()
        _disable_recovery_autostart()
        _refresh_internet()
        _log("system proxy enable failed; rolled back")
        return False
    _refresh_internet()
    _log("system proxy enabled: %s" % url)
    return True


def disable_system_proxy():
    if not is_windows():
        _log("system proxy: (non-Windows) disabled")
        return True
    was_active = system_proxy_enabled()
    valid_backup = _valid_internet_backup_at(_internet_backup_path())
    ok = _restore_internet_backup()
    env_ok = _disable_client_proxy_env()
    # Если собственный PAC уже снят и env backup отсутствует/восстановлен,
    # страховочный Run-value больше не нужен. При неполном rollback оставляем
    # его, чтобы следующий вход в Windows не получил мёртвый localhost proxy.
    env_pending = os.path.exists(_env_backup_path())
    still_active = system_proxy_enabled()
    if not still_active and (env_ok or not env_pending):
        _disable_recovery_autostart()
    _refresh_internet()
    still_active = system_proxy_enabled()
    if still_active:
        if valid_backup:
            _log("system proxy restore incomplete")
        else:
            _log("system proxy restore skipped: ownership unverified")
    elif was_active or valid_backup:
        _log("system proxy restored successfully")
    else:
        _log("system proxy already inactive")
    return ok and (env_ok or not env_pending) and not still_active


def system_proxy_enabled():
    if not is_windows():
        return False
    values = _read_internet_settings() or {}
    item = values.get("AutoConfigURL") or {}
    return bool(item.get("exists") and _exact_arvectum_pac_url(item.get("value")))


def network_restore_pending():
    """Есть ли признаки незавершённого восстановления сети.

    Backup-файлы удаляются только после успешного restore. Поэтому их
    наличие после команды --stop/--rollback — надёжный сигнал, что нельзя
    сообщать пользователю об успешном восстановлении и тем более удалять
    каталог приложения.
    """
    if not is_windows():
        return False
    return (
        os.path.exists(_internet_backup_path())
        or os.path.exists(_env_backup_path())
    )


def stale_system_proxy():
    """PAC points at us, but no owned engine or provable rollback exists."""
    return (system_proxy_enabled() and not is_running() and
            not network_restore_pending() and not state_migration_blocked())


def orphaned_arvectum_pac():
    """True only for the narrowly proven, dead Arvectum localhost PAC case."""
    if not is_windows() or state_migration_blocked():
        return False
    values = _read_internet_settings()
    item = (values or {}).get("AutoConfigURL") or {}
    if not item.get("exists") or not _exact_arvectum_pac_url(item.get("value")):
        return False
    if proxy_listener_active() or is_running():
        return False
    if _any_known_internet_backup_exists():
        return False
    # A non-canonical copy should hand off to the owned Documents install;
    # never let it clean state while that canonical instance is available.
    if canonical_install_exe():
        return False
    return True


def _write_orphaned_pac_snapshot(values):
    try:
        os.makedirs(data_dir(), exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S") + "-%d" % int(time.time() * 1000 % 1000)
        path = os.path.join(data_dir(), "orphaned_arvectum_pac_%s.json" % stamp)
        snapshot = {
            "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "reason": "orphaned_arvectum_pac",
            "internet_settings": values,
            "expected_pac_url": pac_url(load_settings()),
        }
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        return path
    except Exception as e:
        _log("orphan PAC diagnostic snapshot error: %r" % e)
        return None


def clear_orphaned_arvectum_pac():
    """Delete only a re-verified dead Arvectum AutoConfigURL entry.

    This is deliberately not a network reset and it never alters environment
    variables.  A changed registry value is treated as a race and aborts.
    """
    if not orphaned_arvectum_pac():
        _log("orphan PAC cleanup skipped: ownership conditions are not proven")
        return False
    values = _read_internet_settings()
    item = (values or {}).get("AutoConfigURL") or {}
    if not item.get("exists") or not _exact_arvectum_pac_url(item.get("value")):
        _log("orphan PAC cleanup aborted: AutoConfigURL changed before mutation")
        return False
    if not _write_orphaned_pac_snapshot(values):
        _log("orphan PAC cleanup aborted: diagnostic snapshot was not written")
        return False
    if not _reg_del("AutoConfigURL"):
        _log("orphan PAC cleanup incomplete: AutoConfigURL delete failed")
        return False
    _refresh_internet()
    if system_proxy_enabled():
        _log("orphan PAC cleanup incomplete: PAC is still active")
        return False
    _log("orphan Arvectum PAC removed safely")
    return True


# ---------------------------------------------------------------------------
# Собственно прокси
# ---------------------------------------------------------------------------


class ProxyCore:
    def __init__(self, settings=None):
        self.settings = settings if settings is not None else load_settings()
        self._stop = threading.Event()
        self._socks = []
        self._threads = []
        self._upstreams = self._build_upstreams()

    def _build_upstreams(self):
        out = []
        for up in self.settings.get("upstream") or []:
            host = (up.get("host") or "").strip()
            if not host:
                continue
            raw = ("%s:%s" % (up.get("username") or "", up.get("password") or "")).encode("utf-8")
            token = base64.b64encode(raw).decode("ascii")
            try:
                port = int(up.get("port", 8000))
            except (TypeError, ValueError):
                port = 8000
            out.append((host, port, token))
        return out

    # -- помощь ------------------------------------------------------------

    @staticmethod
    def _send_error(client, code, text):
        reason = {400: "Bad Request", 502: "Bad Gateway"}.get(code, "Error")
        body = (text or reason).encode("utf-8")
        try:
            client.sendall(
                b"HTTP/1.1 %d %s\r\nContent-Type: text/plain; charset=utf-8\r\n"
                b"Content-Length: %d\r\nConnection: close\r\n\r\n%s"
                % (code, reason.encode("ascii"), len(body), body)
            )
        except Exception:
            pass

    @staticmethod
    def _relay(src, dst, stop):
        try:
            while not stop.is_set():
                try:
                    r, _, _ = select.select([src, dst], [], [], 300)
                except (OSError, ValueError):
                    return
                if not r:
                    continue
                for s in r:
                    try:
                        data = s.recv(65536)
                    except OSError:
                        return
                    if not data:
                        return
                    (dst if s is src else src).sendall(data)
        except Exception:
            pass
        finally:
            for s in (src, dst):
                try:
                    s.close()
                except Exception:
                    pass

    # -- HTTP ----------------------------------------------------------------

    def _handle_http(self, client):
        try:
            client.settimeout(30)
            data = client.recv(8192)
            if not data:
                return
            first = data.split(b"\r\n", 1)[0]
            is_connect = first.startswith(b"CONNECT")

            if is_connect:
                try:
                    dest = first.split(b" ")[1].decode()
                    host, port_s = dest.rsplit(":", 1)
                    port = int(port_s)
                except Exception:
                    self._send_error(client, 400, "Bad CONNECT")
                    return
                method = None
                path = None
            else:
                parts = first.split(b" ")
                if len(parts) < 2:
                    self._send_error(client, 400, "Bad request")
                    return
                method = parts[0]
                url = parts[1].decode()
                if url.startswith("http://"):
                    url = url[7:]
                elif url.startswith("https://"):
                    url = url[8:]
                slash = url.find("/")
                hostport = url if slash == -1 else url[:slash]
                path = "/" if slash == -1 else url[slash:]
                if ":" in hostport:
                    host, port_s = hostport.rsplit(":", 1)
                    try:
                        port = int(port_s)
                    except ValueError:
                        port = 80
                else:
                    host = hostport
                    port = 80

            host = _normalize_host(host)
            if host_bypasses_proxy(host):
                # no_proxy — напрямую, без внешних прокси
                try:
                    direct = socket.create_connection((host, port), timeout=15)
                except Exception:
                    self._send_error(client, 502, "Localhost connection failed")
                    return
                direct.settimeout(300)
                if is_connect:
                    client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                else:
                    rest = data.split(b"\r\n", 1)[1]
                    data = method + b" " + path.encode() + b" HTTP/1.1\r\n" + rest
                    direct.sendall(data)
                self._relay(direct, client, self._stop)
            else:
                upstream = None
                for host_u, pport, token in self._upstreams:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(15)
                        s.connect((host_u, pport))
                        if is_connect:
                            # Формируем чистый CONNECT для внешнего HTTP-
                            # прокси. Нельзя пересылать служебные заголовки
                            # клиента как есть: некоторые upstream-прокси
                            # из-за этого направляют TLS-туннель неверно.
                            target = ("%s:%d" % (host, port)).encode("idna")
                            request = (b"CONNECT " + target + b" HTTP/1.1\r\n"
                                       b"Host: " + target + b"\r\n"
                                       b"Proxy-Authorization: Basic " + token.encode("ascii") +
                                       b"\r\n\r\n")
                        else:
                            hdr = b"Proxy-Authorization: Basic " + token.encode("ascii") + b"\r\n"
                            request = data.replace(b"\r\n", b"\r\n" + hdr, 1)
                        s.sendall(request)
                        upstream = s
                        break
                    except Exception:
                        try:
                            s.close()
                        except Exception:
                            pass
                        continue
                if upstream is None:
                    self._send_error(client, 502, "All external proxies unreachable")
                    return
                self._relay(upstream, client, self._stop)
        except OSError:
            try:
                self._send_error(client, 502, "Proxy error")
            except Exception:
                pass
        finally:
            try:
                client.close()
            except Exception:
                pass

    # -- SOCKS5 ---------------------------------------------------------------

    def _handle_socks(self, client):
        try:
            client.settimeout(15)
            if client.recv(1) != b"\x05":
                return
            nmethods = client.recv(1)[0]
            client.recv(nmethods)
            client.sendall(b"\x05\x00")
            data = client.recv(4)
            if len(data) < 4 or data[0] != 5:
                return
            atype = data[3]
            if atype == 1:
                host = socket.inet_ntoa(client.recv(4))
            elif atype == 3:
                n = client.recv(1)[0]
                host = client.recv(n).decode()
            elif atype == 4:
                host = socket.inet_ntop(socket.AF_INET6, client.recv(16))
            else:
                return
            port = struct.unpack(">H", client.recv(2))[0]

            upstream = None
            host = _normalize_host(host)
            if host_bypasses_proxy(host):
                try:
                    upstream = socket.create_connection((host, port), timeout=15)
                except Exception:
                    upstream = None
            else:
                for host_u, pport, token in self._upstreams:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(15)
                        s.connect((host_u, pport))
                        cr = (
                            "CONNECT %s:%d HTTP/1.1\r\n"
                            "Proxy-Authorization: Basic %s\r\n"
                            "Host: %s:%d\r\n\r\n" % (host, port, token, host, port)
                        ).encode()
                        s.sendall(cr)
                        upstream = s
                        break
                    except Exception:
                        try:
                            s.close()
                        except Exception:
                            pass
                        continue

            if upstream is None:
                client.sendall(b"\x05\x03\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack(">H", 0))
                return
            if not host_bypasses_proxy(host):
                resp = b""
                while b"\r\n\r\n" not in resp:
                    chunk = upstream.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                if b"200" not in resp:
                    upstream.close()
                    client.sendall(b"\x05\x03\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack(">H", 0))
                    return
            client.sendall(b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack(">H", 0))
            self._relay(upstream, client, self._stop)
        except Exception:
            pass
        finally:
            try:
                client.close()
            except Exception:
                pass

    # -- PAC --------------------------------------------------------------------

    def _handle_pac(self, client):
        try:
            data = client.recv(4096)
            if not data:
                return
            match = re.search(rb"GET\s+(\S+)\s+HTTP", data)
            if not match:
                client.close()
                return
            path = match.group(1).decode()
            if path != self.settings.get("pac_path", "/proxy.pac"):
                resp = b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            else:
                pac = build_pac().encode("utf-8")
                resp = (
                    b"HTTP/1.1 200 OK\r\n"
                    b"Content-Type: application/x-ns-proxy-autoconfig\r\n"
                    b"Cache-Control: no-cache\r\n"
                    b"Content-Length: " + str(len(pac)).encode() + b"\r\n"
                    b"Connection: close\r\n\r\n" + pac
                )
            client.sendall(resp)
        except Exception:
            pass
        finally:
            try:
                client.close()
            except Exception:
                pass

    # -- жизненный цикл -----------------------------------------------------------

    def start(self):
        if self._socks:
            return False, "Уже запущено"
        ports = (
            ("HTTP", int(self.settings.get("local_http_port", 8080)), self._handle_http),
            ("SOCKS5", int(self.settings.get("local_socks_port", 1080)), self._handle_socks),
            ("PAC", int(self.settings.get("local_pac_port", 8082)), self._handle_pac),
        )
        bound = []
        try:
            for name, port, handler in ports:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("127.0.0.1", port))
                s.listen(200)
                s.settimeout(1.0)
                bound.append(s)
        except OSError as e:
            for s in bound:
                try:
                    s.close()
                except Exception:
                    pass
            return False, "Не удалось занять порт: %s" % e
        self._socks = bound
        self._stop = threading.Event()
        for lsock, (name, port, handler) in zip(bound, ports):
            t = threading.Thread(target=self._accept_loop, args=(lsock, handler), daemon=True)
            t.start()
            self._threads.append(t)
        _log("proxy started (http=%d socks=%d pac=%d, upstreams=%d)"
             % (ports[0][1], ports[1][1], ports[2][1], len(self._upstreams)))
        return True, "OK"

    def _accept_loop(self, lsock, handler):
        while not self._stop.is_set():
            try:
                c, _ = lsock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            if self._stop.is_set():
                try:
                    c.close()
                except Exception:
                    pass
                break
            threading.Thread(target=handler, args=(c,), daemon=True).start()

    def stop(self):
        self._stop.set()
        for s in self._socks:
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s.close()
            except Exception:
                pass
        self._socks = []
        _log("proxy stopped")
        return True


# ---------------------------------------------------------------------------
# Статус: проверка портов / процесса
# ---------------------------------------------------------------------------

def _pac_healthy(settings=None):
    settings = settings or load_settings()
    port = int(settings.get("local_pac_port", 8082))
    path = str(settings.get("pac_path", "/proxy.pac") or "/proxy.pac")
    if not path.startswith("/"):
        path = "/" + path
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=1.0)
        req = ("GET %s HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n" % path).encode("ascii")
        s.sendall(req)
        data = b""
        while len(data) < 65536:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        s.close()
        return b"200 OK" in data and b"FindProxyForURL" in data and b"127.0.0.1:" in data
    except Exception:
        return False


def proxy_listener_active():
    """Whether a compatible PAC endpoint is active on the configured localhost port.

    This intentionally does not imply ownership: another Arvectum installation
    can expose the same endpoint.  Use is_running() for instance-owned status.
    """
    return _pac_healthy(load_settings())


def _windows_process_creation_time(pid):
    if not is_windows():
        return None
    try:
        import ctypes
        from ctypes import wintypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        kernel32 = ctypes.windll.kernel32
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetProcessTimes.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME), ctypes.POINTER(wintypes.FILETIME)]
        kernel32.GetProcessTimes.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return None
        try:
            creation = wintypes.FILETIME()
            exit_time = wintypes.FILETIME()
            kernel = wintypes.FILETIME()
            user = wintypes.FILETIME()
            if not kernel32.GetProcessTimes(
                    handle, ctypes.byref(creation), ctypes.byref(exit_time),
                    ctypes.byref(kernel), ctypes.byref(user)):
                return None
            return (int(creation.dwHighDateTime) << 32) | int(creation.dwLowDateTime)
        finally:
            kernel32.CloseHandle(handle)
    except Exception as e:
        _log("process creation time error: %r" % e)
        return None


def _windows_process_executable_path(pid):
    if not is_windows():
        return None
    try:
        import ctypes
        from ctypes import wintypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return None
        try:
            size = wintypes.DWORD(32768)
            buffer = ctypes.create_unicode_buffer(size.value)
            if not ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                return None
            return os.path.realpath(buffer.value)
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        return None


def _read_pid():
    try:
        with io.open(pid_path(), "r", encoding="utf-8") as f:
            raw = f.read().strip()
        try:
            data = json.loads(raw)
        except Exception:
            data = None
        if isinstance(data, dict) and data.get("pid"):
            return {"pid": int(data["pid"]), "created": data.get("created"),
                    "exe_path": data.get("exe_path"), "identity": data.get("identity")}
        # Старый формат содержал только PID. Он небезопасен для taskkill после
        # перезагрузки/PID reuse, поэтому читаем его как непроверяемый.
        return {"pid": int(raw), "created": None}
    except Exception:
        return None


def is_running():
    """Return True only for the proxy process owned by this app directory.

    RC2 treated any healthy PAC endpoint as this instance, which could confuse
    two installations using the same localhost ports.  On Windows we require
    the local PID record *and* matching process creation time in addition to a
    healthy PAC response.
    """
    if not proxy_listener_active():
        return False
    if not is_windows():
        return True
    record = _read_pid()
    if not isinstance(record, dict) or not record.get("pid") or record.get("created") is None:
        return False
    actual = _windows_process_creation_time(int(record["pid"]))
    if actual is None or int(actual) != int(record["created"]):
        return False
    recorded_path = record.get("exe_path")
    actual_path = _windows_process_executable_path(int(record["pid"]))
    return bool(recorded_path and actual_path and
                os.path.normcase(os.path.realpath(recorded_path)) == os.path.normcase(os.path.realpath(actual_path)))


def _write_pid():
    try:
        pid = os.getpid()
        record = {"pid": pid, "created": _windows_process_creation_time(pid),
                  "exe_path": os.path.realpath(sys.executable),
                  "identity": os.path.normcase(os.path.realpath(install_dir()))}
        with io.open(pid_path(), "w", encoding="utf-8") as f:
            json.dump(record, f)
    except Exception as e:
        _log("pid write error: %r" % e)


def _remove_pid():
    try:
        os.remove(pid_path())
    except Exception:
        pass


def _kill_pid(record):
    if not record:
        return False
    pid = int(record.get("pid")) if isinstance(record, dict) else int(record)
    expected_created = record.get("created") if isinstance(record, dict) else None
    try:
        if is_windows():
            actual_created = _windows_process_creation_time(pid)
            if expected_created is None or actual_created is None or int(expected_created) != int(actual_created):
                _log("refusing unsafe taskkill for pid=%s: process identity mismatch/unverified" % pid)
                return False
            result = subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"], capture_output=True, text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if result.returncode != 0:
                _log("taskkill failed for pid=%s: %s" % (pid, (result.stderr or result.stdout).strip()))
                return False
            return True
        os.kill(pid, 9)
        return True
    except Exception as e:
        _log("kill pid error (%s): %r" % (pid, e))
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_start():
    settings = load_settings()
    configured = any((u.get("host") or "").strip() for u in settings.get("upstream") or [])
    if not configured:
        _log("start aborted: no upstream proxy configured")
        print("upstream proxy is not configured")
        return 2
    if is_running():
        _log("already running, enabling system proxy")
        return 0 if enable_system_proxy() else 1
    core = ProxyCore(settings)
    ok, msg = core.start()
    if not ok:
        _log("start failed: %s" % msg)
        print(msg)
        return 1
    _write_pid()
    if not enable_system_proxy():
        core.stop()
        _remove_pid()
        print("failed to enable system proxy; network settings rolled back")
        return 1
    print("proxy started")
    try:
        while not core._stop.wait(3600):
            pass
    except KeyboardInterrupt:
        pass
    finally:
        core.stop()
        _remove_pid()
    return 0


def _cmd_stop():
    record = _read_pid()
    killed = _kill_pid(record)
    still_running = is_running()
    if killed or not still_running:
        _remove_pid()
    network_ok = disable_system_proxy()
    still_running = is_running()
    pending = network_restore_pending()
    if still_running:
        print("proxy process is still running; network proxy was disabled where possible")
        return 1
    if not network_ok or pending:
        print("proxy stopped, but network settings restore is incomplete; retry --rollback")
        return 1
    print("proxy stopped; network settings restored")
    return 0


def _cmd_rollback():
    """Аварийный откат, не зависящий от работающего GUI или proxy."""
    record = _read_pid()
    killed = _kill_pid(record)
    still_running = is_running()
    if killed or not still_running:
        _remove_pid()
    network_ok = disable_system_proxy()
    still_running = is_running()
    pending = network_restore_pending()
    if still_running:
        print("network proxy was disabled where possible, but proxy process is still running")
        return 1
    if not network_ok or pending:
        print("network settings restore is incomplete; recovery files were kept for retry")
        return 1
    print("network settings restored")
    return 0


def _cmd_status():
    s = load_settings()
    if is_running():
        print("RUNNING (http=127.0.0.1:%d socks=127.0.0.1:%d pac=%s)"
              % (s["local_http_port"], s["local_socks_port"], pac_url(s)))
        print("system proxy: %s" % ("ENABLED" if system_proxy_enabled() else "disabled"))
        print("exceptions: %d domains" % len(load_no_proxy()))
    else:
        print("STOPPED")


def main():
    if not _ensure_local_files():
        print("state initialization failed")
        return 1
    if handoff_to_canonical_install():
        print("opened canonical installed launcher")
        return 0
    action = sys.argv[1][2:] if len(sys.argv) > 1 and sys.argv[1].startswith("--") else ("start" if len(sys.argv) == 1 else None)
    if action == "start":
        return _cmd_start()
    if action == "stop":
        return _cmd_stop()
    if action == "status":
        _cmd_status()
        return 0
    if action == "rollback":
        return _cmd_rollback()
    print("usage: proxy_core.py --start | --stop | --status | --rollback")
    return 2


if __name__ == "__main__":
    sys.exit(main())
