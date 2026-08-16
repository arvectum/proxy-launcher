# -*- coding: utf-8 -*-
"""
Arvectum Proxy Launcher — графический лаунчер прокси для Windows.

Дизайн по брендбуку Arvectum: Deep Navy + Mint Primary (#00C8A0),
PT Sans / JetBrains Mono, фирменный знак и горизонтальный логотип.

Возможности:
  * включение/выключение прокси (поднимает proxy_core и системный PAC)
  * окно настроек внешнего прокси: IP, порт, логин, пароль (можно несколько)
  * удобное добавление/удаление исключений no_proxy
  * проверка работы ("мой IP")
  * автозапуск при входе в Windows (планировщик задач)

Запуск: pythonw proxy_gui.py  (или собранный Arvectum Proxy Launcher.exe)
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox

import proxy_core as core
import doctor as doctor_module

# ---------------------------------------------------------------------------
# Бренд Arvectum
# ---------------------------------------------------------------------------

APP_NAME = "Arvectum Proxy Launcher"
APP_VERSION = core.APP_VERSION
TASK_NAME = "ArvectumProxyLauncher"  # legacy scheduled-task name
AUTOSTART_RUN_VALUE = "ArvectumProxyLauncher"
AUTOSTART_RUN_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

NAVY = "#001432"          # Deep Navy
MINT = "#00C8A0"          # Mint Primary
MINT_LIGHT = "#78FAE6"    # Mint Light
SOFT_GRAY = "#C8D2DC"     # Soft Gray
GRAPHITE = "#283246"      # Graphite
WHITE = "#FFFFFF"
MINT_SOFT = "#E5F7F3"     # очень светлый мятный (hover)
DISABLED_BG = "#E6ECEE"
DISABLED_FG = "#96AAA6"

B = {}  # бренд-конфиг: шрифты и стили, заполняется после создания root


def setup_brand(root):
    fams = set(tkfont.families(root))

    def pick(group):
        for f in group:
            if f in fams:
                return f
        return group[-1]

    body = pick(["PT Sans", "Segoe UI", "Tahoma", "Helvetica Neue", "Helvetica", "Arial"])
    mono = pick(["JetBrains Mono", "Cascadia Mono", "Consolas", "Menlo", "Courier New"])
    B["font"] = (body, 10)
    B["font_bold"] = (body, 10, "bold")
    B["font_small"] = (body, 9)
    B["font_h"] = (body, 12, "bold")
    B["font_brand"] = (body, 20, "bold")
    B["font_section"] = (body, 10, "bold")
    B["font_mono"] = (mono, 9)
    B["font_mono_bold"] = (mono, 10, "bold")
    B["title"] = body

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(".", font=B["font"], background=WHITE, foreground=GRAPHITE)

    style.configure("TFrame", background=WHITE)
    style.configure("Header.TFrame", background=NAVY)
    style.configure("TLabelframe", background=WHITE, bordercolor=SOFT_GRAY)
    style.configure("TLabelframe.Label", background=WHITE, foreground=GRAPHITE, font=B["font_bold"])

    style.configure("Mint.TButton",
                    background=MINT, foreground=NAVY, bordercolor=MINT,
                    focuscolor=NAVY, relief="flat", padding=(14, 8), font=B["font_bold"])
    style.map("Mint.TButton",
              background=[("disabled", DISABLED_BG), ("active", MINT_LIGHT), ("pressed", "#00B893")],
              foreground=[("disabled", DISABLED_FG)],
              bordercolor=[("disabled", DISABLED_BG), ("active", MINT_LIGHT)])

    style.configure("Navy.TButton",
                    background=NAVY, foreground=WHITE, bordercolor=NAVY,
                    focuscolor=WHITE, relief="flat", padding=(14, 8), font=B["font_bold"])
    style.map("Navy.TButton",
              background=[("disabled", DISABLED_BG), ("active", GRAPHITE), ("pressed", "#000C20")],
              foreground=[("disabled", DISABLED_FG)],
              bordercolor=[("disabled", DISABLED_BG), ("active", GRAPHITE)])

    style.configure("Ghost.TButton",
                    background=WHITE, foreground=NAVY, bordercolor=SOFT_GRAY,
                    focuscolor=NAVY, relief="flat", padding=(10, 8), font=B["font"])
    style.map("Ghost.TButton",
              background=[("active", MINT_SOFT), ("pressed", "#D4EEE9")],
              bordercolor=[("active", MINT), ("disabled", SOFT_GRAY)],
              foreground=[("disabled", DISABLED_FG)])

    style.configure("Brand.TCheckbutton", background=WHITE, foreground=GRAPHITE, font=B["font"])
    style.map("Brand.TCheckbutton",
              background=[("active", WHITE)],
              indicatorcolor=[("selected", MINT), ("pressed", MINT_LIGHT)],
              foreground=[("disabled", DISABLED_FG)])


def _asset_path(name):
    base = os.path.join(core.app_dir(), "assets")
    if not os.path.isdir(base) and getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = os.path.join(sys._MEIPASS, "assets")
    p = os.path.join(base, name)
    return p if os.path.exists(p) else None


def _load_photo(png_name, gif_name=None):
    """Загрузить картинку. PNG — на Tk 8.6+ (Windows), GIF — запасной (Tk 8.5)."""
    for name in (png_name, gif_name):
        path = _asset_path(name)
        if not path:
            continue
        try:
            return tk.PhotoImage(file=path)
        except Exception:
            continue
    return None


def _bind_clipboard_paste(entry):
    """Надёжная вставка текста из буфера Windows в поля Tk."""
    def paste(event=None):
        try:
            value = entry.clipboard_get()
        except tk.TclError:
            # Резервный путь для случаев, когда Tk не видит CLIPBOARD
            # (например, при запуске exe с другим уровнем прав).
            value = None
            if os.name == "nt":
                try:
                    import ctypes
                    from ctypes import wintypes
                    user32 = ctypes.windll.user32
                    kernel32 = ctypes.windll.kernel32
                    CF_UNICODETEXT = 13
                    user32.GetClipboardData.argtypes = [wintypes.UINT]
                    user32.GetClipboardData.restype = wintypes.HANDLE
                    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
                    kernel32.GlobalLock.restype = wintypes.LPVOID
                    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
                    kernel32.GlobalUnlock.restype = wintypes.BOOL
                    if user32.OpenClipboard(entry.winfo_id()):
                        handle = user32.GetClipboardData(CF_UNICODETEXT)
                        if handle:
                            ptr = kernel32.GlobalLock(handle)
                            if ptr:
                                value = ctypes.wstring_at(ptr)
                                kernel32.GlobalUnlock(handle)
                        user32.CloseClipboard()
                except Exception:
                    value = None
            if value is None:
                return "break"

        # Entry не предназначен для многострочного текста: берём одну
        # строку, иначе вставка прокси из буфера может silently не сработать.
        value = str(value).replace("\r", " ").replace("\n", " ").strip()
        try:
            entry.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        entry.insert(tk.INSERT, value)
        return "break"

    entry.bind("<Control-v>", paste)
    entry.bind("<Control-V>", paste)
    # В русской раскладке Tk получает Ctrl+V как keysym «м». Проверяем
    # физический keycode клавиши V, чтобы Ctrl+V работал при любой раскладке.
    def paste_ctrl_v(event):
        if event.keycode == 86 or event.keysym in ("v", "V", "м", "М"):
            return paste(event)
        return None

    entry.bind("<Control-KeyPress>", paste_ctrl_v)
    entry.bind("<Shift-Insert>", paste)

    menu = tk.Menu(entry, tearoff=False)
    menu.add_command(label="Вставить", command=paste)

    def show_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    entry.bind("<Button-3>", show_menu)


def _run_headless(mode):
    """Запустить core в отдельном процессе (чтобы работал после закрытия окна)."""
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, mode]
    else:
        cmd = [sys.executable, os.path.join(core.app_dir(), "proxy_core.py"), mode]
    flags = 0
    if os.name == "nt":
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(
        cmd, cwd=core.app_dir(), creationflags=flags,
        stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        close_fds=True,
    )


def _portable_fallback_active():
    """True while a frozen GUI remains on a non-canonical executable.

    A failed canonical handoff must not make the already-running portable GUI
    unusable, and must never redirect autostart to an executable whose launch
    was not confirmed.
    """
    if not (os.name == "nt" and getattr(sys, "frozen", False)):
        return False
    try:
        current = os.path.normcase(os.path.realpath(sys.executable))
        canonical = os.path.normcase(os.path.realpath(core.stable_app_exe()))
        return current != canonical
    except Exception:
        return True


def _autostart_target():
    if getattr(sys, "frozen", False):
        if _portable_fallback_active():
            raise RuntimeError(
                "Автозапуск временно недоступен: постоянная копия Launcher "
                "не была подтверждена как запускаемая Windows. Текущий portable "
                "Launcher можно использовать вручную."
            )
        target = core.managed_executable()
        if not target:
            raise RuntimeError(core.self_heal_error() or "Не удалось подготовить постоянную копию Launcher.")
        return '"%s" --start' % target
    return '"%s" "%s" --start' % (sys.executable, os.path.join(core.app_dir(), "proxy_core.py"))


def _header_title(root, title):
    """Однотонная фирменная шапка без декоративных линий."""
    hdr = tk.Frame(root, bg=NAVY, padx=16, pady=12)
    tk.Label(hdr, text=title, bg=NAVY, fg=WHITE, font=B["font_h"]).pack(side="left")
    tk.Label(hdr, text=APP_NAME, bg=NAVY, fg=MINT, font=B["font_bold"]).pack(side="right")
    hdr.pack(fill="x")


class SettingsDialog(tk.Toplevel):
    """Окно настроек внешнего прокси: несколько upstream'ов (IP, порт, логин, пароль)."""

    def __init__(self, master, settings):
        super().__init__(master)
        self.title("Настройки прокси · " + APP_NAME)
        self.settings = settings
        self.result = None
        self.configure(bg=WHITE)
        self.grab_set()
        self.resizable(False, False)
        self._build()
        self._center(master)

    def _center(self, master):
        self.update_idletasks()
        try:
            x = master.winfo_rootx() + 60
            y = master.winfo_rooty() + 60
            self.geometry("+%d+%d" % (x, y))
        except Exception:
            pass

    def _build(self):
        _header_title(self, "Настройки прокси")

        frm = tk.Frame(self, bg=WHITE, padx=16, pady=14)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Внешние прокси-серверы (по порядку, с запасным):",
                 bg=WHITE, fg=GRAPHITE, font=B["font_bold"]).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        self.listbox = tk.Listbox(frm, width=46, height=6, bg=WHITE, fg=GRAPHITE,
                                  selectbackground=MINT, selectforeground=NAVY,
                                  relief="solid", bd=1, highlightthickness=0, font=B["font"])
        self.listbox.grid(row=1, column=0, columnspan=3, sticky="nsew")
        scroll = ttk.Scrollbar(frm, orient="vertical", command=self.listbox.yview)
        scroll.grid(row=1, column=3, sticky="ns")
        self.listbox.configure(yscrollcommand=scroll.set)

        btns = tk.Frame(frm, bg=WHITE)
        btns.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 8))
        b_add = ttk.Button(btns, text="Добавить", style="Ghost.TButton", command=self._add)
        b_add.grid(row=0, column=0, padx=3)
        b_edit = ttk.Button(btns, text="Изменить", style="Ghost.TButton", command=self._edit)
        b_edit.grid(row=0, column=1, padx=3)
        b_del = ttk.Button(btns, text="Удалить", style="Ghost.TButton", command=self._delete)
        b_del.grid(row=0, column=2, padx=3)

        self._fields = {}
        labels = ("IP адрес", "Порт", "Логин", "Пароль")
        keys = ("host", "port", "username", "password")
        shows = (None, None, None, "*")
        for i, (label, key, show) in enumerate(zip(labels, keys, shows)):
            tk.Label(frm, text=label, bg=WHITE, fg=GRAPHITE, font=B["font"]).grid(
                row=3 + i, column=0, sticky="e", pady=3, padx=(0, 8))
            e = tk.Entry(frm, width=30, show=show, bg=WHITE, fg=NAVY,
                         relief="solid", bd=1, insertbackground=GRAPHITE,
                         font=B["font_mono"] if key in ("host", "port") else B["font"])
            e.grid(row=3 + i, column=1, columnspan=3, sticky="w", pady=3)
            self._fields[key] = e
            _bind_clipboard_paste(e)

        foot = tk.Frame(frm, bg=WHITE)
        foot.grid(row=9, column=0, columnspan=4, sticky="e", pady=(10, 0))
        ttk.Button(foot, text="Сохранить", style="Mint.TButton", command=self._ok).grid(row=0, column=0, padx=4)
        ttk.Button(foot, text="Отмена", style="Ghost.TButton", command=self.destroy).grid(row=0, column=1)

        self._refresh_list()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for up in self.settings.get("upstream") or []:
            host = up.get("host") or ""
            if not host:
                self.listbox.insert(tk.END, "  <не настроено — заполни поля ниже>")
            else:
                self.listbox.insert(
                    tk.END, "  %s:%s  (логин: %s)" % (host, up.get("port"), up.get("username")))

    def _fill(self, up):
        for key in self._fields:
            e = self._fields[key]
            e.delete(0, tk.END)
        self._fields["host"].insert(0, str(up.get("host") or ""))
        self._fields["port"].insert(0, str(up.get("port") or 8000))
        self._fields["username"].insert(0, str(up.get("username") or ""))
        self._fields["password"].insert(0, str(up.get("password") or ""))

    def _values(self):
        raw_port = self._fields["port"].get().strip()
        try:
            port = int(raw_port or 8000)
        except ValueError:
            port = None
        return {
            "host": (self._fields["host"].get() or "").strip(),
            "port": port,
            "username": self._fields["username"].get().strip(),
            "password": self._fields["password"].get(),
        }

    def _check_and_get(self):
        v = self._values()
        if not v["host"]:
            messagebox.showwarning("Настройки", "Введи IP адрес внешнего прокси.", parent=self)
            return None
        if v["port"] is None or not (0 < v["port"] < 65536):
            messagebox.showwarning("Настройки", "Порт должен быть числом от 1 до 65535.", parent=self)
            return None
        return v

    def _add(self):
        v = self._check_and_get()
        if not v:
            return
        self.settings.setdefault("upstream", []).append(v)
        self._refresh_list()
        self._fill({"host": "", "port": 8000, "username": "", "password": ""})

    def _edit(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        ups = self.settings.setdefault("upstream", [])
        if idx >= len(ups):
            return
        v = self._check_and_get()
        if not v:
            return
        ups[idx] = v
        self._refresh_list()

    def _delete(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        ups = self.settings.setdefault("upstream", [])
        if idx < len(ups):
            ups.pop(idx)
        self._refresh_list()

    def _ok(self):
        ups = self.settings.setdefault("upstream", [])

        # Сохраняем данные, введённые непосредственно в поля. Раньше
        # «Сохранить» учитывала только записи, добавленные кнопкой «Добавить»,
        # из-за чего первоначальный пустой шаблон удалялся и настройки
        # терялись при каждом запуске.
        host = (self._fields["host"].get() or "").strip()
        if host:
            v = self._check_and_get()
            if not v:
                return
            empty_idx = next((i for i, u in enumerate(ups) if not (u.get("host") or "").strip()), None)
            if empty_idx is None:
                ups.append(v)
            else:
                ups[empty_idx] = v
        self.settings["upstream"] = [u for u in ups if u.get("host")]
        self.result = self.settings
        self.destroy()


class ExceptionsDialog(tk.Toplevel):
    """Окно управления исключениями no_proxy."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Исключения (no_proxy) · " + APP_NAME)
        self.domains = core.load_no_proxy()
        self.configure(bg=WHITE)
        self.grab_set()
        self.resizable(False, False)
        self._build()
        self._center(master)

    def _center(self, master):
        self.update_idletasks()
        try:
            x = master.winfo_rootx() + 60
            y = master.winfo_rooty() + 60
            self.geometry("+%d+%d" % (x, y))
        except Exception:
            pass

    def _build(self):
        _header_title(self, "Исключения (no_proxy)")

        frm = tk.Frame(self, bg=WHITE, padx=16, pady=14)
        frm.pack(fill="both", expand=True)

        tk.Label(frm,
                 text="Сайты из списка открываются напрямую (минуя прокси).\n"
                      "Можно вставлять целиком URL или host:port — само «почистится».\n"
                      "Изменения применяются сразу, перезапуск не нужен.",
                 bg=WHITE, fg=GRAPHITE, font=B["font_small"], justify="left").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        self.listbox = tk.Listbox(frm, width=54, height=12, bg=WHITE, fg=GRAPHITE,
                                  selectbackground=MINT, selectforeground=NAVY,
                                  relief="solid", bd=1, highlightthickness=0, font=B["font"])
        self.listbox.grid(row=1, column=0, columnspan=3, sticky="nsew")
        scroll = ttk.Scrollbar(frm, orient="vertical", command=self.listbox.yview)
        scroll.grid(row=1, column=3, sticky="ns")
        self.listbox.configure(yscrollcommand=scroll.set)

        tk.Label(frm, text="Новое исключение:", bg=WHITE, fg=GRAPHITE,
                 font=B["font"]).grid(row=2, column=0, sticky="e", pady=(8, 0), padx=(0, 6))
        self.entry = tk.Entry(frm, width=32, bg=WHITE, fg=NAVY, relief="solid", bd=1,
                              insertbackground=GRAPHITE, font=B["font"])
        self.entry.grid(row=2, column=1, pady=(8, 0), sticky="w")
        self.entry.bind("<Return>", lambda e: self._add())
        _bind_clipboard_paste(self.entry)
        ttk.Button(frm, text="Добавить", style="Mint.TButton",
                   command=self._add).grid(row=2, column=2, pady=(8, 0), padx=(6, 0))

        btns = tk.Frame(frm, bg=WHITE)
        btns.grid(row=3, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(btns, text="Удалить выбранное", style="Ghost.TButton",
                   command=self._remove).grid(row=0, column=0, padx=3)
        ttk.Button(btns, text="Очистить всё", style="Ghost.TButton",
                   command=self._clear).grid(row=0, column=1, padx=3)

        foot = tk.Frame(frm, bg=WHITE)
        foot.grid(row=4, column=0, columnspan=4, sticky="e", pady=(10, 0))
        ttk.Button(foot, text="Сохранить", style="Mint.TButton", command=self._save).grid(row=0, column=0, padx=4)
        ttk.Button(foot, text="Отмена", style="Ghost.TButton", command=self.destroy).grid(row=0, column=1)

        self._refresh()

    def _refresh(self):
        self.listbox.delete(0, tk.END)
        for d in self.domains:
            self.listbox.insert(tk.END, "  " + d)

    def _add(self):
        raw = self.entry.get()
        d = core.clean_domain(raw)
        if not d:
            return
        if d not in self.domains:
            self.domains.append(d)
        self.entry.delete(0, tk.END)
        self._refresh()

    def _remove(self):
        sel = self.listbox.curselection()
        for idx in reversed(sel):
            self.domains.pop(idx)
        self._refresh()

    def _clear(self):
        self.domains = []
        self._refresh()

    def _save(self):
        self.domains = sorted(set(self.domains))
        core.save_no_proxy(self.domains)
        if core.is_running():
            if not core.sync_client_no_proxy():
                messagebox.showwarning(
                    APP_NAME,
                    "Исключения сохранены, но Windows NO_PROXY не удалось обновить. "
                    "Перезапустите прокси и проверьте «Журнал».",
                    parent=self)
            core._refresh_internet()
        self.destroy()


class Launcher:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.resizable(False, False)
        root.configure(bg=WHITE)
        core._ensure_local_files()
        setup_brand(root)
        self._images = []
        self._recovery_prompt_shown = False
        self._set_window_icon()

        # ---------- фирменная шапка ----------
        # Не используем растровый banner: заголовок должен быть частью UI,
        # а не картинкой. По брендбуку: PT Sans Bold, Mint на Deep Navy.
        header = tk.Frame(root, bg=NAVY, padx=20, pady=16)
        header.pack(fill="x")
        tk.Label(
            header, text=APP_NAME, bg=NAVY, fg=MINT,
            font=B["font_brand"], anchor="w").pack(side="left")
        tk.Label(
            header, text="Windows · %s" % APP_VERSION, bg=NAVY, fg=MINT_LIGHT,
            font=B["font_small"]).pack(side="right", pady=(5, 0))

        body = tk.Frame(root, bg=WHITE, padx=20, pady=18)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)

        # ---------- состояние ----------
        status_card = tk.Frame(
            body, bg=WHITE, padx=14, pady=12,
            highlightbackground=SOFT_GRAY, highlightthickness=1)
        status_card.grid(row=0, column=0, sticky="ew")
        status_card.grid_columnconfigure(0, weight=1)

        status_top = tk.Frame(status_card, bg=WHITE)
        status_top.grid(row=0, column=0, sticky="ew")
        tk.Label(
            status_top, text="Состояние", bg=WHITE, fg=GRAPHITE,
            font=B["font_section"]).pack(side="left")
        self.chip = tk.Label(
            status_top, text="", bg=SOFT_GRAY, fg=NAVY,
            font=B["font_bold"], padx=12, pady=5)
        self.chip.pack(side="right")

        current = core.load_settings()
        ports_text = "HTTP 127.0.0.1:%s    ·    SOCKS5 127.0.0.1:%s    ·    PAC 127.0.0.1:%s" % (
            current.get("local_http_port", 8080), current.get("local_socks_port", 1080),
            current.get("local_pac_port", 8082))
        tk.Label(
            status_card, text=ports_text, bg=WHITE, fg=GRAPHITE,
            font=B["font_mono"]).grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.status_hint = tk.Label(
            status_card, text="", bg=MINT_SOFT, fg=NAVY, font=B["font_small"],
            justify="left", anchor="w", padx=10, pady=7)
        self.status_hint.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.status_hint.grid_remove()

        # ---------- основные действия ----------
        tk.Label(
            body, text="Управление", bg=WHITE, fg=GRAPHITE,
            font=B["font_section"]).grid(row=1, column=0, sticky="w", pady=(16, 7))

        row1 = tk.Frame(body, bg=WHITE)
        row1.grid(row=2, column=0, sticky="ew")
        self.btn_on = ttk.Button(
            row1, text="Включить прокси", style="Mint.TButton", command=self.on)
        self.btn_on.pack(side="left", padx=(0, 6))
        self.btn_off = ttk.Button(
            row1, text="Выключить прокси", style="Navy.TButton", command=self.off)
        self.btn_off.pack(side="left", padx=6)
        self.btn_check = ttk.Button(
            row1, text="Проверить соединение", style="Ghost.TButton", command=self.check)
        self.btn_check.pack(side="left", padx=6)
        self.btn_orphan_pac = ttk.Button(
            row1, text="Удалить старый PAC и продолжить", style="Mint.TButton",
            command=self.clear_orphaned_pac)

        # ---------- URL диагностики ----------
        check_row = tk.Frame(body, bg=WHITE)
        check_row.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        tk.Label(
            check_row, text="URL проверки", bg=WHITE, fg=GRAPHITE,
            font=B["font_small"]).pack(side="left", padx=(0, 8))
        self.check_url_var = tk.StringVar(value="https://arvectum.com")
        check_entry = tk.Entry(
            check_row, textvariable=self.check_url_var, width=38,
            bg=WHITE, fg=NAVY, relief="solid", bd=1,
            insertbackground=GRAPHITE, font=B["font_mono"])
        check_entry.pack(side="left", fill="x", expand=True, ipady=3)
        _bind_clipboard_paste(check_entry)

        # ---------- настройки и сервис ----------
        tk.Label(
            body, text="Настройки и сервис", bg=WHITE, fg=GRAPHITE,
            font=B["font_section"]).grid(row=4, column=0, sticky="w", pady=(16, 7))

        service = tk.Frame(body, bg=WHITE)
        service.grid(row=5, column=0, sticky="ew")
        service.grid_columnconfigure(0, weight=1)
        left_tools = tk.Frame(service, bg=WHITE)
        left_tools.grid(row=0, column=0, sticky="w")
        ttk.Button(
            left_tools, text="Настройки прокси…", style="Ghost.TButton",
            command=self.settings).pack(side="left", padx=(0, 6))
        ttk.Button(
            left_tools, text="Исключения…", style="Ghost.TButton",
            command=self.exceptions).pack(side="left", padx=6)
        ttk.Button(
            left_tools, text="Журнал", style="Ghost.TButton",
            command=self.show_log).pack(side="left", padx=6)
        self.btn_doctor = ttk.Button(
            left_tools, text="Диагностика", style="Ghost.TButton",
            command=self.doctor)
        self.btn_doctor.pack(side="left", padx=6)

        self.btn_restore = ttk.Button(
            service, text="Восстановить настройки сети", style="Ghost.TButton",
            command=self.restore_network)
        self.btn_restore.grid(row=0, column=1, sticky="e", padx=(12, 0))

        # ---------- автозапуск ----------
        portable_fallback = _portable_fallback_active()
        self.auto_var = tk.BooleanVar(
            value=False if portable_fallback else self._autostart_enabled())
        self.autostart_check = ttk.Checkbutton(
            body, text="Запускать прокси при входе в Windows",
            variable=self.auto_var, command=self._toggle_autostart,
            style="Brand.TCheckbutton")
        self.autostart_check.grid(row=6, column=0, sticky="w", pady=(16, 0))
        if portable_fallback:
            self.autostart_check.state(["disabled"])

        tk.Label(
            body, text="Окно можно закрыть — запущенный proxy продолжит работать в фоне.",
            bg=WHITE, fg=GRAPHITE, font=B["font_small"]).grid(
            row=7, column=0, sticky="w", pady=(4, 0))

        # ---------- футер ----------
        tk.Frame(body, bg=SOFT_GRAY, height=1).grid(row=8, column=0, sticky="ew", pady=(16, 8))
        tk.Label(
            body, text="ARVECTUM · %s · arvectum.com" % APP_VERSION,
            bg=WHITE, fg=DISABLED_FG, font=B["font_mono"]).grid(
            row=9, column=0, sticky="w")

        self.refresh_status()
        self._maybe_first_run()
        self.root.after(200, self._maybe_prompt_recovery)

    def _set_window_icon(self):
        try:
            if os.name == "nt":
                ico = _asset_path("arvectum.ico")
                if ico:
                    self.root.iconbitmap(ico)
            icon = _load_photo("arvectum-icon.png", "arvectum-icon.gif")
            if icon:
                self._images.append(icon)
                self.root.iconphoto(False, icon)
        except Exception:
            pass

    # -- статус -------------------------------------------------------------

    def refresh_status(self):
        running = core.is_running()
        enabled = core.system_proxy_enabled()
        pending = core.network_restore_pending()
        orphaned_pac = core.orphaned_arvectum_pac()

        self.btn_check.state(["!disabled"])
        self.btn_doctor.state(["!disabled"])
        self.btn_restore.state(["!disabled"])
        self.btn_restore.configure(style="Ghost.TButton")
        self.btn_orphan_pac.pack_forget()
        self.status_hint.grid_remove()
        if running and enabled:
            self.chip.config(text="  ПРОКСИ ВКЛЮЧЁН  ", bg=MINT, fg=NAVY)
            self.btn_on.state(["disabled"])
            self.btn_off.state(["!disabled"])
        elif running:
            self.chip.config(text="  ДВИЖОК ЗАПУЩЕН · PAC ВЫКЛЮЧЕН  ", bg=MINT_LIGHT, fg=NAVY)
            self.btn_on.state(["!disabled"])
            self.btn_off.state(["!disabled"])
        elif pending:
            self.chip.config(text="  ТРЕБУЕТСЯ ВОССТАНОВЛЕНИЕ СЕТИ  ", bg=MINT_LIGHT, fg=NAVY)
            self.status_hint.config(
                text="Предыдущий сеанс proxy завершился некорректно. "
                     "Сначала восстановите сеть, затем снова включите прокси.")
            self.status_hint.grid()
            self.btn_on.state(["disabled"])
            self.btn_off.state(["disabled"])
            self.btn_restore.configure(style="Mint.TButton")
        elif orphaned_pac:
            self.chip.config(text="  ОБНАРУЖЕН СТАРЫЙ PAC ARVECTUM  ", bg=MINT_LIGHT, fg=NAVY)
            self.status_hint.config(
                text="Windows использует локальный PAC Arvectum от предыдущего сеанса, "
                     "но сам proxy engine не работает. Старую резервную копию найти "
                     "не удалось. Можно безопасно удалить только неработающий PAC "
                     "Arvectum, не изменяя остальные настройки Windows.")
            self.status_hint.grid()
            self.btn_on.state(["disabled"])
            self.btn_off.state(["disabled"])
            self.btn_check.state(["disabled"])
            self.btn_orphan_pac.pack(side="left", padx=6)
        elif core.stale_system_proxy():
            self.chip.config(text="  ТРЕБУЕТСЯ ДИАГНОСТИКА СЕТИ  ", bg=MINT_LIGHT, fg=NAVY)
            self.status_hint.config(
                text="Windows всё ещё использует PAC Arvectum, но подтверждённый "
                     "engine и резервная копия не найдены. Автоматический сброс "
                     "небезопасен: откройте установленный Launcher или журнал.")
            self.status_hint.grid()
            self.btn_on.state(["disabled"])
            self.btn_off.state(["disabled"])
        else:
            self.chip.config(text="  ВЫКЛЮЧЕН  ", bg=SOFT_GRAY, fg=NAVY)
            self.btn_on.state(["!disabled"])
            self.btn_off.state(["disabled"])

    # -- действия ------------------------------------------------------------

    def _maybe_prompt_recovery(self):
        if self._recovery_prompt_shown:
            return
        if core.is_running() or not core.network_restore_pending():
            return
        self._recovery_prompt_shown = True
        if messagebox.askyesno(
                APP_NAME,
                "Предыдущий сеанс proxy завершился некорректно.\n\n"
                "Чтобы Windows не осталась с устаревшими настройками proxy, "
                "сначала нужно восстановить исходные настройки сети.\n\n"
                "Восстановить сеть сейчас?",
                icon="warning"):
            self.restore_network(confirm=False)

    def on(self):
        s = core.load_settings()
        ok = any((u.get("host") or "").strip() for u in s.get("upstream") or [])
        if not ok:
            messagebox.showwarning(APP_NAME, "Сначала укажи IP/порт/логин/пароль внешнего прокси в «Настройки прокси».")
            self.settings()
            return
        if core.is_running():
            if core.system_proxy_enabled():
                self.refresh_status()
                return
            self._set_busy("Включение PAC…", MINT_LIGHT)
            _run_headless("--start")
            self.root.after(250, self._after_start)
            return
        self._set_busy("Запуск…", MINT_LIGHT)
        _run_headless("--start")
        # Фоновому процессу нужно время на запуск и открытие трёх сокетов.
        self.root.after(250, self._after_start)

    def _after_start(self, attempt=0):
        ok = core.is_running() and core.system_proxy_enabled()
        self.refresh_status()
        if ok:
            messagebox.showinfo(
                APP_NAME,
                "Прокси подключен.\nСистемный proxy установлен.\n\n"
                "Для корректной работы приложений через proxy полностью "
                "закройте их через Диспетчер задач и запустите заново.")
        elif attempt < 40:
            # One-file PyInstaller + антивирус на первом запуске могут
            # стартовать заметно дольше нескольких секунд.
            self.root.after(250, lambda: self._after_start(attempt + 1))
        else:
            messagebox.showerror(APP_NAME, "Не удалось запустить прокси. Подробности в «Журнал».")

    def off(self):
        self._set_busy("Остановка…", SOFT_GRAY)
        _run_headless("--stop")
        self.root.after(250, self._after_stop)

    def _after_stop(self, attempt=0):
        still_active = core.is_running() or core.network_restore_pending()
        if still_active and attempt < 32:
            self.root.after(250, lambda: self._after_stop(attempt + 1))
            return
        self.refresh_status()
        if core.is_running():
            messagebox.showerror(APP_NAME, "Прокси-процесс не удалось остановить. Подробности в «Журнал».")
        elif core.network_restore_pending():
            messagebox.showerror(
                APP_NAME,
                "Прокси остановлен, но настройки сети восстановлены не полностью. "
                "Не удаляйте приложение: нажмите «Восстановить настройки сети» ещё раз и проверьте «Журнал».")
        else:
            messagebox.showinfo(APP_NAME, "Прокси выключен, исходные настройки сети восстановлены.")

    def restore_network(self, confirm=True):
        if confirm and not messagebox.askyesno(
                APP_NAME,
                "Восстановить исходные настройки сети Windows и остановить proxy?",
                icon="warning"):
            return
        self._set_busy("Восстановление сети…", MINT_LIGHT)
        _run_headless("--rollback")
        self.root.after(250, self._after_restore_network)

    def clear_orphaned_pac(self):
        self._set_busy("Удаление старого PAC…", MINT_LIGHT)
        if core.clear_orphaned_arvectum_pac():
            self.refresh_status()
            messagebox.showinfo(
                APP_NAME,
                "Старый PAC Arvectum удалён. Остальные настройки Windows не изменялись. "
                "Теперь можно снова включить прокси.")
        else:
            self.refresh_status()
            messagebox.showerror(
                APP_NAME,
                "Старый PAC не был удалён: состояние сети изменилось или ownership "
                "не удалось подтвердить. См. «Журнал».")

    def _after_restore_network(self, attempt=0):
        still_active = core.is_running() or core.network_restore_pending()
        if still_active and attempt < 32:
            self.root.after(250, lambda: self._after_restore_network(attempt + 1))
            return
        self.refresh_status()
        if core.is_running():
            messagebox.showerror(APP_NAME, "Proxy-процесс всё ещё работает. См. «Журнал».")
        elif core.network_restore_pending():
            messagebox.showerror(
                APP_NAME,
                "Восстановление сети не завершено. Файлы резервной копии сохранены; "
                "повторите восстановление и не удаляйте приложение до успешного результата.")
        else:
            messagebox.showinfo(APP_NAME, "Сеть восстановлена. Теперь можно снова включить прокси.")

    def _set_busy(self, text, color):
        self.chip.config(text="  %s  " % text, bg=color, fg=NAVY)
        for b in (
                self.btn_on, self.btn_off, self.btn_check, self.btn_doctor,
                self.btn_restore, self.btn_orphan_pac):
            b.state(["disabled"])

    # -- проверка -------------------------------------------------------------

    def check(self):
        s = core.load_settings()
        port = int(s.get("local_http_port", 8080))
        url = self.check_url_var.get().strip()
        if not url:
            messagebox.showwarning(APP_NAME, "Укажи URL для проверки.")
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        if not core.is_running():
            if core.network_restore_pending():
                messagebox.showwarning(
                    APP_NAME,
                    "Предыдущий сеанс proxy завершился некорректно.\n\n"
                    "Сначала нажмите «Восстановить настройки сети», дождитесь "
                    "успешного восстановления и затем снова включите прокси.")
            elif core.stale_system_proxy():
                messagebox.showwarning(
                    APP_NAME,
                    "Windows использует PAC Arvectum, но этот Launcher не может "
                    "доказать владение предыдущим сеансом. Автоматический сброс "
                    "не выполняется, чтобы не повредить настройки сети.")
            else:
                messagebox.showinfo(APP_NAME, "Прокси не запущен. Нажмите «Включить прокси».")
            return
        self._set_busy("Проверка…", MINT_LIGHT)
        threading.Thread(target=self._do_check, args=(port, url), daemon=True).start()

    def _do_check(self, port, url):
        import urllib.request
        import urllib.error

        def probe(label, proxy_handler):
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy_handler))
            try:
                resp = opener.open(url, timeout=20)
                code = getattr(resp, "status", resp.getcode())
                reason = getattr(resp, "reason", "") or ""
                final_url = resp.geturl()
                # Не читаем весь ответ: у google.com он может быть большим.
                resp.read(256)
                suffix = "" if final_url == url else "\n  После редиректа: %s" % final_url
                return "%s: HTTP %s %s%s" % (label, code, reason, suffix)
            except urllib.error.HTTPError as e:
                final_url = e.geturl() or url
                suffix = "" if final_url == url else "\n  После редиректа: %s" % final_url
                return "%s: HTTP %s %s%s" % (label, e.code, e.reason, suffix)
            except Exception as e:
                return "%s: ошибка соединения — %s" % (label, e)

        result = "Проверка: %s\n%s" % (
            probe("Через прокси", {"http": "http://127.0.0.1:%d" % port,
                                   "https": "http://127.0.0.1:%d" % port}),
            probe("Напрямую", {}),
        )

        def show():
            self.refresh_status()
            messagebox.showinfo(APP_NAME, result)
        self.root.after(0, show)

    # -- диалоги ---------------------------------------------------------------

    def settings(self):
        settings = core.load_settings()
        dlg = SettingsDialog(self.root, settings)
        dlg.wait_window()
        if dlg.result:
            if not core.save_settings(dlg.result):
                messagebox.showerror(
                    APP_NAME,
                    "Не удалось безопасно сохранить настройки proxy. "
                    "Пароль не записан в открытом виде. Подробности в «Журнал».")
                return
            self._maybe_restart_after_settings()

    def _maybe_restart_after_settings(self):
        if not core.is_running():
            return
        if messagebox.askyesno(
                APP_NAME,
                "Настройки сохранены. Прокси сейчас работает — перезапустить, чтобы применить?",
                icon="question"):
            self._set_busy("Перезапуск…", MINT_LIGHT)
            _run_headless("--stop")
            self.root.after(250, self._restart_after_stop)
        else:
            self.root.after(250, self.refresh_status)

    def _restart_after_stop(self, attempt=0):
        if core.is_running():
            if attempt < 20:
                self.root.after(250, lambda: self._restart_after_stop(attempt + 1))
                return
            self.refresh_status()
            messagebox.showerror(APP_NAME, "Не удалось остановить старый процесс для перезапуска. См. «Журнал».")
            return
        _run_headless("--start")
        self.root.after(250, self._after_start)

    def exceptions(self):
        ExceptionsDialog(self.root)
        self.refresh_status()

    def show_log(self):
        path = core.log_path()
        if os.path.exists(path):
            try:
                os.startfile(path) if os.name == "nt" else subprocess.run(["open", path])
            except Exception as e:
                messagebox.showerror(APP_NAME, "Не удалось открыть журнал: %s" % e)
        else:
            messagebox.showinfo(APP_NAME, "Журнал пока пуст.")

    def doctor(self):
        """Run read-only APL-DIAG-004 checks without blocking the Tk event loop."""
        self._set_busy("Диагностика…", MINT_LIGHT)
        threading.Thread(target=self._do_doctor, daemon=True).start()

    def _do_doctor(self):
        try:
            report = doctor_module.run_doctor()
        except Exception as exc:
            try:
                core.structured_log(
                    "doctor failed",
                    event="diagnostics.doctor_failed",
                    error=repr(exc),
                )
            except Exception:
                pass

            def show_error():
                self.refresh_status()
                messagebox.showerror(
                    APP_NAME,
                    "Автоматическая диагностика завершилась внутренней ошибкой. "
                    "Состояние сети не изменялось. Подробности сохранены в «Журнал».")
            self.root.after(0, show_error)
            return

        def show_result():
            self.refresh_status()
            overall = report.get("overall", doctor_module.FAIL)
            counts = report.get("counts") or {}
            problem_checks = [
                item for item in report.get("checks") or []
                if item.get("status") != doctor_module.PASS
            ]
            title = {
                doctor_module.PASS: "Диагностика: проблем не обнаружено.",
                doctor_module.WARN: "Диагностика: есть предупреждения.",
                doctor_module.FAIL: "Диагностика: требуется действие.",
            }.get(overall, "Диагностика завершена.")
            lines = [
                title,
                "PASS %s · WARN %s · FAIL %s" % (
                    counts.get(doctor_module.PASS, 0),
                    counts.get(doctor_module.WARN, 0),
                    counts.get(doctor_module.FAIL, 0),
                ),
            ]
            if problem_checks:
                lines.append("")
                lines.append("Проверки, требующие внимания:")
                for item in problem_checks[:8]:
                    lines.append("[%s] %s" % (item.get("status"), item.get("id")))
            actions = report.get("recommended_actions") or []
            if actions:
                lines.append("")
                lines.append("Рекомендуемые действия:")
                for action in actions[:5]:
                    lines.append("• %s" % action)
            text = "\n".join(lines)
            if overall == doctor_module.FAIL:
                messagebox.showerror(APP_NAME, text)
            elif overall == doctor_module.WARN:
                messagebox.showwarning(APP_NAME, text)
            else:
                messagebox.showinfo(APP_NAME, text)

        self.root.after(0, show_result)

    # -- автозапуск -------------------------------------------------------------

    def _autostart_run_value(self):
        """Return the per-user Run value, or None when it is absent/unreadable."""
        if os.name != "nt":
            return None
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_RUN_PATH) as key:
                value, _ = winreg.QueryValueEx(key, AUTOSTART_RUN_VALUE)
                return str(value or "")
        except FileNotFoundError:
            return None
        except Exception:
            return None

    def _autostart_run_is_ours(self, value=None):
        value = self._autostart_run_value() if value is None else value
        if not value:
            return False
        return core.is_owned_arvectum_start_command(value)

    def _autostart_task_xml(self):
        try:
            result = subprocess.run(
                ["schtasks", "/Query", "/TN", TASK_NAME, "/XML"],
                capture_output=True, text=True)
            if result.returncode != 0:
                return None
            return result.stdout or ""
        except Exception:
            return None

    def _autostart_task_is_ours(self, xml=None):
        xml = self._autostart_task_xml() if xml is None else xml
        if xml is None:
            return False
        if getattr(sys, "frozen", False):
            identity = os.path.realpath(sys.executable)
        else:
            identity = os.path.realpath(os.path.join(core.app_dir(), "proxy_core.py"))
        return identity.lower() in xml.lower()

    def _autostart_enabled(self):
        # Current versions use HKCU\\...\\Run: no elevation is required and this
        # works even when Task Scheduler creation is restricted by Windows policy.
        return self._autostart_run_is_ours() or self._autostart_task_is_ours()

    def _toggle_autostart(self):
        if self.auto_var.get():
            if not self._enable_autostart():
                # A checkbutton flips its variable before invoking command.
                # Keep the visible state truthful when enabling was refused
                # (for example, a foreign task has the same name).
                self.auto_var.set(False)
                return
        else:
            self._disable_autostart()
        self.auto_var.set(self._autostart_enabled())

    def _enable_autostart(self):
        settings = core.load_settings()
        configured = any((u.get("host") or "").strip() for u in settings.get("upstream") or [])
        if not configured:
            messagebox.showwarning(APP_NAME, "Сначала настройте внешний прокси, затем включайте автозапуск.")
            return False
        if _portable_fallback_active():
            self.auto_var.set(False)
            messagebox.showwarning(
                APP_NAME,
                "Автозапуск временно недоступен: Windows не запустила "
                "постоянную копию Launcher. Текущую portable-версию можно "
                "использовать вручную; не переносите её и не удаляйте, пока "
                "proxy работает."
            )
            return False
        existing_run = self._autostart_run_value()
        if existing_run is not None and not self._autostart_run_is_ours(existing_run):
            self.auto_var.set(False)
            messagebox.showerror(
                APP_NAME,
                "Запись автозапуска Windows с именем ArvectumProxyLauncher уже "
                "принадлежит другой команде. Она не будет перезаписана.")
            return False
        existing_task = self._autostart_task_xml()
        if existing_task is not None and not self._autostart_task_is_ours(existing_task):
            self.auto_var.set(False)
            messagebox.showerror(
                APP_NAME,
                "Задача Windows с именем ArvectumProxyLauncher уже существует, "
                "но принадлежит другой команде. Она не будет перезаписана.")
            return False
        try:
            target = _autostart_target()
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, AUTOSTART_RUN_PATH) as key:
                winreg.SetValueEx(key, AUTOSTART_RUN_VALUE, 0, winreg.REG_SZ, target)
            messagebox.showinfo(APP_NAME, "Прокси будет запускаться автоматически при входе в Windows.")
            return True
        except Exception as e:
            self.auto_var.set(False)
            messagebox.showerror(APP_NAME, "Не удалось включить автозапуск: %s" % e)
            return False

    def _disable_autostart(self):
        try:
            import winreg
            current = self._autostart_run_value()
            if self._autostart_run_is_ours(current):
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_RUN_PATH, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, AUTOSTART_RUN_VALUE)
                return
            # Compatibility cleanup for tasks created by releases before RC2.1.
            xml = self._autostart_task_xml()
            if xml is not None and self._autostart_task_is_ours(xml):
                subprocess.run(["schtasks", "/Delete", "/F", "/TN", TASK_NAME],
                               capture_output=True, text=True)
        except Exception:
            pass

    # -- прочее --------------------------------------------------------------------

    def _maybe_first_run(self):
        s = core.load_settings()
        configured = any((u.get("host") or "").strip() for u in s.get("upstream") or [])
        if not configured:
            messagebox.showinfo(
                APP_NAME,
                "Укажи данные внешнего прокси: IP адрес, порт, логин и пароль.")
            self.settings()


def main():
    # Doctor is intentionally evaluated before portable self-handoff: the exit
    # code/report must describe the exact executable the operator invoked.
    if len(sys.argv) > 1 and sys.argv[1] in ("--doctor", "--doctor-json"):
        if sys.argv[1] == "--doctor":
            return doctor_module.main([])
        doctor_args = ["--json"]
        if len(sys.argv) > 2:
            doctor_args.extend(["--output", sys.argv[2]])
        return doctor_module.main(doctor_args)

    # A portable launch first tries the permanent Documents location.
    # If Windows refuses that handoff, the already-running portable GUI remains
    # a valid manual P0 fallback for the current session.
    if core.handoff_to_stable_copy(sys.argv[1:]):
        return 0
    handoff_error = core.self_heal_error()
    portable_fallback = _portable_fallback_active()
    if len(sys.argv) > 1 and sys.argv[1] in ("--start", "--stop", "--status", "--rollback"):
        sys.argv = [sys.argv[0], sys.argv[1]]
        return core.main()
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    if not core._ensure_local_files():
        return 1
    if portable_fallback:
        core._log(
            "portable fallback active; Run entries left unchanged because "
            "canonical execution was not confirmed"
        )
    else:
        core.repair_portable_run_entries()
    root = tk.Tk()
    if handoff_error:
        messagebox.showerror(
            APP_NAME,
            handoff_error + "\n\nLauncher оставлен открытым из текущей папки. "
            "Закройте старую копию приложения и повторите запуск.",
        )
    elif portable_fallback:
        messagebox.showwarning(
            APP_NAME,
            "Не удалось запустить постоянную копию Launcher в Documents.\n\n"
            "Текущая portable-версия продолжит работать в этом сеансе. "
            "Автозапуск временно отключён: запускайте этот EXE вручную."
        )
    app = Launcher(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
