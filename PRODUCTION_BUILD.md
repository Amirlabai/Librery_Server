# Production Build Guide - Single Port Flask Server

This guide explains how to build the Angular frontend and serve it from Flask on a single port.

## Quick Start

### Step 1: Build Angular Frontend

```bash
cd merkaz-frontend
ng build --configuration production
```

This creates the production build in `merkaz-frontend/dist/angular/browser/`

### Step 2: Run Flask Server

```bash
cd merkaz_backend
python app.py
```

The Flask server will:
- Serve the Angular app from `dist/angular/browser/`
- Handle API requests on the same port (8000)
- Automatically detect if the build exists

### Step 3: Access the Application

Open your browser: **http://localhost:8000**

- Frontend: Served from Flask
- API: Same port, routes like `/login`, `/register`, `/browse`, etc.

## How It Works

1. **API Routes** (registered first):
   - `/login`, `/register`, `/logout`, etc.
   - `/browse`, `/upload`, `/download`, etc.
   - `/admin/*` routes

2. **Static Files** (served after API routes):
   - `/assets/*` - Angular assets
   - `/*.js`, `/*.css` - JavaScript and CSS bundles
   - `/*` - Catch-all for Angular routes (serves `index.html`)

3. **Angular Routing**:
   - All non-API routes serve `index.html`
   - Angular Router handles client-side routing

## Configuration

### API URL Configuration

The frontend automatically detects when served from Flask:
- If port is 8000 → Uses relative URLs (same origin)
- If ngrok → Uses relative URLs (proxied)
- Otherwise → Uses `http://localhost:8000`

No manual configuration needed!

## Building for Production

### Production Build Command

```bash
cd merkaz-frontend
ng build --configuration production
```

### Build Output

The build is created at:
```
merkaz-frontend/dist/angular/browser/
├── index.html
├── main-*.js
├── polyfills-*.js
├── styles-*.css
├── assets/
└── ...
```

### Rebuilding After Changes

After making frontend changes:

```bash
cd merkaz-frontend
ng build --configuration production
# Flask will automatically serve the new build
```

## Troubleshooting

### Issue: Flask shows "Angular build not found"

**Solution:** Make sure you've built the Angular app:
```bash
cd merkaz-frontend
ng build --configuration production
```

### Issue: API routes return 404

**Solution:** Check that blueprints are registered before static routes. The current code handles this correctly.

### Issue: Angular routes don't work (shows 404)

**Solution:** The catch-all route should serve `index.html`. Check Flask logs to see if the route is being matched.

### Issue: Static files (JS/CSS) not loading

**Solution:** 
1. Verify build exists: `merkaz-frontend/dist/angular/browser/`
2. Check browser console for 404 errors
3. Verify file paths in `index.html` match the build structure

## Development vs Production

### Development Mode (Separate Ports)
- Frontend: `ng serve` → http://localhost:4200
- Backend: `python app.py` → http://localhost:8000
- API calls go to `http://localhost:8000`

### Production Mode (Single Port)
- Build: `ng build --configuration production`
- Flask: `python app.py` → http://localhost:8000
- Everything served from port 8000
- API calls use relative URLs (same origin)

## Deployment

For production deployment:

1. **Build the frontend:**
   ```bash
   cd merkaz-frontend
   ng build --configuration production
   ```

2. **Run Flask with production settings:**
   ```bash
   cd merkaz_backend
   python app.py
   ```

3. **Use a reverse proxy (recommended):**
   - Nginx or Apache in front of Flask
   - Configure SSL/HTTPS
   - Set up proper domain

## Notes

- The Flask app automatically detects the Angular build
- If build doesn't exist, Flask falls back to API-only mode
- CORS is configured to allow same-origin requests
- All routes are handled correctly (API first, then static files)
