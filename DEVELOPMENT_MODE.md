# Running in Development Mode (Without Building)

This guide explains how to run the application in development mode without building the Angular frontend.

## Quick Start

### Terminal 1 - Backend Server

```bash
# Navigate to backend directory
cd merkaz_backend

# Activate virtual environment (if using one)
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Run Flask in development mode
python app.py
```

The backend will start on **http://localhost:8000**

### Terminal 2 - Frontend Development Server

```bash
# Navigate to frontend directory
cd merkaz-frontend

# Start Angular dev server (uses Vite)
ng serve
# OR
npm start
```

The frontend will start on **http://localhost:4200**

## How It Works

1. **Frontend (Port 4200)**: Angular dev server runs with hot-reload
2. **Backend (Port 8000)**: Flask server handles API requests
3. **Proxy**: Vite automatically proxies API calls from frontend to backend
   - Configured in `merkaz-frontend/vite.config.ts`
   - All `/login`, `/browse`, `/preview`, `/download`, etc. requests are proxied to `http://localhost:8000`

## Access the Application

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000

## Development Features

### Hot Reload
- **Frontend**: Changes to TypeScript/HTML/CSS files automatically reload
- **Backend**: Flask uses Waitress (no auto-reload). For auto-reload, see "Using Flask Dev Server" below

### Preview Feature
The preview feature works in development mode:
- Click "Preview" button on any file
- Preview modal opens with file content
- Supported: Images, Videos, PDFs, Text files

## Using Flask Dev Server (Optional)

For automatic backend reload on code changes, modify `merkaz_backend/app.py`:

**Replace this:**
```python
logger.info("Starting server with Waitress on 0.0.0.0:8000")
serve(app, host="0.0.0.0", port=8000)
```

**With this:**
```python
if __name__ == "__main__":
    logger.info("Starting Flask development server on 0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=True)
```

⚠️ **Warning**: Only use Flask dev server in development! Never in production.

## Troubleshooting

### Issue: Preview not working
- Check that `/preview` is in `vite.config.ts` proxy configuration
- Verify backend is running on port 8000
- Check browser console for errors

### Issue: CORS errors
- Make sure Vite proxy is configured correctly
- Check that `vite.config.ts` includes all API endpoints

### Issue: Changes not reflecting
- **Frontend**: Should auto-reload. If not, restart `ng serve`
- **Backend**: Restart Flask server (or use Flask dev server for auto-reload)

## Differences from Production Mode

| Development Mode | Production Mode |
|-----------------|-----------------|
| Frontend: `ng serve` (port 4200) | Frontend: Built and served by Flask |
| Backend: `python app.py` (port 8000) | Backend: `python app.py` (port 8000) |
| Two separate servers | Single Flask server |
| Hot reload enabled | No hot reload |
| No build required | Requires `ng build` first |

