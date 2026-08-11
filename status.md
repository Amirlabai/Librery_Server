# Status

## Completed (rename)

- [x] Renamed `merkaz_backend/` → `server/` (git mv + reference updates)
- [x] Autogen docs under `documentation/autogen/server/`
- [x] Ponytail audit of `server/` (report-only; see chat / plan)

## Completed (security audit remediation)

- [x] Path traversal fixes (`is_path_under`) in file service
- [x] Search cache dir split (`ROOT_SEARCH_CACHE_DIR`); removed bad startup JSON write
- [x] Removed easter-egg controller subsystem
- [x] JWT auth + file-backed session state (`session_state.json`)
- [x] Password reset one-time tokens in CSV
- [x] Upload log ordering/rollback, upload ID scan, log locks
- [x] Frontend auth/routing/upload/guards fixes
- [x] Branch `audit/integration` for review merge to `main`

## Completed (ponytail findings fixes)

- [x] Deleted path-only log repositories (`DownloadRepository`, `SessionRepository`, `SuggestionRepository`)
- [x] Inlined log-path resolution in controllers/services
- [x] Removed unused `Upload` and `LogEntry` model classes + trimmed model exports
- [x] Simplified `services` and `repositories` package exports (explicit imports only)
- [x] Regenerated `documentation/autogen/server/` after module deletions

## Next steps

- [ ] Run full manual smoke test (login, browse, upload progress, admin, puzzles) — use `cd server` then `python app.py`
- [ ] Open PR: `audit/integration` → `main`
- [ ] `pip install -r server/requirements.txt` on server (adds PyJWT)
