# Module `server/repositories/password_reset_repository.py`

Password reset token persistence (one-time use).

## Functions

### `_db_path()`

No description provided.

### `save_token(email: str, token: str)`

No description provided.

**Arguments:**
- `email` : `str`
- `token` : `str`

### `token_exists(email: str, token: str)`

No description provided.

**Arguments:**
- `email` : `str`
- `token` : `str`

### `delete_token(email: str, token: str)`

No description provided.

**Arguments:**
- `email` : `str`
- `token` : `str`
