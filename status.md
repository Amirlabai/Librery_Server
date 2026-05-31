# Status

## Completed (security audit remediation)

- [x] Path traversal fixes (`is_path_under`) in file service
- [x] Search cache dir split (`ROOT_SEARCH_CACHE_DIR`); removed bad startup JSON write
- [x] Easter egg controller hardening (auth, puzzle whitelist, answer normalization, locked challenge CSV)
- [x] JWT auth + file-backed session state (`session_state.json`)
- [x] Password reset one-time tokens in CSV
- [x] Upload log ordering/rollback, upload ID scan, log locks
- [x] Frontend auth/routing/upload/guards fixes
- [x] Branch `audit/integration` for review merge to `main`

## Next steps

- [ ] Run full manual smoke test (login, browse, upload progress, admin, puzzles)
- [ ] Open PR: `audit/integration` → `main`
- [ ] `pip install -r merkaz_backend/requirements.txt` on server (adds PyJWT)
