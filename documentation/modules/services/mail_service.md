# mail_service.py

Mail service for sending email notifications.

## Location
`merkaz_backend/services/mail_service.py`

## Overview

Handles all email notifications including user registration alerts, approval/denial notifications, and password reset emails. All emails are sent asynchronously in background threads.

## Global Variables

### `mail: Mail`
Flask-Mail instance for sending emails. Must be initialized with Flask app context.

## Functions

### `send_new_user_notification(app, user_email: str) -> None`
Notify all admins that a new user has registered.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of newly registered user

**Actions:**
- Sends email to all admin users (BCC)
- Includes link to pending approvals page
- Runs asynchronously in background thread

**Email Content:**
- **Subject:** "New User Registration"
- **Recipients:** All admin emails (BCC)
- **Body:** HTML email with user email and approval link

---

### `send_approval_email(app, user_email: str) -> None`
Send email when user account is approved.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of approved user

**Actions:**
- Sends approval notification email
- Includes login link
- Runs asynchronously in background thread

**Email Content:**
- **Subject:** "Your Account has been Approved!"
- **Recipients:** User email
- **Body:** HTML email with approval message and login link

---

### `send_denial_email(app, user_email: str) -> None`
Send email when user account is denied.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of denied user

**Actions:**
- Sends denial notification email
- Runs asynchronously in background thread

**Email Content:**
- **Subject:** "Your Registration Status"
- **Recipients:** User email
- **Body:** HTML email with denial message

---

### `send_password_reset_email(app, user_email: str, token: str) -> None`
Send password reset email with token link.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of user requesting reset
- `token` (str): Password reset token

**Actions:**
- Sends password reset email with token link
- Link expires in 1 hour
- Runs asynchronously in background thread

**Email Content:**
- **Subject:** "Password Reset Request"
- **Recipients:** User email
- **Body:** HTML email with reset link (1 hour expiration)

---

## Internal Functions

### `_send_new_user_notification_sync(app, user_email: str, pending_url: str) -> None`
Internal function that actually sends the new user notification email.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of new user
- `pending_url` (str): URL to pending approvals page

**Runs in:** Background thread with app context

---

### `_send_approval_email_sync(app, user_email: str, login_url: str) -> None`
Internal function that actually sends the approval email.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of approved user
- `login_url` (str): URL to login page

**Runs in:** Background thread with app context

---

### `_send_denial_email_sync(app, user_email: str) -> None`
Internal function that actually sends the denial email.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of denied user

**Runs in:** Background thread with app context

---

### `_send_password_reset_email_sync(app, user_email: str, token: str, reset_url: str) -> None`
Internal function that actually sends the password reset email.

**Parameters:**
- `app`: Flask application instance
- `user_email` (str): Email of user
- `token` (str): Password reset token
- `reset_url` (str): URL to password reset page

**Runs in:** Background thread with app context

---

## Threading

All email sending functions use background threads:
- **Thread Type:** Daemon threads
- **App Context:** Each thread gets its own app context
- **Error Handling:** Logs errors but doesn't raise exceptions

---

## Configuration

Email settings are configured in `config.config`:
- `MAIL_SERVER` - SMTP server address
- `MAIL_PORT` - SMTP server port
- `MAIL_USERNAME` - Email username
- `MAIL_PASSWORD` - Email password
- `MAIL_USE_TLS` - Use TLS encryption
- `MAIL_USE_SSL` - Use SSL encryption
- `MAIL_DEFAULT_SENDER` - Default sender email

---

## Dependencies

- `flask_mail.Mail` - Email sending
- `flask.url_for` - URL generation
- `flask.current_app` - Application context
- `threading` - Background thread execution
- `models.user_entity.User` - Admin email retrieval
- `config.config` - Email configuration

---

## Usage Example

```python
from services.mail_service import send_approval_email

# Send approval email
send_approval_email(current_app._get_current_object(), "user@example.com")
```

