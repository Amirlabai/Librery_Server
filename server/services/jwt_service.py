"""
JWT issuance and validation for API authentication.
"""
from datetime import datetime, timedelta, timezone

import jwt
from flask import request

import config.config as config
from services import session_state_store
from utils.logger_config import get_logger

logger = get_logger(__name__)


def _secret() -> str:
    return getattr(config, "JWT_SECRET_KEY", None) or config.TOKEN_SECRET_KEY


def _expires_minutes() -> int:
    return int(getattr(config, "JWT_ACCESS_EXPIRES_MINUTES", config.SESSION_TIMEOUT_MINUTES))


def issue_token(user) -> str:
    ver = session_state_store.get_token_version(user.email)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.email,
        "uid": user.user_id,
        "role": "admin" if user.is_admin else "user",
        "ver": ver,
        "iat": now,
        "exp": now + timedelta(minutes=_expires_minutes()),
    }
    encoded = jwt.encode(payload, _secret(), algorithm="HS256")
    return encoded if isinstance(encoded, str) else encoded.decode('utf-8')


def decode_token(token: str):
    try:
        return jwt.decode(token, _secret(), algorithms=["HS256"])
    except jwt.PyJWTError as e:
        logger.debug(f"JWT decode failed: {e}")
        return None


def get_bearer_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def validate_token(token: str):
    claims = decode_token(token)
    if not claims:
        return None
    email = claims.get("sub")
    if not email:
        return None
    if session_state_store.is_invalidated(email):
        return None
    expected_ver = session_state_store.get_token_version(email)
    if int(claims.get("ver", -1)) != expected_ver:
        return None
    return claims
