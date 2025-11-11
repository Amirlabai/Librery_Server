# Module `merkaz_backend/controllers/uploads_controller.py`

## Functions

### `remove_from_pending_log(upload_id)`

Removes an entry from the pending log by upload_id.
Returns the removed row data if found, None otherwise.

**Arguments:**
- `upload_id`

### `allowed_file(filename)`

No description provided.

**Arguments:**
- `filename`

### `is_file_malicious(file_stream)`

Checks the magic number of a file to determine if it's potentially malicious.

**Arguments:**
- `file_stream`

### `get_unique_filename(upload_dir, filename, share_dir=None, share_subpath='', save_flat=True)`

Generates a unique filename by appending _1, _2, etc. if a file with the same name exists.
Checks in both the upload directory and the share directory (eventual destination).

For folder uploads: saves files flat in uploads directory but preserves path in metadata.

Args:
    upload_dir: Base upload directory
    filename: Original filename (may include relative path for folder uploads)
    share_dir: Optional base share directory to check for conflicts
    share_subpath: Optional subpath in share directory where file will eventually be placed
    save_flat: If True, save files flat (no directory structure) in upload_dir

Returns:
    Tuple of (flat_filename_for_storage, full_save_path, full_relative_path_for_log)
    - flat_filename_for_storage: Filename to use for actual file storage (flat, no directories)
    - full_save_path: Full path where file will be saved in upload_dir
    - full_relative_path_for_log: Full relative path including folder structure (for logging/reconstruction)

**Arguments:**
- `upload_dir`
- `filename`
- `share_dir` (default: `None`)
- `share_subpath` (default: `''`)
- `save_flat` (default: `True`)

### `upload_file()`

No description provided.

### `my_uploads()`

No description provided.

### `admin_uploads()`

No description provided.

### `move_upload(filename)`

No description provided.

**Arguments:**
- `filename`

### `decline_upload(filename)`

No description provided.

**Arguments:**
- `filename`

### `edit_upload_path()`

No description provided.

### `move_file(upload_id, old_path, new_path)`

No description provided.

**Arguments:**
- `upload_id`
- `old_path`
- `new_path`
