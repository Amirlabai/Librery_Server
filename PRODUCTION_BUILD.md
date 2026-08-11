# Production / run guide

Flask is **API only** (no `client/dist` hosting). UI is Vite (dev) or Vercel (prod).

## Backend

```bash
cd server
python app.py
```

API: **http://localhost:8000** (`GET /` returns JSON status).

## Frontend (local)

```bash
cd client
npm install
npm run dev
```

Open **http://localhost:5173** (Vite proxies API to Flask, or set `VITE_API_BASE_URL`).

## Vercel UI + ngrok API

1. Flask on the PC; expose with your **stable** ngrok HTTPS URL.
2. In `server/config/config.py`: set `PUBLIC_BASE_URL` to that ngrok URL; set `SESSION_COOKIE_SECURE = True` for HTTPS (use `False` only for plain `http://localhost`).
3. Deploy `client/` on Vercel (Root Directory = `client`). Set env:
   - `VITE_API_BASE_URL=https://your-stable-subdomain.ngrok-free.dev`
4. See [`client/.env.example`](client/.env.example). SPA rewrites are in [`client/vercel.json`](client/vercel.json).

Ngrok bandwidth still applies to downloads/uploads. UI stays up on Vercel when the PC is offline; API will not.
