# Module `merkaz_backend/repositories/user_repository.py`

User repository - Data access layer for user data (CSV or DB).

## Classes

### `UserRepository`

Repository for user data operations.

#### Methods

- `find_by_email(email)`
  - Find a user by email in the authentication database.
  - Arguments:
    - `email`

- `find_pending_by_email(email)`
  - Find a user by email in the pending database.
  - Arguments:
    - `email`

- `find_denied_by_email(email)`
  - Find a user by email in the denied database.
  - Arguments:
    - `email`

- `get_all()`
  - Get all authenticated users.

- `save_all(users)`
  - Save all authenticated users.
  - Arguments:
    - `users`

- `get_pending()`
  - Get all pending users.

- `save_pending(users)`
  - Save all pending users.
  - Arguments:
    - `users`

- `get_denied()`
  - Get all denied users.

- `save_denied(users)`
  - Save all denied users.
  - Arguments:
    - `users`

- `get_admin_emails()`
  - Get all admin email addresses.

- `create_user(email, password, role, status, user_id)`
  - Create a new user using the factory method.
  - Arguments:
    - `email`
    - `password`
    - `role`
    - `status`
    - `user_id`

- `toggle_role(email)`
  - Toggle a user's role between admin and user.
  - Arguments:
    - `email`

- `toggle_status(email)`
  - Toggle a user's status between active and inactive.
  - Arguments:
    - `email`
