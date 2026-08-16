# -*- coding: utf-8 -*-
"""Durable ownership/recovery journal for future per-application enforcement.

APL-ROUTE-004 contains no driver/firewall mutation. Platform adapters must
persist this journal before creating any owned enforcement resource.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
import tempfile
import uuid
from typing import Iterable, Mapping, Optional, Tuple

OWNER_ID = "arvectum.proxy-launcher.routing"
SCHEMA_VERSION = 1
RESOURCE_PREFIX = "Arvectum.ProxyLauncher."
_PHASES = {"prepared", "applied", "restoring"}


class RoutingOwnershipError(RuntimeError):
    pass


@dataclass(frozen=True)
class OwnedRoutingResource:
    resource_type: str
    resource_id: str

    def __post_init__(self):
        resource_type = str(self.resource_type or "").strip().lower()
        resource_id = str(self.resource_id or "").strip()
        if not resource_type or not resource_id.startswith(RESOURCE_PREFIX):
            raise ValueError("routing resources must use the Arvectum ownership namespace")
        object.__setattr__(self, "resource_type", resource_type)
        object.__setattr__(self, "resource_id", resource_id)


@dataclass(frozen=True)
class RoutingOwnershipState:
    session_id: str
    platform: str
    plan_digest: str
    phase: str
    resources: Tuple[OwnedRoutingResource, ...]
    created_at_utc: str

    def to_dict(self):
        return {
            "schema_version": SCHEMA_VERSION,
            "owner_id": OWNER_ID,
            "session_id": self.session_id,
            "platform": self.platform,
            "plan_digest": self.plan_digest,
            "phase": self.phase,
            "resources": [{"resource_type": r.resource_type, "resource_id": r.resource_id} for r in self.resources],
            "created_at_utc": self.created_at_utc,
        }

    @classmethod
    def from_dict(cls, payload: Mapping):
        if payload.get("schema_version") != SCHEMA_VERSION or payload.get("owner_id") != OWNER_ID:
            raise RoutingOwnershipError("routing ownership state belongs to another schema/owner")
        phase = str(payload.get("phase", ""))
        if phase not in _PHASES:
            raise RoutingOwnershipError("invalid routing ownership phase")
        digest = str(payload.get("plan_digest", ""))
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise RoutingOwnershipError("invalid routing plan digest")
        resources = tuple(OwnedRoutingResource(**item) for item in payload.get("resources", ()))
        if not resources:
            raise RoutingOwnershipError("routing ownership state has no resources")
        return cls(
            session_id=str(payload.get("session_id", "")),
            platform=str(payload.get("platform", "")),
            plan_digest=digest,
            phase=phase,
            resources=resources,
            created_at_utc=str(payload.get("created_at_utc", "")),
        )


def plan_digest(canonical_plan_json: str) -> str:
    return hashlib.sha256(str(canonical_plan_json).encode("utf-8")).hexdigest()


class RoutingOwnershipStore:
    def __init__(self, path: str):
        self.path = os.path.abspath(os.path.expanduser(path))

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def load(self) -> RoutingOwnershipState:
        try:
            with open(self.path, "r", encoding="utf-8") as stream:
                payload = json.load(stream)
        except Exception as exc:
            raise RoutingOwnershipError("routing ownership state is unreadable") from exc
        return RoutingOwnershipState.from_dict(payload)

    def _save(self, state: RoutingOwnershipState) -> None:
        parent = os.path.dirname(self.path)
        os.makedirs(parent, mode=0o700, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix="routing-ownership-", suffix=".tmp", dir=parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(state.to_dict(), stream, ensure_ascii=False, sort_keys=True, indent=2)
                stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
            os.chmod(temp, 0o600)
            os.replace(temp, self.path)
        finally:
            if os.path.exists(temp): os.unlink(temp)

    def prepare(self, *, platform: str, canonical_plan_json: str, resources: Iterable[OwnedRoutingResource], session_id: Optional[str] = None, now: Optional[str] = None) -> RoutingOwnershipState:
        if self.exists():
            raise RoutingOwnershipError("pending routing ownership state must be recovered before a new session")
        state = RoutingOwnershipState(
            session_id=session_id or str(uuid.uuid4()),
            platform=str(platform or "").strip().lower(),
            plan_digest=plan_digest(canonical_plan_json),
            phase="prepared",
            resources=tuple(resources),
            created_at_utc=now or datetime.now(timezone.utc).isoformat(),
        )
        if state.platform not in {"windows", "linux", "macos"} or not state.resources:
            raise RoutingOwnershipError("invalid routing ownership preparation")
        self._save(state)
        return state

    def transition(self, target_phase: str) -> RoutingOwnershipState:
        state = self.load()
        target = str(target_phase)
        allowed = {("prepared", "applied"), ("prepared", "restoring"), ("applied", "restoring")}
        if (state.phase, target) not in allowed:
            raise RoutingOwnershipError("unsafe routing ownership phase transition")
        updated = RoutingOwnershipState(state.session_id, state.platform, state.plan_digest, target, state.resources, state.created_at_utc)
        self._save(updated)
        return updated

    def clear_after_verified_restore(self, *, verified: bool) -> None:
        state = self.load()
        if not verified or state.phase != "restoring":
            raise RoutingOwnershipError("routing ownership evidence cannot be cleared before verified restoration")
        os.remove(self.path)
