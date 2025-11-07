# API Reference

Complete reference for all API endpoints in the Merkaz_lib backend.

**Base URL**: `http://localhost:8000`

**Content-Type**: `application/json` (unless specified otherwise)

## Authentication

Most endpoints require authentication via Flask session. Include session cookies in requests.

---

## Authentication Endpoints

### POST `/login`

User login endpoint.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "message": "Login successful",
  "email": "user@example.com",
  "role": "user",
  "token": "mock-token"
}
```

**Error Responses**:
- `400`: Missing JSON body
- `401`: Invalid credentials
- `403`: Account inactive

---

### POST `/register`

User registration endpoint. Creates a pending user account.

**Request Body**:
```json
{
  "email": "newuser@example.com",
  "password": "password123"
}
```

**Response** (201 Created):
```json
{
  "message": "Registration successful. Pending admin approval."
}
```

**Error Responses**:
- `400`: Missing JSON body or password too short (< 8 characters)
- `409`: Email already registered or pending

---

### POST `/logout`

Logout endpoint. Clears session.

**Response** (200 OK):
```json
{
  "message": "Logged out"
}
```

---

### POST `/forgot-password`

Request password reset email.

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset link sent"
}
```

**Error Responses**:
- `404`: Email not found

---

### POST `/reset-password/<token>`

Reset password using token from email.

**Request Body**:
```json
{
  "password": "newpassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Your password has been updated successfully."
}
```

**Error Responses**:
- `400`: Invalid or expired token, missing password, or password too short

---

## File Management Endpoints

### GET `/browse`

Browse root directory.

**Response** (200 OK):
```json
{
  "items": [
    {
      "upload_id": "1",
      "name": "document.pdf",
      "path": "document.pdf",
      "is_folder": false
    },
    {
      "upload_id": "0",
      "name": "folder",
      "path": "folder",
      "is_folder": true
    }
  ],
  "current_path": "",
  "back_path": null,
  "is_admin": false,
  "cooldown_level": 1
}
```

**Authentication**: Required

---

### GET `/browse/<path:subpath>`

Browse specific directory.

**Example**: `GET /browse/folder/subfolder`

**Response**: Same format as `/browse`

**Error Responses**:
- `401`: Not logged in
- `403`: Access denied
- `404`: Invalid path

---

### GET `/download/file/<path:file_path>`

Download a file.

**Example**: `GET /download/file/folder/document.pdf`

**Response**: File download (binary)

**Error Responses**:
- `401`: Not logged in
- `403`: Access denied

---

### GET `/download/folder/<path:folder_path>`

Download a folder as ZIP.

**Example**: `GET /download/folder/myfolder`

**Response**: ZIP file download

**Error Responses**:
- `401`: Not logged in
- `404`: Folder not found

---

### POST `/create_folder`

Create a new folder (Admin only).

**Request Body**:
```json
{
  "parent_path": "folder/subfolder",
  "folder_name": "new_folder"
}
```

**Response** (200 OK):
```json
{
  "message": "Folder 'new_folder' created successfully."
}
```

**Error Responses**:
- `400`: Invalid folder name or path
- `403`: Access denied (not admin)
- `409`: Folder already exists

---

### POST `/delete/<path:item_path>`

Delete a file or folder (Admin only). Moves to trash.

**Example**: `POST /delete/folder/file.pdf`

**Response** (200 OK):
```json
{
  "message": "Successfully moved 'file.pdf' to trash."
}
```

**Error Responses**:
- `403`: Access denied (not admin)
- `404`: File or folder not found

---

### POST `/suggest`

Submit a suggestion (with cooldown system).

**Request Body**:
```json
{
  "suggestion": "Please add dark mode support"
}
```

**Response** (200 OK):
```json
{
  "message": "Thank you, your suggestion has been submitted!"
}
```

**Error Responses**:
- `400`: Missing suggestion text
- `401`: Not logged in
- `429`: Cooldown period not expired

**Cooldown Levels**: 0s, 60s, 5min, 10min, 30min, 1hr (increases with each submission)

---

## Upload Endpoints

### POST `/upload`

Upload file(s). Files are saved to uploads directory and require admin approval.

**Request**: `multipart/form-data`
- `file`: File(s) to upload (can be multiple)
- `subpath`: Optional subpath where file should be placed

**Response** (200 OK):
```json
{
  "message": "Successfully uploaded 2 file(s). Files are pending review.",
  "successful_uploads": ["file1.pdf", "file2.jpg"],
  "count": 2,
  "errors": []
}
```

**Error Responses**:
- `400`: No files selected or validation errors
- `401`: Not logged in

**Note**: Files are stored flat in uploads directory but preserve folder structure in metadata.

---

### GET `/my_uploads`

Get current user's upload history.

**Response** (200 OK):
```json
[
  {
    "upload_id": "1",
    "timestamp": "2024-01-15 10:30:00",
    "email": "user@example.com",
    "user_id": "5",
    "filename": "document.pdf",
    "path": "document.pdf",
    "status": "Pending Review"
  },
  {
    "upload_id": "2",
    "timestamp": "2024-01-14 09:15:00",
    "email": "user@example.com",
    "user_id": "5",
    "filename": "image.jpg",
    "path": "folder/image.jpg",
    "status": "Approved & Moved",
    "approval_timestamp": "2024-01-14 10:00:00"
  }
]
```

**Status Values**:
- `Pending Review`: File awaiting admin approval
- `Approved & Moved`: File approved and moved to share directory
- `Declined`: File was declined by admin

---

## Admin Endpoints

All admin endpoints require admin role.

### GET `/admin/metrics`

Get available log file types for download.

**Response** (200 OK):
```json
[
  {
    "type": "session",
    "name": "Session Log (Login/Logout)",
    "description": "Track user login and failure events."
  },
  {
    "type": "download",
    "name": "Download Log (File/Folder/Delete)",
    "description": "Track all file, folder, and delete events."
  },
  {
    "type": "suggestion",
    "name": "Suggestion Log (User Feedback)",
    "description": "Records all user suggestions."
  }
]
```

---

### GET `/admin/users`

Get all users with online status.

**Response** (200 OK):
```json
{
  "current_admin": "admin@example.com",
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "role": "user",
      "status": "active",
      "is_admin": false,
      "is_active": true,
      "online_status": true
    }
  ]
}
```

---

### GET `/admin/pending`

Get pending user registrations.

**Response** (200 OK):
```json
[
  {
    "id": 10,
    "email": "newuser@example.com",
    "role": "user",
    "status": "pending",
    "is_admin": false,
    "is_active": false
  }
]
```

---

### GET `/admin/denied`

Get denied user registrations.

**Response** (200 OK):
```json
[
  {
    "id": 9,
    "email": "denied@example.com",
    "role": "user",
    "status": "denied",
    "is_admin": false,
    "is_active": false
  }
]
```

---

### GET `/admin/uploads`

Get all pending uploads awaiting approval.

**Response** (200 OK):
```json
[
  {
    "upload_id": "1",
    "timestamp": "2024-01-15 10:30:00",
    "email": "user@example.com",
    "user_id": "5",
    "user": {
      "id": 5,
      "email": "user@example.com",
      "role": "user"
    },
    "filename": "folder/document.pdf",
    "path": "folder/document.pdf",
    "flat_filename": "document.pdf"
  }
]
```

---

### POST `/admin/approve/<email>`

Approve a pending user registration.

**Response** (200 OK):
```json
{
  "message": "User user@example.com approved successfully"
}
```

**Error Responses**:
- `403`: Access denied
- `404`: User not found in pending list

---

### POST `/admin/deny/<email>`

Deny a pending user registration.

**Response** (200 OK):
```json
{
  "message": "User user@example.com has been denied"
}
```

---

### POST `/admin/re-pend/<email>`

Move a denied user back to pending.

**Response** (200 OK):
```json
{
  "message": "User user@example.com moved back to pending"
}
```

---

### POST `/admin/toggle-role/<email>`

Toggle user role between admin and user.

**Response** (200 OK):
```json
{
  "message": "Successfully updated role for user@example.com"
}
```

**Error Responses**:
- `403`: Cannot change own admin status

---

### POST `/admin/toggle-status/<email>`

Toggle user status between active and inactive.

**Response** (200 OK):
```json
{
  "message": "Successfully updated status for user@example.com"
}
```

**Error Responses**:
- `403`: Cannot change own status

---

### POST `/admin/move_upload/<path:filename>`

Approve and move an upload to the share directory.

**Request Body**:
```json
{
  "upload_id": "1",
  "target_path": "folder/document.pdf"
}
```

**Response** (200 OK):
```json
{
  "message": "Item 'document.pdf' has been successfully moved to 'folder/document.pdf'."
}
```

**Error Responses**:
- `400`: Missing target path or invalid path
- `403`: Access denied
- `404`: Source file not found

---

### POST `/admin/decline_upload/<path:filename>`

Decline an upload and delete it.

**Request Body** (optional):
```json
{
  "upload_id": "1"
}
```

**Response** (200 OK):
```json
{
  "message": "Item 'document.pdf' has been declined and removed."
}
```

---

### GET `/admin/metrics/download/<log_type>`

Download a log file as XLSX.

**Log Types**: `session`, `download`, `suggestion`, `upload`, `declined`

**Example**: `GET /admin/metrics/download/session`

**Response**: XLSX file download

**Error Responses**:
- `403`: Access denied
- `404`: Invalid log type or file not found

---

### POST `/admin/heartbeat`

Update user's online status (heartbeat).

**Response** (200 OK):
```json
{
  "message": "Heartbeat received"
}
```

**Error Responses**:
- `401`: Not logged in

---

## Error Response Format

All errors follow this format:

```json
{
  "error": "Error message description"
}
```

## Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `429`: Too Many Requests
- `500`: Internal Server Error

