# Module `merkaz_backend/dev_toolkit/set_boss_admin_gui.py`

Tkinter GUI for managing boss admin status.
Shows a list of users and allows setting/revoking boss admin status.
Usage: python set_boss_admin_gui.py

## Functions

### `main()`

Main entry point.

## Classes

### `BossAdminGUI`

No description provided.

#### Methods

- `__init__(self, root)`
  - No description provided.
  - Arguments:
    - `self`
    - `root`

- `create_widgets(self)`
  - Create and layout all GUI widgets.
  - Arguments:
    - `self`

- `get_username(self, email)`
  - Extract username part from email (before @).
  - Arguments:
    - `self`
    - `email`

- `refresh_user_list(self)`
  - Refresh the user list and boss admins list.
  - Arguments:
    - `self`

- `on_search_change(self, *args)`
  - Handle search box changes.
  - Arguments:
    - `self`
    - `*args` [vararg]

- `update_boss_admins_list(self)`
  - Update the boss admins listbox.
  - Arguments:
    - `self`

- `on_user_select(self, event)`
  - Handle user selection from main list.
  - Arguments:
    - `self`
    - `event`

- `on_boss_admin_select(self, event)`
  - Handle boss admin selection from boss admins list.
  - Arguments:
    - `self`
    - `event`

- `update_user_info(self)`
  - Update the user info display and button states.
  - Arguments:
    - `self`

- `set_boss_admin(self)`
  - Set selected user as boss admin.
  - Arguments:
    - `self`

- `revoke_boss_admin(self)`
  - Revoke boss admin status from selected user.
  - Arguments:
    - `self`

- `on_ok(self)`
  - Handle OK button click.
  - Arguments:
    - `self`

- `on_cancel(self)`
  - Handle Cancel button click.
  - Arguments:
    - `self`
