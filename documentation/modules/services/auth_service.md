# auth_service.py

Authentication service for session handling and user status tracking.

## Location
`merkaz_backend/services/auth_service.py`

## Overview

Manages user session state and active user tracking. Provides functions for marking users online/offline and retrieving active sessions.

## Global Variables

### `active_sessions: dict`
Dictionary mapping email addresses to their last active timestamp.
- **Key:** User email (str)
- **Value:** Last active datetime (datetime)

## Functions

### `mark_user_online() -> None`
Mark the current user as online.

**Session Requirements:**
- Requires `email` in session

**Actions:**
- Adds user email to `active_sessions` dictionary
- Sets timestamp to current UTC time
- Logs session event via `SessionRepository`

**Output:**
- Prints: `🟢 {email} marked online`

---

### `mark_user_offline() -> None`
Mark the current user as offline.

**Session Requirements:**
- Requires `email` in session

**Actions:**
- Removes user email from `active_sessions` dictionary
- Logs logout event via `SessionRepository`

**Output:**
- Prints: `🔴 {email} marked offline`

---

### `get_active_users() -> list[str]`
Get list of currently active users.

**Returns:**
- `list[str]`: List of email addresses of active users

**Usage:**
- Used by admin dashboard to show online users
- Returns empty list if no active users

---

### `is_user_authenticated() -> bool`
Check if the current user is authenticated.

**Returns:**
- `bool`: True if user is logged in, False otherwise

**Checks:**
- Session key: `logged_in`

---

### `is_user_admin() -> bool`
Check if the current user is an admin.

**Returns:**
- `bool`: True if user is admin, False otherwise

**Checks:**
- Session key: `is_admin`

---

### `get_current_user_email() -> str | None`
Get the email of the current user.

**Returns:**
- `str | None`: User email from session, or None if not set

---

### `get_current_user_id() -> int | None`
Get the user ID of the current user.

**Returns:**
- `int | None`: User ID from session, or None if not set

---

## Session Integration

This service relies on Flask session for user identification:
- `session.get("email")` - User email
- `session.get("logged_in")` - Authentication status
- `session.get("is_admin")` - Admin status
- `session.get("user_id")` - User ID

---

## Dependencies

- `flask.session` - Session management
- `datetime` - Timestamp handling
- `repositories.session_repository.SessionRepository` - Session logging

---

## Usage Example

```python
from services.auth_service import mark_user_online, get_active_users

# Mark user online after login
mark_user_online()

# Get list of active users
active = get_active_users()
print(f"Active users: {active}")
```

