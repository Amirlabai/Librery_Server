# Production Build Guide - Single Port Flask Server

Build the React frontend and serve it from Flask on a single port.

## Quick Start

### Step 1: Build frontend

```bash
cd client
npm install
npm run build
```

Output: `client/dist/`

### Step 2: Run Flask Server

```bash
cd server
python app.py
```

Flask serves the React app from `client/dist/` and API routes on port 8000.

### Step 3: Access the Application

Open your browser: **http://localhost:8000**

## How It Works

1. **API Routes** (registered first): `/login`, `/browse`, `/admin/*`, etc.
2. **Static files**: `/assets/*`, JS/CSS bundles from `dist/assets/`
3. **SPA fallback**: other paths serve `dist/index.html`

## Development vs Production

| Development | Production |
|-------------|------------|
| `npm run dev` on :5173 | `npm run build` |
| Flask on :8000 | Flask on :8000 serves `dist/` |
| Vite proxies API | Same-origin relative URLs |

## Troubleshooting

**Flask shows "Client build not found"**

```bash
cd client && npm run build
```

**Static files 404**

Verify `client/dist/index.html` and `client/dist/assets/` exist after build.
