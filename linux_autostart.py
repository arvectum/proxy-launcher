# -*- coding: utf-8 -*-
"""Production-safe per-user Linux/Astra autostart (Linux autostart ownership).

The canonical mechanism is an XDG Autostart desktop entry owned by the current
user.  The module is deliberately fail-closed: it never overwrites or removes a
same-named entry unless the existing file exactly matches the Arvectum-owned
contract for the canonical packaged executable.
"""

from __future__ import annotations

import os
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


AUTOSTART_FILENAME = "arvectum-proxy-launcher.desktop"
OWNERSHIP_MARKER = "X-Arvectum-Autostart=Linux autostart ownership"
EXPECTED_EXECUTABLE_NAME = "Arvectum Proxy Launcher"


class LinuxAutostartError(RuntimeError):
    """Raised when autostart cannot be changed without violating ownership."""


@dataclass(frozen=True)
class LinuxAutostartStatus:
    enabled: bool
    managed: bool
    conflict: bool
    path: str
    message: str


def _xdg_config_home(environ=None, home=None):
    env = os.environ if environ is None else environ
    raw = str(env.get("XDG_CONFIG_HOME") or "").strip()
    if raw and os.path.isabs(raw):
        return Path(raw)
    base_home = Path(home or env.get("HOME") or Path.home())
    return base_home / ".config"


def autostart_path(environ=None, home=None):
    return _xdg_config_home(environ=environ, home=home) / "autostart" / AUTOSTART_FILENAME


def _desktop_quote(value):
    """Quote one desktop Exec argument according to the desktop-entry rules."""
    text = str(value)
    for old, new in (("\\", "\\\\"), ('"', '\\"'), ("`", "\\`"), ("$", "\\$")):
        text = text.replace(old, new)
    return '"%s"' % text


def canonical_executable(executable=None, frozen=None):
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)
    if not is_frozen:
        raise LinuxAutostartError(
            "Автозапуск доступен только для собранного Linux-приложения, а не для запуска из исходников."
        )
    raw = executable or sys.executable
    path = Path(raw).expanduser()
    try:
        path = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise LinuxAutostartError("Не удалось подтвердить путь установленного приложения: %s" % exc)
    if not path.is_file():
        raise LinuxAutostartError("Канонический файл приложения не найден.")
    if path.name != EXPECTED_EXECUTABLE_NAME:
        raise LinuxAutostartError(
            "Автозапуск разрешён только для канонического файла «%s»." % EXPECTED_EXECUTABLE_NAME
        )
    if not os.access(str(path), os.X_OK):
        raise LinuxAutostartError("Канонический файл приложения не является исполняемым.")
    return path


def render_autostart_entry(executable):
    command = "%s --start" % _desktop_quote(executable)
    return "\n".join(
        (
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.0",
            "Name=Arvectum Proxy Launcher",
            "Comment=Start Arvectum Proxy Launcher proxy at login",
            "Exec=%s" % command,
            "Terminal=false",
            "X-GNOME-Autostart-enabled=true",
            "Hidden=false",
            OWNERSHIP_MARKER,
            "",
        )
    )


def _read_regular_file(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise LinuxAutostartError("Не удалось проверить файл автозапуска: %s" % exc)
    if stat.S_ISLNK(info.st_mode):
        raise LinuxAutostartError("Файл автозапуска является символической ссылкой; изменение запрещено.")
    if not stat.S_ISREG(info.st_mode):
        raise LinuxAutostartError("Путь автозапуска занят не обычным файлом; изменение запрещено.")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise LinuxAutostartError("Не удалось безопасно прочитать файл автозапуска: %s" % exc)


def _expected(executable=None, frozen=None):
    canonical = canonical_executable(executable=executable, frozen=frozen)
    return canonical, render_autostart_entry(str(canonical))


def status(executable=None, frozen=None, environ=None, home=None):
    path = autostart_path(environ=environ, home=home)
    try:
        _, expected = _expected(executable=executable, frozen=frozen)
    except LinuxAutostartError as exc:
        return LinuxAutostartStatus(False, False, False, str(path), str(exc))
    try:
        existing = _read_regular_file(path)
    except LinuxAutostartError as exc:
        return LinuxAutostartStatus(False, False, True, str(path), str(exc))
    if existing is None:
        return LinuxAutostartStatus(False, True, False, str(path), "Автозапуск не настроен.")
    if existing == expected:
        return LinuxAutostartStatus(True, True, False, str(path), "Автозапуск включён.")
    return LinuxAutostartStatus(
        False,
        False,
        True,
        str(path),
        "Одноимённый файл автозапуска уже существует и не принадлежит текущей конфигурации Arvectum.",
    )


def enable(executable=None, frozen=None, environ=None, home=None):
    canonical, expected = _expected(executable=executable, frozen=frozen)
    path = autostart_path(environ=environ, home=home)
    existing = _read_regular_file(path)
    if existing is not None:
        if existing == expected:
            return status(str(canonical), True, environ=environ, home=home)
        raise LinuxAutostartError(
            "Автозапуск не изменён: одноимённый .desktop-файл не подтверждён как принадлежащий Arvectum."
        )

    parent = path.parent
    try:
        parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if parent.is_symlink():
            raise LinuxAutostartError("Каталог autostart является символической ссылкой; изменение запрещено.")
    except LinuxAutostartError:
        raise
    except OSError as exc:
        raise LinuxAutostartError("Не удалось подготовить каталог автозапуска: %s" % exc)

    tmp_name = None
    try:
        fd, tmp_name = tempfile.mkstemp(prefix=".%s." % AUTOSTART_FILENAME, dir=str(parent), text=True)
        try:
            # chmod(path) is deliberately used instead of fchmod(fd): the
            # production target is POSIX, where 0600 is enforced, while the
            # module also remains importable/testable by the shared Windows CI.
            os.chmod(tmp_name, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(expected)
                handle.flush()
                os.fsync(handle.fileno())
            # Publish with a hard link rather than os.replace(): link() is
            # atomic and fails if the destination appeared concurrently, so a
            # foreign entry can never be clobbered in the final race window.
            try:
                os.link(tmp_name, path)
            except FileExistsError:
                raise LinuxAutostartError(
                    "Автозапуск изменился параллельно; существующий файл оставлен без изменений."
                )
            os.unlink(tmp_name)
            tmp_name = None
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            raise
    except LinuxAutostartError:
        raise
    except OSError as exc:
        raise LinuxAutostartError("Не удалось атомарно записать файл автозапуска: %s" % exc)
    finally:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
            except OSError:
                pass

    verified = _read_regular_file(path)
    if verified != expected:
        raise LinuxAutostartError("Проверка записи автозапуска не пройдена; состояние не подтверждено.")
    return status(str(canonical), True, environ=environ, home=home)


def disable(executable=None, frozen=None, environ=None, home=None):
    canonical, expected = _expected(executable=executable, frozen=frozen)
    path = autostart_path(environ=environ, home=home)
    existing = _read_regular_file(path)
    if existing is None:
        return status(str(canonical), True, environ=environ, home=home)
    if existing != expected:
        raise LinuxAutostartError(
            "Автозапуск не удалён: одноимённый .desktop-файл не подтверждён как принадлежащий Arvectum."
        )
    try:
        path.unlink()
    except OSError as exc:
        raise LinuxAutostartError("Не удалось удалить принадлежащий Arvectum файл автозапуска: %s" % exc)
    if _read_regular_file(path) is not None:
        raise LinuxAutostartError("Файл автозапуска сохранился после удаления; состояние не подтверждено.")
    return status(str(canonical), True, environ=environ, home=home)
