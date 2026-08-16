from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI_PATH = ROOT / "proxy_gui.py"


def patch_gui():
    text = GUI_PATH.read_text(encoding="utf-8")

    import_marker = "import proxy_core as core\nimport doctor as doctor_module\n"
    if "import connection_test as connection_test_module" not in text:
        if import_marker not in text:
            raise SystemExit("proxy_gui.py import marker not found")
        text = text.replace(
            import_marker,
            import_marker + "import connection_test as connection_test_module\n",
            1,
        )

    text = text.replace(
        '  * проверка работы ("мой IP")',
        "  * встроенная проверка internet / upstream / HTTP / SOCKS5 / PAC / Windows",
        1,
    )

    start = text.index("    def check(self):")
    end = text.index("    # -- диалоги", start)
    replacement = r'''    def check(self):
        url = self.check_url_var.get().strip()
        if not url:
            messagebox.showwarning(APP_NAME, "Укажи URL для проверки.")
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        self._set_busy("Проверка соединения…", MINT_LIGHT)
        threading.Thread(target=self._do_check, args=(url,), daemon=True).start()

    def _do_check(self, url):
        try:
            report = connection_test_module.run_connection_test(url)
        except Exception as exc:
            try:
                core.structured_log(
                    "connection test failed",
                    event="diagnostics.connection_test_failed",
                    error=repr(exc),
                )
            except Exception:
                pass

            def show_error():
                self.refresh_status()
                messagebox.showerror(
                    APP_NAME,
                    "Встроенная проверка соединения завершилась внутренней ошибкой. "
                    "Состояние сети не изменялось. Подробности сохранены в «Журнал».",
                )

            self.root.after(0, show_error)
            return

        def show():
            self.refresh_status()
            text = connection_test_module.format_report(report)
            overall = report.get("overall", connection_test_module.FAIL)
            if overall == connection_test_module.FAIL:
                messagebox.showerror(APP_NAME, text)
            elif overall == connection_test_module.WARN:
                messagebox.showwarning(APP_NAME, text)
            else:
                messagebox.showinfo(APP_NAME, text)

        self.root.after(0, show)

'''
    text = text[:start] + replacement + text[end:]
    GUI_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    patch_gui()
