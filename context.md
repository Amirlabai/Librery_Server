# Merkaz Server — context

## Purpose

Flask backend (`merkaz_backend`) + Angular frontend (`merkaz-frontend`) for shared file library, admin approval, and optional easter-egg puzzle challenge.

## Auth (post-audit)

- Flask session cookies (`withCredentials`) for cooldown and legacy flows
- JWT in `Authorization: Bearer` from login/refresh; validated with `PyJWT` and `token_version` in `data/session_state.json`
- Session invalidation bumps `token_version` per email (multi-worker safe)

## Key config (`merkaz_backend/config/config.py`)

- `ROOT_SEARCH_CACHE_DIR` — directory of letter CSV search shards (not a single JSON file)
- `CHALLENGE_ACTIVATION_CODE`, `SESSION_STATE_FILE`, `JWT_SECRET_KEY`, `DEBUG`, `SESSION_COOKIE_SECURE`, `PUBLIC_BASE_URL`

## Conventions

- Log paths: prefer `UploadRepository.get_*_log_path()` or `utils.path_utils.resolve_config_path`
- User CSV writes: `UserRepository` with `_auth_db_lock`
- Append logs: `utils.log_utils.log_event` (module lock)
