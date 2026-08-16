# APL-WIN-001 — Final status UX

Status: **implemented**

## Contract

The Windows launcher must always present one stable, user-facing final state. The primary label describes the outcome in product language; the persistent hint explains what Windows is doing and the next safe action. Low-level engine/PAC terminology is not used as the primary status for normal operation.

| State | Primary status | Main action policy |
| --- | --- | --- |
| `active` | `ПРОКСИ РАБОТАЕТ` | disable On; enable Off/Check |
| `engine_only` | `ПРОКСИ ЗАПУЩЕН · НЕ ПОДКЛЮЧЕН` | enable On/Off/Check |
| `recovery_required` | `НУЖНО ВОССТАНОВИТЬ СЕТЬ` | block On/Off; promote Restore |
| `orphaned_arvectum_pac` | `НУЖНО УДАЛИТЬ СТАРЫЕ НАСТРОЙКИ` | expose only governed Arvectum cleanup |
| `diagnostics_required` | `НУЖНА ДИАГНОСТИКА СЕТИ` | block On/Off; keep diagnostics available |
| `off` | `ПРОКСИ ВЫКЛЮЧЕН` | enable On; disable Off |

## Acceptance

- final status is deterministic and independently unit-testable;
- normal ON/OFF states include a persistent explanatory hint, not only modal dialogs;
- partial and unsafe states are explicit and action-oriented;
- recovery and ownership safety semantics from Gate R4 are preserved;
- existing release-contract markers for recovery promotion and orphaned Arvectum PAC handling remain intact;
- no status claims that a third-party application necessarily obeys the Windows system proxy.

## Verification

The implementation is covered by `tests/test_proxy_gui.py` and the full repository regression suite. The branch implementation passed Python compilation, the targeted GUI contract suite, and the complete unit-test discovery run before admission to pull-request review.
