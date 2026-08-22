# -*- coding: utf-8 -*-
"""Cross-platform routing rule domain model (routing-rule ownership).

This module deliberately contains no OS/network mutation code. It is the stable
control-plane schema consumed by later platform-specific routing adapters.
"""
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import json
import re
from typing import Any, Iterable, Mapping, Optional, Tuple

_RULE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


class RoutingAction(str, Enum):
    PROXY = "proxy"
    DIRECT = "direct"


class DestinationKind(str, Enum):
    ALL = "all"
    DOMAIN = "domain"
    CIDR = "cidr"


@dataclass(frozen=True)
class ApplicationIdentity:
    platform: str
    executable_path: str = ""
    bundle_id: str = ""
    package_id: str = ""
    display_name: str = ""

    def __post_init__(self):
        platform = str(self.platform or "").strip().lower()
        if platform not in {"windows", "macos", "linux"}:
            raise ValueError("application platform must be windows, macos or linux")
        executable = str(self.executable_path or "").strip()
        bundle = str(self.bundle_id or "").strip().lower()
        package = str(self.package_id or "").strip().lower()
        if not any((executable, bundle, package)):
            raise ValueError("application identity requires a stable executable/bundle/package id")
        object.__setattr__(self, "platform", platform)
        object.__setattr__(self, "executable_path", executable)
        object.__setattr__(self, "bundle_id", bundle)
        object.__setattr__(self, "package_id", package)
        object.__setattr__(self, "display_name", str(self.display_name or "").strip())

    @property
    def stable_id(self) -> str:
        if self.bundle_id:
            return f"{self.platform}:bundle:{self.bundle_id}"
        if self.package_id:
            return f"{self.platform}:package:{self.package_id}"
        value = self.executable_path.replace("\\", "/")
        if self.platform == "windows":
            value = value.lower()
        return f"{self.platform}:exe:{value}"


@dataclass(frozen=True)
class DestinationSelector:
    kind: DestinationKind
    value: str = ""

    def __post_init__(self):
        kind = self.kind if isinstance(self.kind, DestinationKind) else DestinationKind(str(self.kind))
        raw = str(self.value or "").strip()
        if kind == DestinationKind.ALL:
            normalized = "*"
        elif kind == DestinationKind.DOMAIN:
            normalized = raw.rstrip(".").lower().encode("idna").decode("ascii")
            if not normalized or "." not in normalized and normalized == "*":
                raise ValueError("invalid domain selector")
            if any(not label or len(label) > 63 for label in normalized.split(".")):
                raise ValueError("invalid domain selector")
        else:
            normalized = str(ipaddress.ip_network(raw, strict=False))
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class RoutingRule:
    rule_id: str
    action: RoutingAction
    destinations: Tuple[DestinationSelector, ...] = field(default_factory=lambda: (DestinationSelector(DestinationKind.ALL),))
    application: Optional[ApplicationIdentity] = None
    priority: int = 100
    enabled: bool = True
    description: str = ""

    def __post_init__(self):
        rule_id = str(self.rule_id or "").strip()
        if not _RULE_ID.match(rule_id):
            raise ValueError("invalid routing rule id")
        action = self.action if isinstance(self.action, RoutingAction) else RoutingAction(str(self.action))
        destinations = tuple(d if isinstance(d, DestinationSelector) else DestinationSelector(**d) for d in self.destinations)
        if not destinations:
            raise ValueError("routing rule requires at least one destination")
        if any(d.kind == DestinationKind.ALL for d in destinations) and len(destinations) != 1:
            raise ValueError("all destination cannot be combined with narrower selectors")
        priority = int(self.priority)
        if priority < 0 or priority > 10000:
            raise ValueError("routing rule priority out of range")
        object.__setattr__(self, "rule_id", rule_id)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "destinations", destinations)
        object.__setattr__(self, "priority", priority)
        object.__setattr__(self, "enabled", bool(self.enabled))
        object.__setattr__(self, "description", str(self.description or "").strip())

    def to_dict(self) -> Mapping[str, Any]:
        app = None
        if self.application:
            app = {
                "platform": self.application.platform,
                "executable_path": self.application.executable_path,
                "bundle_id": self.application.bundle_id,
                "package_id": self.application.package_id,
                "display_name": self.application.display_name,
            }
        return {
            "schema_version": 1,
            "rule_id": self.rule_id,
            "action": self.action.value,
            "destinations": [{"kind": d.kind.value, "value": d.value} for d in self.destinations],
            "application": app,
            "priority": self.priority,
            "enabled": self.enabled,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]):
        if int(payload.get("schema_version", 0)) != 1:
            raise ValueError("unsupported routing rule schema")
        app_payload = payload.get("application")
        app = ApplicationIdentity(**app_payload) if isinstance(app_payload, Mapping) else None
        destinations = tuple(DestinationSelector(DestinationKind(item["kind"]), item.get("value", "")) for item in payload.get("destinations", ()))
        return cls(
            rule_id=payload.get("rule_id", ""),
            action=RoutingAction(payload.get("action", "")),
            destinations=destinations,
            application=app,
            priority=payload.get("priority", 100),
            enabled=payload.get("enabled", True),
            description=payload.get("description", ""),
        )

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def ordered_rules(rules: Iterable[RoutingRule]) -> Tuple[RoutingRule, ...]:
    return tuple(sorted((r for r in rules if r.enabled), key=lambda r: (r.priority, r.rule_id)))
