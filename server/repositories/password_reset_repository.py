"""
Password reset token persistence (one-time use).
"""
import csv
import os
import threading
from datetime import datetime

import config.config as config
from utils.path_utils import resolve_config_path
from utils.logger_config import get_logger

logger = get_logger(__name__)
_lock = threading.Lock()


def _db_path() -> str:
    return resolve_config_path(config.PASSWORD_RESET_DATABASE)


def save_token(email: str, token: str) -> None:
    path = _db_path()
    rows = []
    with _lock:
        if os.path.exists(path):
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if row and row[0] != email:
                        rows.append(row)
        rows.append([email, token, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["email", "token", "timestamp"])
            writer.writerows(rows)
    logger.debug(f"Password reset token stored for {email}")


def token_exists(email: str, token: str) -> bool:
    path = _db_path()
    if not os.path.exists(path):
        return False
    with _lock:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[0] == email and row[1] == token:
                    return True
    return False


def delete_token(email: str, token: str) -> None:
    path = _db_path()
    if not os.path.exists(path):
        return
    kept = []
    with _lock:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 2 and not (row[0] == email and row[1] == token):
                    kept.append(row)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["email", "token", "timestamp"])
            writer.writerows(kept)
