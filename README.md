# Merkaz_lib

An open library for file-sharing among students. A full-stack web application built with Flask (Python) backend and Angular frontend.

## Authors

- **Amir Labai** - Backend Developer
- **Yosef Nago** - Frontend Developer

## Features

- **User Authentication & Authorization**
  - User registration with admin approval system
  - Login/logout functionality
  - Password reset via email
  - Role-based access control (Admin/User)
  - Session management with 15-minute timeout

- **File Management**
  - Browse and navigate folder structure
  - Upload files (with admin approval workflow)
  - Download files and folders (folders as ZIP)
  - Create folders
  - Delete files/folders (admin only)
  - File type validation and security checks

- **Upload System**
  - Unique upload IDs for each file upload
  - Separate pending and completed upload logs
  - Admin approval workflow for uploaded files
  - File upload with folder structure preservation
  - User upload history tracking

- **Admin Dashboard**
  - View and manage user registrations
  - Approve/deny pending uploads
  - View system metrics and logs
  - Manage user accounts
  - Track active sessions

- **Additional Features**
  - Suggestion submission system with cooldown levels
  - Activity logging (downloads, sessions, suggestions)
  - Email notifications for user approvals/denials
  - Trash folder for deleted files
  - Responsive Angular frontend

## Backend structure

```
merkaz_backend/
├── app.py                        # Main application entry point
├── config/
│   └── config.py                 # Application configuration and environment settings
│
├── controllers/                  # Controller layer (Flask routes / API endpoints)
│   ├── auth_controller.py        # User authentication and session routes
│   ├── files_controller.py       # File browsing and download endpoints
│   ├── uploads_controller.py     # File upload endpoints
│   └── admin_controller.py       # Admin dashboard endpoints
│
├── services/                     # Business logic layer
│   ├── auth_service.py           # Authentication and session handling
│   ├── file_service.py           # File management and validation
│   ├── upload_service.py         # File upload logic and workflow
│   ├── admin_service.py          # Admin operations, approvals, and reports
│   └── mail_service.py           # Email sending and notifications
│
├── repositories/                 # Data access layer
│   ├── user_repository.py        # Read/write user data (CSV or DB)
│   ├── upload_repository.py      # Manage upload logs and data
│   ├── download_repository.py    # Manage download history
│   ├── session_repository.py     # Handle session logs
│   └── suggestion_repository.py  # Manage user suggestions
│
├── models/                       # Entity and data models
│   ├── user_entity.py            # User entity definition
│   ├── upload_entity.py          # Upload entity definition
│   ├── log_entity.py             # Base log record structure
│   └── __init__.py
│
├── utils/                        # Utility and helper functions
│   ├── file_utils.py             # File operations and MIME validation
│   ├── csv_utils.py              # CSV read/write utilities
│   ├── log_utils.py              # Logging helper functions
│   └── path_utils.py             # Path and directory management
│
└── __init__.py
```
## Frontend structure
```
merkaz-frontend/
├── src/
│   ├── app/
│   │   ├── components/                   # Main feature components
│   │   │   ├── dashboard/
│   │   │   │   ├── admin-dash/           # Admin dashboard page
│   │   │   │   ├── dashboard.component.css
│   │   │   │   ├── dashboard.component.html
│   │   │   │   └── dashboard.component.ts
│   │   │   │
│   │   │   ├── forgotpass/               # Forgot password page
│   │   │   │   ├── forgotpass.component.css
│   │   │   │   ├── forgotpass.component.html
│   │   │   │   └── forgotpass.component.ts
│   │   │   │
│   │   │   ├── login/                    # Login page
│   │   │   │   ├── login.component.css
│   │   │   │   ├── login.component.html
│   │   │   │   └── login.component.ts
│   │   │   │
│   │   │   ├── register/                 # User registration page
│   │   │   │   ├── register.component.css
│   │   │   │   ├── register.component.html
│   │   │   │   └── register.component.ts
│   │   │   │
│   │   │   └── uploads/                  # Uploads and user files
│   │   │       ├── my-uploads.component.css
│   │   │       ├── my-uploads.component.html
│   │   │       ├── my-uploads.component.ts
│   │   │       ├── upload-file.component.css
│   │   │       ├── upload-file.component.html
│   │   │       └── upload-file.component.ts
│   │   │
│   │   ├── interceptors/
│   │   │   └── auth.interceptor.ts       # HTTP interceptor for auth headers
│   │   │
│   │   ├── models/
│   │   │   └── pending-user.model.ts     # Pending user data model
│   │   │
│   │   ├── services/
│   │   │   ├── auth.guard.ts             # Route guard for authentication
│   │   │   └── auth.service.ts           # Authentication and user session service
│   │   │
│   │   ├── app.config.ts                 # Global app configuration
│   │   ├── app.css                       # Global styling
│   │   ├── app.html                      # Root template
│   │   └── app.ts                        # Root component / bootstrap
```

## Installation

### Prerequisites

- Python 3.7+ 
- Node.js 14+ and npm
- Angular CLI (for frontend development)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NagoAmir_Server
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   ```

   On Windows (PowerShell):
   ```bash
   .venv\Scripts\Activate.ps1
   ```
   
   If you encounter an execution policy error:
   ```bash
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   ```

   On Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Note: If you encounter encoding issues, you may need to install dependencies manually from `venv_prerequsites.txt`

4. **Configure the application**
   
   The configuration file is located at `merkaz_backend/config/config.py`. A template file (`merkaz_backend/config/config_template.py`) is provided for reference.
   
   Edit `merkaz_backend/config/config.py` to set:
   - Secret keys for sessions and tokens (automatically generated, but can be customized)
   - Mail server configuration (Gmail SMTP settings)
   - File paths and folder names
   - Allowed file extensions
   
   **Note**: On first run, the application will automatically create the necessary directories (`merkaz_server/data/`, `merkaz_server/logs/`, `merkaz_server/server_files/`) and initialize CSV log files.

5. **Run the backend server**
   ```bash
   cd merkaz_backend
   python app.py
   ```
   
   The server will start on `http://localhost:8000` using Waitress.

### Frontend Setup

1. **Install Node.js**
   
   Download and install from: https://nodejs.org
   
   Verify installation:
   ```bash
   node -v
   npm -v
   ```

2. **Install Angular CLI globally**
   ```bash
   npm install -g @angular/cli
   ```

3. **Navigate to frontend directory**
   ```bash
   cd merkaz-frontend
   ```

4. **Install frontend dependencies**
   ```bash
   npm install
   ```

5. **Run the development server**
   ```bash
   ng serve
   ```
   
   The frontend will be available at `http://localhost:4200`

## Configuration

### Backend Configuration (`merkaz_backend/config/config.py`)

Key configuration options:

- **Secret Keys**: `SUPER_SECRET_KEY` and `TOKEN_SECRET_KEY` are automatically generated using `os.urandom()`, but can be customized for production
- **Mail Settings**: Configure Gmail SMTP settings for email notifications
- **File Paths**: All paths are automatically resolved relative to the project root. Data, logs, and server files are stored in the `merkaz_server/` directory
- **Allowed Extensions**: Modify `ALLOWED_EXTENSIONS` and `VIDEO_EXTENSIONS` as needed
- **File Size Limits**: Adjust `MAX_CONTENT_LENGTH` and `MAX_VIDEO_CONTENT_LENGTH`

**Note**: A template configuration file (`config_template.py`) is available in the same directory for reference. The actual `config.py` uses dynamic path resolution and includes additional settings for ID sequence management.

### Frontend Configuration

The frontend is configured to connect to `http://localhost:8000` by default. Update API endpoints in components if using a different backend URL.

## Running the Application

### Development Mode

1. **Start the backend server** (from `merkaz_backend/`):
   ```bash
   python app.py
   ```

2. **Start the frontend** (from `merkaz-frontend/`):
   ```bash
   ng serve
   ```

3. **Access the application**:
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000

### Production Deployment

For production, consider:
- Using a production WSGI server (Waitress is already configured)
- Building the Angular app: `ng build --configuration production`
- Setting up proper HTTPS
- Configuring environment variables for sensitive data
- Using a reverse proxy (nginx, Apache)

## API Endpoints Overview

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `POST /logout` - User logout
- `POST /forgot_password` - Request password reset
- `POST /reset_password` - Reset password with token

### File Management
- `GET /browse` - Browse root directory
- `GET /browse/<path>` - Browse specific directory
- `GET /download/file/<path>` - Download file
- `GET /download/folder/<path>` - Download folder as ZIP
- `POST /create_folder` - Create new folder
- `POST /delete/<path>` - Delete file/folder (admin only)

### Uploads
- `POST /upload` - Upload file(s)
- `GET /my_uploads` - Get user's upload history
- `GET /admin/uploads` - Get pending uploads (admin only)
- `POST /admin/move_upload/<filename>` - Approve and move upload (admin only)
- `POST /admin/decline_upload/<filename>` - Decline upload (admin only)

### Admin
- `GET /admin/metrics` - System metrics
- `GET /admin/users` - User management
- `GET /admin/pending` - Pending user registrations
- `GET /admin/denied` - Denied user registrations
- `POST /admin/approve_user/<email>` - Approve user registration
- `POST /admin/deny_user/<email>` - Deny user registration

### Suggestions
- `POST /suggest` - Submit suggestion (with cooldown system)

## Upload System Improvements

The upload system has been enhanced with:

- **Unique Upload IDs**: Each upload receives a unique identifier for tracking
- **Separate Log Files**: 
  - `upload_pending_log.csv` - Files awaiting admin approval
  - `upload_completed_log.csv` - Files that have been approved and moved
  - Prevents duplicate entries and ensures accurate status tracking
- **Improved Tracking**: Admin can see exactly which files are pending approval
- **Better History**: Users can view their complete upload history with accurate status

## Ngrok Setup (Optional)

To expose the local server to the internet for testing:

### Installation on Windows

**Option 1 - Using winget (Recommended):**
```powershell
winget install ngrok.ngrok
```

**Option 2 - Using Chocolatey:**
```powershell
choco install ngrok
```

**Option 3 - Manual Installation:**
1. Visit: https://dashboard.ngrok.com/get-started/setup
2. Download ngrok for Windows
3. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok`)
4. Add that folder to your system PATH:
   - Press `Win+X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add the folder path (e.g., `C:\ngrok`)
   - Click "OK" on all dialogs
5. Restart your terminal/PowerShell
6. Verify installation: `ngrok version`

### Running Ngrok

After installation, you can use the provided script:
```bash
python merkaz_backend/run_ngrok.py [BACKEND_PORT] [FRONTEND_PORT]
```

Or run ngrok manually:
```bash
ngrok http 8000
```

This creates a public URL that tunnels to your local server.

## Development Notes

### Generating Requirements File
```bash
pip freeze > requirements.txt
```

### Database Files
User data and activity logs are stored in CSV format within the `merkaz_server/` directory:
- `merkaz_server/data/auth_users.csv` - Authenticated users
- `merkaz_server/data/new_users.csv` - Pending user registrations
- `merkaz_server/data/denied_users.csv` - Denied registrations
- `merkaz_server/data/password_reset.csv` - Password reset tokens
- `merkaz_server/data/user_id_sequence.txt` - User ID sequence counter
- `merkaz_server/logs/` - Various activity logs (session, download, upload, suggestion logs)
- `merkaz_server/server_files/files_to_share/` - Approved shared files
- `merkaz_server/server_files/uploads/` - Pending uploads awaiting approval
- `merkaz_server/server_files/trash/` - Deleted files

### File Upload Flow
1. User uploads file → Saved in `merkaz_server/server_files/uploads/` directory (flat structure)
2. Entry created in `merkaz_server/logs/upload_pending_log.csv` with unique upload ID
3. Admin reviews pending uploads via admin dashboard
4. Admin approves → File moved to `merkaz_server/server_files/files_to_share/`, entry moved to `merkaz_server/logs/upload_completed_log.csv`
5. Admin declines → File deleted, entry moved to `merkaz_server/logs/declined_log.csv`

## Security Considerations

- **Secret Keys**: While secret keys are automatically generated, review and customize them for production if needed
- **Mail Credentials**: Never commit `config.py` with real mail credentials to version control. Use environment variables or secure configuration management
- **HTTPS**: Use HTTPS in production
- **Input Validation**: Implement proper input validation (already included in the application)
- **Regular Updates**: Keep dependencies updated
- **File Upload Restrictions**: Review and adjust `ALLOWED_EXTENSIONS` and file size limits as needed
- **CORS Configuration**: Update CORS origins in `app.py` for production to restrict access to authorized domains only

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

[Add contribution guidelines if applicable]

## Support

For issues or questions, please [create an issue or contact information].
