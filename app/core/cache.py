import json
import time
from typing import Any

import redis

from app.core.config import settings


_memory_cache: dict[str, dict[str, Any]] = {}


def get_redis_client():
    if not settings.redis_enabled:
        return None

    try:
        client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
        client.ping()
        return client
    except redis.RedisError:
        return None


redis_client = get_redis_client()


def get_cache(key: str) -> Any | None:
    if redis_client:
        try:
            cached_value = redis_client.get(key)

            if cached_value is None:
                return None

            return json.loads(cached_value)
        except redis.RedisError:
            return None

    cached_item = _memory_cache.get(key)

    if not cached_item:
        return None

    if cached_item["expires_at"] < time.time():
        _memory_cache.pop(key, None)
        return None

    return cached_item["value"]


def set_cache(key: str, value: Any, ttl_seconds: int = 60) -> None:
    if redis_client:
        try:
            redis_client.setex(
                key,
                ttl_seconds,
                json.dumps(value, default=str),
            )
            return
        except redis.RedisError:
            return

    _memory_cache[key] = {
        "value": value,
        "expires_at": time.time() + ttl_seconds,
    }


def delete_cache_pattern(pattern: str) -> None:
    if redis_client:
        try:
            for key in redis_client.scan_iter(pattern):
                redis_client.delete(key)
            return
        except redis.RedisError:
            return

    if pattern.endswith("*"):
        prefix = pattern[:-1]
        keys_to_delete = [key for key in _memory_cache if key.startswith(prefix)]

        for key in keys_to_delete:
            _memory_cache.pop(key, None)
    else:
        _memory_cache.pop(pattern, None)