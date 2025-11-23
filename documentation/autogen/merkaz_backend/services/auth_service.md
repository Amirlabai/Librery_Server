# Module `merkaz_backend/services/auth_service.py`

Auth service - Authentication and session handling.

## Functions

### `mark_user_online()`

Mark the current user as online.

### `mark_user_offline()`

Mark the current user as offline.

### `get_active_users()`

Get list of currently active users.

### `is_user_authenticated()`

Check if the current user is authenticated.

### `is_user_admin()`

Check if the current user is an admin.

### `get_current_user_email()`

Get the email of the current user.

### `get_current_user_id()`

Get the user ID of the current user.

## Classes

### `AuthService`

Service for authentication operations.

#### Methods

- `login(email, password)`
  - Authenticate a user and create session.
  - Arguments:
    - `email`
    - `password`

- `register(email, password)`
  - Register a new user.
  - Arguments:
    - `email`
    - `password`

- `reset_password(email, new_password)`
  - Reset a user's password.
  - Arguments:
    - `email`
    - `new_password`

- `refresh_session()`
  - Refresh the current user's session with latest data from database.

- `create_session(user)`
  - Create a session for the given user.
  - Arguments:
    - `user`

- `clear_session()`
  - Clear the current session.

- `invalidate_user_session(email)`
  - Invalidate all sessions for a specific user by email.
  - Arguments:
    - `email`

- `is_session_valid()`
  - Check if the current session is valid (not invalidated).

- `validate_and_clear_if_invalidated()`
  - Validate the current session and clear it if it has been invalidated.
Returns (is_valid, error_message) tuple.

- `find_user_by_email(email)`
  - Find a user by email in authenticated users.
  - Arguments:
    - `email`

- `email_exists(email)`
  - Check if an email exists in auth, pending, or denied users.
  - Arguments:
    - `email`

- `is_user_boss_admin(email)`
  - Check if a user is a boss admin.
  - Arguments:
    - `email`

- `is_outside_user(email)`
  - Check if a user is an outside user without pandas.
  - Arguments:
    - `email`
