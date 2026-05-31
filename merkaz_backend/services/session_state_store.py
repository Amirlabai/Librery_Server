"""
File-backed session state for multi-worker deployments.
"""
import json
import os
import threading
from datetime import datetime, timedelta, timezone

import config.config as config
from utils.path_utils import resolve_config_path
from utils.logger_config import get_logger

logger = get_logger(__name__)
_lock = threading.Lock()

_DEFAULT_STATE = {
    "invalidated": {},
    "active": {},
    "token_version": {},
}


def _state_path() -> str:
    path = getattr(config, "SESSION_STATE_FILE", None)
    if not path:
        path = os.path.join(
            getattr(config, "SERVER_DATA_DIR", "data"), "session_state.json"
        )
    return resolve_config_path(path)


def _load() -> dict:
    path = _state_path()
    if not os.path.exists(path):
        return json.loads(json.dumps(_DEFAULT_STATE))
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in _DEFAULT_STATE:
            data.setdefault(key, _DEFAULT_STATE[key])
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Could not load session state: {e}")
        return json.loads(json.dumps(_DEFAULT_STATE))


def _save(data: dict) -> None:
    path = _state_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_token_version(email: str) -> int:
    with _lock:
        data = _load()
        return int(data["token_version"].get(email, 0))


def bump_token_version(email: str) -> int:
    with _lock:
        data = _load()
        ver = int(data["token_version"].get(email, 0)) + 1
        data["token_version"][email] = ver
        data["invalidated"][email] = datetime.now(timezone.utc).isoformat()
        _save(data)
        return ver


def clear_invalidation(email: str) -> None:
    with _lock:
        data = _load()
        data["invalidated"].pop(email, None)
        _save(data)


def is_invalidated(email: str) -> bool:
    with _lock:
        data = _load()
        return email in data["invalidated"]


def mark_online(email: str) -> None:
    with _lock:
        data = _load()
        data["active"][email] = datetime.now(timezone.utc).isoformat()
        _save(data)


def mark_offline(email: str) -> None:
    with _lock:
        data = _load()
        data["active"].pop(email, None)
        _save(data)


def cleanup_expired(timeout_minutes: int) -> list:
    removed = []
    threshold = timedelta(minutes=timeout_minutes)
    now = datetime.now(timezone.utc)
    with _lock:
        data = _load()
        for email, ts in list(data["active"].items()):
            try:
                last = datetime.fromisoformat(ts)
                if last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)
            except ValueError:
                removed.append(email)
                continue
            if now - last > threshold:
                del data["active"][email]
                removed.append(email)
        if removed:
            _save(data)
    return removed


def list_active() -> list:
    cleanup_expired(getattr(config, "SESSION_TIMEOUT_MINUTES", 15))
    with _lock:
        return list(_load()["active"].keys())
