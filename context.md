# Merkaz Server — context

## Purpose

Flask backend (`server`) + React frontend (`client`) for shared file library and admin approval.
Dev server: Vite on `http://localhost:5173` (API proxied to Flask).

## Auth (post-audit)

- Flask session cookies (`withCredentials`) for cooldown and legacy flows
- JWT in `Authorization: Bearer` from login/refresh; validated with `PyJWT` and `token_version` in `data/session_state.json`
- Session invalidation bumps `token_version` per email (multi-worker safe)

## Key config (`server/config/config.py`)

- `ROOT_SEARCH_CACHE_DIR` — directory of letter CSV search shards (not a single JSON file)
- `SESSION_STATE_FILE`, `JWT_SECRET_KEY`, `DEBUG`, `SESSION_COOKIE_SECURE`, `PUBLIC_BASE_URL`

## Conventions

- Log paths: prefer `UploadRepository.get_*_log_path()` or `utils.path_utils.resolve_config_path`
- User CSV writes: `UserRepository` with `_auth_db_lock`
- Append logs: `utils.log_utils.log_event` (module lock)
