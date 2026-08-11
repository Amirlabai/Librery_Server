# client (React + Vite)

Merkaz web UI. Dev server proxies API calls to Flask on port 8000.

## Commands

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # output: dist/
npm run preview  # serve dist locally
```

## Layout

```
src/
  App.tsx           shell + routing
  api.ts            HTTP + uploads
  auth.tsx          auth context + route guards
  pages/            route components
  styles.css        global theme variables
```

Production: Flask serves `client/dist/` from the same port as the API.
