# Complete Setup Guide for New Computer

This guide will walk you through setting up the Merkaz Server project on a completely new computer from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Optional: Ngrok Setup](#optional-ngrok-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.7+** (Python 3.9+ recommended)
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify installation:
     ```bash
     python --version
     pip --version
     ```

2. **Node.js 14+ and npm**
   - Download from: https://nodejs.org/
   - Verify installation:
     ```bash
     node -v
     npm -v
     ```

3. **Git** (if cloning from repository)
   - Download from: https://git-scm.com/downloads
   - Verify installation:
     ```bash
     git --version
     ```

### Optional Software

- **ngrok** (for exposing local server to internet)
  - See [Ngrok Setup](#optional-ngrok-setup) section

---

## Backend Setup

### Step 1: Get the Project

**Option A: Clone from Git Repository**
```bash
git clone <repository-url>
cd NagoAmir_Server
```

**Option B: Copy Project Folder**
- Copy the entire `NagoAmir_Server` folder to your new computer

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
# Navigate to project directory
cd NagoAmir_Server

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
# Navigate to project directory
cd NagoAmir_Server

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

**Verify activation:** Your terminal prompt should show `(.venv)` at the beginning.

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**If you encounter encoding issues**, install dependencies manually:
```bash
pip install flask==3.1.2
pip install waitress==3.0.2
pip install flask-cors==6.0.1
pip install Flask-Mail==0.10.0
pip install werkzeug==3.1.3
pip install itsdangerous==2.2.0
pip install python-magic-bin  # Windows
# OR
pip install python-magic  # Linux/Mac
pip install openpyxl==3.1.5
```

### Step 4: Configure Backend

1. **Copy configuration template** (if `config.py` doesn't exist):
   ```bash
   cp merkaz_backend/config/config_template.py merkaz_backend/config/config.py
   ```

2. **Edit `merkaz_backend/config/config.py`**:
   - Set secret keys (or leave as-is for auto-generation)
   - Configure email settings if you need email functionality:
     ```python
     MAIL_USERNAME = 'your-email@gmail.com'
     MAIL_PASSWORD = 'your-app-password'  # Gmail App Password, not regular password
     MAIL_DEFAULT_SENDER = 'your-email@gmail.com'
     ```
   - Adjust file paths if needed (defaults should work)

**Note:** The application will automatically create necessary directories and CSV files on first run.

### Step 5: Test Backend

```bash
cd merkaz_backend
python app.py
```

You should see:
- Directory creation messages
- CSV file initialization
- "Starting server with Waitress on 0.0.0.0:8000"

Open browser: `http://localhost:8000/` - You should see a JSON response with API information.

Press `Ctrl+C` to stop the server.

---

## Frontend Setup

### Step 1: Install Angular CLI

```bash
npm install -g @angular/cli
```

Verify installation:
```bash
ng version
```

### Step 2: Navigate to Frontend Directory

```bash
cd merkaz-frontend
```

### Step 3: Install Frontend Dependencies

```bash
npm install
```

This may take a few minutes. Wait for it to complete.

### Step 4: Test Frontend

```bash
ng serve
```

You should see:
- Compilation messages
- "Application bundle generation complete"
- "Local: http://localhost:4200/"

Open browser: `http://localhost:4200/` - You should see the login page.

Press `Ctrl+C` to stop the dev server.

---

## Configuration

### Backend Configuration

**File:** `merkaz_backend/config/config.py`

Key settings:
- `SUPER_SECRET_KEY`: Session encryption key (auto-generated if not set)
- `TOKEN_SECRET_KEY`: Token encryption key (auto-generated if not set)
- `MAIL_*`: Email server settings (for password reset, notifications)
- `ALLOWED_EXTENSIONS`: File types allowed for upload
- `MAX_CONTENT_LENGTH`: Maximum file upload size

### Frontend Configuration

**API URL Configuration:**
- Default: `http://localhost:8000` (for local development)
- The frontend uses `ApiConfigService` to manage backend URL
- For ngrok: Set via browser console (see Ngrok Setup section)

**File:** `merkaz-frontend/src/app/services/api-config.service.ts`
- Automatically detects localhost vs ngrok
- Can be manually configured via localStorage

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
# Activate virtual environment (if not already active)
.venv\Scripts\Activate.ps1  # Windows
# OR
source .venv/bin/activate  # Linux/Mac

# Start backend
cd merkaz_backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd merkaz-frontend
ng serve
```

**Access the application:**
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000

### Creating First Admin User

**Method 1: Via Registration (Recommended)**
1. Start both backend and frontend
2. Go to http://localhost:4200
3. Click "Register" and create an account
4. The account will be in `merkaz_server/data/new_users.csv`
5. Manually edit `merkaz_server/data/auth_users.csv`:
   - Copy the user row from `new_users.csv`
   - Change `role` from `user` to `admin`
   - Change `status` to `active`
   - Remove from `new_users.csv`

**Method 2: Direct CSV Edit**
1. Edit `merkaz_server/data/auth_users.csv`
2. Add a row:
   ```csv
   id,email,password,role,status
   1,admin@example.com,pbkdf2:sha256:260000$...,admin,active
   ```
3. Generate password hash:
   ```python
   from werkzeug.security import generate_password_hash
   print(generate_password_hash("your-password"))
   ```

---

## Optional: Ngrok Setup

### Installation

**Windows - Using winget:**
```powershell
winget install ngrok.ngrok
```

**Windows - Using Chocolatey:**
```powershell
choco install ngrok
```

**Windows - Manual:**
1. Visit: https://dashboard.ngrok.com/get-started/setup
2. Download ngrok for Windows
3. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok`)
4. Add folder to PATH:
   - Win+X → System → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - Add folder path (e.g., `C:\ngrok`)
   - OK on all dialogs
5. Restart terminal

**Linux/Mac:**
```bash
# Download and install from ngrok.com
# Or use package manager
```

**Verify installation:**
```bash
ngrok version
```

### Configure Ngrok

1. **Get your authtoken** from: https://dashboard.ngrok.com/get-started/your-authtoken

2. **Update `merkaz_backend/ngrok.yml`**:
   ```yaml
   version: 3
   agent:
     authtoken: YOUR_AUTHTOKEN_HERE
   tunnels:
     backend:
       proto: http
       addr: 8000
       host_header: rewrite
     frontend:
       proto: http
       addr: 4200
       host_header: rewrite
   ```

### Running with Ngrok

1. **Start backend and frontend** (in separate terminals)

2. **Start ngrok:**
   ```bash
   python merkaz_backend/run_ngrok.py 8000 4200
   ```

3. **Check ngrok console** or web interface (http://127.0.0.1:4040) for URLs:
   - You'll see two URLs: one for backend, one for frontend

4. **Configure frontend to use backend ngrok URL:**
   - Open browser console (F12) on the frontend ngrok URL
   - Run:
     ```javascript
     localStorage.setItem('api_backend_url', 'https://YOUR-BACKEND-NGROK-URL.ngrok-free.app')
     ```
   - Refresh the page

---

## Troubleshooting

### Backend Issues

**Issue: ModuleNotFoundError**
- **Solution:** Ensure virtual environment is activated and dependencies are installed
  ```bash
  .venv\Scripts\Activate.ps1  # Windows
  pip install -r requirements.txt
  ```

**Issue: Port 8000 already in use**
- **Solution:** Change port in `merkaz_backend/app.py`:
  ```python
  serve(app, host="0.0.0.0", port=8001)  # Change to 8001
  ```
- Or kill the process using port 8000:
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -ti:8000 | xargs kill
  ```

**Issue: Permission denied (Windows)**
- **Solution:** Run PowerShell as Administrator or:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

**Issue: python-magic installation fails**
- **Windows:** Use `python-magic-bin` instead
- **Linux:** Install system library first:
  ```bash
  sudo apt-get install libmagic1  # Ubuntu/Debian
  ```

### Frontend Issues

**Issue: ng serve fails**
- **Solution:** Clear cache and reinstall:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  ```

**Issue: Port 4200 already in use**
- **Solution:** Use different port:
  ```bash
  ng serve --port 4201
  ```

**Issue: API calls fail**
- **Solution:** 
  - Verify backend is running on port 8000
  - Check browser console for CORS errors
  - Verify `api_backend_url` in localStorage if using ngrok

### Ngrok Issues

**Issue: Both tunnels show same URL**
- **Solution:** 
  - Check ngrok web interface: http://127.0.0.1:4040
  - Verify `ngrok.yml` has both tunnels configured
  - Restart ngrok

**Issue: 403 Forbidden error**
- **Solution:**
  - Backend CORS is configured for ngrok domains
  - Frontend vite.config.ts allows ngrok hosts
  - Verify you're accessing the frontend URL, not backend URL

**Issue: ngrok not found**
- **Solution:** 
  - Verify ngrok is in PATH: `ngrok version`
  - Reinstall or add to PATH manually

### General Issues

**Issue: CSV files corrupted**
- **Solution:** Delete corrupted files, restart server (they'll be recreated)

**Issue: Email not sending**
- **Solution:**
  - Verify Gmail App Password (not regular password)
  - Check SMTP settings in `config.py`
  - Verify `MAIL_USE_TLS` and `MAIL_USE_SSL` settings

---

## Quick Reference

### Directory Structure After Setup

```
NagoAmir_Server/
├── .venv/                    # Python virtual environment
├── merkaz_backend/           # Backend code
│   ├── config/
│   │   └── config.py        # Configuration (edit this)
│   ├── controllers/          # API endpoints
│   ├── services/             # Business logic
│   ├── repositories/         # Data access
│   ├── models/               # Data models
│   ├── utils/                # Utilities
│   ├── app.py               # Main entry point
│   └── ngrok.yml            # Ngrok config
├── merkaz-frontend/          # Frontend code
│   ├── src/
│   │   └── app/
│   │       └── services/    # API services
│   └── package.json
├── merkaz_server/            # Generated on first run
│   ├── data/                # User databases (CSV)
│   ├── logs/                # Activity logs (CSV)
│   └── server_files/        # Uploaded files
│       ├── files_to_share/
│       ├── uploads/
│       └── trash/
└── requirements.txt         # Python dependencies
```

### Common Commands

```bash
# Backend
cd merkaz_backend
python app.py

# Frontend
cd merkaz-frontend
ng serve

# Ngrok
python merkaz_backend/run_ngrok.py 8000 4200

# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac
```

---

## Next Steps

1. ✅ Backend and frontend are running
2. ✅ Create your first admin user
3. ✅ Test login and registration
4. ✅ Configure email (optional)
5. ✅ Set up ngrok (optional, for external access)

For more information:
- See `README.md` for project overview
- See `documentation/` folder for detailed documentation
- Check `documentation/api-reference.md` for API endpoints

---

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages in terminal/console
3. Check logs in `merkaz_server/logs/`
4. Verify all prerequisites are installed correctly

