# auth_controller.py

Authentication controller handling user authentication, registration, logout, and password reset endpoints.

## Location
`merkaz_backend/controllers/auth_controller.py`

## Blueprint
`auth_bp` - Registered at root level

## Routes

### `POST /login`
User login endpoint.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "email": "user@example.com",
  "role": "admin",
  "token": "mock-token"
}
```

**Errors:**
- `400` - Missing JSON body
- `401` - Invalid credentials
- `403` - Account inactive

**Session Data Set:**
- `logged_in`: `True`
- `email`: User email
- `user_id`: User ID
- `is_admin`: Admin status

**Logs:**
- `LOGIN_SUCCESS` or `LOGIN_FAIL` to session log

---

### `POST /register`
User registration endpoint. Creates a new user account with pending status.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "message": "Registration successful. Pending admin approval."
}
```

**Errors:**
- `400` - Missing JSON body or password too short (< 8 chars)
- `409` - Email already registered or pending

**Actions:**
- Creates user with unique ID
- Saves to pending users database
- Sends email notification to admins

---

### `POST /logout`
User logout endpoint.

**Response (200):**
```json
{
  "message": "Logged out"
}
```

**Actions:**
- Logs logout event
- Marks user offline
- Clears all session data

---

### `POST /forgot-password`
Request password reset endpoint.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset link sent"
}
```

**Errors:**
- `404` - Email not found

**Actions:**
- Generates secure token (1 hour expiration)
- Sends password reset email with token link

---

### `POST /reset-password/<token>`
Reset password endpoint.

**URL Parameters:**
- `token` (str): Password reset token from email

**Request Body:**
```json
{
  "password": "newpassword123"
}
```

**Response (200):**
```json
{
  "message": "Your password has been updated successfully."
}
```

**Errors:**
- `400` - Invalid/expired token, missing JSON body, or password too short
- `500` - Error updating password

**Validations:**
- Token must be valid and not expired (1 hour)
- Password must be at least 8 characters

---

## Helper Functions

### `email_exists(email: str) -> bool`
Checks if an email exists in auth, pending, or denied users.

**Parameters:**
- `email` (str): Email address to check

**Returns:**
- `bool`: True if email exists in any user database

---

## Session Management

- **Timeout:** 15 minutes
- **Extension:** Automatic on each request via `before_request` hook
- **Session Keys:**
  - `logged_in`: Boolean authentication status
  - `email`: User email address
  - `user_id`: Unique user identifier
  - `is_admin`: Boolean admin status

---

## Dependencies

- `flask.Blueprint` - Route organization
- `flask.session` - Session management
- `werkzeug.security` - Password hashing
- `itsdangerous` - Token generation
- `models.user_entity.User` - User entity
- `services.mail_service` - Email notifications
- `services.auth_service` - Session tracking
- `utils` - Logging and ID generation

