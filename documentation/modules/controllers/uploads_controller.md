# uploads_controller.py

Uploads controller handling file upload operations and admin approval workflow.

## Location
`merkaz_backend/controllers/uploads_controller.py`

## Blueprint
`uploads_bp` - Registered at root level

## Routes

### `POST /upload`
Upload file(s) for admin approval.

**Request:**
- `multipart/form-data` with:
  - `file`: One or more files
  - `subpath` (optional): Target subdirectory path

**Response (200):**
```json
{
  "message": "Successfully uploaded 3 file(s). Files are pending review.",
  "successful_uploads": ["file1.txt", "file2.pdf"],
  "count": 3,
  "errors": [],
  "failed_files_by_type": {}
}
```

**Errors:**
- `401` - Not logged in
- `400` - No files selected, invalid path, file type not allowed, or malicious file detected
- `500` - Upload error

**Features:**
- Multi-file upload support
- Folder structure preservation
- File type and safety validation
- Unique filename generation
- Thread-safe logging

**Upload Workflow:**
1. File saved to `uploads/` directory (flat structure)
2. Logged to pending log with upload ID
3. Admin reviews pending uploads
4. Admin approves → Moved to `files_to_share/` with structure
5. Admin declines → Deleted from `uploads/`

---

### `GET /my_uploads`
Get current user's upload history.

**Response (200):**
```json
[
  {
    "upload_id": "1",
    "timestamp": "2024-01-01 12:00:00",
    "email": "user@example.com",
    "user_id": "1",
    "filename": "file.txt",
    "path": "path/to/file.txt",
    "status": "Pending Review"
  }
]
```

**Errors:**
- `401` - Not logged in

**Status Values:**
- `Pending Review` - Awaiting admin approval
- `Approved & Moved` - Approved and moved to share directory
- `Declined` - Declined by admin
- `Processing` - File not found (may have been removed)

---

### `GET /admin/uploads`
Get all pending uploads (admin only).

**Response (200):**
```json
[
  {
    "upload_id": "1",
    "timestamp": "2024-01-01 12:00:00",
    "email": "user@example.com",
    "user_id": "1",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "user"
    },
    "filename": "path/to/file.txt",
    "path": "path/to/file.txt",
    "flat_filename": "file_0.txt"
  }
]
```

**Errors:**
- `403` - Access denied (not admin)

---

### `POST /admin/move_upload/<path:filename>`
Approve and move upload (admin only).

**URL Parameters:**
- `filename` (str): Filename or path of upload

**Request Body:**
```json
{
  "upload_id": "123",
  "target_path": "desired/path/in/share"
}
```

**Response (200):**
```json
{
  "message": "Item 'file.txt' has been successfully moved to 'desired/path/in/share'."
}
```

**Errors:**
- `403` - Access denied
- `400` - Missing JSON body or empty target path
- `404` - Upload not found or source item not found
- `500` - Error during move

**Actions:**
- Moves file from `uploads/` to `files_to_share/`
- Updates pending log to completed log
- Handles filename conflicts with unique naming

---

### `POST /admin/decline_upload/<path:filename>`
Decline upload (admin only).

**URL Parameters:**
- `filename` (str): Filename or path of upload

**Request Body:**
```json
{
  "upload_id": "123",
  "email": "user@example.com",
  "user_id": "1"
}
```

**Response (200):**
```json
{
  "message": "Item 'file.txt' has been declined and removed."
}
```

**Errors:**
- `403` - Access denied
- `404` - Item already removed
- `500` - Error during deletion

**Actions:**
- Removes file from `uploads/` directory
- Removes entry from pending log
- Logs to declined log

---

### `POST /admin/edit_upload_path/`
Edit path of approved upload (admin only).

**Request Body:**
```json
{
  "upload_id": "123",
  "new_path": "/new/path/to/file.txt"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Path updated for upload_id 123"
}
```

**Errors:**
- `403` - Access denied
- `400` - Missing upload_id or new_path
- `404` - Upload ID not found or source item not found
- `500` - Error during move

---

## Helper Functions

### `remove_from_pending_log(upload_id: str) -> dict | None`
Removes an entry from the pending log by upload_id.

**Parameters:**
- `upload_id` (str): Upload ID to remove

**Returns:**
- `dict | None`: Removed row data if found, None otherwise

**Thread Safety:**
- Uses `_log_lock` for thread-safe operations

---

### `allowed_file(filename: str) -> bool`
Checks if file extension is in allowed list.

**Parameters:**
- `filename` (str): Filename to check

**Returns:**
- `bool`: True if extension is allowed

---

### `is_file_malicious(file_stream) -> bool`
Checks if file is potentially malicious using magic numbers.

**Parameters:**
- `file_stream`: File stream object

**Returns:**
- `bool`: True if file is potentially malicious

**Security:**
- Reads first 2048 bytes for magic number detection
- Detects executable files

---

### `get_unique_filename(upload_dir, filename, share_dir=None, share_subpath='', save_flat=True) -> tuple`
Generates a unique filename by appending `_1`, `_2`, etc. if conflicts exist.

**Parameters:**
- `upload_dir` (str): Base upload directory
- `filename` (str): Original filename (may include path)
- `share_dir` (str, optional): Share directory to check for conflicts
- `share_subpath` (str, optional): Subpath in share directory
- `save_flat` (bool): If True, save files flat (no directory structure)

**Returns:**
- `tuple`: `(flat_filename, full_save_path, full_relative_path)`

---

## Thread Safety

- Uses `threading.Lock` (`_log_lock`) for thread-safe CSV operations
- Prevents race conditions during concurrent uploads

---

## Dependencies

- `flask.Blueprint` - Route organization
- `flask.session` - Session management
- `magic` - File type detection
- `threading` - Thread-safe operations
- `models.user_entity.User` - User entity
- `utils` - Logging, path, and file utilities
- `config.config` - Configuration constants

