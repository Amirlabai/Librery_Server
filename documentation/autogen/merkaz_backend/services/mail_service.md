# Module `merkaz_backend/services/mail_service.py`

Mail service - Email sending and notifications.

## Functions

### `_send_new_user_notification_sync(app, user_email, pending_url)`

Internal function that actually sends the email (runs in background thread).

**Arguments:**
- `app`
- `user_email`
- `pending_url`

### `send_new_user_notification(app, user_email)`

Notifies all admins that a new user has registered (asynchronously).

**Arguments:**
- `app`
- `user_email`

### `_send_approval_email_sync(app, user_email, login_url)`

Internal function that actually sends the email (runs in background thread).

**Arguments:**
- `app`
- `user_email`
- `login_url`

### `send_approval_email(app, user_email)`

Sends an email to the user when their account is approved (asynchronously).

**Arguments:**
- `app`
- `user_email`

### `_send_denial_email_sync(app, user_email)`

Internal function that actually sends the email (runs in background thread).

**Arguments:**
- `app`
- `user_email`

### `send_denial_email(app, user_email)`

Sends an email to the user when their account is denied (asynchronously).

**Arguments:**
- `app`
- `user_email`

### `_send_password_reset_email_sync(app, user_email, token, reset_url)`

Internal function that actually sends the email (runs in background thread).

**Arguments:**
- `app`
- `user_email`
- `token`
- `reset_url`

### `send_password_reset_email(app, user_email, token)`

Sends a password reset email to the user (asynchronously).

**Arguments:**
- `app`
- `user_email`
- `token`
