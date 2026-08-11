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

## Completed (React cleanup)

- [x] Deleted legacy Angular tree (`client/src/app/`, `angular.json`, `main.ts`, Compodoc script)
- [x] Kept global + page CSS (`styles.css`, `pages/dashboard.css`, `pages/auth.css`, `pages/admin/admin.css`)
- [x] React-only deps in `client/package.json` (3 runtime packages)

During the Angular → React port, follow this deletion checklist (ponytail rules):

- Delete UI framework stack that was Angular-specific: `@angular/material`, `@angular/cdk`, and `custom.scss` theming; replace with existing CSS variables in `client/src/styles.css` (and per-page CSS).
- Delete Angular runtime plumbing: `rxjs` service layers and `zone.js` assumptions; replace with React `useState` / `useEffect` and Context.
- Delete Angular build/doc tooling as React replaces it: Compodoc output generation (`scripts/generate_frontend_docs.py` + `documentation/autogen/**`) when we remove the Angular app.
- Delete Angular “.component.ts + .html + .css triplets” by porting each page into one or two React files: `pages/*.tsx` plus optional co-located CSS.
- Keep the business logic that actually matters: upload sequencing/retry and progress aggregation; port it into `client/src/api.ts` (or a small `upload.ts` module) with behavior parity.
- Keep the hidden challenge UI as a lightweight React layer: keyboard activation + leaderboard shell; server remains the authority for activation and scoring.

## Verification (best effort in this environment)

- React build succeeds: `cd client && npm run build`.
- Flask end-to-end smoke test could not be executed here because Python dependencies are not installed (`ModuleNotFoundError: No module named 'flask'`). After running `pip install -r server/requirements.txt`, the next check is:
  - `python server/app.py` and confirm `/` serves `client/dist/index.html`.
