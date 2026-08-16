from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI_PATH = ROOT / "proxy_gui.py"
TEST_PATH = ROOT / "tests" / "test_proxy_gui.py"
DOC_PATH = ROOT / "WINDOWS_FINAL_STATUS_UX.md"


def patch_gui():
    text = GUI_PATH.read_text(encoding="utf-8")
    if "def _final_status_view(" in text:
        raise SystemExit("proxy_gui.py already contains APL-WIN-001 helper")

    marker = "\n\nclass Launcher:\n"
    if marker not in text:
        raise SystemExit("Launcher marker not found")

    helper = r'''

def _final_status_view(running, enabled, pending, orphaned_pac, stale_proxy):
    """Return the user-facing final state for the Windows launcher.

    APL-WIN-001 keeps low-level engine/PAC details out of the primary status
    label and makes every stable state answer two questions: what is happening
    now, and what (if anything) the user should do next.
    """
    if running and enabled:
        return {
            "key": "active",
            "label": "ПРОКСИ РАБОТАЕТ",
            "color": MINT,
            "hint": (
                "Системный прокси Windows включён и направлен через Arvectum Proxy Launcher. "
                "Окно можно закрыть — прокси продолжит работать в фоне."
            ),
            "can_on": False,
            "can_off": True,
            "can_check": True,
            "restore_primary": False,
            "show_orphan_action": False,
        }
    if running:
        return {
            "key": "engine_only",
            "label": "ПРОКСИ ЗАПУЩЕН · НЕ ПОДКЛЮЧЕН",
            "color": MINT_LIGHT,
            "hint": (
                "Локальный прокси-процесс работает, но Windows пока не направляет через него трафик. "
                "Нажмите «Включить прокси», чтобы подключить системный прокси."
            ),
            "can_on": True,
            "can_off": True,
            "can_check": True,
            "restore_primary": False,
            "show_orphan_action": False,
        }
    if pending:
        return {
            "key": "recovery_required",
            "label": "НУЖНО ВОССТАНОВИТЬ СЕТЬ",
            "color": MINT_LIGHT,
            "hint": (
                "Предыдущий сеанс завершился некорректно. Сначала нажмите "
                "«Восстановить настройки сети», дождитесь успешного восстановления, "
                "а затем снова включите прокси."
            ),
            "can_on": False,
            "can_off": False,
            "can_check": True,
            "restore_primary": True,
            "show_orphan_action": False,
        }
    if orphaned_pac:
        return {
            "key": "orphaned_arvectum_pac",
            "label": "НУЖНО УДАЛИТЬ СТАРЫЕ НАСТРОЙКИ",
            "color": MINT_LIGHT,
            "hint": (
                "Windows использует локальные настройки Arvectum от предыдущего сеанса, "
                "но прокси-процесс уже не работает и резервная копия недоступна. "
                "Можно безопасно удалить только старую настройку Arvectum, не изменяя остальные настройки Windows."
            ),
            "can_on": False,
            "can_off": False,
            "can_check": False,
            "restore_primary": False,
            "show_orphan_action": True,
        }
    if stale_proxy:
        return {
            "key": "diagnostics_required",
            "label": "НУЖНА ДИАГНОСТИКА СЕТИ",
            "color": MINT_LIGHT,
            "hint": (
                "Windows всё ещё использует настройки Arvectum, но Launcher не может безопасно подтвердить "
                "предыдущий сеанс. Автоматический сброс не выполняется: откройте «Диагностика» или «Журнал»."
            ),
            "can_on": False,
            "can_off": False,
            "can_check": True,
            "restore_primary": False,
            "show_orphan_action": False,
        }
    return {
        "key": "off",
        "label": "ПРОКСИ ВЫКЛЮЧЕН",
        "color": SOFT_GRAY,
        "hint": (
            "Сеанс Arvectum не активен. Исходные сетевые настройки используются без изменений. "
            "Нажмите «Включить прокси», когда он понадобится."
        ),
        "can_on": True,
        "can_off": False,
        "can_check": True,
        "restore_primary": False,
        "show_orphan_action": False,
    }
'''
    text = text.replace(marker, helper + marker, 1)

    start = text.index("    def refresh_status(self):")
    end = text.index("    # -- действия", start)
    replacement = r'''    def refresh_status(self):
        running = core.is_running()
        enabled = core.system_proxy_enabled()
        pending = core.network_restore_pending()
        orphaned_pac = core.orphaned_arvectum_pac()
        stale_proxy = False
        if not running and not pending and not orphaned_pac:
            stale_proxy = core.stale_system_proxy()

        view = _final_status_view(
            running=running,
            enabled=enabled,
            pending=pending,
            orphaned_pac=orphaned_pac,
            stale_proxy=stale_proxy,
        )

        self.btn_doctor.state(["!disabled"])
        self.btn_restore.state(["!disabled"])
        self.btn_restore.configure(
            style="Mint.TButton" if view["restore_primary"] else "Ghost.TButton")
        self.btn_orphan_pac.pack_forget()

        self.chip.config(text="  %s  " % view["label"], bg=view["color"], fg=NAVY)
        self.status_hint.config(text=view["hint"], bg=MINT_SOFT, fg=NAVY)
        self.status_hint.grid()

        self.btn_on.state(["!disabled"] if view["can_on"] else ["disabled"])
        self.btn_off.state(["!disabled"] if view["can_off"] else ["disabled"])
        self.btn_check.state(["!disabled"] if view["can_check"] else ["disabled"])

        if view["show_orphan_action"]:
            self.btn_orphan_pac.state(["!disabled"])
            self.btn_orphan_pac.pack(side="left", padx=6)

'''
    text = text[:start] + replacement + text[end:]
    GUI_PATH.write_text(text, encoding="utf-8")


def patch_tests():
    text = TEST_PATH.read_text(encoding="utf-8")
    if "class FinalStatusUxTests" in text:
        raise SystemExit("test_proxy_gui.py already contains APL-WIN-001 tests")
    marker = '\n\nif __name__ == "__main__":\n'
    if marker not in text:
        raise SystemExit("test module footer not found")
    tests = r'''

class FinalStatusUxTests(unittest.TestCase):
    def status(self, **overrides):
        values = {
            "running": False,
            "enabled": False,
            "pending": False,
            "orphaned_pac": False,
            "stale_proxy": False,
        }
        values.update(overrides)
        return gui._final_status_view(**values)

    def test_active_state_is_unambiguous_and_actionable(self):
        view = self.status(running=True, enabled=True)
        self.assertEqual(view["key"], "active")
        self.assertEqual(view["label"], "ПРОКСИ РАБОТАЕТ")
        self.assertFalse(view["can_on"])
        self.assertTrue(view["can_off"])
        self.assertTrue(view["can_check"])
        self.assertIn("Windows", view["hint"])

    def test_engine_only_state_avoids_internal_pac_jargon_in_primary_label(self):
        view = self.status(running=True, enabled=False)
        self.assertEqual(view["key"], "engine_only")
        self.assertEqual(view["label"], "ПРОКСИ ЗАПУЩЕН · НЕ ПОДКЛЮЧЕН")
        self.assertNotIn("PAC", view["label"])
        self.assertTrue(view["can_on"])
        self.assertTrue(view["can_off"])

    def test_recovery_state_blocks_proxy_actions_and_promotes_restore(self):
        view = self.status(pending=True)
        self.assertEqual(view["key"], "recovery_required")
        self.assertFalse(view["can_on"])
        self.assertFalse(view["can_off"])
        self.assertTrue(view["restore_primary"])
        self.assertIn("Восстановить настройки сети", view["hint"])

    def test_orphaned_state_exposes_only_safe_cleanup_action(self):
        view = self.status(orphaned_pac=True)
        self.assertEqual(view["key"], "orphaned_arvectum_pac")
        self.assertFalse(view["can_on"])
        self.assertFalse(view["can_off"])
        self.assertFalse(view["can_check"])
        self.assertTrue(view["show_orphan_action"])

    def test_diagnostics_state_is_fail_closed(self):
        view = self.status(stale_proxy=True)
        self.assertEqual(view["key"], "diagnostics_required")
        self.assertFalse(view["can_on"])
        self.assertFalse(view["can_off"])
        self.assertIn("Диагностика", view["hint"])

    def test_off_state_confirms_safe_final_state(self):
        view = self.status()
        self.assertEqual(view["key"], "off")
        self.assertEqual(view["label"], "ПРОКСИ ВЫКЛЮЧЕН")
        self.assertTrue(view["can_on"])
        self.assertFalse(view["can_off"])
        self.assertIn("Исходные сетевые настройки", view["hint"])

    def test_running_state_keeps_precedence_over_recovery_evidence(self):
        view = self.status(running=True, enabled=True, pending=True)
        self.assertEqual(view["key"], "active")
'''
    text = text.replace(marker, tests + marker, 1)
    TEST_PATH.write_text(text, encoding="utf-8")


def write_doc():
    DOC_PATH.write_text(
        """# APL-WIN-001 — Final status UX\n\n"
        "Status: implemented\n\n"
        "## Contract\n\n"
        "The Windows launcher must always present one stable, user-facing final state. "
        "The primary label describes the outcome in product language; the hint explains "
        "what Windows is doing and the next safe action. Low-level engine/PAC terminology "
        "is not used as the primary status.\n\n"
        "| State | Primary status | Main action policy |\n"
        "| --- | --- | --- |\n"
        "| active | `ПРОКСИ РАБОТАЕТ` | disable On; enable Off/Check |\n"
        "| engine_only | `ПРОКСИ ЗАПУЩЕН · НЕ ПОДКЛЮЧЕН` | enable On/Off/Check |\n"
        "| recovery_required | `НУЖНО ВОССТАНОВИТЬ СЕТЬ` | block On/Off; promote Restore |\n"
        "| orphaned_arvectum_pac | `НУЖНО УДАЛИТЬ СТАРЫЕ НАСТРОЙКИ` | expose only governed Arvectum cleanup |\n"
        "| diagnostics_required | `НУЖНА ДИАГНОСТИКА СЕТИ` | block On/Off; keep diagnostics available |\n"
        "| off | `ПРОКСИ ВЫКЛЮЧЕН` | enable On; disable Off |\n\n"
        "## Acceptance\n\n"
        "- final status is deterministic and independently unit-testable;\n"
        "- normal ON/OFF states include a persistent explanatory hint, not only modal dialogs;\n"
        "- partial/unsafe states are explicit and action-oriented;\n"
        "- recovery and ownership safety semantics from Gate R4 are preserved;\n"
        "- no status claims that a third-party application necessarily obeys the Windows system proxy.\n"
        """,
        encoding="utf-8",
    )


if __name__ == "__main__":
    patch_gui()
    patch_tests()
    write_doc()
