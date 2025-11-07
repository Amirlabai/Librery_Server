# Configuration Guide

## Configuration File

The main configuration file is located at: `merkaz_backend/config/config.py`

## Configuration Options

### Core App Settings

```python
SUPER_SECRET_KEY = "your-secret-key-here"
TOKEN_SECRET_KEY = "your-token-secret-key-here"
```

**Description**: Secret keys for session management and password reset tokens.

**⚠️ Important**: Change these in production! Use strong, random keys.

**Generation**:
```python
import secrets
print(secrets.token_hex(32))
```

---

### Directory Paths

The configuration automatically sets up directory paths based on the project root:

```python
SERVER_ROOT_DIR = "merkaz_server"
SERVER_DATA_DIR = "merkaz_server/data"
SERVER_LOGS_DIR = "merkaz_server/logs"
SERVER_FILES_DIR = "merkaz_server/server_files"

SHARE_FOLDER = "merkaz_server/server_files/files_to_share"
TRASH_FOLDER = "merkaz_server/server_files/trash"
UPLOAD_FOLDER = "merkaz_server/server_files/uploads"
```

**Note**: These are relative to the project root directory.

---

### User Database Files

```python
AUTH_USER_DATABASE = "merkaz_server/data/auth_users.csv"
NEW_USER_DATABASE = "merkaz_server/data/new_users.csv"
DENIED_USER_DATABASE = "merkaz_server/data/denied_users.csv"
PASSWORD_RESET_DATABASE = "merkaz_server/data/password_reset.csv"
```

**CSV Format** (auth_users, new_users, denied_users):
```
id,email,password,role,status
1,user@example.com,hashed_password,user,active
```

---

### ID Sequence Files

```python
ID_SEQUENCE_FILE = "merkaz_server/data/user_id_sequence.txt"
UPLOAD_ID_SEQUENCE_FILE = "merkaz_server/logs/upload_id_sequence.txt"
```

**Purpose**: Track the next ID to assign for users and uploads.

---

### Log Files

```python
SESSION_LOG_FILE = "merkaz_server/logs/session_log.csv"
DOWNLOAD_LOG_FILE = "merkaz_server/logs/download_log.csv"
SUGGESTION_LOG_FILE = "merkaz_server/logs/suggestion_log.csv"
UPLOAD_PENDING_LOG_FILE = "merkaz_server/logs/upload_pending_log.csv"
UPLOAD_COMPLETED_LOG_FILE = "merkaz_server/logs/upload_completed_log.csv"
DECLINED_UPLOAD_LOG_FILE = "merkaz_server/logs/declined_log.csv"
```

**CSV Formats**:

**Session Log**:
```
timestamp,email,event
2024-01-15 10:30:00,user@example.com,LOGIN_SUCCESS
```

**Download Log**:
```
timestamp,email,type,path
2024-01-15 10:30:00,user@example.com,FILE,document.pdf
```

**Suggestion Log**:
```
timestamp,email,suggestion
2024-01-15 10:30:00,user@example.com,Please add dark mode
```

**Upload Pending Log**:
```
upload_id,timestamp,email,user_id,filename,path
1,2024-01-15 10:30:00,user@example.com,5,document.pdf,folder/document.pdf
```

**Upload Completed Log**:
```
upload_id,original_timestamp,approval_timestamp,email,user_id,filename,final_path
1,2024-01-15 10:30:00,2024-01-15 11:00:00,user@example.com,5,document.pdf,folder/document.pdf
```

---

### File Upload Settings

#### Allowed File Extensions

```python
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
    'zip', 'rar', '7z', 'doc', 'docx', 
    'xls', 'xlsx', 'ppt', 'pptx'
}
```

**To add more extensions**:
```python
ALLOWED_EXTENSIONS.add('mp4')
```

#### Video Extensions

```python
VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
```

#### File Size Limits

```python
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
MAX_VIDEO_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024  # 1 GB
```

**Note**: These limits are set but not currently enforced in the upload handler. Consider adding validation.

---

### Mail Server Configuration

```python
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "your-app-password"
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = "your-email@gmail.com"
```

#### Gmail Setup

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account → Security → App passwords
   - Generate a password for "Mail"
   - Use this password in `MAIL_PASSWORD`

#### Other SMTP Servers

**Outlook/Hotmail**:
```python
MAIL_SERVER = "smtp-mail.outlook.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
```

**Custom SMTP**:
```python
MAIL_SERVER = "smtp.yourdomain.com"
MAIL_PORT = 587  # or 465 for SSL
MAIL_USE_TLS = True  # Use True for port 587
MAIL_USE_SSL = False  # Use True for port 465
```

---

## Environment Variables (Recommended)

For production, use environment variables instead of hardcoding values:

```python
import os

SUPER_SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
TOKEN_SECRET_KEY = os.environ.get('TOKEN_SECRET_KEY', 'default-token-key')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
```

**Setting environment variables**:

**Windows (PowerShell)**:
```powershell
$env:SECRET_KEY="your-secret-key"
```

**Linux/Mac**:
```bash
export SECRET_KEY="your-secret-key"
```

---

## Session Configuration

Configured in `app.py`:

```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
```

**To change session timeout**:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 1 hour
```

---

## CORS Configuration

Configured in `app.py`:

```python
CORS(
    app,
    resources={r"/*": {
        "origins": ["http://localhost:4200"],
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    }},
    supports_credentials=True
)
```

**For production**, update origins:
```python
"origins": ["https://yourdomain.com"]
```

**For multiple origins**:
```python
"origins": ["https://yourdomain.com", "https://www.yourdomain.com"]
```

---

## Server Configuration

The server runs on Waitress WSGI server:

```python
serve(app, host="0.0.0.0", port=8000)
```

**To change port**:
```python
serve(app, host="0.0.0.0", port=5000)
```

**For development**, you can use Flask's built-in server:
```python
app.run(host="0.0.0.0", port=8000, debug=True)
```

---

## Initialization

On startup, `app.py` automatically:
1. Creates necessary directories (share, trash, uploads)
2. Creates CSV files with headers if they don't exist
3. Initializes the Flask app
4. Starts the server

---

## Configuration Template

A template file is available at `merkaz_backend/config_template.py` for reference.

---

## Production Checklist

- [ ] Change `SUPER_SECRET_KEY` and `TOKEN_SECRET_KEY`
- [ ] Use environment variables for sensitive data
- [ ] Configure proper SMTP settings
- [ ] Update CORS origins
- [ ] Set appropriate file size limits
- [ ] Review allowed file extensions
- [ ] Configure HTTPS
- [ ] Set up proper logging
- [ ] Review session timeout
- [ ] Backup configuration file

