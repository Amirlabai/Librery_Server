# Merkaz Server — context

## Purpose

Flask backend (`server`) + React frontend (`client`) for shared file library and admin approval.
Dev server: Vite on `http://localhost:5173` (API proxied to Flask).

## Auth (post-audit)

- Flask session cookies (`withCredentials`) for cooldown and legacy flows
- JWT in `Authorization: Bearer` from login/refresh; validated with `PyJWT` and `token_version` in `data/session_state.json`
- Session invalidation bumps `token_version` per email (multi-worker safe)
- Emails are normalized to lowercase on store and lookup (`User._normalize_email`); login is case-insensitive

## Key config (`server/config/config.py`)

- `ROOT_SEARCH_CACHE_DIR` — directory of letter CSV search shards (not a single JSON file)
- `SESSION_STATE_FILE`, `JWT_SECRET_KEY`, `DEBUG`, `SESSION_COOKIE_SECURE`, `PUBLIC_BASE_URL`

## Conventions

- Log paths: prefer `UploadRepository.get_*_log_path()` or `utils.path_utils.resolve_config_path`
- User CSV writes: `UserRepository` with `_auth_db_lock`
- Append logs: `utils.log_utils.log_event` (module lock)

## Client UI

- Operate mode; tokens in root `DESIGN.md`
- Mobile ≤768px: full-bleed panels, table→card rows (`data-label`), no page X-scroll; desktop ≥769px unchanged
- CSS: `client/src/styles.css`, `pages/dashboard.css`, `pages/auth.css`, `pages/admin/admin.css`

## Design (Impeccable / taste)

- Product truth: root `PRODUCT.md`
- Visual system of record: root `DESIGN.md` + `.impeccable/design.json`
- North star: **The Mustard Brush Desk** (Operate mode, brand mustard `#e6b422`, ink CTAs, Assistant)
- Token source in code: `client/src/styles.css` CSS variables
- Do not invent a second palette; refine through DESIGN.md
