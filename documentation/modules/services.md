# Services Module Documentation

The services layer implements business logic and orchestrates operations across the application.

## Overview

Services contain the core business logic, separating it from controllers and data access. They handle workflows, validations, and cross-cutting concerns.

## Files

### `auth_service.py`

Authentication and session management service.

**Functions**:

#### `mark_user_online()`
- **Purpose**: Mark current user as online
- **Action**: Updates `active_sessions` dictionary with current timestamp
- **Uses**: Flask session to get user email

#### `mark_user_offline()`
- **Purpose**: Mark current user as offline
- **Action**: Removes user from `active_sessions` dictionary

#### `get_active_users()`
- **Purpose**: Get list of currently active users
- **Returns**: List of email addresses

#### `is_user_authenticated()`
- **Purpose**: Check if current user is authenticated
- **Returns**: Boolean

#### `is_user_admin()`
- **Purpose**: Check if current user is admin
- **Returns**: Boolean

#### `get_current_user_email()`
- **Purpose**: Get email of current user
- **Returns**: Email string or None

#### `get_current_user_id()`
- **Purpose**: Get user ID of current user
- **Returns**: User ID or None

**Data Structure**:
```python
active_sessions = {
    "user@example.com": datetime.utcnow(),
    ...
}
```

---

### `file_service.py`

File management and validation service.

**Class**: `FileService`

**Methods**:

#### `get_share_directory()`
- **Returns**: Path to share directory (files_to_share)

#### `get_upload_directory()`
- **Returns**: Path to upload directory

#### `get_trash_directory()`
- **Returns**: Path to trash directory

#### `validate_file_extension(filename)`
- **Purpose**: Validate file extension against whitelist
- **Returns**: Boolean
- **Uses**: `file_utils.allowed_file()`

#### `validate_file_safety(file_stream)`
- **Purpose**: Validate file is not malicious
- **Returns**: Boolean (True if safe)
- **Uses**: `file_utils.is_file_malicious()`

#### `create_folder(folder_path)`
- **Purpose**: Create folder at specified path
- **Action**: Creates directory structure

#### `delete_item(source_path, trash_path)`
- **Purpose**: Move item to trash
- **Action**: Moves file/folder to trash directory

#### `create_zip_from_folder(folder_path)`
- **Purpose**: Create ZIP file from folder in memory
- **Returns**: BytesIO object with ZIP data
- **Uses**: zipfile module

---

### `upload_service.py`

File upload logic and workflow service.

**Class**: `UploadService`

**Thread Safety**: Uses `_log_lock` for thread-safe operations

**Methods**:

#### `get_upload_directory()`
- **Returns**: Path to upload directory

#### `validate_file(file)`
- **Purpose**: Validate file for upload
- **Validations**: 
  - File extension
  - File safety (MIME type)
- **Returns**: `(is_valid, error_message)` tuple

#### `get_next_upload_id()`
- **Purpose**: Get next unique upload ID
- **Returns**: Integer upload ID
- **Uses**: `csv_utils.get_next_upload_id()`

#### `log_pending_upload(upload_id, email, user_id, filename, path)`
- **Purpose**: Log upload to pending log
- **Thread Safe**: Yes (uses lock)
- **Format**: upload_id, timestamp, email, user_id, filename, path

#### `log_completed_upload(upload_id, original_timestamp, email, user_id, filename, final_path)`
- **Purpose**: Log approved upload to completed log
- **Thread Safe**: Yes
- **Format**: upload_id, original_timestamp, approval_timestamp, email, user_id, filename, final_path

#### `log_declined_upload(email, user_id, filename)`
- **Purpose**: Log declined upload
- **Thread Safe**: Yes
- **Format**: timestamp, email, user_id, filename

---

### `admin_service.py`

Admin operations, approvals, and reports service.

**Class**: `AdminService`

**Methods**:

#### `approve_user(email)`
- **Purpose**: Approve pending user registration
- **Actions**:
  1. Find user in pending list
  2. Assign user ID if missing
  3. Move to authenticated users
  4. Set status to active
  5. Remove from pending
- **Returns**: `(user, error_message)` tuple

#### `deny_user(email)`
- **Purpose**: Deny pending user registration
- **Actions**:
  1. Find user in pending list
  2. Assign user ID if missing
  3. Move to denied users
  4. Remove from pending
- **Returns**: `(user, error_message)` tuple

#### `toggle_user_role(email)`
- **Purpose**: Toggle user role between admin and user
- **Returns**: `(users_list, error_message)` tuple

#### `toggle_user_status(email)`
- **Purpose**: Toggle user status between active and inactive
- **Returns**: `(users_list, error_message)` tuple

---

### `mail_service.py`

Email sending and notifications service.

**Mail Object**: `mail = Mail()` (Flask-Mail instance)

**Functions**:

#### `send_new_user_notification(app, user_email)`
- **Purpose**: Notify admins of new user registration
- **Method**: Asynchronous (background thread)
- **Recipients**: All admin emails (BCC)
- **Template**: HTML email with pending approval link

#### `send_approval_email(app, user_email)`
- **Purpose**: Notify user of account approval
- **Method**: Asynchronous
- **Recipients**: User email
- **Template**: HTML email with login link

#### `send_denial_email(app, user_email)`
- **Purpose**: Notify user of account denial
- **Method**: Asynchronous
- **Recipients**: User email
- **Template**: HTML email with denial message

#### `send_password_reset_email(app, user_email, token)`
- **Purpose**: Send password reset email
- **Method**: Asynchronous
- **Recipients**: User email
- **Template**: HTML email with reset link (1 hour expiration)

**Internal Functions** (with `_sync` suffix):
- `_send_new_user_notification_sync()`
- `_send_approval_email_sync()`
- `_send_denial_email_sync()`
- `_send_password_reset_email_sync()`

**Threading**: All email functions use background threads to avoid blocking requests.

---

## Service Patterns

### Validation Pattern
```python
@staticmethod
def validate_file(file):
    if not allowed_file(file.filename):
        return False, "File type not allowed"
    if is_file_malicious(file.stream):
        return False, "Malicious file detected"
    return True, None
```

### Logging Pattern
```python
@staticmethod
def log_event(data):
    with _log_lock:  # Thread-safe
        log_event(config.LOG_FILE, data)
```

### Error Handling Pattern
```python
@staticmethod
def operation(param):
    try:
        result = do_operation(param)
        return result, None  # (result, error)
    except Exception as e:
        return None, str(e)
```

### Async Email Pattern
```python
def send_email(app, email):
    thread = threading.Thread(
        target=_send_email_sync,
        args=(app, email)
    )
    thread.daemon = True
    thread.start()
```

## Dependencies

### External
- Flask-Mail (mail_service)
- threading (async operations)
- zipfile (file_service)
- shutil (file_service)

### Internal
- Models (User entity)
- Utils (file_utils, csv_utils, log_utils, path_utils)
- Config (configuration values)

## Best Practices

1. **Keep services stateless** where possible
2. **Use static methods** for stateless operations
3. **Return tuples** `(result, error)` for error handling
4. **Use thread-safe operations** for shared resources
5. **Keep business logic** separate from controllers
6. **Validate inputs** before processing
7. **Use async operations** for time-consuming tasks (emails)
8. **Log important operations** for audit trail

## Thread Safety

Services that modify shared resources use locks:

- `upload_service`: Uses `_log_lock` for CSV logging
- `mail_service`: Uses threading for async email sending

## Error Handling

Services typically return tuples:
- Success: `(result, None)`
- Error: `(None, error_message)`

This allows controllers to handle errors gracefully:
```python
user, error = AdminService.approve_user(email)
if error:
    return jsonify({"error": error}), 400
```

