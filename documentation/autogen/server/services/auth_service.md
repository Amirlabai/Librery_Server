# Module `server/services/auth_service.py`

Auth service - Authentication and session handling.

## Functions

### `mark_user_online()`

No description provided.

### `mark_user_offline()`

No description provided.

### `cleanup_expired_sessions()`

No description provided.

### `get_active_users()`

No description provided.

### `is_user_authenticated()`

No description provided.

### `is_user_admin()`

No description provided.

### `get_current_user_email()`

No description provided.

### `get_current_user_id()`

No description provided.

## Classes

### `AuthService`

Service for authentication operations.

#### Methods

- `login(email, password)`
  - Authenticate a user and create session.
  - Arguments:
    - `email`
    - `password`

- `register(email, password, first_name, last_name)`
  - Register a new user.
  - Arguments:
    - `email`
    - `password`
    - `first_name`
    - `last_name`

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
  - Validate session; clear if invalidated.

- `get_current_email()`
  - Resolve current user email from JWT or Flask session.

- `require_auth()`
  - Populate g.current_user_email or return (False, error).

- `find_user_by_email(email)`
  - No description provided.
  - Arguments:
    - `email`

- `email_exists(email)`
  - No description provided.
  - Arguments:
    - `email`

- `is_user_boss_admin(email)`
  - No description provided.
  - Arguments:
    - `email`

- `is_outside_user(email)`
  - Check if a user is an outside user (username part, case-insensitive).
  - Arguments:
    - `email`

- `build_login_response(user)`
  - Build login JSON payload including JWT.
  - Arguments:
    - `user`
