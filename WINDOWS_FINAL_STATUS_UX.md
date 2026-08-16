# APL-WIN-001 — Final status UX

"
        "Status: implemented

"
        "## Contract

"
        "The Windows launcher must always present one stable, user-facing final state. "
        "The primary label describes the outcome in product language; the hint explains "
        "what Windows is doing and the next safe action. Low-level engine/PAC terminology "
        "is not used as the primary status.

"
        "| State | Primary status | Main action policy |
"
        "| --- | --- | --- |
"
        "| active | `ПРОКСИ РАБОТАЕТ` | disable On; enable Off/Check |
"
        "| engine_only | `ПРОКСИ ЗАПУЩЕН · НЕ ПОДКЛЮЧЕН` | enable On/Off/Check |
"
        "| recovery_required | `НУЖНО ВОССТАНОВИТЬ СЕТЬ` | block On/Off; promote Restore |
"
        "| orphaned_arvectum_pac | `НУЖНО УДАЛИТЬ СТАРЫЕ НАСТРОЙКИ` | expose only governed Arvectum cleanup |
"
        "| diagnostics_required | `НУЖНА ДИАГНОСТИКА СЕТИ` | block On/Off; keep diagnostics available |
"
        "| off | `ПРОКСИ ВЫКЛЮЧЕН` | enable On; disable Off |

"
        "## Acceptance

"
        "- final status is deterministic and independently unit-testable;
"
        "- normal ON/OFF states include a persistent explanatory hint, not only modal dialogs;
"
        "- partial/unsafe states are explicit and action-oriented;
"
        "- recovery and ownership safety semantics from Gate R4 are preserved;
"
        "- no status claims that a third-party application necessarily obeys the Windows system proxy.
"
        