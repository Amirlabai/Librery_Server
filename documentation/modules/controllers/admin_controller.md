# admin_controller.py

Admin controller handling admin dashboard and user management endpoints.

## Location
`merkaz_backend/controllers/admin_controller.py`

## Blueprint
`admin_bp` - Registered with `/admin` prefix

## Routes

All routes are prefixed with `/admin`.

### `GET /admin/metrics`
Get available log file types for metrics.

**Response (200):**
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

**Errors:**
- `403` - Access denied (not admin)

---

### `GET /admin/users`
Get all users with online status.

**Response (200):**
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

**Errors:**
- `403` - Access denied (not admin)

**Features:**
- Marks current admin as online
- Includes online status for each user

---

### `GET /admin/pending`
Get pending user registrations.

**Response (200):**
```json
[
  {
    "id": 1,
    "email": "newuser@example.com",
    "role": "user",
    "status": "pending"
  }
]
```

**Errors:**
- `403` - Access denied (not admin)

---

### `GET /admin/denied`
Get denied user registrations.

**Response (200):**
```json
[
  {
    "id": 1,
    "email": "denied@example.com",
    "role": "user",
    "status": "denied"
  }
]
```

**Errors:**
- `403` - Access denied (not admin)

---

### `POST /admin/approve/<email>`
Approve pending user registration.

**URL Parameters:**
- `email` (str): Email of user to approve

**Response (200):**
```json
{
  "message": "User user@example.com approved successfully"
}
```

**Errors:**
- `403` - Access denied (not admin)
- `404` - User not found in pending list

**Actions:**
- Moves user from pending to authenticated users
- Sets status to 'active'
- Assigns user ID if missing
- Sends approval email

---

### `POST /admin/deny/<email>`
Deny pending user registration.

**URL Parameters:**
- `email` (str): Email of user to deny

**Response (200):**
```json
{
  "message": "User user@example.com has been denied"
}
```

**Errors:**
- `403` - Access denied (not admin)
- `404` - User not found

**Actions:**
- Moves user from pending to denied users
- Assigns user ID if missing
- Sends denial email

---

### `POST /admin/re-pend/<email>`
Move denied user back to pending.

**URL Parameters:**
- `email` (str): Email of user to re-pend

**Response (200):**
```json
{
  "message": "User user@example.com moved back to pending"
}
```

**Errors:**
- `403` - Access denied (not admin)
- `404` - User not found

**Actions:**
- Moves user from denied to pending users
- Assigns user ID if missing

---

### `POST /admin/toggle-role/<email>`
Toggle user role between admin and user.

**URL Parameters:**
- `email` (str): Email of user

**Response (200):**
```json
{
  "message": "Successfully updated role for user@example.com"
}
```

**Errors:**
- `403` - Access denied (not admin) or cannot change own admin status
- `404` - User not found

**Restrictions:**
- Cannot change own admin status

---

### `POST /admin/toggle-status/<email>`
Toggle user status between active and inactive.

**URL Parameters:**
- `email` (str): Email of user

**Response (200):**
```json
{
  "message": "Successfully updated status for user@example.com"
}
```

**Errors:**
- `403` - Access denied (not admin) or cannot change own status
- `404` - User not found

**Restrictions:**
- Cannot change own status

---

### `GET /admin/metrics/download/<log_type>`
Download log file as XLSX spreadsheet.

**URL Parameters:**
- `log_type` (str): Type of log (session, download, suggestion, upload, declined)

**Response:**
- XLSX file download

**Errors:**
- `403` - Access denied (not admin)
- `404` - Invalid log type or file not found
- `500` - Error during XLSX conversion

**Supported Log Types:**
- `session` - Session log
- `download` - Download log
- `suggestion` - Suggestion log
- `upload` - Upload log (deprecated)
- `declined` - Declined upload log

---

### `POST /admin/heartbeat`
Update user online status (heartbeat endpoint).

**Response (200):**
```json
{
  "message": "Heartbeat received"
}
```

**Errors:**
- `401` - Not logged in

**Actions:**
- Marks user as online
- Extends session timeout

---

## Dependencies

- `flask.Blueprint` - Route organization
- `flask.session` - Session management
- `models.user_entity.User` - User entity
- `services.mail_service` - Email notifications
- `services.auth_service` - Session tracking
- `utils` - CSV conversion and ID generation
- `config.config` - Configuration constants

