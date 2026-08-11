# Module `server/services/session_state_store.py`

File-backed session state for multi-worker deployments.

## Functions

### `_state_path()`

No description provided.

### `_load()`

No description provided.

### `_save(data: dict)`

No description provided.

**Arguments:**
- `data` : `dict`

### `get_token_version(email: str)`

No description provided.

**Arguments:**
- `email` : `str`

### `bump_token_version(email: str)`

No description provided.

**Arguments:**
- `email` : `str`

### `clear_invalidation(email: str)`

No description provided.

**Arguments:**
- `email` : `str`

### `is_invalidated(email: str)`

No description provided.

**Arguments:**
- `email` : `str`

### `mark_online(email: str)`

No description provided.

**Arguments:**
- `email` : `str`

### `mark_offline(email: str)`

No description provided.

**Arguments:**
- `email` : `str`

### `cleanup_expired(timeout_minutes: int)`

No description provided.

**Arguments:**
- `timeout_minutes` : `int`

### `list_active()`

No description provided.
