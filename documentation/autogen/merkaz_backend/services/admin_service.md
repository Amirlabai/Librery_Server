# Module `merkaz_backend/services/admin_service.py`

Admin service - Admin operations, approvals, and reports.

## Classes

### `AdminService`

Service for admin operations.

#### Methods

- `approve_user(email)`
  - Approve a pending user registration.
  - Arguments:
    - `email`

- `deny_user(email)`
  - Deny a pending user registration.
  - Arguments:
    - `email`

- `toggle_user_role(email)`
  - Toggle a user's role between admin and user. Uses polymorphic User.toggle_role().
  - Arguments:
    - `email`

- `toggle_user_status(email)`
  - Toggle a user's status between active and inactive. Uses User.toggle_status().
  - Arguments:
    - `email`

- `re_pend_user(email)`
  - Move a denied user back to pending.
  - Arguments:
    - `email`
