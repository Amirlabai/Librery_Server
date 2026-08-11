# Production / local single-host guide

Flask serves **API + React** from `client/dist` on port 8000 (same origin, no CORS for the UI).

## Build UI (relative API URLs)

Do **not** set `VITE_API_BASE_URL` for this mode (leave unset / empty).

```bash
cd client
npm install
npm run build
```

## Run

```bash
cd server
python app.py
```

Open **http://localhost:8000**

Optional remote access: one ngrok tunnel to `8000` (`server/ngrok.yml`). Set `PUBLIC_BASE_URL` to that HTTPS URL for email links. For plain `http://localhost`, set `SESSION_COOKIE_SECURE = False` in `config.py`.

## Dev (hot reload)

```bash
# terminal 1
cd server && python app.py

# terminal 2
cd client && npm run dev
```

Vite on **http://localhost:5173** proxies API to Flask.
