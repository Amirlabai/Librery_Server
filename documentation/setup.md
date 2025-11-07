# Setup & Installation Guide

Complete guide for setting up the Merkaz_lib backend.

## Prerequisites

- **Python 3.7+** (Python 3.9+ recommended)
- **pip** (Python package manager)
- **Virtual environment** (recommended)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd NagoAmir_Server
```

### 2. Create Virtual Environment

**Windows (PowerShell)**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If you encounter an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

**Linux/Mac**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**If you encounter encoding issues**, install dependencies manually from `venv_prerequsites.txt`:

```bash
pip install flask
pip install waitress
pip install flask-cors
pip install flask-mail
pip install werkzeug
pip install itsdangerous
pip install python-magic-bin  # Windows
# or
pip install python-magic  # Linux/Mac
pip install openpyxl
```

### 4. Configure the Application

Edit `merkaz_backend/config/config.py`:

1. **Set Secret Keys**:
   ```python
   SUPER_SECRET_KEY = "your-secret-key-here"
   TOKEN_SECRET_KEY = "your-token-secret-key-here"
   ```

2. **Configure Mail Settings** (if using email):
   ```python
   MAIL_USERNAME = "your-email@gmail.com"
   MAIL_PASSWORD = "your-app-password"
   MAIL_DEFAULT_SENDER = "your-email@gmail.com"
   ```

See [Configuration Guide](./configuration.md) for detailed configuration options.

### 5. Run the Server

```bash
cd merkaz_backend
python app.py
```

The server will start on `http://localhost:8000`

**Expected Output**:
```
Created file: merkaz_server/data/auth_users.csv
Created file: merkaz_server/data/new_users.csv
...
Starting server with Waitress...
```

## Verification

### Test the Server

Open your browser or use curl:

```bash
curl http://localhost:8000/browse
```

You should get a JSON response (likely an authentication error, which confirms the server is running).

## Development Setup

### Running in Debug Mode

For development, you can modify `app.py` to use Flask's debug server:

```python
# Replace the serve() call with:
if __name__ == "__main__":
    # ... initialization code ...
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
```

**⚠️ Warning**: Never use debug mode in production!

### Hot Reload

With Flask's debug server, code changes will automatically reload the server.

## Directory Structure

After first run, the following directories will be created:

```
merkaz_server/
├── data/
│   ├── auth_users.csv
│   ├── new_users.csv
│   ├── denied_users.csv
│   ├── password_reset.csv
│   └── user_id_sequence.txt
├── logs/
│   ├── session_log.csv
│   ├── download_log.csv
│   ├── suggestion_log.csv
│   ├── upload_pending_log.csv
│   ├── upload_completed_log.csv
│   ├── declined_log.csv
│   └── upload_id_sequence.txt
└── server_files/
    ├── files_to_share/
    ├── trash/
    └── uploads/
```

## Creating the First Admin User

### Method 1: Manual CSV Entry

1. Edit `merkaz_server/data/auth_users.csv`
2. Add a row with your admin user:
   ```csv
   id,email,password,role,status
   1,admin@example.com,pbkdf2:sha256:...your-hashed-password...,admin,active
   ```

**Generate password hash**:
```python
from werkzeug.security import generate_password_hash
print(generate_password_hash("your-password"))
```

### Method 2: Registration + Manual Approval

1. Register via `/register` endpoint
2. Manually move the user from `new_users.csv` to `auth_users.csv`
3. Change `role` to `admin` and `status` to `active`

### Method 3: Python Script

Create a script `create_admin.py`:

```python
from werkzeug.security import generate_password_hash
from models.user_entity import User
from utils.csv_utils import get_next_user_id

email = "admin@example.com"
password = "admin123"
hashed_password = generate_password_hash(password)
user_id = get_next_user_id()

admin_user = User(
    email=email,
    password=hashed_password,
    role='admin',
    status='active',
    user_id=user_id
)

users = User.get_all()
users.append(admin_user)
User.save_all(users)

print(f"Admin user created: {email}")
```

Run:
```bash
python create_admin.py
```

## Common Issues

### Issue: ModuleNotFoundError

**Solution**: Ensure you're in the virtual environment and dependencies are installed.

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Issue: Permission Denied (Windows)

**Solution**: Run PowerShell as Administrator or adjust execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: python-magic Installation Error

**Windows**: Install `python-magic-bin` instead:
```bash
pip install python-magic-bin
```

**Linux**: Install system library first:
```bash
sudo apt-get install libmagic1  # Ubuntu/Debian
# or
sudo yum install file-devel  # CentOS/RHEL
```

### Issue: Port Already in Use

**Solution**: Change the port in `app.py`:
```python
serve(app, host="0.0.0.0", port=8001)
```

Or kill the process using port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

### Issue: Email Not Sending

**Solution**: 
1. Check SMTP credentials in `config.py`
2. For Gmail, ensure you're using an App Password (not your regular password)
3. Check firewall/network settings
4. Verify `MAIL_USE_TLS` and `MAIL_USE_SSL` settings match your SMTP server

## Production Deployment

### Using Waitress (Current)

Waitress is already configured and suitable for production.

### Using Gunicorn (Alternative)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using uWSGI

```bash
pip install uwsgi
uwsgi --http :8000 --module app:app --processes 4
```

### Behind a Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Variables

Set environment variables for sensitive data:

```bash
export SECRET_KEY="your-production-secret-key"
export TOKEN_SECRET_KEY="your-production-token-key"
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"
```

## Next Steps

1. **Configure the application**: See [Configuration Guide](./configuration.md)
2. **Review API endpoints**: See [API Reference](./api-reference.md)
3. **Understand architecture**: See [Architecture Overview](./architecture.md)
4. **Set up frontend**: Connect Angular frontend to backend

## Troubleshooting

### Check Logs

Check the console output for errors. Logs are also written to CSV files in `merkaz_server/logs/`.

### Test Endpoints

Use curl or Postman to test endpoints:

```bash
# Test login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c cookies.txt

# Test browse (with session cookie)
curl http://localhost:8000/browse -b cookies.txt
```

### Database Issues

If CSV files are corrupted:
1. Backup existing files
2. Delete corrupted files
3. Restart server (files will be recreated with headers)

## Support

For issues or questions:
- Check the [API Reference](./api-reference.md)
- Review [Architecture Overview](./architecture.md)
- Check configuration in [Configuration Guide](./configuration.md)

