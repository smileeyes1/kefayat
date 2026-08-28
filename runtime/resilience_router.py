"""Kefayat resilient AI routing core.

Local-first, cache-first, quota-aware, provider-neutral. This module never
attempts to bypass provider limits. It only selects an already-authorized
route and fails closed when no safe route is available.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable, Optional


class Route(str, Enum):
    CACHE = "cache"
    LOCAL_RULES = "local_rules"
    LOCAL_MODEL = "local_model"
    AUTHORIZED_CLOUD = "authorized_cloud"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Request:
    task: str
    payload: dict
    knowledge_version: str
    prompt_version: str = "1"

    @property
    def key(self) -> str:
        raw = json.dumps(
            {
                "task": self.task,
                "payload": self.payload,
                "knowledge_version": self.knowledge_version,
                "prompt_version": self.prompt_version,
            }, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        )
        return sha256(raw.encode("utf-8")).hexdigest()


class Cache:
    def __init__(self, path: str = "runtime/cache.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def get(self, key: str) -> Optional[dict]:
        return self.data.get(key)

    def put(self, key: str, value: dict) -> None:
        self.data[key] = value
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )


@dataclass
class QuotaState:
    cloud_allowed: bool = True
    reason: str = "normal"


class ResilientRouter:
    def __init__(self, cache: Cache | None = None) -> None:
        self.cache = cache or Cache()
        self.stats = {"cache": 0, "local_rules": 0, "local_model": 0, "cloud": 0, "blocked": 0}

    def resolve(
        self,
        request: Request,
        local_rules: Callable[[Request], Optional[dict]],
        local_model: Callable[[Request], Optional[dict]] | None = None,
        authorized_cloud: Callable[[Request], Optional[dict]] | None = None,
        quota: QuotaState | None = None,
    ) -> tuple[Route, Optional[dict]]:
        cached = self.cache.get(request.key)
        if cached is not None:
            self.stats["cache"] += 1
            return Route.CACHE, cached

        result = local_rules(request)
        if result is not None:
            self.stats["local_rules"] += 1
            self.cache.put(request.key, result)
            return Route.LOCAL_RULES, result

        if local_model is not None:
            result = local_model(request)
            if result is not None:
                self.stats["local_model"] += 1
                self.cache.put(request.key, result)
                return Route.LOCAL_MODEL, result

        state = quota or QuotaState()
        if authorized_cloud is not None and state.cloud_allowed:
            result = authorized_cloud(request)
            if result is not None:
                self.stats["cloud"] += 1
                self.cache.put(request.key, result)
                return Route.AUTHORIZED_CLOUD, result

        self.stats["blocked"] += 1
        return Route.BLOCKED, None
