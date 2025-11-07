# Controllers Module Documentation

The controllers layer handles HTTP requests and responses, defining all API endpoints.

## Overview

Controllers are Flask Blueprints that define routes and handle request/response logic. They validate input, call services, and return JSON responses.

## Files

### `auth_controller.py`

Authentication and user management endpoints.

**Blueprint**: `auth_bp`

**Routes**:

#### `POST /login`
- **Function**: `api_login()`
- **Purpose**: Authenticate user and create session
- **Request**: `{email, password}`
- **Response**: User info with role
- **Logs**: Session log (LOGIN_SUCCESS/LOGIN_FAIL)

#### `POST /register`
- **Function**: `api_register()`
- **Purpose**: Register new user (pending approval)
- **Request**: `{email, password}`
- **Response**: Success message
- **Validations**: Email uniqueness, password length (min 8)
- **Sends**: Email notification to admins

#### `POST /logout`
- **Function**: `logout()`
- **Purpose**: Clear user session
- **Logs**: Session log (LOGOUT)

#### `POST /forgot-password`
- **Function**: `api_forgot_password()`
- **Purpose**: Request password reset email
- **Request**: `{email}`
- **Sends**: Password reset email with token

#### `POST /reset-password/<token>`
- **Function**: `reset_password(token)`
- **Purpose**: Reset password using token
- **Request**: `{password}`
- **Validations**: Token expiration (1 hour), password length

**Helper Functions**:
- `email_exists(email)`: Check if email exists in any user database

---

### `files_controller.py`

File browsing, downloading, and folder management endpoints.

**Blueprint**: `files_bp`

**Routes**:

#### `GET /browse` and `GET /browse/<path:subpath>`
- **Function**: `downloads(subpath='')`
- **Purpose**: Browse directory structure
- **Response**: List of files and folders with metadata
- **Features**: Path traversal protection, upload ID tracking

#### `POST /delete/<path:item_path>`
- **Function**: `delete_item(item_path)`
- **Purpose**: Delete file/folder (admin only)
- **Action**: Moves to trash with timestamp
- **Logs**: Download log (DELETE)

#### `POST /create_folder`
- **Function**: `create_folder()`
- **Purpose**: Create new folder (admin only)
- **Request**: `{parent_path, folder_name}`
- **Validations**: Folder name validation, path safety
- **Logs**: Download log (CREATE_FOLDER)

#### `GET /download/file/<path:file_path>`
- **Function**: `download_file(file_path)`
- **Purpose**: Download a file
- **Response**: File download (binary)
- **Logs**: Download log (FILE)

#### `GET /download/folder/<path:folder_path>`
- **Function**: `download_folder(folder_path)`
- **Purpose**: Download folder as ZIP
- **Response**: ZIP file download
- **Logs**: Download log (FOLDER)

#### `POST /suggest`
- **Function**: `suggest()`
- **Purpose**: Submit suggestion with cooldown
- **Request**: `{suggestion}`
- **Features**: Progressive cooldown system (0s → 1hr)
- **Logs**: Suggestion log

**Constants**:
- `COOLDOWN_LEVELS = [0, 60, 300, 600, 1800, 3600]` (seconds)

---

### `uploads_controller.py`

File upload handling and approval workflow.

**Blueprint**: `uploads_bp`

**Routes**:

#### `POST /upload`
- **Function**: `upload_file()`
- **Purpose**: Upload file(s) for admin approval
- **Request**: `multipart/form-data` with `file` and optional `subpath`
- **Validations**: 
  - File type (extension whitelist)
  - File safety (MIME type checking)
  - Path traversal protection
- **Storage**: Files saved flat in uploads directory
- **Logs**: Upload pending log with unique upload ID
- **Response**: List of successful uploads and errors

#### `GET /my_uploads`
- **Function**: `my_uploads()`
- **Purpose**: Get current user's upload history
- **Response**: List of uploads with status (Pending/Approved/Declined)
- **Sources**: Pending log, completed log, declined log

#### `GET /admin/uploads`
- **Function**: `admin_uploads()`
- **Purpose**: Get all pending uploads (admin only)
- **Response**: List of pending uploads with user info

#### `POST /admin/move_upload/<path:filename>`
- **Function**: `move_upload(filename)`
- **Purpose**: Approve and move upload to share directory (admin only)
- **Request**: `{upload_id, target_path}`
- **Actions**: 
  - Moves file from uploads/ to files_to_share/
  - Removes from pending log
  - Adds to completed log
- **Features**: Unique filename generation if conflict

#### `POST /admin/decline_upload/<path:filename>`
- **Function**: `decline_upload(filename)`
- **Purpose**: Decline upload and delete file (admin only)
- **Request**: `{upload_id}` (optional)
- **Actions**: 
  - Deletes file from uploads/
  - Removes from pending log
  - Adds to declined log

**Helper Functions**:
- `remove_from_pending_log(upload_id)`: Remove entry from pending log
- `allowed_file(filename)`: Check file extension
- `is_file_malicious(file_stream)`: Check MIME type for executables
- `get_unique_filename(...)`: Generate unique filename with conflict resolution

**Thread Safety**: Uses `_log_lock` for thread-safe CSV operations

---

### `admin_controller.py`

Admin dashboard and user management endpoints.

**Blueprint**: `admin_bp` (prefix: `/admin`)

**Routes**:

#### `GET /admin/metrics`
- **Function**: `admin_metrics()`
- **Purpose**: Get available log file types
- **Response**: List of log types with descriptions

#### `GET /admin/users`
- **Function**: `admin_users()`
- **Purpose**: Get all users with online status
- **Response**: User list with online status

#### `GET /admin/pending`
- **Function**: `admin_pending()`
- **Purpose**: Get pending user registrations
- **Response**: List of pending users

#### `GET /admin/denied`
- **Function**: `admin_denied()`
- **Purpose**: Get denied user registrations
- **Response**: List of denied users

#### `POST /admin/approve/<email>`
- **Function**: `approve_user(email)`
- **Purpose**: Approve pending user registration
- **Actions**: 
  - Moves user from pending to auth
  - Sets status to active
  - Sends approval email

#### `POST /admin/deny/<email>`
- **Function**: `deny_user(email)`
- **Purpose**: Deny pending user registration
- **Actions**: 
  - Moves user from pending to denied
  - Sends denial email

#### `POST /admin/re-pend/<email>`
- **Function**: `re_pend_user(email)`
- **Purpose**: Move denied user back to pending

#### `POST /admin/toggle-role/<email>`
- **Function**: `toggle_role(email)`
- **Purpose**: Toggle user role (admin ↔ user)
- **Protection**: Cannot change own role

#### `POST /admin/toggle-status/<email>`
- **Function**: `toggle_status(email)`
- **Purpose**: Toggle user status (active ↔ inactive)
- **Protection**: Cannot change own status

#### `GET /admin/metrics/download/<log_type>`
- **Function**: `download_metrics_xlsx(log_type)`
- **Purpose**: Download log file as XLSX
- **Log Types**: session, download, suggestion, upload, declined

#### `POST /admin/heartbeat`
- **Function**: `heartbeat()`
- **Purpose**: Update user's online status
- **Usage**: Called periodically by frontend

---

## Common Patterns

### Authentication Check
```python
if not session.get("logged_in"):
    return jsonify({"error": "Not logged in"}), 401
```

### Admin Check
```python
if not session.get("is_admin"):
    return jsonify({"error": "Access denied"}), 403
```

### Request Validation
```python
data = request.get_json()
if not data:
    return jsonify({"error": "Missing JSON body"}), 400
```

### Error Handling
```python
try:
    # operation
    return jsonify({"message": "Success"}), 200
except Exception as e:
    return jsonify({"error": f"Error: {e}"}), 500
```

### Logging
```python
log_event(config.SESSION_LOG_FILE, [
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    email,
    "EVENT_TYPE"
])
```

## Best Practices

1. **Always validate input** before processing
2. **Check authentication** for protected endpoints
3. **Use appropriate HTTP status codes**
4. **Log important events** for audit trail
5. **Return consistent error format**
6. **Protect against path traversal** in file operations
7. **Use thread-safe operations** for CSV logging
8. **Validate file types** before saving

## Dependencies

- Flask Blueprint
- Flask session
- Services layer (auth_service, mail_service)
- Models (User entity)
- Utils (log_event, get_project_root, etc.)
- Config (configuration values)

