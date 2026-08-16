# -*- coding: utf-8 -*-
"""Stable macOS capability/failure UX mapping for APL-MAC-002."""
from typing import Any, Mapping

from macos_networksetup_preflight import MacOSPreflightStatus


def macos_capability_view(preflight: Any, *, running: bool = False) -> Mapping[str, Any]:
    status = getattr(preflight, "status", MacOSPreflightStatus.UNAVAILABLE)
    reasons = tuple(getattr(preflight, "reasons", ()) or ())
    if status == MacOSPreflightStatus.READY:
        return {
            "key": "macos_ready", "label": "ГОТОВО К ПОДКЛЮЧЕНИЮ",
            "hint": "macOS networksetup доступен, состояние сетевых служб прочитано безопасно.",
            "can_on": True, "can_off": bool(running), "authorization_required": False,
            "reasons": reasons,
        }
    if status == MacOSPreflightStatus.AUTH_REQUIRED:
        return {
            "key": "macos_auth_required", "label": "НУЖНО СИСТЕМНОЕ РАЗРЕШЕНИЕ",
            "hint": "macOS требует системное разрешение. Arvectum не запрашивает и не сохраняет пароль и не меняет сеть до явного действия пользователя.",
            "can_on": True, "can_off": bool(running), "authorization_required": True,
            "reasons": reasons,
        }
    return {
        "key": "macos_unavailable", "label": "СИСТЕМНЫЙ ПРОКСИ НЕДОСТУПЕН",
        "hint": "На этом Mac безопасная работа через networksetup сейчас не подтверждена. Сеть оставлена без изменений.",
        "can_on": False, "can_off": bool(running), "authorization_required": False,
        "reasons": reasons,
    }


def macos_failure_message(error: Any) -> str:
    text = str(error or "").strip()
    lowered = text.lower()
    if any(token in lowered for token in ("not authorized", "authorization", "administrator")):
        return "macOS не разрешила изменение сетевых настроек. Прокси не применён; повторите действие и подтвердите системное разрешение."
    if "networksetup" in lowered:
        return "Системная утилита networksetup недоступна или вернула ошибку. Сеть оставлена без изменений."
    if "rollback" in lowered or "restore" in lowered:
        return "Не удалось безопасно завершить восстановление сетевых настроек. Не включайте прокси повторно до проверки диагностического пакета."
    return "Операция системного прокси не выполнена. Сеть оставлена в подтверждённом состоянии либо восстановлена из rollback-снимка."
