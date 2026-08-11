# Module `merkaz_backend/models/upload_entity.py`

Upload entity definition.
Represents a file upload with its metadata.

## Classes

### `Upload`

No description provided.

#### Methods

- `__init__(self, upload_id: str, timestamp: str, email: str, user_id: Optional[str], filename: str, path: str, status: str='pending')`
  - No description provided.
  - Arguments:
    - `self`
    - `upload_id` : `str`
    - `timestamp` : `str`
    - `email` : `str`
    - `user_id` : `Optional[str]`
    - `filename` : `str`
    - `path` : `str`
    - `status` : `str` (default: `'pending'`)

- `to_dict(self)`
  - Returns a dictionary representation of the upload.
  - Arguments:
    - `self`
