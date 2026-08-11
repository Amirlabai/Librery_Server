# Development Mode

Run backend and frontend separately with hot reload.

## Terminal 1 - Backend

```bash
cd server
python app.py
```

Backend: **http://localhost:8000**

## Terminal 2 - Frontend

```bash
cd client
npm install
npm run dev
```

Frontend: **http://localhost:5173**

## How It Works

1. Vite dev server on port 5173 with hot reload
2. Flask on port 8000 handles API requests
3. `client/vite.config.ts` proxies API paths to Flask

## Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Differences from Production

| Development | Production |
|-------------|------------|
| `npm run dev` (:5173) | Built into `client/dist/`, served by Flask |
| Two servers | Single Flask server on :8000 |
| Hot reload | Rebuild required |
