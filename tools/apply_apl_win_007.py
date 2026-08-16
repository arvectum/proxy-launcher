from pathlib import Path


PATH = Path("proxy_gui.py")
START = "    # -- автозапуск -------------------------------------------------------------\n"
END = "    # -- прочее --------------------------------------------------------------------\n"

NEW_SECTION = r'''    # -- автозапуск -------------------------------------------------------------

    def _autostart_run_value(self):
        """Return the per-user Run value.

        Missing is represented by ``None``. Any other registry read failure is
        an unknown ownership state and therefore raises: production autostart
        must never treat "unreadable" as "safe to overwrite".
        """
        if os.name != "nt":
            return None
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_RUN_PATH) as key:
                value, _ = winreg.QueryValueEx(key, AUTOSTART_RUN_VALUE)
                return str(value or "")
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise RuntimeError(
                "Не удалось безопасно прочитать запись автозапуска Windows: %s" % exc
            ) from exc

    def _autostart_run_is_ours(self, value=None):
        value = self._autostart_run_value() if value is None else value
        if not value:
            return False
        return core.is_owned_arvectum_start_command(value)

    def _write_autostart_run_value(self, command):
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, AUTOSTART_RUN_PATH) as key:
            winreg.SetValueEx(key, AUTOSTART_RUN_VALUE, 0, winreg.REG_SZ, command)

    def _delete_owned_autostart_run_value(self):
        """Delete the Run value only after a live ownership re-check."""
        if os.name != "nt":
            return False
        import winreg
        try:
            with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    AUTOSTART_RUN_PATH,
                    0,
                    winreg.KEY_QUERY_VALUE | winreg.KEY_SET_VALUE) as key:
                try:
                    live, _ = winreg.QueryValueEx(key, AUTOSTART_RUN_VALUE)
                except FileNotFoundError:
                    return False
                live = str(live or "")
                if not self._autostart_run_is_ours(live):
                    return False
                winreg.DeleteValue(key, AUTOSTART_RUN_VALUE)
                return True
        except FileNotFoundError:
            return False

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
        """Prove legacy task ownership from an Exec action, not arbitrary XML text."""
        xml = self._autostart_task_xml() if xml is None else xml
        if not xml:
            return False
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml)
        except Exception:
            return False

        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] != "Exec":
                continue
            command = ""
            arguments = ""
            for child in list(element):
                local = child.tag.rsplit("}", 1)[-1]
                if local == "Command":
                    command = (child.text or "").strip()
                elif local == "Arguments":
                    arguments = (child.text or "").strip()
            if not command:
                continue
            command_line = subprocess.list2cmdline([command])
            if arguments:
                command_line += " " + arguments
            if core.is_owned_arvectum_start_command(command_line):
                return True
        return False

    def _autostart_enabled(self):
        # Current versions use HKCU\\...\\Run: no elevation is required. A
        # provably-owned legacy task still counts as enabled until migrated or
        # explicitly disabled.
        try:
            if self._autostart_run_is_ours():
                return True
        except Exception as exc:
            try:
                core.structured_log(
                    "autostart Run state unreadable",
                    event="autostart.state_unknown",
                    error=repr(exc),
                )
            except Exception:
                pass
        return self._autostart_task_is_ours()

    def _toggle_autostart(self):
        requested = bool(self.auto_var.get())
        ok = self._enable_autostart() if requested else self._disable_autostart()
        # A checkbutton flips before invoking command. Always re-read the real
        # owned state so a refused/partial operation cannot leave a lying UI.
        self.auto_var.set(self._autostart_enabled())
        return ok

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

        try:
            existing_run = self._autostart_run_value()
        except Exception as exc:
            self.auto_var.set(False)
            messagebox.showerror(APP_NAME, str(exc))
            return False

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
                "но её Exec-действие не принадлежит Arvectum Proxy Launcher. "
                "Она не будет изменена или удалена.")
            return False

        try:
            target = _autostart_target()
            self._write_autostart_run_value(target)
            verified = self._autostart_run_value()
        except Exception as exc:
            if existing_run is None:
                try:
                    self._delete_owned_autostart_run_value()
                except Exception:
                    pass
            self.auto_var.set(False)
            messagebox.showerror(APP_NAME, "Не удалось включить автозапуск: %s" % exc)
            return False

        if verified != target or not self._autostart_run_is_ours(verified):
            if existing_run is None:
                try:
                    self._delete_owned_autostart_run_value()
                except Exception:
                    pass
            self.auto_var.set(False)
            messagebox.showerror(
                APP_NAME,
                "Windows не подтвердила точную запись автозапуска Launcher. "
                "Изменение отменено; запускайте приложение вручную и проверьте «Журнал».")
            return False

        # Migrate a provably-owned legacy task only after the canonical Run
        # value has been written and read back successfully.
        if existing_task is not None and self._autostart_task_is_ours(existing_task):
            result = subprocess.run(
                ["schtasks", "/Delete", "/F", "/TN", TASK_NAME],
                capture_output=True,
                text=True,
            )
            still_owned = self._autostart_task_is_ours(self._autostart_task_xml())
            if result.returncode != 0 or still_owned:
                # If this operation introduced the Run value, remove it again
                # so a failed migration cannot create two startup paths.
                if existing_run is None:
                    try:
                        self._delete_owned_autostart_run_value()
                    except Exception:
                        pass
                messagebox.showerror(
                    APP_NAME,
                    "Каноническая запись Run создана, но старую задачу автозапуска "
                    "не удалось безопасно удалить. Новый Run откатан, если он был "
                    "создан сейчас. Проверьте права Task Scheduler и повторите.")
                return False

        messagebox.showinfo(APP_NAME, "Прокси будет запускаться автоматически при входе в Windows.")
        return True

    def _disable_autostart(self):
        errors = []

        try:
            current = self._autostart_run_value()
            if self._autostart_run_is_ours(current):
                if not self._delete_owned_autostart_run_value():
                    errors.append("owned Run-запись не была удалена")
                else:
                    remaining = self._autostart_run_value()
                    if self._autostart_run_is_ours(remaining):
                        errors.append("owned Run-запись осталась после удаления")
        except Exception as exc:
            errors.append("не удалось безопасно проверить/удалить Run: %s" % exc)

        # Do not return after Run cleanup: old releases may have both mechanisms.
        task_xml = self._autostart_task_xml()
        if task_xml is not None and self._autostart_task_is_ours(task_xml):
            result = subprocess.run(
                ["schtasks", "/Delete", "/F", "/TN", TASK_NAME],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                errors.append("legacy-задачу Task Scheduler не удалось удалить")
            elif self._autostart_task_is_ours(self._autostart_task_xml()):
                errors.append("legacy-задача Task Scheduler осталась после удаления")

        if errors:
            messagebox.showerror(
                APP_NAME,
                "Автозапуск выключен не полностью:\n• " + "\n• ".join(errors) +
                "\n\nЧужие записи не изменялись. Проверьте «Журнал» и повторите операцию."
            )
            return False
        return True

'''


def main():
    text = PATH.read_text(encoding="utf-8")
    start = text.find(START)
    if start < 0:
        raise SystemExit("autostart start marker not found")
    end = text.find(END, start)
    if end < 0:
        raise SystemExit("autostart end marker not found")
    updated = text[:start] + NEW_SECTION + text[end:]
    if updated == text:
        raise SystemExit("proxy_gui.py was not changed")
    PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
