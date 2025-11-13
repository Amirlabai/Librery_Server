# Module `merkaz_backend/models/user_entity.py`

## Classes

### `User`

Base class for all user types. Implements common functionality.

#### Methods

- `__init__(self, email, password, role='user', status='active', user_id=None, is_boss_admin=False)`
  - No description provided.
  - Arguments:
    - `self`
    - `email`
    - `password`
    - `role` (default: `'user'`)
    - `status` (default: `'active'`)
    - `user_id` (default: `None`)
    - `is_boss_admin` (default: `False`)

- `is_admin(self)`
  - Returns True if user is an admin. Overridden in Admin class.
  - Arguments:
    - `self`

- `is_active(self)`
  - Returns True if user status is active.
  - Arguments:
    - `self`

- `is_boss_admin(self)`
  - Returns True if user is a boss admin (set manually by dev).
  - Arguments:
    - `self`

- `check_password(self, password_to_check)`
  - Checks the provided password against the stored hash.
  - Arguments:
    - `self`
    - `password_to_check`

- `get_permissions(self)`
  - Returns a list of permissions for this user type. Polymorphic method.
  - Arguments:
    - `self`

- `can_manage_users(self)`
  - Returns True if user can manage other users. Polymorphic method.
  - Arguments:
    - `self`

- `to_dict(self)`
  - Returns a dictionary representation of the user, safe for JSON serialization.
  - Arguments:
    - `self`

- `create_user(email, password, role='user', status='active', user_id=None, is_boss_admin=False)`
  - Factory method to create the appropriate user type based on role. Polymorphic factory.
  - Arguments:
    - `email`
    - `password`
    - `role` (default: `'user'`)
    - `status` (default: `'active'`)
    - `user_id` (default: `None`)
    - `is_boss_admin` (default: `False`)

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

- `toggle_role(email)`
  - Toggles the role of a user between 'admin' and 'user'. Uses polymorphism to change instance type.
  - Arguments:
    - `email`

- `toggle_status(email)`
  - Toggles the status of a user between 'active' and 'inactive'.
  - Arguments:
    - `email`

- `_read_users_from_file(filepath)`
  - Helper to read users from a given CSV file.
  - Arguments:
    - `filepath`

- `_save_users_to_file(filepath, users)`
  - Helper to write a list of users to a given CSV file.
  - Arguments:
    - `filepath`
    - `users`

### `RegularUser`

Regular user class. Inherits from User base class.

#### Methods

- `__init__(self, email, password, status='active', user_id=None, is_boss_admin=False)`
  - No description provided.
  - Arguments:
    - `self`
    - `email`
    - `password`
    - `status` (default: `'active'`)
    - `user_id` (default: `None`)
    - `is_boss_admin` (default: `False`)

- `is_admin(self)`
  - Regular users are not admins.
  - Arguments:
    - `self`

- `get_permissions(self)`
  - Returns permissions for regular users.
  - Arguments:
    - `self`

- `can_manage_users(self)`
  - Regular users cannot manage other users.
  - Arguments:
    - `self`

### `Admin`

Admin user class. Inherits from User base class with admin privileges.

#### Methods

- `__init__(self, email, password, status='active', user_id=None, is_boss_admin=False)`
  - No description provided.
  - Arguments:
    - `self`
    - `email`
    - `password`
    - `status` (default: `'active'`)
    - `user_id` (default: `None`)
    - `is_boss_admin` (default: `False`)

- `is_admin(self)`
  - Admin users are always admins.
  - Arguments:
    - `self`

- `get_permissions(self)`
  - Returns permissions for admin users. Overrides parent method.
  - Arguments:
    - `self`

- `can_manage_users(self)`
  - Admin users can manage other users. Overrides parent method.
  - Arguments:
    - `self`
