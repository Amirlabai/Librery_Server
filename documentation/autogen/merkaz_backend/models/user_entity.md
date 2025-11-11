# Module `merkaz_backend/models/user_entity.py`

## Classes

### `User`

No description provided.

#### Methods

- `__init__(self, email, password, role='user', status='active', user_id=None)`
  - No description provided.
  - Arguments:
    - `self`
    - `email`
    - `password`
    - `role` (default: `'user'`)
    - `status` (default: `'active'`)
    - `user_id` (default: `None`)

- `is_admin(self)`
  - No description provided.
  - Arguments:
    - `self`

- `is_active(self)`
  - No description provided.
  - Arguments:
    - `self`

- `check_password(self, password_to_check)`
  - Checks the provided password against the stored hash.
  - Arguments:
    - `self`
    - `password_to_check`

- `find_by_email(email)`
  - Finds a user by email in the authentication database.
  - Arguments:
    - `email`

- `get_all()`
  - Reads all users from the authentication database.

- `save_all(users)`
  - Rewrites the entire auth user database.
  - Arguments:
    - `users`

- `get_admin_emails()`
  - Returns a list of all admin email addresses.

- `find_pending_by_email(email)`
  - Finds a user by email in the pending database.
  - Arguments:
    - `email`

- `get_pending()`
  - Reads all users from the pending registration database.

- `save_pending(users)`
  - Rewrites the entire pending user database.
  - Arguments:
    - `users`

- `find_denied_by_email(email)`
  - Finds a user by email in the denied database.
  - Arguments:
    - `email`

- `get_denied()`
  - Reads all users from the denied registration database.

- `save_denied(users)`
  - Rewrites the entire denied user database.
  - Arguments:
    - `users`

- `_read_users_from_file(filepath)`
  - Helper to read users from a given CSV file.
  - Arguments:
    - `filepath`

- `_save_users_to_file(filepath, users)`
  - Helper to write a list of users to a given CSV file.
  - Arguments:
    - `filepath`
    - `users`

- `to_dict(self)`
  - Returns a dictionary representation of the user, safe for JSON serialization.
  - Arguments:
    - `self`
